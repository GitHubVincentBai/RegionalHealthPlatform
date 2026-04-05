<script setup>
defineProps({
  currentView: {
    type: String,
    required: true,
  },
  items: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["navigate"]);
</script>

<template>
  <nav class="app-nav" aria-label="应用导航">
    <button
      v-for="item in items"
      :key="item.key"
      type="button"
      class="app-nav__item"
      :class="{ 'is-active': currentView === item.key }"
      @click="emit('navigate', item.key)"
    >
      <span class="app-nav__label">{{ item.label }}</span>
      <span class="app-nav__hint">{{ item.hint }}</span>
    </button>
  </nav>
</template>
