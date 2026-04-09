import type { TripPlanRequest, TripPlanResponse } from "@/types/trip";

const BASE = "/api/v1";

export async function planTrip(body: TripPlanRequest): Promise<TripPlanResponse> {
  const res = await fetch(`${BASE}/trips/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<TripPlanResponse>;
}

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/health`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<{ status: string }>;
}
