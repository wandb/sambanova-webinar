# src/services/api.js
const API_URL = 'http://localhost:8000'

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

    return await response.json()
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}