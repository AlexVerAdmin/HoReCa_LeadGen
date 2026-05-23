<script setup lang="ts">
/**
 * ProposalCard — карточка коммерческого предложения.
 * Показывает статус, дату, язык, раскрываемый текст КП, рекомендации и кнопку PDF.
 */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowDownTrayIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/common/StatusBadge.vue'
import * as proposalService from '@/services/proposalService'
import type { Proposal } from '@/types'

const props = defineProps<{ proposal: Proposal }>()
const { t } = useI18n()

const expanded   = ref(false)
const downloading = ref(false)

const formatDate = (iso: string | null) =>
  iso ? new Date(iso).toLocaleString(undefined, {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }) : '—'

/** Скачать PDF через ObjectURL */
const downloadPdf = async () => {
  downloading.value = true
  try {
    const blob = await proposalService.downloadPdf(props.proposal.id)
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `proposal_${props.proposal.id}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    downloading.value = false
  }
}
</script>

<template>
  <div class="border border-gray-200 rounded-xl overflow-hidden">
    <!-- Шапка карточки -->
    <div class="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
      <div class="flex items-center gap-3">
        <StatusBadge :status="proposal.status" />
        <span class="text-xs text-gray-500 uppercase font-medium">{{ proposal.language }}</span>
        <span class="text-xs text-gray-400">{{ formatDate(proposal.generated_at) }}</span>
      </div>
      <div class="flex items-center gap-2">
        <!-- Скачать PDF -->
        <button
          v-if="proposal.pdf_url || proposal.status === 'generated'"
          class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors disabled:opacity-50"
          :disabled="downloading"
          @click="downloadPdf"
        >
          <ArrowDownTrayIcon class="w-3.5 h-3.5" />
          {{ t('proposal.download') }}
        </button>

        <!-- Развернуть/свернуть -->
        <button
          class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
          @click="expanded = !expanded"
        >
          <component :is="expanded ? ChevronUpIcon : ChevronDownIcon" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Раскрываемый контент -->
    <div v-if="expanded" class="p-4 space-y-4">
      <!-- Текст КП -->
      <div>
        <p class="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
          {{ proposal.content_text }}
        </p>
      </div>

      <!-- Рекомендации -->
      <div v-if="proposal.recommendations?.length">
        <p class="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">
          {{ t('proposal.recommendations') }}
        </p>
        <ul class="space-y-1">
          <li
            v-for="(rec, i) in proposal.recommendations"
            :key="i"
            class="flex items-start gap-2 text-sm text-gray-700"
          >
            <span class="text-indigo-500 mt-0.5">•</span>
            {{ rec }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
