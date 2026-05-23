<script setup lang="ts">
/**
 * LoadingSpinner — SVG-анимированный спиннер.
 * Props: size ('sm' | 'md' | 'lg'), color (Tailwind text-* класс).
 */
withDefaults(defineProps<{
  size?: 'sm' | 'md' | 'lg'
  color?: string
}>(), {
  size: 'md',
  color: 'text-indigo-600',
})

const sizeMap = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' }
</script>

<template>
  <svg
    class="animate-spin"
    :class="[sizeMap[size], color]"
    viewBox="0 0 24 24"
    fill="none"
    aria-hidden="true"
  >
    <circle
      class="opacity-25"
      cx="12" cy="12" r="10"
      stroke="currentColor"
      stroke-width="4"
    />
    <path
      class="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8v8H4z"
    />
  </svg>
</template>
