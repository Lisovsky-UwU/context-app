const MONTHS = [
  "января", "февраля", "марта", "апреля", "мая", "июня",
  "июля", "августа", "сентября", "октября", "ноября", "декабря",
]
const WEEKDAYS = ["воскресенье", "понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]

export function parseDate(value: string): Date {
  const [year, month, day] = value.split("-").map(Number)
  return new Date(year, month - 1, day)
}

export function formatDate(value: string, options: { weekday?: boolean; year?: boolean } = {}): string {
  const date = parseDate(value)
  const showYear = options.year ?? date.getFullYear() !== new Date().getFullYear()
  const base = `${date.getDate()} ${MONTHS[date.getMonth()]}${showYear ? ` ${date.getFullYear()}` : ""}`
  return options.weekday ? `${base}, ${WEEKDAYS[date.getDay()]}` : base
}

export function formatTime(value: string | null): string {
  return value ? value.slice(0, 5) : ""
}

export function formatDateTime(date: string, time: string | null): string {
  const stamp = formatDate(date)
  return time ? `${stamp} в ${formatTime(time)}` : stamp
}

export function stampDate(value: string): string {
  const date = parseDate(value)
  const day = String(date.getDate()).padStart(2, "0")
  const month = String(date.getMonth() + 1).padStart(2, "0")
  return `${day}.${month}.${String(date.getFullYear()).slice(2)}`
}

export function daysUntil(value: string): number {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return Math.round((parseDate(value).getTime() - today.getTime()) / 86_400_000)
}

export function relativeDay(value: string): string {
  const days = daysUntil(value)
  if (days === 0) return "сегодня"
  if (days === 1) return "завтра"
  if (days === 2) return "послезавтра"
  if (days < 0) return formatDate(value)
  if (days <= 7) return `через ${days} дн.`
  return formatDate(value)
}
