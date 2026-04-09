<template>
  <div class="app">
    <header class="header">
      <h1>智能旅行助手</h1>
      <p class="subtitle">Vue3 · FastAPI · HelloAgents</p>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<style scoped>
.app {
  min-height: 100vh;
  font-family: system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #1a1a1a;
  background: linear-gradient(160deg, #f0f4ff 0%, #fff 45%);
}
.header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
}
.header h1 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 650;
}
.subtitle {
  margin: 0.35rem 0 0;
  font-size: 0.85rem;
  color: #64748b;
}
.main {
  max-width: 960px;
  margin: 0 auto;
  padding: 1.5rem;
}
</style>
