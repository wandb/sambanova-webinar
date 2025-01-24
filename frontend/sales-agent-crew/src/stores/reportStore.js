import { defineStore } from 'pinia'

export const useReportStore = defineStore('reportStore', {
  state: () => ({
    savedReports: []
  }),
  actions: {
    saveReport(type, query, results) {
      const report = {
        id: Date.now(),
        type,                   // 'educational_content' or 'sales_leads'
        query,                  // The user's search query
        timestamp: new Date().toISOString(),
        results                 // The actual report/leads data
      }
      
      // Add to start of array
      this.savedReports.unshift(report)
      
      // Persist to localStorage
      this.persistReports()
    },

    loadSavedReports() {
      const saved = localStorage.getItem('savedReports')
      if (saved) {
        this.savedReports = JSON.parse(saved)
      }
    },

    persistReports() {
      localStorage.setItem('savedReports', JSON.stringify(this.savedReports))
    },

    deleteReport(reportId) {
      this.savedReports = this.savedReports.filter(r => r.id !== reportId)
      this.persistReports()
    }
  }
}) 