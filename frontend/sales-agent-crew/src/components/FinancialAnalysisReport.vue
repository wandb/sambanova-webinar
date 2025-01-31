<script setup>
/**
 * FinancialAnalysisReport: 
 * 1) Displays competitor data in a combined bar+line chart (market cap vs. PE ratio).
 * 2) Shows a donut chart of margin distribution from fundamentals (profit vs. operating vs. EBITDA).
 * 3) Shows daily returns as a line chart from the risk section.
 * 4) Also displays textual data in tabular form.
 * 5) Provides "View Full Report" and "Download PDF" functionality.
 *
 * Make sure to install Chart.js:
 *   npm install chart.js
 */

import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import html2pdf from 'html2pdf.js'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import Chart from 'chart.js/auto'

import {
  ArrowDownTrayIcon,
  DocumentTextIcon,
  PresentationChartLineIcon,
  UsersIcon,
  ChartPieIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'

import FullFinancialReportModal from './FullFinancialReportModal.vue'

const props = defineProps({
  report: {
    type: Object,
    required: true
  }
})

// States for "full report" modal
const isFullReportOpen = ref(false)

// Chart references
let competitorChart = null
let marginsChart = null
let dailyReturnsChart = null

// Canvas refs
const competitorCanvasRef = ref(null)
const marginsCanvasRef = ref(null)
const dailyReturnsCanvasRef = ref(null)

/**
 * onMounted => Initialize charts (if data is present)
 * watch => Re-initialize if 'report' changes
 * onBeforeUnmount => Destroy charts
 */
onMounted(() => {
  createOrUpdateCharts()
})

watch(() => props.report, () => {
  createOrUpdateCharts()
}, { deep: true })

onBeforeUnmount(() => {
  destroyCharts()
})

function destroyCharts() {
  if (competitorChart) {
    competitorChart.destroy()
    competitorChart = null
  }
  if (marginsChart) {
    marginsChart.destroy()
    marginsChart = null
  }
  if (dailyReturnsChart) {
    dailyReturnsChart.destroy()
    dailyReturnsChart = null
  }
}

/**
 * createOrUpdateCharts => sets up:
 *   1) competitorChart (bar/line multi-axis)
 *   2) marginsChart (donut chart)
 *   3) dailyReturnsChart (line)
 */
function createOrUpdateCharts() {
  // Destroy existing
  destroyCharts()

  // 1) Competitor Chart
  if (competitorCanvasRef.value && props.report?.competitor?.competitor_details?.length) {
    const competitorDetails = props.report.competitor.competitor_details
    // Convert market cap to billions
    const competitorNames = competitorDetails.map(c => c.name)
    const marketCaps = competitorDetails.map(c => {
      const mc = parseFloat(c.market_cap || '0')
      return mc > 0 ? mc / 1e9 : 0  // billions
    })
    const peRatios = competitorDetails.map(c => parseFloat(c.pe_ratio || '0'))

    const ctx1 = competitorCanvasRef.value.getContext('2d')
    competitorChart = new Chart(ctx1, {
      data: {
        labels: competitorNames,
        datasets: [
          {
            type: 'bar',
            label: 'Market Cap (B)',
            data: marketCaps,
            backgroundColor: 'rgba(99, 102, 241, 0.8)', // Indigo
            yAxisID: 'y1'
          },
          {
            type: 'line',
            label: 'PE Ratio',
            data: peRatios,
            borderColor: 'rgba(255, 99, 132, 0.8)', // Red
            backgroundColor: 'rgba(255, 99, 132, 0.4)',
            yAxisID: 'y2'
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y1: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: 'Market Cap (B)'
            }
          },
          y2: {
            type: 'linear',
            display: true,
            position: 'right',
            title: {
              display: true,
              text: 'PE Ratio'
            },
            grid: {
              drawOnChartArea: false
            }
          }
        },
        plugins: {
          legend: { position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        }
      }
    })
  }

  // 2) Margins donut chart
  if (marginsCanvasRef.value && props.report?.fundamental) {
    const f = props.report.fundamental
    // parse margin data
    // We check if not null or empty, then parse float
    const pm = parseFloat(f.profit_margins || '0')
    const om = parseFloat(f.operating_margins || '0')
    const em = parseFloat(f.ebitda_margins || '0')
    // if all zero, skip
    if (pm !== 0 || om !== 0 || em !== 0) {
      const ctx2 = marginsCanvasRef.value.getContext('2d')
      marginsChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: ['Profit Margin', 'Operating Margin', 'EBITDA Margin'],
          datasets: [
            {
              data: [pm, om, em],
              backgroundColor: [
                'rgba(16, 185, 129, 0.7)', // green
                'rgba(234, 179, 8, 0.7)',  // amber
                'rgba(59, 130, 246, 0.7)'  // blue
              ]
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      })
    }
  }

  // 3) Daily Returns line chart
  if (dailyReturnsCanvasRef.value && props.report?.risk?.daily_returns?.length) {
    const dailyData = props.report.risk.daily_returns
    const xLabels = dailyData.map(d => d.date)
    const returnsData = dailyData.map(d => parseFloat(d.daily_return || '0') * 100) // convert to % 

    const ctx3 = dailyReturnsCanvasRef.value.getContext('2d')
    dailyReturnsChart = new Chart(ctx3, {
      type: 'line',
      data: {
        labels: xLabels,
        datasets: [
          {
            label: 'Daily Return %',
            data: returnsData,
            borderColor: 'rgba(75, 192, 192, 0.8)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.2
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = ctx.parsed.y?.toFixed(4)
                return ` ${val}%`
              }
            }
          }
        },
        scales: {
          y: {
            title: {
              display: true,
              text: 'Daily Return (%)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Date'
            }
          }
        }
      }
    })
  }
}

/**
 * "View Full Report" => open the modal
 */
function viewFullReport() {
  isFullReportOpen.value = true
}
function closeFullReport() {
  isFullReportOpen.value = false
}

/**
 * Download PDF from the main "overview" (similar to the "ResearchReport" approach).
 * We will do minimal text-based PDF plus capturing the chart DOM using html2canvas.
 */
async function downloadPDF() {
  const container = document.createElement('div')
  container.style.padding = '40px'
  container.style.fontFamily = 'Arial, sans-serif'

  // Some simple styling
  const styleSheet = document.createElement('style')
  styleSheet.textContent = `
    .financial-section {
      margin-bottom: 1.5rem;
    }
    .section-title {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 0.5rem;
      color: #1a1a1a;
    }
    .chart-container {
      margin: 1rem 0;
      text-align: center;
    }
    .section-content {
      margin-left: 1rem;
      margin-bottom: 1rem;
    }
  `
  container.appendChild(styleSheet)

  // Title
  const title = document.createElement('h1')
  title.textContent = `Financial Analysis for ${props.report.company_name}`
  title.style.fontSize = '24px'
  title.style.marginBottom = '20px'
  container.appendChild(title)

  // We'll clone the existing DOM from this component's root
  // so we can capture the charts visually.
  // This approach: we create a wrapper, cloneNode from the main container
  // or simply build partial text for data. Then we rely on html2canvas to 
  // snapshot the chart canvases from the screen. 
  // A simpler approach might be to do a direct .from() on the actual container 
  // in the DOM. So let's do that approach: we have a ref to the entire container in the template.

  // We'll just do text-based sections + we can also do a "clone" of the canvases if we want them in the PDF.
  // A simpler approach: we point html2pdf at the .financial-analysis-pdf-target
  // from the actual DOM.

  // Let’s do that approach:
  const realElement = document.querySelector('#financial-analysis-report-root')
  if (!realElement) {
    console.warn('Could not find #financial-analysis-report-root in DOM. Falling back to minimal PDF content.')
    // fallback to textual content only:
    fallbackTextToContainer(container)
    await html2pdf().set(pdfOpts).from(container).save()
    return
  }

  const pdfOpts = {
    margin: [10, 10],
    filename: 'financial_analysis.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { 
      scale: 2,
      useCORS: true,
      letterRendering: true
    },
    jsPDF: { 
      unit: 'mm', 
      format: 'a4', 
      orientation: 'portrait'
    }
  }

  try {
    await html2pdf().set(pdfOpts).from(realElement).save()
  } catch (error) {
    console.error('Error generating PDF:', error)
  }
}

// fallback if no DOM element found
function fallbackTextToContainer(container) {
  const basicsDiv = document.createElement('div')
  basicsDiv.className = 'financial-section'
  basicsDiv.innerHTML = `
    <h2 class="section-title">Basic Info</h2>
    <div class="section-content">
      <p><strong>Ticker:</strong> ${props.report.ticker || ''}</p>
      <p><strong>Company Name:</strong> ${props.report.company_name || ''}</p>
    </div>
  `
  container.appendChild(basicsDiv)
}

function formatSummary(text = '') {
  return DOMPurify.sanitize(marked(text))
}
</script>

<template>
  <!-- We'll wrap the entire UI in a container we can snapshot for PDF (#financial-analysis-report-root) -->
  <div 
    id="financial-analysis-report-root"
    class="bg-white rounded-lg shadow p-6 max-h-[calc(100vh-16rem)] overflow-y-auto"
  >
    <!-- Header -->
    <div class="flex items-center space-x-3 mb-4">
      <PresentationChartLineIcon class="w-6 h-6 text-purple-600" />
      <h2 class="text-xl font-bold text-gray-800">
        Financial Analysis: {{ report.company_name }}
      </h2>
    </div>

    <!-- Basic Info -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-gray-700">Overview</h3>
      <p class="text-sm text-gray-600 mt-2">
        <strong>Ticker:</strong> {{ report.ticker }} |
        <strong>Company Name:</strong> {{ report.company_name }}
      </p>
    </div>

    <!-- Competitor Analysis -->
    <div class="mb-6">
      <div class="flex items-center space-x-2 mb-2">
        <UsersIcon class="w-5 h-5 text-gray-600" />
        <h4 class="font-semibold text-gray-800">Competitor Analysis</h4>
      </div>

      <!-- Combined bar+line chart for competitor data (market cap vs. PE ratio) -->
      <div class="border border-gray-200 p-3 rounded-lg chart-container">
        <canvas ref="competitorCanvasRef" width="400" height="250"></canvas>
      </div>
    </div>

    <!-- Fundamentals with Margins Donut -->
    <div class="mb-6">
      <div class="flex items-center space-x-2 mb-2">
        <ChartPieIcon class="w-5 h-5 text-gray-600" />
        <h4 class="font-semibold text-gray-800">Fundamentals & Margins</h4>
      </div>

      <div class="text-sm grid grid-cols-2 gap-y-2 gap-x-6 mt-2 mb-4">
        <p><strong>Market Cap:</strong> {{ report.fundamental?.market_cap }}</p>
        <p><strong>PE Ratio:</strong> {{ report.fundamental?.pe_ratio }}</p>
        <p><strong>Forward PE:</strong> {{ report.fundamental?.forward_pe }}</p>
        <p><strong>PS Ratio:</strong> {{ report.fundamental?.ps_ratio }}</p>
        <p><strong>Dividend Yield:</strong> {{ report.fundamental?.dividend_yield }}</p>
        <p><strong>Analyst Rec:</strong> {{ report.fundamental?.analyst_recommendation }}</p>
        <p><strong>Target Price:</strong> {{ report.fundamental?.target_price }}</p>
        <p><strong>Earnings/Share:</strong> {{ report.fundamental?.earnings_per_share }}</p>
      </div>

      <!-- donut chart for margins: profit, operating, ebitda -->
      <div class="border border-gray-200 p-3 rounded-lg chart-container">
        <canvas ref="marginsCanvasRef" width="300" height="250"></canvas>
      </div>
    </div>

    <!-- Risk Section + daily returns chart -->
    <div class="mb-6">
      <div class="flex items-center space-x-2 mb-2">
        <ShieldCheckIcon class="w-5 h-5 text-gray-600" />
        <h4 class="font-semibold text-gray-800">Risk & Daily Returns</h4>
      </div>
      <div class="text-sm grid grid-cols-2 gap-y-2 gap-x-6 mt-2 mb-4">
        <p><strong>Beta:</strong> {{ report.risk?.beta }}</p>
        <p><strong>Sharpe Ratio:</strong> {{ report.risk?.sharpe_ratio }}</p>
        <p><strong>VaR (95%):</strong> {{ report.risk?.value_at_risk_95 }}</p>
        <p><strong>Max Drawdown:</strong> {{ report.risk?.max_drawdown }}</p>
        <p><strong>Volatility:</strong> {{ report.risk?.volatility }}</p>
      </div>

      <!-- daily returns line chart -->
      <div class="border border-gray-200 p-3 rounded-lg chart-container">
        <canvas ref="dailyReturnsCanvasRef" width="300" height="250"></canvas>
      </div>
    </div>

    <!-- Comprehensive Summary -->
    <div class="mb-6">
      <div class="flex items-center space-x-2 mb-2">
        <DocumentTextIcon class="w-5 h-5 text-gray-600" />
        <h4 class="font-semibold text-gray-800">Comprehensive Summary</h4>
      </div>
      <div class="text-sm text-gray-700 prose max-w-none">
        <div v-html="formatSummary(report.comprehensive_summary)"></div>
      </div>
    </div>

    <!-- ACTIONS -->
    <div class="flex justify-end space-x-4 mt-6">
      <button
        @click="viewFullReport"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
      >
        <DocumentTextIcon class="w-5 h-5 mr-2" />
        View Full Report
      </button>
      <button
        @click="downloadPDF"
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-700"
      >
        <ArrowDownTrayIcon class="w-5 h-5 mr-2" />
        Download PDF
      </button>
    </div>

    <!-- FULL FINANCIAL REPORT MODAL -->
    <FullFinancialReportModal
      :open="isFullReportOpen"
      :reportData="report"
      @close="closeFullReport"
    />
  </div>
</template>

<style scoped>
.prose p {
  margin-bottom: 0.75rem;
}
.chart-container {
  overflow-x: auto;
}
</style>
