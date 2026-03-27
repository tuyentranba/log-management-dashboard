# Technology Choices

Rationale for all major technology decisions in the Logs Dashboard project.

## Philosophy

Technology choices prioritize:
1. **Production-readiness:** Mature libraries with active maintenance
2. **Performance:** Sub-500ms queries, fast initial page load
3. **Developer experience:** Type safety, auto-generated docs, modern patterns
4. **Portfolio demonstration:** Showcase current best practices (2025-2026)

## Backend Stack

### FastAPI 0.135.1

**What:** Modern, async Python web framework with automatic API documentation.

**Why chosen:**
- **Async/await native:** Non-blocking database operations with SQLAlchemy async
- **Automatic API docs:** /docs endpoint generates OpenAPI/Swagger documentation from code
- **Pydantic integration:** Request/response validation with type hints
- **Performance:** Comparable to Node.js/Go for I/O-bound workloads
- **Developer experience:** Type hints enable IDE autocomplete, catch errors at development time

**Alternatives considered:**
- **Django REST Framework:** More features (admin, auth) but heavier, sync-only (WSGI)
- **Flask:** Lighter but requires manual OpenAPI docs, no built-in async support
- **Node.js (Express):** JavaScript eliminates backend/frontend language split, but Python better for data processing

**Trade-offs accepted:**
- Python slower than Rust/Go for CPU-bound work (not a concern for database-backed API)
- Smaller ecosystem than Django (acceptable - don't need full framework features)

### PostgreSQL 18

**What:** Open-source relational database with advanced time-series features.

**Why chosen:**
- **BRIN indexes:** Optimized for time-series data (0.1% storage overhead vs 5% B-tree)
- **timestamptz:** Timezone-aware timestamps prevent timezone bugs
- **Mature aggregations:** date_trunc, COUNT FILTER for analytics queries
- **Free and open-source:** No licensing costs, self-hostable
- **Industry standard:** Well-understood, extensive documentation

**Alternatives considered:**
- **TimescaleDB:** Purpose-built for time-series, but adds complexity (extension installation, learning curve)
- **MySQL:** Popular but weaker time-series support (no BRIN, worse date_trunc)
- **MongoDB:** Schema-less flexibility, but loses ACID guarantees and SQL query power

**Trade-offs accepted:**
- Requires relational schema (acceptable - log structure is fixed)
- No built-in full-text search (using ILIKE for MVP, GIN index deferred to v2)

**Related:** See [ADR-003: Database Indexing](./decisions/003-database-indexing.md) for BRIN + composite index strategy.

### SQLAlchemy 2.0.48

**What:** Python ORM with async support and advanced query building.

**Why chosen:**
- **Async/await:** Non-blocking queries with async engine and AsyncSession
- **Type safety:** Modern API with type hints for IDE support
- **stream() API:** Memory-efficient batch fetching with yield_per()
- **Migration support:** Alembic integration for database versioning
- **Flexibility:** Can drop to raw SQL when needed (no ORM lock-in)

**Alternatives considered:**
- **Raw SQL:** Maximum performance, but loses type safety and requires manual query building
- **Tortoise ORM:** Django-like async ORM, but less mature and smaller community
- **PonyORM:** Pythonic query syntax, but no async support

**Trade-offs accepted:**
- ORM overhead (~10% performance vs raw SQL, acceptable for readability gain)
- Learning curve (SQLAlchemy 2.0 API differs from 1.x)

### pytest + pytest-cov 6.0.0

**What:** Python testing framework with async support and code coverage measurement.

**Why chosen:**
- **asyncio_mode='auto':** Automatic async test detection (no @pytest.mark.asyncio decorators)
- **Fixtures:** Reusable test setup (database, client, mock data)
- **Coverage integration:** pytest-cov plugin measures line coverage with --cov flag
- **Performance testing:** Supports @pytest.mark.slow for optional performance tests

**Alternatives considered:**
- **unittest:** Built-in but verbose, no async support, requires self.assertEqual syntax
- **nose2:** Similar to pytest but less maintained

**Trade-offs accepted:**
- Requires pytest-cov plugin for coverage (small dependency)

## Frontend Stack

### Next.js 15.5.14

**What:** React framework with Server Components, App Router, and built-in optimizations.

**Why chosen:**
- **Server Components:** SSR performance without client-side data fetching waterfall
- **App Router:** Modern file-based routing with layouts and parallel routes
- **Zero-config:** TypeScript, Tailwind, image optimization work out of the box
- **Production-ready:** Used by Vercel, Netflix, TikTok - proven at scale
- **Developer experience:** Fast Refresh, built-in dev server, clear error messages

**Alternatives considered:**
- **Create React App:** Simpler setup but no SSR, client-only rendering (slower initial load)
- **Remix:** Similar SSR benefits, but smaller ecosystem and less mature
- **Vite + React:** Fast dev server, but requires manual SSR setup

**Trade-offs accepted:**
- Framework lock-in (Vercel-specific patterns)
- Server Components learning curve (new mental model vs traditional React)

**Related:** See [ADR-005: Frontend Architecture](./decisions/005-frontend-architecture.md) for Server/Client Component strategy.

### React 19.2.4

**What:** Latest React version with improved async rendering and Server Components support.

**Why chosen:**
- **Async support:** Better handling of asynchronous data fetching in components
- **Performance:** Improved reconciliation and rendering speed vs React 18
- **Server Components:** Full support for Next.js 15 Server Components pattern
- **Modern hooks:** useTransition, useDeferredValue for better UX during slow operations

**Alternatives considered:**
- **Vue 3:** Simpler API (Composition API), but smaller ecosystem for UI components
- **Svelte:** Fastest runtime, but smaller community and job market
- **React 18:** Stable but missing React 19 performance improvements

**Trade-offs accepted:**
- React 19 is latest major release (potential breaking changes in ecosystem)
- Larger bundle size than Svelte/Preact (acceptable for portfolio - React is industry standard)

### TypeScript 5.9.3

**What:** Type-safe JavaScript with static analysis and IDE support.

**Why chosen:**
- **Type safety:** Catch bugs at compile time (missing fields, wrong types)
- **IDE autocomplete:** IntelliSense for API functions, component props
- **Refactoring confidence:** Rename function, IDE updates all call sites
- **Documentation:** Types serve as inline documentation
- **Industry standard:** Required for most professional React jobs

**Alternatives considered:**
- **JavaScript:** Simpler, no compilation step, but loses type safety and IDE benefits
- **JSDoc:** Type annotations in comments, but less strict and incomplete

**Trade-offs accepted:**
- Compilation step adds ~2-3 seconds to dev server startup
- Learning curve for advanced types (generics, conditional types)

### Tailwind CSS 3.4.17

**What:** Utility-first CSS framework with low-level utility classes.

**Why chosen:**
- **Rapid prototyping:** Build UI without writing CSS files
- **Consistency:** Design system enforced via utility classes (spacing, colors)
- **Performance:** Unused classes purged at build time (small bundle)
- **shadcn/ui compatibility:** Component library requires Tailwind 3.x (not v4)
- **No naming:** Avoids CSS class naming bikeshedding (BEM, OOCSS, etc.)

**Alternatives considered:**
- **CSS Modules:** Component-scoped CSS, but requires naming classes and writing CSS
- **Styled Components:** CSS-in-JS, but runtime performance cost and SSR complexity
- **Bootstrap:** Component library, but opinionated styling and large bundle

**Trade-offs accepted:**
- HTML cluttered with many utility classes (accepted for speed/consistency tradeoff)
- Custom designs require Tailwind config (acceptable - default palette covers 90% needs)

**Note:** Downgraded from Tailwind v4 to v3.4.17 for shadcn/ui compatibility (v4 has incompatible PostCSS architecture).

### shadcn/ui

**What:** Copy-paste component library built on Radix UI and Tailwind.

**Why chosen:**
- **Copy-paste model:** Components live in project (not node_modules), fully customizable
- **Radix UI primitives:** Accessible, unstyled components (ARIA attributes, keyboard navigation)
- **Tailwind styling:** Matches project styling system
- **No lock-in:** Can modify any component code directly
- **Modern design:** Professional look out of the box

**Alternatives considered:**
- **Material-UI:** Comprehensive but opinionated styling, large bundle, hard to customize
- **Chakra UI:** Accessible and themeable, but different mental model than Tailwind
- **Ant Design:** Enterprise-focused, but heavy and hard to customize

**Trade-offs accepted:**
- Components added to project (increases codebase size)
- Manual updates (run shadcn CLI to update components)

### Jest 29.7.0 + React Testing Library 16.3.2

**What:** Testing framework for React components with user-focused testing approach.

**Why chosen:**
- **User-focused:** Test what users see/do (not implementation details)
- **Accessibility:** jest-axe integration validates ARIA attributes
- **Fast:** Tests run in parallel with jsdom (no browser needed)
- **Community standard:** Most popular React testing library

**Alternatives considered:**
- **Cypress:** E2E testing with real browser, but slower and more complex setup
- **Playwright:** Modern E2E testing, but heavier than jest for component tests
- **Vitest:** Faster than Jest (Vite-based), but less mature ecosystem

**Trade-offs accepted:**
- jsdom limitations (no layout, can't test CSS positioning)

## Infrastructure

### Docker Compose

**What:** Container orchestration for local development.

**Why chosen:**
- **Consistent environment:** Same versions across all developers
- **Easy setup:** Single `docker-compose up` command starts all services
- **Isolated dependencies:** Backend Python, frontend Node.js don't conflict
- **Production parity:** Same container images can deploy to production

**Alternatives considered:**
- **Local installation:** Simpler, but "works on my machine" problems
- **Kubernetes:** Production-grade, but overkill for local development

**Trade-offs accepted:**
- Docker Desktop resource usage (~2-4GB RAM)
- Slower file watching on macOS (volume mount performance)

### Alembic

**What:** Database migration tool for SQLAlchemy.

**Why chosen:**
- **Version control:** Migrations in git, reviewable in PRs
- **Rollback support:** Can revert migrations if needed
- **Auto-generation:** alembic revision --autogenerate detects model changes
- **SQLAlchemy integration:** Uses same models as application

**Alternatives considered:**
- **Django migrations:** Automatic but requires Django framework
- **Raw SQL scripts:** Maximum control but no rollback support

**Trade-offs accepted:**
- Manual migration review needed (auto-generation isn't perfect)

## Why Not...?

### Why not NoSQL (MongoDB, DynamoDB)?

Logs have fixed schema (timestamp, severity, source, message) - relational model is natural fit. PostgreSQL time-series features (BRIN, date_trunc) specifically designed for this use case. NoSQL flexibility not needed.

### Why not GraphQL?

REST API is simpler for CRUD operations. GraphQL overhead (schema, resolvers, client libraries) not justified for straightforward log management. FastAPI auto-generates OpenAPI docs - GraphQL requires separate tools (GraphiQL).

### Why not microservices?

Monolithic backend is simpler for portfolio project. No independent scaling needs (logs API, analytics API have similar load). Microservices add complexity (service discovery, API gateway, distributed tracing) without benefit at this scale.

### Why not serverless (AWS Lambda, Vercel Functions)?

Local development with Docker Compose is easier. Serverless adds cold start latency (200-500ms) which breaks <500ms pagination requirement. Persistent database connection pooling simpler with traditional server.

### Why not Kubernetes?

Docker Compose sufficient for local development. Kubernetes adds significant complexity (YAML configs, cluster management, learning curve) without benefit for single-developer portfolio project. Can containerize for production deployment if needed.

## Version Pinning Strategy

**Exact versions specified** in package.json and requirements.txt for reproducibility. Lock files (package-lock.json, requirements.txt) committed to git.

**Update strategy:**
- Patch updates (0.135.1 → 0.135.2): Apply automatically (bug fixes)
- Minor updates (0.135.x → 0.136.x): Review changelog, update if no breaking changes
- Major updates (0.x → 1.x): Evaluate carefully, may require code changes

## Related Documentation

- [README.md](../README.md) - Technology stack summary
- [ARCHITECTURE.md](./ARCHITECTURE.md) - How technologies fit together
- [docs/decisions/](./decisions/) - ADRs documenting specific technology decisions

---

*Last updated: 2026-03-27 (Phase 7 documentation)*
