<script setup lang="ts">
/**
 * LeadsTable — таблица лидов с inline-сменой статуса, болевыми точками и действиями.
 * Кнопка "КП" эмитит generate-proposal — modal реализован в родителе (F12).
 */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { DocumentTextIcon, EyeIcon } from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/common/StatusBadge.vue'
import PainPointsList from '@/components/leads/PainPointsList.vue'
import * as leadService from '@/services/leadService'
import type { Lead, LeadStatus } from '@/types'

const props = defineProps<{ leads: Lead[] }>()

const emit = defineEmits<{
  (e: 'generate-proposal', leadId: number): void
  (e: 'status-updated', lead: Lead): void
}>()

const { t } = useI18n()

// Inline-редактирование статуса
const editingStatus = ref<number | null>(null)

const LEAD_STATUSES: LeadStatus[] = ['New', 'Contacted', 'Qualified', 'Rejected']

const onStatusChange = async (lead: Lead, newStatus: LeadStatus) => {
  try {
    const updated = await leadService.updateStatus(lead.id, newStatus)
    emit('status-updated', updated)
  } finally {
    editingStatus.value = null
  }
}

/** Цвет рейтинга: красный < 3.5, оранжевый 3.5–4.3, зелёный > 4.3 */
const ratingClass = (r: number | null) => {
  if (r === null) return 'text-gray-400'
  if (r < 3.5)   return 'text-red-600'
  if (r <= 4.3)  return 'text-amber-600'
  return 'text-green-600'
}
</script>

<template>
  <div class="bg-white rounded-xl border border-gray-200 overflow-x-auto">
    <table class="w-full text-sm">
      <thead>
        <tr class="bg-gray-50 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          <th class="px-3 py-3 w-8">#</th>
          <th class="px-3 py-3">{{ t('leads.title') }}</th>
          <th class="px-3 py-3 hidden md:table-cell">{{ t('leads.address') }}</th>
          <th class="px-3 py-3">{{ t('leads.rating') }}</th>
          <th class="px-3 py-3 hidden lg:table-cell">{{ t('leads.reviews') }}</th>
          <th class="px-3 py-3 hidden xl:table-cell">{{ t('leads.painPoints') }}</th>
          <th class="px-3 py-3">{{ t('leads.status') }}</th>
          <th class="px-3 py-3"></th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr
          v-for="(lead, idx) in leads"
          :key="lead.id"
          class="hover:bg-gray-50 transition-colors"
        >
          <!-- Порядковый номер -->
          <td class="px-3 py-3 text-gray-400 text-xs">{{ idx + 1 }}</td>

          <!-- Название -->
          <td class="px-3 py-3">
            <span class="font-medium text-gray-800">{{ lead.name }}</span>
          </td>

          <!-- Адрес -->
          <td class="px-3 py-3 text-gray-500 text-xs hidden md:table-cell max-w-[200px] truncate">
            {{ lead.address ?? '—' }}
          </td>

          <!-- Рейтинг -->
          <td class="px-3 py-3 font-semibold" :class="ratingClass(lead.rating)">
            {{ lead.rating !== null ? `⭐ ${lead.rating}` : '—' }}
          </td>

          <!-- Отзывов -->
          <td class="px-3 py-3 text-gray-500 hidden lg:table-cell">
            {{ lead.review_count ?? '—' }}
          </td>

          <!-- Болевые точки -->
          <td class="px-3 py-3 hidden xl:table-cell">
            <PainPointsList :points="lead.pain_points ?? []" />
          </td>

          <!-- Статус — inline dropdown -->
          <td class="px-3 py-3">
            <div v-if="editingStatus === lead.id">
              <select
                class="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-400"
                :value="lead.status"
                @change="onStatusChange(lead, ($event.target as HTMLSelectElement).value as LeadStatus)"
                @blur="editingStatus = null"
              >
                <option v-for="s in LEAD_STATUSES" :key="s" :value="s">
                  {{ t(`status.${s}`) }}
                </option>
              </select>
            </div>
            <button v-else class="text-left" @click="editingStatus = lead.id">
              <StatusBadge :status="lead.status" />
            </button>
          </td>

          <!-- Действия -->
          <td class="px-3 py-3">
            <div class="flex items-center gap-2 justify-end">
              <button
                class="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 rounded-lg hover:bg-emerald-100 transition-colors"
                @click="emit('generate-proposal', lead.id)"
              >
                <DocumentTextIcon class="w-3.5 h-3.5" />
                {{ t('leads.generateKP') }}
              </button>
              <RouterLink
                :to="`/leads/${lead.id}`"
                class="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
              >
                <EyeIcon class="w-3.5 h-3.5" />
                {{ t('leads.details') }}
              </RouterLink>
            </div>
          </td>
        </tr>

        <!-- Пустое состояние -->
        <tr v-if="leads.length === 0">
          <td colspan="8" class="px-4 py-8 text-center text-gray-400 text-sm">
            {{ t('common.loading') }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
