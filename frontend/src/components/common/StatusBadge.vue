<script setup lang="ts">
/**
 * StatusBadge — цветной бейдж статуса.
 * Поддерживает SearchStatus, LeadStatus и ProposalStatus.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ status: string }>()
const { t } = useI18n()

/** Карта статус → Tailwind классы */
const colorMap: Record<string, string> = {
  // SearchStatus
  pending:     'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed:   'bg-green-100 text-green-800',
  failed:      'bg-red-100 text-red-800',
  // LeadStatus
  New:         'bg-sky-100 text-sky-800',
  Contacted:   'bg-purple-100 text-purple-800',
  Qualified:   'bg-green-100 text-green-800',
  Rejected:    'bg-red-100 text-red-800',
  // ProposalStatus
  draft:       'bg-gray-100 text-gray-700',
  generated:   'bg-indigo-100 text-indigo-800',
  sent:        'bg-blue-100 text-blue-800',
  accepted:    'bg-green-100 text-green-800',
  rejected:    'bg-red-100 text-red-800',
}

const classes = computed(
  () => colorMap[props.status] ?? 'bg-gray-100 text-gray-700'
)

/** Перевод через i18n, fallback — сам статус */
const label = computed(() => {
  const key = `status.${props.status}`
  const translated = t(key)
  return translated === key ? props.status : translated
})
</script>

<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="classes"
  >
    {{ label }}
  </span>
</template>
