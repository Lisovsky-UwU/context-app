interface MapTarget {
  address: string
  lat: number | null
  lon: number | null
}

const hasCoords = (place: MapTarget): place is MapTarget & { lat: number; lon: number } =>
  typeof place.lat === "number" && typeof place.lon === "number"

/** Встраиваемый виджет Яндекс.Карт — работает без ключа и подписки. */
export function widgetUrl(place: MapTarget): string | null {
  if (hasCoords(place)) {
    const point = `${place.lon},${place.lat}`
    return `https://yandex.ru/map-widget/v1/?ll=${point}&z=16&pt=${point},pm2rdm&lang=ru_RU`
  }
  if (place.address) {
    return `https://yandex.ru/map-widget/v1/?text=${encodeURIComponent(place.address)}&z=15&lang=ru_RU`
  }
  return null
}

export function yandexUrl(place: MapTarget): string {
  if (hasCoords(place)) {
    const point = `${place.lon},${place.lat}`
    return `https://yandex.ru/maps/?ll=${point}&z=17&pt=${point},pm2rdm&text=${encodeURIComponent(place.address)}`
  }
  return `https://yandex.ru/maps/?text=${encodeURIComponent(place.address)}`
}

export function gisUrl(place: MapTarget): string {
  if (hasCoords(place)) {
    return `https://2gis.ru/geo/${place.lon},${place.lat}`
  }
  return `https://2gis.ru/search/${encodeURIComponent(place.address)}`
}
