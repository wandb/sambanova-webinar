// src/services/api.js
import axios from 'axios'
import { useAuth } from '@clerk/vue'
import { decryptKey } from '../utils/encryption'

const API_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add interceptor to include API keys in requests
api.interceptors.request.use(async (config) => {
  try {
    const { userId } = useAuth()
    const sambanovaKey = sessionStorage.getItem(`sambanova_key_${userId}`)
    const exaKey = sessionStorage.getItem(`exa_key_${userId}`)
    
    if (sambanovaKey) {
      config.headers['x-sambanova-key'] = await decryptKey(sambanovaKey)
    }
    if (exaKey) {
      config.headers['x-exa-key'] = await decryptKey(exaKey)
    }
    
    return config
  } catch (error) {
    console.error('API interceptor error:', error)
    return config
  }
})

export const generateLeads = async (prompt, sambanovaKey, exaKey) => {
  try {
    const response = await api.post('/generate-leads', 
      { prompt },
      {
        headers: {
          'x-sambanova-key': sambanovaKey,
          'x-exa-key': exaKey
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
    const response = await fetch(`${API_URL}/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ query })
    })

    if (!response.ok) {
      throw new Error('API request failed')
    }
    // log the response body
    console.log(await response.json())

    return await response.json()
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}