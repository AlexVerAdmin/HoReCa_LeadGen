<script setup lang="ts">
/**
 * AdminSettingsView — управление глобальными настройками системы (ключ/значение).
 * Доступно только для роли admin.
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import * as adminService from '@/services/adminService'
import type { GlobalSettings } from '@/types'

const { t } = useI18n()

const settings    = ref<GlobalSettings[]>([])
const loading     = ref(true)
const error       = ref<string | null>(null)
const editingKey  = ref<string | null>(null)
const editValue   = ref('')
const savingKey   = ref<string | null>(null)
const savedKey    = ref<string | null>(null)

onMounted(async () => {
  try {
    settings.value = await adminService.getSettings()
  } catch {
    error.value = t('common.error')
  } finally {
    loading.value = false
  }
})

const startEdit = (s: GlobalSettings) => {
  editingKey.value = s.key
  editValue.value  = s.value
}

const cancelEdit = () => { editingKey.value = null }

const saveEdit = async (key: string) => {
  savingKey.value = key
  error.value = null
  try {
    const updated = await adminService.updateSetting(key, editValue.value)
    const idx = settings.value.findIndex(s => s.key === key)
    if (idx !== -1) settings.value[idx] = updated
    editingKey.value = null
    savedKey.value   = key
    setTimeout(() => { savedKey.value = null }, 2000)
  } catch {
    error.value = t('common.error')
  } finally {
    savingKey.value = null
  }
}
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6">{{ t('admin.globalSettings') }}</h2>

    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
      {{ error }}
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-400 text-sm">{{ t('common.loading') }}</div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
          <tr>
            <th class="px-4 py-3 text-left w-56">{{ t('admin.key') }}</th>
            <th class="px-4 py-3 text-left">{{ t('admin.value') }}</th>
            <th class="px-4 py-3 text-left hidden md:table-cell">{{ t('admin.description') }}</th>
            <th class="px-4 py-3 text-right w-32"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="s in settings" :key="s.key" class="hover:bg-gray-50">
            <!-- Ключ -->
            <td class="px-4 py-3 font-mono text-gray-600 text-xs">{{ s.key }}</td>

            <!-- Значение: обычный вид / редактирование -->
            <td class="px-4 py-3">
              <template v-if="editingKey === s.key">
                <input
                  v-model="editValue"
                  type="text"
                  class="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  @keyup.enter="saveEdit(s.key)"
                  @keyup.escape="cancelEdit"
                />
              </template>
              <span v-else class="text-gray-700 break-all">{{ s.value }}</span>
            </td>

            <!-- Описание -->
            <td class="px-4 py-3 text-gray-400 text-xs hidden md:table-cell">
              {{ s.description ?? '—' }}
            </td>

            <!-- Действия -->
            <td class="px-4 py-3 text-right whitespace-nowrap">
              <template v-if="editingKey === s.key">
                <button
                  class="text-xs px-3 py-1 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 mr-1 disabled:opacity-50"
                  :disabled="savingKey === s.key"
                  @click="saveEdit(s.key)"
                >{{ t('common.save') }}</button>
                <button
                  class="text-xs px-3 py-1 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50"
                  @click="cancelEdit"
                >{{ t('common.cancel') }}</button>
              </template>
              <template v-else>
                <span v-if="savedKey === s.key" class="text-xs text-green-600 mr-2">✓</span>
                <button
                  class="text-xs px-3 py-1 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50"
                  @click="startEdit(s)"
                >{{ t('common.edit') }}</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
