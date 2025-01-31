<script setup>
/**
 * FinancialAnalysisReport:
 *  - Displays competitor data in a combined bar+line chart (market cap vs. PE ratio).
 *  - Shows a set of "mini dashboard" competitor cards to compare each competitor's metrics to the main company.
 *  - Shows fundamentals & margins as a "dashboard" grid with icons, tooltips, and properly rounded values.
 *  - Shows risk metrics similarly, with icons and tooltips.
 *  - Displays an "Avg Monthly Returns" line chart (formerly daily returns).
 *  - Provides "View Full Report" and "Download PDF" functionality.
 */

import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue'
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
  ShieldCheckIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon,
  LightBulbIcon,
  ArrowTrendingDownIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

import FullFinancialReportModal from './FullFinancialReportModal.vue'

// Props
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
let monthlyReturnsChart = null

// Canvas refs
const competitorCanvasRef = ref(null)
const marginsCanvasRef = ref(null)
const monthlyReturnsCanvasRef = ref(null)

// Utility for tooltips: define a small dictionary
const metricTooltips = {
  market_cap: 'Total market value of all outstanding shares (approx).',
  pe_ratio: 'Price-to-Earnings Ratio: share price / earnings per share.',
  ps_ratio: 'Price-to-Sales Ratio: market cap / total revenue.',
  profit_margins: 'Net income / total revenue (expressed as fraction).',
  operating_margins: 'Operating income / total revenue.',
  ebitda_margins: 'EBITDA / total revenue.',
  revenue_growth: 'Change in revenue over a given period (year/year or quarter/quarter).',
  earnings_growth: 'Change in net income (earnings) over a given period.',
  short_ratio: 'Shares shorted / average daily volume. Indicates short interest.',
  forward_pe: 'PE ratio based on forecasted future earnings.',
  dividend_yield: 'Annual dividends per share / share price.',
  analyst_recommendation: 'Summary of analyst consensus (e.g. strong_buy).',
  target_price: 'Analyst mean or median target price for the stock.',
  beta: 'Volatility measure compared to the market (beta > 1 => more volatile).',
  sharpe_ratio: 'Risk-adjusted return measure. Higher is better.',
  value_at_risk_95: 'Max expected loss with 95% confidence over a period.',
  max_drawdown: 'Largest drop from a peak to a trough over a timeframe.',
  volatility: 'Standard deviation of returns. Higher => more risk.'
}

// Helper function to format large numeric values (market cap, etc.) in trillions/billions/millions
function formatLargeNumber(num) {
  if (!num || isNaN(num)) return '-'
  const n = parseFloat(num)
  if (n >= 1e12) {
    return (n / 1e12).toFixed(2) + 'T'
  } else if (n >= 1e9) {
    return (n / 1e9).toFixed(2) + 'B'
  } else if (n >= 1e6) {
    return (n / 1e6).toFixed(2) + 'M'
  }
  return n.toFixed(2)
}

// Helper to format generic float values to 2 decimals
function formatFloat(num, decimals = 2) {
  if (!num || isNaN(num)) return '-'
  return parseFloat(num).toFixed(decimals)
}

// We'll also interpret small margin/ratio values as e.g. "55.32%" if they are typically in fraction form. 
// If a margin is 0.55 => display "55.00%"
function formatPercentage(num, decimals = 2) {
  if (!num || isNaN(num)) return '-'
  const val = parseFloat(num) * 100
  return val.toFixed(decimals) + '%'
}

// This function decides how to show a metric based on its key
function formatMetricValue(key, value) {
  // If "market_cap" => formatLargeNumber
  if (key === 'market_cap') return formatLargeNumber(value)
  // If "pe_ratio" / "ps_ratio" / "forward_pe" => just float, e.g. 2 decimals
  if (['pe_ratio','ps_ratio','forward_pe','short_ratio','target_price','earnings_per_share'].includes(key)) {
    return formatFloat(value, 2)
  }
  // If margins or yield => treat them as fraction => formatPercentage
  if (['profit_margins','operating_margins','ebitda_margins','dividend_yield','revenue_growth','earnings_growth'].includes(key)) {
    return formatPercentage(value, 2)
  }
  // fallback
  return value || '-'
}

/**
 * CREATE/UPDATE Charts
 */
onMounted(() => {
  createOrUpdateCharts()
})

watch(() => props.report, async () => {
  await createOrUpdateCharts()
}, { deep: true })

onBeforeUnmount(() => {
  destroyCharts()
})

async function createOrUpdateCharts() {
  destroyCharts()
  // Wait for DOM
  await nextTick()

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
    const pm = parseFloat(f.profit_margins || '0')
    const om = parseFloat(f.operating_margins || '0')
    const em = parseFloat(f.ebitda_margins || '0')

    if (pm !== 0 || om !== 0 || em !== 0) {
      const ctx2 = marginsCanvasRef.value.getContext('2d')
      marginsChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: ['Profit Margin', 'Operating Margin', 'EBITDA Margin'],
          datasets: [
            {
              data: [pm * 100, om * 100, em * 100], // convert fraction => percent
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

  // 3) Monthly Returns line chart (formerly daily returns)
  if (monthlyReturnsCanvasRef.value && props.report?.risk?.daily_returns?.length) {
    const dailyData = props.report.risk.daily_returns
    // The user has month-labeled data => rename them
    const xLabels = dailyData.map(d => d.date)  // e.g. "2024-05"
    const returnsData = dailyData.map(d => parseFloat(d.daily_return || '0') * 100) // convert fraction => percent

    const ctx3 = monthlyReturnsCanvasRef.value.getContext('2d')
    monthlyReturnsChart = new Chart(ctx3, {
      type: 'line',
      data: {
        labels: xLabels,
        datasets: [
          {
            label: 'Avg Monthly Return %',
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
                const val = ctx.parsed.y?.toFixed(2)
                return ` ${val}%`
              }
            }
          }
        },
        scales: {
          y: {
            title: {
              display: true,
              text: 'Avg Monthly Return (%)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Month'
            }
          }
        }
      }
    })
  }
}

function destroyCharts() {
  if (competitorChart) {
    competitorChart.destroy()
    competitorChart = null
  }
  if (marginsChart) {
    marginsChart.destroy()
    marginsChart = null
  }
  if (monthlyReturnsChart) {
    monthlyReturnsChart.destroy()
    monthlyReturnsChart = null
  }
}

/**
 * Actions
 */
function viewFullReport() {
  isFullReportOpen.value = true
}
function closeFullReport() {
  isFullReportOpen.value = false
}
async function downloadPDF() {
  const realElement = document.querySelector('#financial-analysis-report-root')
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

  if (!realElement) {
    console.warn('Could not find #financial-analysis-report-root in DOM.')
    return
  }

  try {
    await html2pdf().set(pdfOpts).from(realElement).save()
  } catch (error) {
    console.error('Error generating PDF:', error)
  }
}

const comprehensiveSummaryHtml = computed(() => {
  return DOMPurify.sanitize(marked(props.report.comprehensive_summary || ''))
})
</script>

<template>
  <!-- We'll wrap the entire UI in a container we can snapshot for PDF -->
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
    <div class="mb-8">
      <div class="flex items-center space-x-2 mb-2">
        <UsersIcon class="w-5 h-5 text-gray-600" />
        <h4 class="font-semibold text-gray-800">Competitor Analysis</h4>
      </div>

      <!-- Combined bar+line chart for competitor data (market cap vs. PE ratio) -->
      <div class="border border-gray-200 p-3 rounded-lg chart-container mb-6">
        <canvas ref="competitorCanvasRef" width="400" height="250"></canvas>
      </div>

      <!-- Grid of competitor cards, each with full metrics displayed -->
      <div 
        v-if="report.competitor?.competitor_details?.length"
        class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
      >
        <div
          v-for="(comp, idx) in report.competitor.competitor_details"
          :key="idx"
          class="p-4 border rounded-lg shadow-sm bg-white"
        >
          <div class="mb-2">
            <h5 class="font-semibold text-gray-700">
              {{ comp.ticker }} - {{ comp.name }}
            </h5>
            <p class="text-xs text-gray-500">
              {{ comp.industry }}, {{ comp.sector }}
            </p>
          </div>

          <!-- Display each metric in a small row with icon, label, tooltip, and value -->
          <div class="space-y-1 text-sm">
            <div 
              class="flex items-center justify-between"
              title="Total market value of all outstanding shares."
            >
              <div class="flex items-center space-x-1">
                <BanknotesIcon class="w-4 h-4 text-gray-500" />
                <span>Market Cap</span>
              </div>
              <strong>{{ formatMetricValue('market_cap', comp.market_cap) }}</strong>
            </div>

            <div 
              class="flex items-center justify-between"
              :title="metricTooltips['pe_ratio']"
            >
              <div class="flex items-center space-x-1">
                <ArrowTrendingUpIcon class="w-4 h-4 text-gray-500" />
                <span>PE Ratio</span>
              </div>
              <strong>{{ formatMetricValue('pe_ratio', comp.pe_ratio) }}</strong>
            </div>

            <div 
              class="flex items-center justify-between"
              :title="metricTooltips['ps_ratio']"
            >
              <div class="flex items-center space-x-1">
                <ArrowTrendingUpIcon class="w-4 h-4 text-gray-500" />
                <span>PS Ratio</span>
              </div>
              <strong>{{ formatMetricValue('ps_ratio', comp.ps_ratio) }}</strong>
            </div>

            <div 
              class="flex items-center justify-between"
              :title="metricTooltips['profit_margins']"
            >
              <div class="flex items-center space-x-1">
                <ArrowTrendingUpIcon class="w-4 h-4 text-gray-500" />
                <span>Profit Margin</span>
              </div>
              <strong>{{ formatPercentage(comp.profit_margins, 2) }}</strong>
            </div>

            <div 
              class="flex items-center justify-between"
              :title="metricTooltips['ebitda_margins']"
            >
              <div class="flex items-center space-x-1">
                <ArrowTrendingUpIcon class="w-4 h-4 text-gray-500" />
                <span>EBITDA Margin</span>
              </div>
              <strong>{{ formatPercentage(comp.ebitda_margins, 2) }}</strong>
            </div>

            <div 
              class="flex items-center justify-between"
              :title="metricTooltips['revenue_growth']"
            >
              <div class="flex items-center space-x-1">
                <LightBulbIcon class="w-4 h-4 text-gray-500" />
                <span>Rev Growth</span>
              </div>
              <strong>{{ formatPercentage(comp.revenue_growth, 2) }}</strong>
            </div>

            <div 
              class="flex items-center justify-between"
              :title="metricTooltips['earnings_growth']"
            >
              <div class="flex items-center space-x-1">
                <LightBulbIcon class="w-4 h-4 text-gray-500" />
                <span>EPS Growth</span>
              </div>
              <strong>{{ formatPercentage(comp.earnings_growth, 2) }}</strong>
            </div>

            <div 
              class="flex items-center justify-between"
              :title="metricTooltips['short_ratio']"
            >
              <div class="flex items-center space-x-1">
                <ExclamationTriangleIcon class="w-4 h-4 text-gray-500" />
                <span>Short Ratio</span>
              </div>
              <strong>{{ formatFloat(comp.short_ratio, 2) }}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Fundamentals & Margins -->
    <div class="mb-8">
      <div class="flex items-center space-x-2 mb-2">
        <ChartPieIcon class="w-5 h-5 text-gray-600" />
        <h4 class="font-semibold text-gray-800">Fundamentals & Margins</h4>
      </div>

      <!-- Grid of fundamentals using small "indicator cards" -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        <!-- Market Cap -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['market_cap']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <BanknotesIcon class="w-5 h-5 text-gray-500" />
            <span>Market Cap</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatMetricValue('market_cap', report.fundamental?.market_cap) }}
          </div>
        </div>

        <!-- PE Ratio -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['pe_ratio']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingUpIcon class="w-5 h-5 text-gray-500" />
            <span>PE Ratio</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatMetricValue('pe_ratio', report.fundamental?.pe_ratio) }}
          </div>
        </div>

        <!-- Forward PE -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['forward_pe']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingUpIcon class="w-5 h-5 text-gray-500" />
            <span>Forward PE</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatMetricValue('forward_pe', report.fundamental?.forward_pe) }}
          </div>
        </div>

        <!-- PS Ratio -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['ps_ratio']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingUpIcon class="w-5 h-5 text-gray-500" />
            <span>PS Ratio</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatMetricValue('ps_ratio', report.fundamental?.ps_ratio) }}
          </div>
        </div>

        <!-- Dividend Yield -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['dividend_yield']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingDownIcon class="w-5 h-5 text-gray-500" />
            <span>Dividend Yield</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatMetricValue('dividend_yield', report.fundamental?.dividend_yield) }}
          </div>
        </div>

        <!-- Analyst Recommendation -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['analyst_recommendation']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <LightBulbIcon class="w-5 h-5 text-gray-500" />
            <span>Recommendation</span>
          </div>
          <div class="text-lg font-bold text-gray-800 capitalize">
            {{ report.fundamental?.analyst_recommendation || '-' }}
          </div>
        </div>

        <!-- Target Price -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['target_price']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingUpIcon class="w-5 h-5 text-gray-500" />
            <span>Target Price</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatMetricValue('target_price', report.fundamental?.target_price) }}
          </div>
        </div>

        <!-- Earnings Per Share -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          title="Earnings Per Share: net income / outstanding shares."
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingUpIcon class="w-5 h-5 text-gray-500" />
            <span>EPS</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatFloat(report.fundamental?.earnings_per_share, 2) }}
          </div>
        </div>

        <!-- Margins donut chart -->
        <div class="col-span-full md:col-span-2 lg:col-span-2 xl:col-span-2 border border-gray-200 p-3 rounded-md bg-white shadow-sm flex flex-col">
          <div class="flex items-center space-x-1 mb-2 text-sm text-gray-600">
            <ChartPieIcon class="w-5 h-5 text-gray-500" />
            <span>Margin Distribution</span>
          </div>
          <div class="chart-container mx-auto">
            <canvas ref="marginsCanvasRef" width="300" height="250"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Risk & Avg Monthly Returns -->
    <div class="mb-8">
      <div class="flex items-center space-x-2 mb-2">
        <ShieldCheckIcon class="w-5 h-5 text-gray-600" />
        <h4 class="font-semibold text-gray-800">Risk & Avg Monthly Returns</h4>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-4">
        <!-- Beta -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['beta']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingUpIcon class="w-5 h-5 text-gray-500" />
            <span>Beta</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatFloat(report.risk?.beta, 2) }}
          </div>
        </div>

        <!-- Sharpe Ratio -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['sharpe_ratio']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingUpIcon class="w-5 h-5 text-gray-500" />
            <span>Sharpe Ratio</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatFloat(report.risk?.sharpe_ratio, 2) }}
          </div>
        </div>

        <!-- Value at Risk 95% -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['value_at_risk_95']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ExclamationTriangleIcon class="w-5 h-5 text-gray-500" />
            <span>VaR (95%)</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatFloat(report.risk?.value_at_risk_95, 4) }}
          </div>
        </div>

        <!-- Max Drawdown -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['max_drawdown']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingDownIcon class="w-5 h-5 text-gray-500" />
            <span>Max Drawdown</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatPercentage(report.risk?.max_drawdown, 2) }}
          </div>
        </div>

        <!-- Volatility -->
        <div 
          class="p-3 border border-gray-200 rounded-md bg-white shadow-sm"
          :title="metricTooltips['volatility']"
        >
          <div class="flex items-center space-x-2 mb-1 text-sm font-semibold text-gray-700">
            <ArrowTrendingDownIcon class="w-5 h-5 text-gray-500" />
            <span>Volatility</span>
          </div>
          <div class="text-lg font-bold text-gray-800">
            {{ formatPercentage(report.risk?.volatility, 2) }}
          </div>
        </div>

        <!-- (Optional) Could show more risk stats if present -->
      </div>

      <!-- line chart: average monthly returns -->
      <div class="border border-gray-200 p-3 rounded-lg chart-container">
        <canvas ref="monthlyReturnsCanvasRef" width="300" height="250"></canvas>
      </div>
    </div>

    <!-- Comprehensive Summary -->
    <div class="mb-6">
      <div class="flex items-center space-x-2 mb-2">
        <DocumentTextIcon class="w-5 h-5 text-gray-600" />
        <h4 class="font-semibold text-gray-800">Comprehensive Summary</h4>
      </div>
      <div class="text-sm text-gray-700 prose max-w-none">
        <div v-html="comprehensiveSummaryHtml"></div>
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
