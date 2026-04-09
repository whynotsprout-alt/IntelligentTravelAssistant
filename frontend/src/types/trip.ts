/** Align with backend `app.models.schemas` */

export interface TripPlanRequest {
  destination: string;
  start_date: string;
  end_date: string;
  budget_hint?: string | null;
  interests: string[];
  party_size: number;
}

export interface MapPoint {
  name: string;
  lng: number;
  lat: number;
  kind?: string;
}

export interface WeatherSnapshot {
  date: string;
  summary: string;
  temp_high_c?: number | null;
  temp_low_c?: number | null;
}

export interface HotelSuggestion {
  name: string;
  area?: string | null;
  price_level?: string | null;
  image_url?: string | null;
}

export interface ItineraryDay {
  day_index: number;
  title: string;
  activities: string[];
}

export interface TripPlanResponse {
  destination: string;
  summary: string;
  itinerary: ItineraryDay[];
  map_points: MapPoint[];
  weather: WeatherSnapshot[];
  hotels: HotelSuggestion[];
}
