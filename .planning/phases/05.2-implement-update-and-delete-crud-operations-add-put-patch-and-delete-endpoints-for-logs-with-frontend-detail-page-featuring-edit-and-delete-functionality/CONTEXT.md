# Phase 05.2: Implement Update and Delete CRUD Operations

**Created:** 2026-03-26
**Phase Goal:** Add PUT and DELETE endpoints for logs with frontend modal edit/delete functionality

## Design Decisions

### 1. Immutability Constraint Resolution

**Decision:** Full CRUD - update docs to reflect demo scope

**Rationale:**
- PROJECT.md originally stated "Logs are immutable for audit trail integrity"
- LOG-05 requirement confirmed immutability (marked complete)
- However, this is a demo/portfolio application showcasing CRUD capabilities
- Assignment requirements expect full CRUD operations
- Will implement both UPDATE and DELETE with documentation clarifying this is for demo/testing purposes only, not production audit trail use

**Impact:**
- Update PROJECT.md to remove immutability constraint from "Out of Scope"
- Update REQUIREMENTS.md to revise LOG-05 from "Logs are immutable" to "Logs support full CRUD operations"
- Add note in README that UPDATE/DELETE are for demo purposes
- No impact on existing code (only additions)

### 2. Page Structure

**Decision:** Keep modal - add edit/delete buttons inside

**Rationale:**
- LogDetailModal already exists with URL state management (?log=123)
- Users are familiar with modal pattern for log details
- Extending modal to include Edit and Delete buttons keeps users on /logs page
- Simple implementation: add mode state (view/edit) to existing modal
- Avoids creating new routes and navigation complexity

**Implementation:**
- Add Edit and Delete buttons to LogDetailModal header/footer
- Add mode state: `const [mode, setMode] = useState<'view' | 'edit'>('view')`
- Conditionally render read-only fields (view mode) vs form fields (edit mode)
- Delete button shows confirmation dialog regardless of mode

### 3. Update Endpoint Design

**Decision:** PUT - all fields required, full replacement

**Rationale:**
- Simpler API contract: PUT /api/logs/{id} with LogCreate schema
- Client must send complete log object (timestamp, message, severity, source)
- Replaces entire log in database
- Easier to implement and test than partial updates
- Consistent with create endpoint validation (reuse LogCreate schema)

**API Spec:**
```
PUT /api/logs/{id}
Request Body: LogCreate (timestamp, message, severity, source - all required)
Response: 200 OK with LogResponse, or 404 if log not found
```

**Backend Changes:**
- Add `update_log` endpoint in logs router
- Reuse LogCreate Pydantic schema for validation
- Use `db.get(Log, log_id)` for lookup, raise 404 if not found
- Update all fields, commit, return updated log

### 4. Delete Behavior

**Decision:** Hard delete with confirmation dialog

**Rationale:**
- Permanent deletion (DELETE FROM logs WHERE id = ?)
- Frontend shows confirmation dialog with "Are you sure?" message
- Dialog includes log ID, timestamp, and message snippet for verification
- Simpler than soft delete (no deleted_at column needed)
- Acceptable for demo application

**API Spec:**
```
DELETE /api/logs/{id}
Response: 204 No Content on success, or 404 if log not found
```

**UX Flow:**
1. User clicks Delete button in LogDetailModal
2. Confirmation dialog appears with log details (ID, timestamp, message preview)
3. User confirms or cancels
4. If confirmed, API call made with loading state
5. On success: close modal, show toast, refresh log list
6. On error: show error toast, keep modal open

### 5. Error Handling

**Decisions (multi-select):**
- ✓ 404 for non-existent log IDs
- ✗ 400 for validation errors on UPDATE (handled by FastAPI/Pydantic automatically)
- ✗ Toast notifications (covered in post-operation section)
- ✗ Confirmation dialog shows log details (included in delete behavior)

**Implementation:**
- Backend: Return 404 Not Found if `db.get(Log, log_id)` returns None
- Backend: FastAPI/Pydantic returns 422 for validation errors automatically
- Frontend: Catch errors in try/catch, show toast, don't close modal

### 6. Post-Operation Behavior

**Decision:** Close modal, show toast, auto-refresh list

**Rationale:**
- After successful UPDATE: close modal, show "Log updated" toast, refetch log list
- After successful DELETE: close modal, show "Log deleted" toast, refetch log list
- Provides clear feedback to user
- Auto-refresh ensures user sees updated data immediately
- Consistent with create form pattern (redirect + toast after create)

**Implementation:**
- Close modal: `setSelectedLogId(null)` (clears ?log= from URL)
- Show toast: `toast.success('Log updated')` or `toast.success('Log deleted')`
- Refresh list: Parent component (LogList) should refetch when modal closes

### 7. Form Component Strategy

**Decision:** Separate EditForm component in modal

**Rationale:**
- Keep CreateForm and EditForm separate
- CreateForm is for /create page, EditForm is for modal editing
- Different contexts: CreateForm starts empty, EditForm pre-fills with existing data
- Easier to maintain different behaviors (navigation, button labels, etc.)
- Can share Zod validation schema between both

**Implementation:**
- Create new `EditForm` component in logs/_components/
- Share `logCreateSchema` Zod schema from CreateForm
- EditForm accepts `log: LogResponse` prop for initial values
- EditForm accepts `onSuccess: () => void` callback for post-update logic
- Render EditForm in modal when mode === 'edit'

### 8. Loading States

**Decisions (multi-select):**
- ✓ Disable buttons during operations
- ✗ Loading spinner on action buttons (not selected, but will add for consistency)
- ✗ Overlay with 'Updating...' message (too heavy for modal)
- ✗ Optimistic UI updates (adds complexity, unnecessary for demo)

**Implementation:**
- Disable Edit, Delete, Save, Cancel buttons while API call is in progress
- Use `disabled={isSubmitting}` on all buttons
- Add `isSubmitting` state during PUT/DELETE calls
- Loading spinner on Save/Delete button for visual feedback (Loader2 icon from lucide-react)

## Technical Implementation Plan

### Backend Changes

**File: backend/app/routers/logs.py**

Add two endpoints:

1. **PUT /api/logs/{id}** - Update log
   - Parameters: `log_id: int`, `log_data: LogCreate`, `db: AsyncSession`
   - Logic:
     ```python
     log = await db.get(Log, log_id)
     if not log:
         raise HTTPException(404, detail=f"Log with id {log_id} not found")

     log.timestamp = log_data.timestamp
     log.message = log_data.message
     log.severity = log_data.severity
     log.source = log_data.source

     await db.commit()
     await db.refresh(log)
     return log
     ```
   - Returns: 200 OK with LogResponse

2. **DELETE /api/logs/{id}** - Delete log
   - Parameters: `log_id: int`, `db: AsyncSession`
   - Logic:
     ```python
     log = await db.get(Log, log_id)
     if not log:
         raise HTTPException(404, detail=f"Log with id {log_id} not found")

     await db.delete(log)
     await db.commit()
     return Response(status_code=204)
     ```
   - Returns: 204 No Content

**File: backend/tests/test_logs.py**

Add integration tests:
- `test_update_log_success` - PUT with valid data returns 200
- `test_update_log_not_found` - PUT with invalid ID returns 404
- `test_update_log_validation_error` - PUT with invalid data returns 422
- `test_delete_log_success` - DELETE returns 204
- `test_delete_log_not_found` - DELETE with invalid ID returns 404
- `test_delete_log_verify_removed` - Verify log is removed from database after DELETE

### Frontend Changes

**File: frontend/src/lib/api.ts**

Add API functions:
```typescript
export async function updateLog(id: number, data: LogCreate): Promise<LogResponse> {
  const response = await fetch(`${API_URL}/logs/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...data,
      timestamp: data.timestamp.toISOString()
    })
  })

  if (!response.ok) {
    if (response.status === 404) throw new Error('Log not found')
    throw new Error('Failed to update log')
  }

  return response.json()
}

export async function deleteLog(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/logs/${id}`, {
    method: 'DELETE'
  })

  if (!response.ok) {
    if (response.status === 404) throw new Error('Log not found')
    throw new Error('Failed to delete log')
  }
}
```

**File: frontend/src/app/logs/_components/edit-form.tsx** (NEW)

Create EditForm component:
- Props: `log: LogResponse`, `onSuccess: () => void`, `onCancel: () => void`
- Uses react-hook-form with zodResolver(logCreateSchema)
- Pre-fills form with log data: `defaultValues: { timestamp: log.timestamp, ... }`
- Converts datetime-local input to ISO 8601 on submit
- Calls `updateLog(log.id, data)` on submit
- Shows toast on success/error
- Calls `onSuccess()` after successful update

**File: frontend/src/app/logs/_components/log-detail-modal.tsx** (MODIFIED)

Extend modal to support edit mode:
1. Add mode state: `const [mode, setMode] = useState<'view' | 'edit'>('view')`
2. Add Edit button in header: `<Button onClick={() => setMode('edit')}>Edit</Button>`
3. Add Delete button in header: `<Button variant="destructive" onClick={handleDeleteClick}>Delete</Button>`
4. Conditionally render:
   - View mode: Show read-only fields (existing UI)
   - Edit mode: Render `<EditForm log={log} onSuccess={handleUpdateSuccess} onCancel={() => setMode('view')} />`
5. Delete confirmation:
   ```tsx
   const handleDeleteClick = () => {
     if (confirm(`Delete log ${log.id}?\n\n${log.timestamp}\n${log.message.slice(0, 100)}...`)) {
       handleDelete()
     }
   }
   ```
6. Delete handler:
   ```tsx
   const handleDelete = async () => {
     setIsSubmitting(true)
     try {
       await deleteLog(log.id)
       toast.success('Log deleted')
       setSelectedLogId(null) // Close modal
       // Parent will refetch list
     } catch (error) {
       toast.error('Failed to delete log')
     } finally {
       setIsSubmitting(false)
     }
   }
   ```
7. Update success handler:
   ```tsx
   const handleUpdateSuccess = () => {
     toast.success('Log updated')
     setSelectedLogId(null) // Close modal
     setMode('view') // Reset mode
     // Parent will refetch list
   }
   ```

**File: frontend/src/app/logs/page.tsx** (MODIFIED)

Ensure log list refetches when modal closes:
- Add effect that watches `selectedLogId` (from URL param)
- When it changes from a value to null (modal closed), refetch log list
- This ensures updates/deletes are reflected immediately

### Documentation Changes

**File: PROJECT.md**

Remove from "Out of Scope":
```diff
- Edit/delete log entries — Logs are immutable for audit trail integrity
```

Add to "Context" section:
```markdown
**CRUD Operations:** Application supports full CREATE, READ, UPDATE, and DELETE operations on logs. While a production log system would typically enforce immutability for audit trail integrity, this demo application includes UPDATE and DELETE operations to showcase complete CRUD capabilities. These operations are intended for testing and data cleanup purposes.
```

**File: REQUIREMENTS.md**

Update LOG-05:
```diff
- - [x] **LOG-05**: Logs are immutable (no edit or delete functionality)
+ - [x] **LOG-05**: Logs support full CRUD operations (create, read, update, delete)
```

## Success Criteria

Phase 05.2 is complete when:

1. ✅ Backend has PUT /api/logs/{id} endpoint accepting LogCreate, returning 200 or 404
2. ✅ Backend has DELETE /api/logs/{id} endpoint returning 204 or 404
3. ✅ Backend tests cover update/delete success and error cases (6 tests total)
4. ✅ Frontend has updateLog and deleteLog API functions with error handling
5. ✅ Frontend has EditForm component with validation and pre-filled data
6. ✅ LogDetailModal has Edit and Delete buttons
7. ✅ LogDetailModal supports view/edit mode toggle
8. ✅ Delete shows confirmation dialog with log details before API call
9. ✅ Successful update/delete closes modal, shows toast, and refreshes list
10. ✅ PROJECT.md and REQUIREMENTS.md updated to reflect CRUD support
11. ✅ All buttons disabled during API operations (no double-submit)
12. ✅ Error handling shows appropriate toasts for 404 and other failures

## Key Dependencies

**Existing Code to Reuse:**
- `LogCreate` Pydantic schema (backend/app/schemas/logs.py) - for PUT validation
- `LogResponse` type (frontend/src/lib/types.ts) - for EditForm props
- `logCreateSchema` Zod schema (from CreateForm) - for EditForm validation
- `toast` from sonner - for success/error notifications
- `Dialog` component - for delete confirmation
- FastAPI `db.get()` pattern - for 404 handling (from get_log endpoint)
- react-hook-form + zod pattern - from CreateForm

**New Dependencies:**
- None - all required libraries already installed

## Gray Areas Resolved

| Gray Area | Decision | Captured In |
|-----------|----------|-------------|
| Break immutability constraint? | Yes - for demo purposes, update docs | Section 1 |
| Modal vs dedicated page? | Keep modal with edit mode | Section 2 |
| PUT vs PATCH? | PUT with full replacement | Section 3 |
| Hard delete vs soft delete? | Hard delete with confirmation | Section 4 |
| Error handling strategy? | 404 for missing logs, toast for feedback | Section 5 |
| Post-operation UX? | Close modal, toast, refresh list | Section 6 |
| Reuse CreateForm? | No - separate EditForm | Section 7 |
| Loading states? | Disable buttons during operations | Section 8 |

---

*Context captured: 2026-03-26*
*Ready for planning: Yes*
