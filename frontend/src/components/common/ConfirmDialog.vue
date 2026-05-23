<script setup lang="ts">
/**
 * ConfirmDialog — переиспользуемый диалог подтверждения.
 * Открывается через v-model:open, сообщает о выборе через emit confirm/cancel.
 */
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  open: boolean
  message?: string
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const { t } = useI18n()

const onConfirm = () => {
  emit('confirm')
  emit('update:open', false)
}

const onCancel = () => {
  emit('cancel')
  emit('update:open', false)
}
</script>

<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      @click.self="onCancel"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-sm mx-4">
        <p class="text-gray-800 text-sm mb-6">
          {{ message ?? t('common.confirm') }}
        </p>
        <div class="flex justify-end gap-3">
          <button
            class="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            @click="onCancel"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
            @click="onConfirm"
          >
            {{ t('common.delete') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
