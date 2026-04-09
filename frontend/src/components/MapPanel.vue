<template>
  <section class="map-card">
    <h3>地图可视化</h3>
    <p class="hint">
      此处接入高德 JS API / Leaflet，展示 <code>map_points</code> 坐标与路线。
    </p>
    <div class="map-placeholder" role="img" aria-label="地图占位">
      <ul>
        <li v-for="p in points" :key="p.name">
          {{ p.name }} — {{ p.lng.toFixed(4) }}, {{ p.lat.toFixed(4) }}
        </li>
        <li v-if="!points.length" class="muted">暂无坐标点</li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { MapPoint } from "@/types/trip";

defineProps<{
  points: MapPoint[];
}>();
</script>

<style scoped>
.map-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;
}
h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
}
.hint {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: #64748b;
}
code {
  font-size: 0.85em;
  background: #f1f5f9;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}
.map-placeholder {
  min-height: 220px;
  background: linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%);
  border-radius: 10px;
  border: 1px dashed #c7d2fe;
  padding: 1rem;
  font-size: 0.9rem;
  color: #334155;
}
ul {
  margin: 0;
  padding-left: 1.1rem;
}
.muted {
  color: #94a3b8;
}
</style>
