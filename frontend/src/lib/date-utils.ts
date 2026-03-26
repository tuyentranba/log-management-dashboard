/**
 * Converts a Date object to datetime-local input format (YYYY-MM-DDTHH:mm:ss)
 * in the user's local timezone.
 *
 * datetime-local inputs expect local time format without timezone suffix.
 * This is used for both creating new logs (current time) and editing existing
 * logs (converting from ISO 8601 UTC to local time).
 *
 * @param date - Date object to convert (defaults to current time)
 * @returns Formatted string: "2026-03-26T19:30:45"
 */
export function toDatetimeLocalString(date: Date = new Date()): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')

  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
}
