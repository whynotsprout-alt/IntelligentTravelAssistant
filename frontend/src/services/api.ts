import axios from 'axios'
import type { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import type { TripFormData, TripPlanResponse } from '@/types'

type ImportMetaEnvLike = { VITE_API_BASE_URL?: string }
const API_BASE_URL =
  (import.meta as ImportMeta & { env: ImportMetaEnvLike }).env.VITE_API_BASE_URL ||
  'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error: AxiosError) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('收到响应:', response.status, response.config.url)
    return response
  },
  (error: AxiosError) => {
    console.error('响应错误:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

/**
 * 生成旅行计划
 */
export async function generateTripPlan(formData: TripFormData): Promise<TripPlanResponse> {
  try {
    const response = await apiClient.post<TripPlanResponse>('/api/v1/trip/plan', formData, {
      timeout: 300000 // 5分钟，规划任务较重
    })
    return response.data
  } catch (error: any) {
    console.error('生成旅行计划失败:', error)
    const detail = error.response?.data?.detail
    if (error.code === 'ECONNABORTED') {
      throw new Error('旅行计划生成超时，请稍后重试（请求超过5分钟）')
    }
    throw new Error(detail || error.message || '生成旅行计划失败')
  }
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<any> {
  try {
    const response = await apiClient.get('/api/v1/health')
    return response.data
  } catch (error: any) {
    console.error('健康检查失败:', error)
    throw new Error(error.message || '健康检查失败')
  }
}

export interface PoiPhotoResponse {
  success: boolean
  data?: {
    photo_url?: string
  }
  message?: string
}

export interface StaticMapPoint {
  longitude: number
  latitude: number
}

export interface StaticMapResponse {
  success: boolean
  data?: {
    map_url?: string
    map_image_data_url?: string
  }
  message?: string
}

/**
 * 获取景点图片
 */
export async function getPoiPhoto(name: string, city?: string): Promise<PoiPhotoResponse> {
  const response = await apiClient.get<PoiPhotoResponse>('/api/v1/poi/photo', {
    params: { name, city }
  })
  return response.data
}

/**
 * 生成导出用静态地图
 */
export async function getStaticMapUrl(payload: {
  city?: string
  points: StaticMapPoint[]
  width?: number
  height?: number
  zoom?: number
}): Promise<StaticMapResponse> {
  const response = await apiClient.post<StaticMapResponse>('/api/v1/map/static-map', payload, {
    timeout: 10000 // 导出阶段需要快速返回，超时则走前端降级
  })
  return response.data
}

/**
 * 生成导出用静态地图图片（data URL）
 */
export async function getStaticMapImage(payload: {
  city?: string
  points: StaticMapPoint[]
  width?: number
  height?: number
  zoom?: number
}): Promise<StaticMapResponse> {
  const response = await apiClient.post<StaticMapResponse>('/api/v1/map/static-map-image', payload, {
    timeout: 12000
  })
  return response.data
}

export default apiClient

