<template>
  <div v-if="!plan" class="card empty">
    <p>暂无结果，请从首页提交规划。</p>
    <a-button type="link" class="link-btn" @click="emit('reset')">返回表单</a-button>
  </div>
  <div v-else class="layout">
    <section class="card">
      <header class="result-head">
        <h2>{{ plan.destination }}</h2>
        <a-button type="link" class="link-btn" @click="emit('reset')">重新规划</a-button>
      </header>
      <p class="summary">{{ plan.summary }}</p>
      <h3>每日行程</h3>
      <ul class="days">
        <li v-for="d in plan.itinerary" :key="d.day_index">
          <strong>第 {{ d.day_index }} 天 · {{ d.title }}</strong>
          <ul>
            <li v-for="(a, i) in d.activities" :key="i">{{ a }}</li>
          </ul>
        </li>
      </ul>
      <h3>天气</h3>
      <ul class="inline">
        <li v-for="w in plan.weather" :key="w.date">
          {{ w.date }} — {{ w.summary }}
          <span v-if="w.temp_high_c != null" class="muted">
            {{ w.temp_low_c }}~{{ w.temp_high_c }}°C
          </span>
        </li>
      </ul>
      <h3>酒店</h3>
      <ul>
        <li v-for="h in plan.hotels" :key="h.name">
          {{ h.name }}
          <span v-if="h.area" class="muted"> · {{ h.area }}</span>
        </li>
      </ul>
    </section>
    <MapPanel :points="plan.map_points" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import MapPanel from "@/components/MapPanel.vue";
import { getLastPlan } from "@/services/planState";
import type { TripPlanResponse } from "@/types/trip";

const emit = defineEmits<{
  reset: [];
}>();
const plan = computed<TripPlanResponse | null>(() => getLastPlan());
</script>

<style scoped>
.layout {
  display: grid;
  gap: 1rem;
}
@media (min-width: 840px) {
  .layout {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
}
.card {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;
}
.empty {
  text-align: center;
}
.result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
h2 {
  margin: 0;
  font-size: 1.2rem;
}
h3 {
  margin: 1.25rem 0 0.5rem;
  font-size: 1rem;
}
.summary {
  color: #475569;
  line-height: 1.55;
  margin: 0;
}
.days {
  padding-left: 1.1rem;
  margin: 0;
}
.days ul {
  margin: 0.35rem 0 0.75rem;
  padding-left: 1.1rem;
  color: #64748b;
}
.inline {
  margin: 0;
  padding-left: 1.1rem;
  color: #475569;
}
.muted {
  color: #94a3b8;
  font-size: 0.9rem;
}
.link-btn {
  font-size: 0.9rem !important;
}
.link-btn:hover {
  text-decoration: underline;
}
</style>
