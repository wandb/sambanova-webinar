// src/services/api.js
import axios from 'axios'

const API_URL = 'http://localhost:8000'

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
    if (error.response?.status === 401) {
      throw new Error('Invalid API keys')
    }
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