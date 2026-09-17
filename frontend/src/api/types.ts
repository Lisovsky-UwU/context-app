export type Category = "bar" | "cafe" | "restaurant" | "culture" | "activity" | "nature" | "other"
export type PlaceStatus = "wish" | "planned" | "visited"
export type VisitStatus = "planned" | "done" | "cancelled"

export interface UserPublic {
  id: number
  display_name: string
  accent: string
}

export interface UserMe extends UserPublic {
  username: string
  created_at: string
}

export interface Invite {
  id: number
  code: string
  created_at: string
  expires_at: string | null
  used_at: string | null
  used_by: UserPublic | null
}

export interface AppConfig {
  geocoder_enabled: boolean
  default_center: [number, number]
  default_city: string
  media_url: string
  max_upload_mb: number
}

export interface Photo {
  id: number
  url: string
  thumb_url: string
  width: number
  height: number
  caption: string
  uploaded_by: UserPublic | null
  created_at: string
}

export interface Review {
  id: number
  score: number
  text: string
  user: UserPublic
  created_at: string
}

export interface VisitBrief {
  id: number
  scheduled_date: string
  scheduled_time: string | null
  status: VisitStatus
}

export interface Place {
  id: number
  title: string
  category: Category
  address: string
  lat: number | null
  lon: number | null
  status: PlaceStatus
  interest_count: number
  interested: boolean
  photo_count: number
  cover_url: string | null
  average_score: number | null
  next_visit: VisitBrief | null
  last_visit_date: string | null
  created_by: UserPublic | null
}

export interface PlaceDetail extends Place {
  description: string
  website_url: string | null
  created_at: string
  interested_by: UserPublic[]
  reviews: Review[]
  my_review: Review | null
}

export interface PlaceInput {
  title: string
  category: Category
  description: string
  address: string
  lat: number | null
  lon: number | null
  website_url: string | null
}

export interface Visit {
  id: number
  place: { id: number; title: string; category: Category; address: string }
  scheduled_date: string
  scheduled_time: string | null
  status: VisitStatus
  note: string
  created_by: UserPublic | null
  participants: UserPublic[]
  photos: Photo[]
  completed_at: string | null
  created_at: string
}

export interface VisitInput {
  place_id: number
  scheduled_date: string
  scheduled_time: string | null
  note: string
  participant_ids: number[]
}

export interface GeoSuggestion {
  title: string
  address: string
  lat: number | null
  lon: number | null
}
