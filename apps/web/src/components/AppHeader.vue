<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
});
</script>

<template>
  <header class="topbar">
    <div>
      <p class="eyebrow">Regional Health Platform</p>
      <h1>{{ title }}</h1>
      <p class="summary">
        {{ description }}
      </p>
    </div>
    <div class="topbar-metadata">
      <span class="pill pill-accent">Vue 3</span>
      <span class="pill">Vite</span>
      <span class="pill">长者档案 / 入住</span>
    </div>
  </header>
</template>
