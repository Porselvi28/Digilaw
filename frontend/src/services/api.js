import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
})

// The UI intentionally reads from src/data while backend integration is pending.
// Replace demo repository functions with API calls when the product is connected.
export const isApiConnected = false
