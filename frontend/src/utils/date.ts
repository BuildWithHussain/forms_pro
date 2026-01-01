import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import isToday from "dayjs/plugin/isToday";
import isYesterday from "dayjs/plugin/isYesterday";
import customParseFormat from "dayjs/plugin/customParseFormat";

// Extend dayjs with plugins
dayjs.extend(relativeTime);
dayjs.extend(isToday);
dayjs.extend(isYesterday);
dayjs.extend(customParseFormat);

/**
 * Format a date string or Date object to a readable date format
 * @param date - Date string, Date object, or dayjs object
 * @param format - Optional format string (default: "MMM D, YYYY")
 * @returns Formatted date string
 */
export function formatDate(
  date: string | Date | dayjs.Dayjs | null | undefined,
  format: string = "MMM D, YYYY"
): string {
  if (!date) return "";
  return dayjs(date).format(format);
}

/**
 * Format a date string or Date object to include both date and time
 * @param date - Date string, Date object, or dayjs object
 * @param format - Optional format string (default: "MMM D, YYYY h:mm A")
 * @returns Formatted datetime string
 */
export function formatDateTime(
  date: string | Date | dayjs.Dayjs | null | undefined,
  format: string = "MMM D, YYYY h:mm A"
): string {
  if (!date) return "";
  return dayjs(date).format(format);
}

/**
 * Format a date to a human-readable, pretty format
 * Shows relative time for recent dates, formatted date for older ones
 * @param date - Date string, Date object, or dayjs object
 * @returns Pretty formatted date string
 */
export function formatPrettyDate(
  date: string | Date | dayjs.Dayjs | null | undefined
): string {
  if (!date) return "";

  const dayjsDate = dayjs(date);
  const now = dayjs();
  const diffInDays = now.diff(dayjsDate, "day");

  if (dayjsDate.isToday()) {
    return "Today";
  }

  if (dayjsDate.isYesterday()) {
    return "Yesterday";
  }

  if (diffInDays < 7) {
    return dayjsDate.fromNow();
  }

  if (diffInDays < 365) {
    return dayjsDate.format("MMM D");
  }

  return dayjsDate.format("MMM D, YYYY");
}

/**
 * Format just the time portion of a date
 * @param date - Date string, Date object, or dayjs object
 * @param format - Optional format string (default: "h:mm A")
 * @returns Formatted time string
 */
export function formatTime(
  date: string | Date | dayjs.Dayjs | null | undefined,
  format: string = "h:mm A"
): string {
  if (!date) return "";
  return dayjs(date).format(format);
}

/**
 * Get relative time from now (e.g., "2 hours ago", "in 3 days")
 * @param date - Date string, Date object, or dayjs object
 * @returns Relative time string
 */
export function getRelativeTime(
  date: string | Date | dayjs.Dayjs | null | undefined
): string {
  if (!date) return "";
  return dayjs(date).fromNow();
}

/**
 * Check if a date is today
 * @param date - Date string, Date object, or dayjs object
 * @returns True if the date is today
 */
export function isDateToday(
  date: string | Date | dayjs.Dayjs | null | undefined
): boolean {
  if (!date) return false;
  return dayjs(date).isToday();
}

/**
 * Check if a date is in the past
 * @param date - Date string, Date object, or dayjs object
 * @returns True if the date is in the past
 */
export function isDatePast(
  date: string | Date | dayjs.Dayjs | null | undefined
): boolean {
  if (!date) return false;
  return dayjs(date).isBefore(dayjs());
}

/**
 * Check if a date is in the future
 * @param date - Date string, Date object, or dayjs object
 * @returns True if the date is in the future
 */
export function isDateFuture(
  date: string | Date | dayjs.Dayjs | null | undefined
): boolean {
  if (!date) return false;
  return dayjs(date).isAfter(dayjs());
}

/**
 * Get the difference between two dates in a specified unit
 * @param date1 - First date
 * @param date2 - Second date (defaults to now)
 * @param unit - Unit of difference (e.g., "day", "hour", "minute")
 * @returns Difference in the specified unit
 */
export function getDateDiff(
  date1: string | Date | dayjs.Dayjs | null | undefined,
  date2: string | Date | dayjs.Dayjs | null | undefined = dayjs(),
  unit: dayjs.ManipulateType = "day"
): number {
  if (!date1) return 0;
  return dayjs(date1).diff(dayjs(date2), unit);
}

/**
 * Format date in a short format (e.g., "12/25/2023")
 * @param date - Date string, Date object, or dayjs object
 * @returns Short formatted date string
 */
export function formatShortDate(
  date: string | Date | dayjs.Dayjs | null | undefined
): string {
  if (!date) return "";
  return dayjs(date).format("M/D/YYYY");
}

/**
 * Format date in ISO format (e.g., "2023-12-25")
 * @param date - Date string, Date object, or dayjs object
 * @returns ISO formatted date string
 */
export function formatISODate(
  date: string | Date | dayjs.Dayjs | null | undefined
): string {
  if (!date) return "";
  return dayjs(date).format("YYYY-MM-DD");
}
