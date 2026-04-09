<template>
  <section class="map-card">
    <h3>地图可视化</h3>
    <p class="hint">已接入高德 JS API Loader；未配置 key 时自动回退为坐标列表。</p>
    <div ref="mapEl" class="map-placeholder" role="img" aria-label="地图占位">
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
import { onMounted, ref, watch } from "vue";
import { ensureAmapLoaded } from "@/services/amapLoader";
import type { MapPoint } from "@/types/trip";

const props = defineProps<{
  points: MapPoint[];
}>();

const mapEl = ref<HTMLElement | null>(null);
let amapMap: any = null;
let markerList: any[] = [];

function drawMarkers(points: MapPoint[]) {
  if (!amapMap || !window.AMap) return;
  markerList.forEach((m) => amapMap.remove(m));
  markerList = points.map(
    (p) =>
      new window.AMap.Marker({
        position: [p.lng, p.lat],
        title: p.name,
      }),
  );
  markerList.forEach((m) => amapMap.add(m));
  if (markerList.length) {
    amapMap.setFitView(markerList);
  }
}

onMounted(async () => {
  if (!mapEl.value) return;
  try {
    const AMap = await ensureAmapLoaded();
    amapMap = new AMap.Map(mapEl.value, {
      zoom: 11,
      center: props.points[0] ? [props.points[0].lng, props.points[0].lat] : [116.397428, 39.90923],
    });
    drawMarkers(props.points);
  } catch {
    // fallback list already visible in template
  }
});

watch(
  () => props.points,
  (next) => {
    drawMarkers(next);
  },
  { deep: true },
);
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
  overflow: hidden;
}
ul {
  margin: 0;
  padding-left: 1.1rem;
}
.muted {
  color: #94a3b8;
}
</style>
