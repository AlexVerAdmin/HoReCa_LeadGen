<script setup lang="ts">
/**
 * PainPointsList — список «болевых точек» лида в виде тегов.
 * Props: points — массив строк. Пустой массив не рендерит ничего.
 */
defineProps<{ points: string[] }>()
</script>

<template>
  <div v-if="points.length" class="flex flex-wrap gap-1.5">
    <span
      v-for="(point, i) in points"
      :key="i"
      class="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-50 border border-amber-200 text-amber-800 text-xs rounded-full"
    >
      <span>⚠️</span>
      {{ point }}
    </span>
  </div>
</template>
