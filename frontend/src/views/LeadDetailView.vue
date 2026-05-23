<script setup lang="ts">
/**
 * LeadDetailView — детальная страница лида.
 * Показывает полную информацию, болевые точки, последний отзыв и список КП.
 * Кнопка «Стратегия переговоров» создаёт КП на языке из настроек пользователя.
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeftIcon, PhoneIcon, GlobeAltIcon, MapPinIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import PainPointsList from '@/components/leads/PainPointsList.vue'
import ProposalCard from '@/components/proposals/ProposalCard.vue'
import * as leadService from '@/services/leadService'
import * as proposalService from '@/services/proposalService'
import * as userService from '@/services/userService'
import type { Lead, Proposal } from '@/types'

const route   = useRoute()
const router  = useRouter()
const { t }   = useI18n()
const authStore = useAuthStore()

const lead        = ref<Lead | null>(null)
const proposals   = ref<Proposal[]>([])
const generating  = ref(false)
const loadingLead = ref(true)
const error       = ref<string | null>(null)

const leadId = Number(route.params.id)

onMounted(async () => {
  try {
    lead.value      = await leadService.getLead(leadId)
    proposals.value = await proposalService.getByLead(leadId)
  } catch {
    error.value = t('common.error')
  } finally {
    loadingLead.value = false
  }
})

/** Сгенерировать КП / стратегию переговоров */
const generateProposal = async () => {
  generating.value = true
  error.value = null
  try {
    // Язык берём из настроек пользователя, fallback — 'ru'
    let lang = 'ru'
    try {
      const settings = await userService.getSettings()
      lang = settings.proposal_language
    } catch {}

    const proposal = await proposalService.createProposal({ lead_id: leadId, language: lang })
    proposals.value.unshift(proposal)
  } catch {
    error.value = t('common.error')
  } finally {
    generating.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Назад -->
    <button
      class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800 transition-colors"
      @click="router.back()"
    >
      <ArrowLeftIcon class="w-4 h-4" />
      Назад
    </button>

    <!-- Ошибка -->
    <div v-if="error" class="px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
      {{ error }}
    </div>

    <!-- Загрузка -->
    <div v-if="loadingLead" class="text-center py-12 text-gray-400 text-sm">
      {{ t('common.loading') }}
    </div>

    <template v-else-if="lead">
      <!-- Основная информация -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-gray-900">{{ lead.name }}</h2>
            <p v-if="lead.address" class="flex items-center gap-1 mt-1 text-sm text-gray-500">
              <MapPinIcon class="w-4 h-4 flex-shrink-0" />
              {{ lead.address }}
            </p>
          </div>
          <!-- Рейтинг -->
          <div v-if="lead.rating !== null" class="text-right">
            <span class="text-2xl font-bold" :class="{
              'text-red-600': lead.rating < 3.5,
              'text-amber-600': lead.rating >= 3.5 && lead.rating <= 4.3,
              'text-green-600': lead.rating > 4.3,
            }">⭐ {{ lead.rating }}</span>
            <p class="text-xs text-gray-400 mt-0.5">{{ lead.review_count }} {{ t('leads.reviews') }}</p>
          </div>
        </div>

        <!-- Контакты -->
        <div class="flex flex-wrap gap-4 text-sm">
          <a v-if="lead.phone" :href="`tel:${lead.phone}`" class="flex items-center gap-1 text-indigo-600 hover:underline">
            <PhoneIcon class="w-4 h-4" />
            {{ lead.phone }}
          </a>
          <a v-if="lead.website" :href="lead.website" target="_blank" rel="noopener noreferrer" class="flex items-center gap-1 text-indigo-600 hover:underline">
            <GlobeAltIcon class="w-4 h-4" />
            {{ t('leads.website') }}
          </a>
        </div>
      </div>

      <!-- Болевые точки -->
      <div v-if="lead.pain_points?.length" class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">{{ t('leads.painPoints') }}</h3>
        <PainPointsList :points="lead.pain_points" />
      </div>

      <!-- Последний негативный отзыв -->
      <div v-if="lead.last_negative_review_text" class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="text-sm font-semibold text-gray-700 mb-2">{{ t('leads.lastReview') }}</h3>
        <p class="text-sm text-gray-700 italic leading-relaxed">
          "{{ lead.last_negative_review_text }}"
        </p>
      </div>

      <!-- КП / Стратегия -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-gray-700">{{ t('proposal.title') }}</h3>
          <button
            class="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            :disabled="generating"
            @click="generateProposal"
          >
            <svg v-if="generating" class="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            {{ t('leads.generateStrategy') }}
          </button>
        </div>

        <!-- Список КП -->
        <div v-if="proposals.length" class="space-y-3">
          <ProposalCard
            v-for="proposal in proposals"
            :key="proposal.id"
            :proposal="proposal"
          />
        </div>
        <p v-else class="text-sm text-gray-400 text-center py-4">
          КП ещё не созданы
        </p>
      </div>
    </template>
  </div>
</template>
