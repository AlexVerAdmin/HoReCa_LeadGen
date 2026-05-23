<script setup lang="ts">
/**
 * ProposalGenerateModal — modal генерации коммерческого предложения.
 * Открывается по leadId. Выбор языка, кнопка «Генерировать», LoadingSpinner,
 * после ответа — ProposalCard с кнопкой скачать PDF.
 */
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ProposalCard from '@/components/proposals/ProposalCard.vue'
import * as proposalService from '@/services/proposalService'
import * as userService from '@/services/userService'
import type { Proposal } from '@/types'

const props = defineProps<{
  leadId: number | null
}>()

const emit = defineEmits<{
  (e: 'update:leadId', value: null): void
  (e: 'generated', proposal: Proposal): void
}>()

const { t } = useI18n()

const LANGS = ['ru', 'en', 'de'] as const

const language  = ref<string>('ru')
const loading   = ref(false)
const result    = ref<Proposal | null>(null)
const error     = ref<string | null>(null)

// При открытии — загрузить язык из настроек пользователя и сбросить предыдущий результат
watch(() => props.leadId, async (id) => {
  if (id !== null) {
    result.value  = null
    error.value   = null
    loading.value = false
    try {
      const settings = await userService.getSettings()
      language.value = settings.proposal_language
    } catch {
      language.value = 'ru'
    }
  }
})

const close = () => emit('update:leadId', null)

const generate = async () => {
  if (props.leadId === null) return
  loading.value = true
  error.value   = null
  result.value  = null
  try {
    const proposal = await proposalService.createProposal({
      lead_id: props.leadId,
      language: language.value,
    })
    result.value = proposal
    emit('generated', proposal)
  } catch {
    error.value = t('common.error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="leadId !== null"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="close"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Заголовок modal -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <h2 class="text-base font-semibold text-gray-800">{{ t('proposal.title') }}</h2>
          <button
            class="p-1 text-gray-400 hover:text-gray-700 transition-colors rounded-lg hover:bg-gray-100"
            @click="close"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Тело modal -->
        <div class="flex-1 overflow-y-auto px-6 py-5 space-y-5">

          <!-- Выбор языка + кнопка (только пока нет результата) -->
          <div v-if="!result" class="flex items-end gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ t('proposal.language') }}
              </label>
              <select
                v-model="language"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              >
                <option v-for="lang in LANGS" :key="lang" :value="lang">
                  {{ lang.toUpperCase() }}
                </option>
              </select>
            </div>
            <button
              class="flex items-center gap-2 px-5 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              :disabled="loading"
              @click="generate"
            >
              <LoadingSpinner v-if="loading" size="sm" color="text-white" />
              {{ t('proposal.generate') }}
            </button>
          </div>

          <!-- Прогресс -->
          <div v-if="loading" class="flex flex-col items-center gap-3 py-8 text-gray-500">
            <LoadingSpinner size="lg" />
            <p class="text-sm">{{ t('common.loading') }}</p>
          </div>

          <!-- Ошибка -->
          <div v-if="error" class="px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {{ error }}
          </div>

          <!-- Результат -->
          <div v-if="result">
            <p class="text-xs text-green-700 font-medium mb-3">✓ КП успешно сгенерировано</p>
            <ProposalCard :proposal="result" />
            <!-- Кнопка «Новый» чтобы сгенерировать ещё раз -->
            <button
              class="mt-4 text-sm text-indigo-600 hover:underline"
              @click="result = null"
            >
              ← {{ t('proposal.generate') }} ({{ t('proposal.language') }})
            </button>
          </div>
        </div>

        <!-- Футер -->
        <div class="px-6 py-4 border-t border-gray-200 flex justify-end flex-shrink-0">
          <button
            class="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            @click="close"
          >
            {{ t('common.cancel') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
