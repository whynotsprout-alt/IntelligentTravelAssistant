import type { TripPlanRequest, TripPlanResponse } from "@/types/trip";
import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";
const client = axios.create({
  baseURL: BASE,
  timeout: 15000,
});

export async function planTrip(body: TripPlanRequest): Promise<TripPlanResponse> {
  const { data } = await client.post<TripPlanResponse>("/trip/plan", body);
  return data;
}

export async function healthCheck(): Promise<{ status: string }> {
  const { data } = await client.get<{ status: string }>("/health");
  return data;
}
