import { createRouter, createWebHistory } from "vue-router";
import PlanningForm from "@/views/PlanningForm.vue";
import ResultView from "@/views/ResultView.vue";

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "plan", component: PlanningForm },
    { path: "/result", name: "result", component: ResultView },
  ],
});
