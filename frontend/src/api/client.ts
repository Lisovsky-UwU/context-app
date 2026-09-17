import type {
  AppConfig,
  Category,
  CategoryInput,
  GeoSuggestion,
  Invite,
  Photo,
  Place,
  PlaceDetail,
  PlaceInput,
  PlaceStatus,
  UserMe,
  UserPublic,
  Visit,
  VisitInput,
} from "./types"

const BASE = import.meta.env.VITE_API_BASE ?? "/api"

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    credentials: "include",
    ...options,
    headers:
      options.body instanceof FormData
        ? options.headers
        : { "Content-Type": "application/json", ...(options.headers ?? {}) },
  })

  if (response.status === 204) return undefined as T
  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, errorMessage(payload?.detail))
  }
  return payload as T
}

// FastAPI отдаёт ошибки валидации по-английски — показываем понятную подсказку по полю.
const FIELD_HINTS: Record<string, string> = {
  username: "Имя — от 3 до 32 символов: латиница, цифры, точка, дефис или подчёркивание",
  password: "Пароль должен быть не короче 6 символов",
  display_name: "Имя — от 2 до 80 символов",
  invite_code: "Проверьте код приглашения",
  title: "Впишите название места",
  name: "Название категории — до 40 символов",
  scheduled_date: "Выберите дату",
  score: "Оценка — от 1 до 5",
  website_url: "Ссылка должна начинаться с http:// или https://",
}

function errorMessage(detail: unknown): string {
  if (typeof detail === "string") return detail
  if (Array.isArray(detail) && detail.length) {
    const field = String(detail[0]?.loc?.at(-1) ?? "")
    return FIELD_HINTS[field] ?? "Проверьте заполненные поля"
  }
  return "Что-то пошло не так. Попробуйте ещё раз"
}

const body = (data: unknown) => JSON.stringify(data)

export const api = {
  config: () => request<AppConfig>("/config"),

  me: () => request<UserMe>("/auth/me"),
  login: (username: string, password: string) =>
    request<UserMe>("/auth/login", { method: "POST", body: body({ username, password }) }),
  register: (data: {
    username: string
    password: string
    invite_code: string
    display_name?: string
  }) =>
    request<UserMe>("/auth/register", { method: "POST", body: body(data) }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  updateProfile: (data: { display_name?: string }) =>
    request<UserMe>("/auth/me", { method: "PATCH", body: body(data) }),
  users: () => request<UserPublic[]>("/users"),

  invites: () => request<Invite[]>("/invites"),
  createInvite: () => request<Invite>("/invites", { method: "POST" }),

  categories: () => request<Category[]>("/categories"),
  createCategory: (data: CategoryInput) =>
    request<Category>("/categories", { method: "POST", body: body(data) }),
  updateCategory: (id: number, data: Partial<CategoryInput>) =>
    request<Category>(`/categories/${id}`, { method: "PATCH", body: body(data) }),
  deleteCategory: (id: number, moveTo?: number | null) => {
    const suffix = moveTo === undefined ? "" : `?move_to=${moveTo ?? 0}`
    return request<void>(`/categories/${id}${suffix}`, { method: "DELETE" })
  },

  places: (
    params: { status?: PlaceStatus; category_id?: number; q?: string; sort?: string } = {},
  ) => {
    const search = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value) search.set(key, String(value))
    })
    const suffix = search.toString()
    return request<Place[]>(`/places${suffix ? `?${suffix}` : ""}`)
  },
  place: (id: number) => request<PlaceDetail>(`/places/${id}`),
  createPlace: (data: PlaceInput) => request<PlaceDetail>("/places", { method: "POST", body: body(data) }),
  updatePlace: (id: number, data: Partial<PlaceInput>) =>
    request<PlaceDetail>(`/places/${id}`, { method: "PATCH", body: body(data) }),
  deletePlace: (id: number) => request<void>(`/places/${id}`, { method: "DELETE" }),
  setInterest: (id: number, interested: boolean) =>
    request<PlaceDetail>(`/places/${id}/interest`, { method: interested ? "PUT" : "DELETE" }),
  saveReview: (id: number, score: number, text: string) =>
    request<PlaceDetail>(`/places/${id}/review`, { method: "PUT", body: body({ score, text }) }),
  roulettePool: (params: { category_id?: number; include_planned?: boolean } = {}) => {
    const search = new URLSearchParams()
    if (params.category_id) search.set("category_id", String(params.category_id))
    if (params.include_planned) search.set("include_planned", "true")
    const suffix = search.toString()
    return request<Place[]>(`/places/roulette-pool${suffix ? `?${suffix}` : ""}`)
  },

  visits: (params: { upcoming?: boolean; place_id?: number; status?: string } = {}) => {
    const search = new URLSearchParams()
    if (params.upcoming) search.set("upcoming", "true")
    if (params.place_id) search.set("place_id", String(params.place_id))
    if (params.status) search.set("status", params.status)
    const suffix = search.toString()
    return request<Visit[]>(`/visits${suffix ? `?${suffix}` : ""}`)
  },
  createVisit: (data: VisitInput) => request<Visit>("/visits", { method: "POST", body: body(data) }),
  updateVisit: (id: number, data: Partial<VisitInput> & { status?: string }) =>
    request<Visit>(`/visits/${id}`, { method: "PATCH", body: body(data) }),
  deleteVisit: (id: number) => request<void>(`/visits/${id}`, { method: "DELETE" }),

  uploadPhotos: (visitId: number, files: File[], caption = "") => {
    const form = new FormData()
    files.forEach((file) => form.append("files", file))
    form.append("caption", caption)
    return request<Photo[]>(`/visits/${visitId}/photos`, { method: "POST", body: form })
  },
  deletePhoto: (id: number) => request<void>(`/photos/${id}`, { method: "DELETE" }),

  geoSuggest: (q: string) => request<GeoSuggestion[]>(`/geo/suggest?q=${encodeURIComponent(q)}`),
}
