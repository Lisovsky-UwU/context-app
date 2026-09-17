import type { Category, PlaceStatus } from "../api/types"

export const CATEGORIES: { value: Category; label: string }[] = [
  { value: "bar", label: "Бар" },
  { value: "cafe", label: "Кофейня" },
  { value: "restaurant", label: "Ресторан" },
  { value: "culture", label: "Культура" },
  { value: "activity", label: "Активность" },
  { value: "nature", label: "Природа" },
  { value: "other", label: "Другое" },
]

export function categoryLabel(value: Category): string {
  return CATEGORIES.find((item) => item.value === value)?.label ?? "Другое"
}

export const STATUS_LABEL: Record<PlaceStatus, string> = {
  wish: "Хотим",
  planned: "Запланировано",
  visited: "Были",
}

export function plural(count: number, one: string, few: string, many: string): string {
  const mod10 = count % 10
  const mod100 = count % 100
  if (mod10 === 1 && mod100 !== 11) return one
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few
  return many
}
