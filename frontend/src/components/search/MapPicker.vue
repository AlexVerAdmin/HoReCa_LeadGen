<script setup lang="ts">
/**
 * MapPicker — интерактивная карта Leaflet для выбора координат.
 * Клик по карте → emit update:coords. Кнопка геолокации центрирует карту.
 * Показывает маркер и круг радиуса вокруг выбранной точки.
 */
import { ref, computed, watch } from 'vue'
import { LMap, LTileLayer, LMarker, LCircle } from '@vue-leaflet/vue-leaflet'
import { Icon } from 'leaflet'
import type { LeafletMouseEvent } from 'leaflet'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

// ─── Исправление иконок маркеров Leaflet (баг с Vite/webpack) ────────────
;(Icon.Default.prototype as any)._getIconUrl = undefined
Icon.Default.mergeOptions({ iconUrl, iconRetinaUrl, shadowUrl })

// ─── Props / Emits ───────────────────────────────────────────────────────
interface Coords { lat: number; lng: number }

const props = withDefaults(defineProps<{
  coords: Coords | null
  radiusKm: number
}>(), {
  coords: null,
  radiusKm: 1,
})

const emit = defineEmits<{
  (e: 'update:coords', value: Coords): void
}>()

// ─── State ───────────────────────────────────────────────────────────────
const zoom = ref(13)
// Центр карты — Берлин по умолчанию
const center = ref<[number, number]>([52.52, 13.405])
const selectedCoords = ref<Coords | null>(props.coords)
const geoError = ref<string | null>(null)

/** Радиус в метрах для LCircle */
const radiusMeters = computed(() => props.radiusKm * 1000)

/** Позиция маркера/круга как tuple для vue-leaflet */
const markerLatLng = computed<[number, number] | null>(() =>
  selectedCoords.value
    ? [selectedCoords.value.lat, selectedCoords.value.lng]
    : null
)

// Синхронизировать с внешним v-model:coords при изменении извне
watch(() => props.coords, (val) => {
  if (val) {
    selectedCoords.value = val
    center.value = [val.lat, val.lng]
  }
})

// ─── Handlers ────────────────────────────────────────────────────────────

/** Клик по карте — выбрать координаты */
const onMapClick = (e: LeafletMouseEvent) => {
  const coords: Coords = { lat: e.latlng.lat, lng: e.latlng.lng }
  selectedCoords.value = coords
  emit('update:coords', coords)
}

/** Кнопка "Моё местоположение" — Geolocation API */
const locateMe = () => {
  geoError.value = null
  if (!navigator.geolocation) {
    geoError.value = 'Геолокация не поддерживается браузером'
    return
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const coords: Coords = { lat: pos.coords.latitude, lng: pos.coords.longitude }
      selectedCoords.value = coords
      center.value = [coords.lat, coords.lng]
      zoom.value = 14
      emit('update:coords', coords)
    },
    () => {
      geoError.value = 'Не удалось определить местоположение'
    }
  )
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <!-- Кнопка геолокации -->
    <button
      type="button"
      class="flex items-center gap-2 px-3 py-2 text-sm font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors w-fit"
      @click="locateMe"
    >
      📍 Определить моё местоположение
    </button>

    <p v-if="geoError" class="text-xs text-red-600">{{ geoError }}</p>

    <!-- Карта -->
    <div class="rounded-xl overflow-hidden border border-gray-200" style="height: 420px">
      <LMap
        :zoom="zoom"
        :center="center"
        :use-global-leaflet="false"
        class="h-full w-full"
        @click="onMapClick"
      >
        <LTileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
          layer-type="base"
          name="OpenStreetMap"
        />

        <!-- Маркер + круг радиуса -->
        <template v-if="markerLatLng">
          <LMarker :lat-lng="markerLatLng" />
          <LCircle
            :lat-lng="markerLatLng"
            :radius="radiusMeters"
            :color="'#6366f1'"
            :fill-color="'#6366f1'"
            :fill-opacity="0.1"
          />
        </template>
      </LMap>
    </div>

    <p v-if="selectedCoords" class="text-xs text-gray-500">
      {{ selectedCoords.lat.toFixed(5) }}, {{ selectedCoords.lng.toFixed(5) }}
    </p>
    <p v-else class="text-xs text-gray-400">Кликните по карте для выбора точки</p>
  </div>
</template>
