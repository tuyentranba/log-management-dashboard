import {
  fetchLogs,
  fetchLogById,
  createLog,
  updateLog,
  deleteLog,
  exportLogs,
} from '@/lib/api'

// Mock global fetch
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('API Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({}),
    })
  })

  describe('fetchLogs', () => {
    it('returns paginated logs', async () => {
      const mockResponse = {
        logs: [
          { id: 1, timestamp: '2024-01-15T10:30:00Z', message: 'Log 1', severity: 'INFO', source: 'service-1' },
          { id: 2, timestamp: '2024-01-15T11:30:00Z', message: 'Log 2', severity: 'ERROR', source: 'service-2' },
        ],
        next_cursor: 'cursor123',
        has_more: true,
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await fetchLogs({})

      expect(result.logs).toHaveLength(2)
      expect(result.has_more).toBe(true)
      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/api/logs'))
    })

    it('includes filter parameters in query string', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ logs: [], has_more: false }),
      })

      await fetchLogs({ severity: ['ERROR'], source: 'api-service' })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('severity=ERROR')
      )
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('source=api-service')
      )
    })
  })

  describe('fetchLogById', () => {
    it('returns single log', async () => {
      const mockLog = { id: 1, timestamp: '2024-01-15T10:30:00Z', message: 'Log 1', severity: 'INFO', source: 'service-1' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLog,
      })

      const result = await fetchLogById(1)

      expect(result.id).toBe(1)
      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/api/logs/1'))
    })
  })

  describe('createLog', () => {
    it('sends POST with log data', async () => {
      const newLog = {
        timestamp: '2024-01-15T10:30:00Z',
        message: 'New log',
        severity: 'INFO' as const,
        source: 'test-service',
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, ...newLog }),
      })

      await createLog(newLog)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/logs'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(newLog),
        })
      )
    })
  })

  describe('updateLog', () => {
    it('sends PUT with id and updated data', async () => {
      const updatedLog = {
        timestamp: '2024-01-15T10:30:00Z',
        message: 'Updated log',
        severity: 'ERROR' as const,
        source: 'test-service',
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, ...updatedLog }),
      })

      await updateLog(1, updatedLog)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/logs/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(updatedLog),
        })
      )
    })
  })

  describe('deleteLog', () => {
    it('sends DELETE with id', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
      })

      await deleteLog(1)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/logs/1'),
        expect.objectContaining({
          method: 'DELETE',
        })
      )
    })
  })

  describe('exportLogs', () => {
    it('returns void and triggers download', async () => {
      const mockBlob = new Blob(['csv content'], { type: 'text/csv' })
      mockFetch.mockResolvedValueOnce({
        ok: true,
        blob: async () => mockBlob,
        headers: new Headers({
          'Content-Disposition': 'attachment; filename=logs-2024.csv'
        }),
      })

      // Mock DOM methods
      document.createElement = jest.fn().mockReturnValue({
        href: '',
        download: '',
        click: jest.fn(),
      })
      document.body.appendChild = jest.fn()
      document.body.removeChild = jest.fn()
      URL.createObjectURL = jest.fn()
      URL.revokeObjectURL = jest.fn()

      await exportLogs({})

      expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/api/export'))
    })
  })

  describe('error handling', () => {
    it('throws error when fetch fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      await expect(fetchLogs({})).rejects.toThrow()
    })

    it('throws error for 404 in fetchLogById', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      })

      await expect(fetchLogById(999)).rejects.toThrow()
    })

    it('handles error in createLog', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid data' }),
      })

      await expect(createLog({
        timestamp: '2024-01-15T10:30:00Z',
        message: 'Test',
        severity: 'INFO',
        source: 'test'
      })).rejects.toThrow('Invalid data')
    })

    it('handles 404 error in updateLog', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' }),
      })

      await expect(updateLog(999, {
        timestamp: '2024-01-15T10:30:00Z',
        message: 'Test',
        severity: 'INFO',
        source: 'test'
      })).rejects.toThrow('Log not found')
    })

    it('handles generic error in updateLog', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' }),
      })

      await expect(updateLog(1, {
        timestamp: '2024-01-15T10:30:00Z',
        message: 'Test',
        severity: 'INFO',
        source: 'test'
      })).rejects.toThrow('Server error')
    })

    it('handles 404 error in deleteLog', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' }),
      })

      await expect(deleteLog(999)).rejects.toThrow('Log not found')
    })

    it('handles generic error in deleteLog', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' }),
      })

      await expect(deleteLog(1)).rejects.toThrow('Server error')
    })

    it('handles error in exportLogs', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Export failed' }),
      })

      await expect(exportLogs({})).rejects.toThrow('Export failed')
    })
  })
})
