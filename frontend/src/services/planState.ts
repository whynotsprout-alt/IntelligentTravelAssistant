import type { TripPlanResponse } from "@/types/trip";

let last: TripPlanResponse | null = null;

export function setLastPlan(plan: TripPlanResponse): void {
  last = plan;
}

export function getLastPlan(): TripPlanResponse | null {
  return last;
}
