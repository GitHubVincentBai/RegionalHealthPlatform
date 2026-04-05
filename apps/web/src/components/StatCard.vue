<script setup>
defineProps({
  stat: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <article class="stat-card">
    <div class="stat-card__label">{{ stat.label }}</div>
    <div class="stat-card__value">{{ stat.value }}</div>
    <div class="stat-card__helper">{{ stat.helper }}</div>
  </article>
</template>
