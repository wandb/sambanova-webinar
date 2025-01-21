// src/services/api.js
import axios from 'axios'

// Use environment variable for the API base URL
const API_URL = import.meta.env.PROD 
  ? '/api'  // In production, use relative path for proxy
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const generateLeads = async (prompt, keys) => {
  try {
    if (!keys?.sambanovaKey || !keys?.exaKey) {
      throw new Error('API keys are required')
    }

    const response = await api.post('/generate-leads', 
      { prompt },
      {
        headers: {
          'x-sambanova-key': keys.sambanovaKey,
          'x-exa-key': keys.exaKey
        }
      }
    )
    return response.data
  } catch (error) {
    console.error('API error:', error)
    throw error
  }
}

export default api

export const searchLeads = async (query) => {
  try {
    const response = await api.post('/research', {
      query
    })
    
    if (!response.data) {
      throw new Error('API request failed')
    }
    
    return response.data
  } catch (error) {
    console.error('Search error:', error)
    throw error
  }
}