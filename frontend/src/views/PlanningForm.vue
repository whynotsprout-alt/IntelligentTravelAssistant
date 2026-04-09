<template>
  <section class="card">
    <h2>行程规划</h2>
    <form class="form" @submit.prevent="onSubmit">
      <label>
        目的地
        <input v-model="form.destination" required placeholder="例如：北京" />
      </label>
      <div class="row">
        <label>
          开始日期
          <input v-model="form.start_date" type="date" required />
        </label>
        <label>
          结束日期
          <input v-model="form.end_date" type="date" required />
        </label>
      </div>
      <label>
        预算说明（可选）
        <input v-model="form.budget_hint" placeholder="例如：经济型" />
      </label>
      <label>
        兴趣标签（逗号分隔）
        <input v-model="interestsText" placeholder="美食, 博物馆" />
      </label>
      <label>
        出行人数
        <input v-model.number="form.party_size" type="number" min="1" max="20" />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" class="btn" :disabled="loading">
        {{ loading ? "规划中…" : "生成行程" }}
      </button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { planTrip } from "@/services/api";
import { setLastPlan } from "@/services/planState";
import type { TripPlanRequest } from "@/types/trip";

const router = useRouter();
const loading = ref(false);
const error = ref("");

const form = reactive({
  destination: "",
  start_date: "",
  end_date: "",
  budget_hint: "",
  party_size: 2,
});

const interestsText = ref("");

const interests = computed(() =>
  interestsText.value
    .split(/[,，]/)
    .map((s) => s.trim())
    .filter(Boolean),
);

async function onSubmit() {
  error.value = "";
  loading.value = true;
  try {
    const body: TripPlanRequest = {
      destination: form.destination,
      start_date: form.start_date,
      end_date: form.end_date,
      budget_hint: form.budget_hint || null,
      interests: interests.value,
      party_size: form.party_size,
    };
    const plan = await planTrip(body);
    setLastPlan(plan);
    await router.push({ name: "result" });
  } catch (e) {
    error.value = e instanceof Error ? e.message : "请求失败";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;
}
h2 {
  margin: 0 0 1rem;
  font-size: 1.15rem;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.88rem;
  color: #334155;
}
input {
  padding: 0.5rem 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1rem;
}
.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.btn {
  margin-top: 0.25rem;
  padding: 0.65rem 1rem;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.error {
  color: #b91c1c;
  margin: 0;
  font-size: 0.9rem;
}
</style>
