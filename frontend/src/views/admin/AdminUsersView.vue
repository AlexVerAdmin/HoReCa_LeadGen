<script setup lang="ts">
/**
 * AdminUsersView — управление пользователями (CRUD).
 * Доступно только для роли admin.
 */
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import * as adminService from '@/services/adminService'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import type { UserAdmin, UserAdminCreate, UserAdminUpdate, UserRole } from '@/types'

const { t } = useI18n()

const ROLES: UserRole[] = ['admin', 'manager', 'agent']

// ─── State ────────────────────────────────────────────────────────────────
const users   = ref<UserAdmin[]>([])
const loading = ref(true)
const error   = ref<string | null>(null)

// ─── Создание пользователя ────────────────────────────────────────────────
const showCreate = ref(false)
const creating   = ref(false)
const createForm = reactive<UserAdminCreate>({
  email: '', username: '', password: '', role: 'agent', is_active: true,
})
const createError = ref<string | null>(null)

// ─── Inline-редактирование ────────────────────────────────────────────────
const editingId   = ref<number | null>(null)
const editRole    = ref<UserRole>('agent')
const editActive  = ref(true)
const editSaving  = ref(false)

// ─── Удаление ─────────────────────────────────────────────────────────────
const deleteUserId   = ref<number | null>(null)
const confirmOpen    = ref(false)

// ─── Загрузка ─────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    users.value = await adminService.getUsers()
  } catch {
    error.value = t('common.error')
  } finally {
    loading.value = false
  }
})

// ─── CRUD ─────────────────────────────────────────────────────────────────
const openCreate = () => {
  Object.assign(createForm, { email: '', username: '', password: '', role: 'agent', is_active: true })
  createError.value = null
  showCreate.value = true
}

const submitCreate = async () => {
  creating.value = true
  createError.value = null
  try {
    const user = await adminService.createUser({ ...createForm })
    users.value.unshift(user)
    showCreate.value = false
  } catch {
    createError.value = t('common.error')
  } finally {
    creating.value = false
  }
}

const startEdit = (u: UserAdmin) => {
  editingId.value  = u.id
  editRole.value   = u.role
  editActive.value = u.is_active
}

const cancelEdit = () => { editingId.value = null }

const saveEdit = async (id: number) => {
  editSaving.value = true
  try {
    const payload: UserAdminUpdate = { role: editRole.value, is_active: editActive.value }
    const updated = await adminService.updateUser(id, payload)
    const idx = users.value.findIndex(u => u.id === id)
    if (idx !== -1) users.value[idx] = updated
    editingId.value = null
  } catch {
    error.value = t('common.error')
  } finally {
    editSaving.value = false
  }
}

const askDelete = (id: number) => {
  deleteUserId.value = id
  confirmOpen.value  = true
}

const confirmDelete = async () => {
  if (deleteUserId.value === null) return
  try {
    await adminService.deleteUser(deleteUserId.value)
    users.value = users.value.filter(u => u.id !== deleteUserId.value)
  } catch {
    error.value = t('common.error')
  } finally {
    confirmOpen.value  = false
    deleteUserId.value = null
  }
}
</script>

<template>
  <div>
    <!-- Заголовок -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-gray-800">{{ t('admin.users') }}</h2>
      <button
        class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        @click="openCreate"
      >
        + {{ t('admin.createUser') }}
      </button>
    </div>

    <!-- Ошибка -->
    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
      {{ error }}
    </div>

    <!-- Загрузка -->
    <div v-if="loading" class="text-center py-16 text-gray-400 text-sm">{{ t('common.loading') }}</div>

    <!-- Таблица -->
    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
          <tr>
            <th class="px-4 py-3 text-left">ID</th>
            <th class="px-4 py-3 text-left">{{ t('admin.email') }}</th>
            <th class="px-4 py-3 text-left">{{ t('settings.username') }}</th>
            <th class="px-4 py-3 text-left">{{ t('admin.role') }}</th>
            <th class="px-4 py-3 text-center">{{ t('admin.active') }}</th>
            <th class="px-4 py-3 text-right"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-gray-400">{{ u.id }}</td>
            <td class="px-4 py-3 text-gray-700">{{ u.email }}</td>
            <td class="px-4 py-3 text-gray-700">{{ u.username }}</td>

            <!-- Роль: обычный вид / inline-edit -->
            <td class="px-4 py-3">
              <template v-if="editingId === u.id">
                <select
                  v-model="editRole"
                  class="px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none"
                >
                  <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
                </select>
              </template>
              <span v-else class="capitalize text-gray-700">{{ u.role }}</span>
            </td>

            <!-- Активен -->
            <td class="px-4 py-3 text-center">
              <template v-if="editingId === u.id">
                <input v-model="editActive" type="checkbox" class="accent-indigo-600" />
              </template>
              <span v-else :class="u.is_active ? 'text-green-600' : 'text-gray-400'">
                {{ u.is_active ? '✓' : '✗' }}
              </span>
            </td>

            <!-- Действия -->
            <td class="px-4 py-3 text-right whitespace-nowrap">
              <template v-if="editingId === u.id">
                <button
                  class="text-xs px-3 py-1 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 mr-1 disabled:opacity-50"
                  :disabled="editSaving"
                  @click="saveEdit(u.id)"
                >{{ t('common.save') }}</button>
                <button
                  class="text-xs px-3 py-1 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50"
                  @click="cancelEdit"
                >{{ t('common.cancel') }}</button>
              </template>
              <template v-else>
                <button
                  class="text-xs px-3 py-1 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 mr-1"
                  @click="startEdit(u)"
                >{{ t('common.edit') }}</button>
                <button
                  class="text-xs px-3 py-1 bg-red-50 border border-red-200 text-red-600 rounded-lg hover:bg-red-100"
                  @click="askDelete(u.id)"
                >{{ t('common.delete') }}</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal создания пользователя -->
    <Teleport to="body">
      <div
        v-if="showCreate"
        class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
        @click.self="showCreate = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">{{ t('admin.newUser') }}</h3>

          <div v-if="createError" class="mb-3 text-sm text-red-600">{{ createError }}</div>

          <form class="space-y-3" @submit.prevent="submitCreate">
            <!-- Email -->
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">{{ t('admin.email') }}</label>
              <input
                v-model="createForm.email"
                type="email"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>
            <!-- Username -->
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">{{ t('settings.username') }}</label>
              <input
                v-model="createForm.username"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>
            <!-- Password -->
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">{{ t('admin.password') }}</label>
              <input
                v-model="createForm.password"
                type="password"
                required
                minlength="8"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>
            <!-- Role -->
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">{{ t('admin.role') }}</label>
              <select
                v-model="createForm.role"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              >
                <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>

            <!-- Buttons -->
            <div class="flex justify-end gap-2 pt-2">
              <button
                type="button"
                class="px-4 py-2 text-sm border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50"
                @click="showCreate = false"
              >{{ t('common.cancel') }}</button>
              <button
                type="submit"
                :disabled="creating"
                class="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                <span v-if="creating">...</span>
                <span v-else>{{ t('common.create') }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- ConfirmDialog удаления -->
    <ConfirmDialog
      v-model:open="confirmOpen"
      :message="t('common.confirm')"
      @confirm="confirmDelete"
      @cancel="confirmOpen = false"
    />
  </div>
</template>
