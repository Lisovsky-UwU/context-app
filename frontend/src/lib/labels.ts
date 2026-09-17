import type { Category, PlaceStatus } from "../api/types"

/** Ключи палитры из tokens.css: у каждого свой оттенок в светлой и тёмной теме. */
export const ACCENTS: { value: string; label: string }[] = [
  { value: "pomegranate", label: "Гранат" },
  { value: "amber", label: "Янтарь" },
  { value: "plum", label: "Слива" },
  { value: "indigo", label: "Индиго" },
  { value: "mint", label: "Мята" },
  { value: "olive", label: "Олива" },
  { value: "teal", label: "Бирюза" },
  { value: "rose", label: "Роза" },
  { value: "slate", label: "Графит" },
]

export function accentVar(color: string | undefined): string {
  const known = ACCENTS.some((accent) => accent.value === color)
  return `var(--accent-${known ? color : "slate"})`
}

export function categoryLabel(category: Category | null | undefined): string {
  return category?.name ?? "Без категории"
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
