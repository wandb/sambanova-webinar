<template>
  <transition name="fade">
    <div
      v-if="open"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center"
    >
      <div class="bg-white rounded-lg w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col relative">
        <!-- Modal Header -->
        <div class="flex items-center justify-between px-4 py-2 border-b border-gray-200">
          <h3 class="font-semibold text-xl text-gray-800">
            Full Financial Analysis
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-500 hover:text-gray-700 focus:outline-none"
          >
            <!-- Close icon -->
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- Modal Content (scrollable) -->
        <div 
          ref="modalRootRef"
          class="p-4 overflow-y-auto space-y-6 flex-1"
          id="financial-full-modal-root"
        >
          <!-- Title / Overview -->
          <section class="border-b border-gray-200 pb-4">
            <h4 class="text-md font-bold text-gray-700 mb-2">
              {{ reportData.company_name }} ({{ reportData.ticker }})
            </h4>
            <p class="text-sm text-gray-600">
              This is the full expanded financial analysis, including competitor breakdown, fundamentals, risk metrics, quarterly data, and more.
            </p>
          </section>

          <!-- Competitor Analysis -->
          <section>
            <h5 class="text-lg font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2"
                  d="M17 20h5V4H2v16h5m10-10h.01M12 15l2.09-2.09L9 8l-2.09 2.09L12 15z"
                />
              </svg>
              <span>Competitor Analysis</span>
            </h5>
            <!-- Competitor Chart -->
            <div class="border border-gray-200 p-3 rounded-lg mb-4">
              <canvas ref="competitorModalCanvasRef" width="400" height="250"></canvas>
            </div>

            <!-- Competitor Table -->
            <table v-if="reportData?.competitor?.competitor_details?.length" class="w-full text-sm border">
              <thead class="bg-gray-50 text-gray-700">
                <tr>
                  <th class="px-2 py-1 border-r">Ticker</th>
                  <th class="px-2 py-1 border-r">Name</th>
                  <th class="px-2 py-1 border-r">Market Cap (B)</th>
                  <th class="px-2 py-1 border-r">PE Ratio</th>
                  <th class="px-2 py-1 border-r">PS Ratio</th>
                  <th class="px-2 py-1 border-r">Profit Margin</th>
                  <th class="px-2 py-1">EBITDA Margin</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="(comp, idx) in reportData.competitor.competitor_details" 
                  :key="idx"
                  class="border-b"
                >
                  <td class="px-2 py-1 border-r">{{ comp.ticker }}</td>
                  <td class="px-2 py-1 border-r">{{ comp.name }}</td>
                  <td class="px-2 py-1 border-r">
                    {{ formatBillion(comp.market_cap) }}
                  </td>
                  <td class="px-2 py-1 border-r">{{ comp.pe_ratio }}</td>
                  <td class="px-2 py-1 border-r">{{ comp.ps_ratio }}</td>
                  <td class="px-2 py-1 border-r">
                    {{ formatPct(comp.profit_margins) }}
                  </td>
                  <td class="px-2 py-1">
                    {{ formatPct(comp.ebitda_margins) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </section>

          <!-- Fundamentals -->
          <section>
            <h5 class="text-lg font-semibold text-gray-800 mb-2 flex items-center space-x-2 mt-4">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2"
                  d="M3 7h18M3 10h18M9 20V4m6 0v16"
                />
              </svg>
              <span>Fundamentals</span>
            </h5>

            <!-- Fundamentals grid -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              <div class="border p-2 rounded bg-white shadow-sm">
                <strong class="text-gray-700 block text-sm">Market Cap</strong>
                <span class="text-gray-800 text-sm">
                  {{ formatBillion(reportData.fundamental?.market_cap) }}
                </span>
              </div>
              <div class="border p-2 rounded bg-white shadow-sm">
                <strong class="text-gray-700 block text-sm">PE Ratio</strong>
                <span class="text-gray-800 text-sm">
                  {{ formatFloat(reportData.fundamental?.pe_ratio) }}
                </span>
              </div>
              <div class="border p-2 rounded bg-white shadow-sm">
                <strong class="text-gray-700 block text-sm">Forward PE</strong>
                <span class="text-gray-800 text-sm">
                  {{ formatFloat(reportData.fundamental?.forward_pe) }}
                </span>
              </div>
              <div class="border p-2 rounded bg-white shadow-sm">
                <strong class="text-gray-700 block text-sm">PS Ratio</strong>
                <span class="text-gray-800 text-sm">
                  {{ formatFloat(reportData.fundamental?.ps_ratio) }}
                </span>
              </div>
              <div class="border p-2 rounded bg-white shadow-sm">
                <strong class="text-gray-700 block text-sm">Dividend Yield</strong>
                <span class="text-gray-800 text-sm">
                  {{ formatPct(reportData.fundamental?.dividend_yield) }}
                </span>
              </div>
              <div class="border p-2 rounded bg-white shadow-sm">
                <strong class="text-gray-700 block text-sm">Analyst Rec</strong>
                <span class="text-gray-800 text-sm">
                  {{ reportData.fundamental?.analyst_recommendation }}
                </span>
              </div>
              <div class="border p-2 rounded bg-white shadow-sm">
                <strong class="text-gray-700 block text-sm">Target Price</strong>
                <span class="text-gray-800 text-sm">
                  {{ formatFloat(reportData.fundamental?.target_price) }}
                </span>
              </div>
              <div class="border p-2 rounded bg-white shadow-sm">
                <strong class="text-gray-700 block text-sm">EPS</strong>
                <span class="text-gray-800 text-sm">
                  {{ formatFloat(reportData.fundamental?.earnings_per_share) }}
                </span>
              </div>
            </div>

            <!-- quarterly fundamentals chart -->
            <div class="mt-4 border border-gray-200 p-3 rounded">
              <canvas ref="quarterlyFundModalCanvasRef" width="400" height="200"></canvas>
            </div>

            <!-- advanced data -->
            <div class="mt-4 text-sm space-y-2">
              <p>
                <strong class="text-gray-700">Advanced Fundamentals:</strong>
              </p>
              <ul class="list-disc list-inside space-y-1">
                <li v-for="(val, key) in reportData.fundamental?.advanced_fundamentals || {}" :key="key">
                  <strong>{{ key }}:</strong> {{ val }}
                </li>
              </ul>

              <!-- dividends -->
              <div v-if="(reportData.fundamental?.dividend_history || []).length > 0" class="overflow-x-auto mt-2">
                <table class="border text-sm">
                  <thead class="bg-gray-100">
                    <tr>
                      <th class="px-2 py-1 border-r">Date</th>
                      <th class="px-2 py-1">Dividend</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="(d, dIdx) in reportData.fundamental.dividend_history" 
                      :key="dIdx"
                      class="border-b"
                    >
                      <td class="px-2 py-1 border-r">{{ d.date }}</td>
                      <td class="px-2 py-1">{{ d.dividend }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <!-- Risk & monthly returns chart -->
          <section>
            <h5 class="text-lg font-semibold text-gray-800 mb-2 flex items-center space-x-2 mt-4">
              <svg class="w-5 h-5 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2"
                  d="M4 6h16M4 10h16M4 14h16M4 18h16"
                />
              </svg>
              <span>Risk & Monthly Returns</span>
            </h5>
            <div class="flex flex-wrap gap-4 text-sm text-gray-700 mb-4">
              <div><strong>Beta:</strong> {{ reportData.risk?.beta }}</div>
              <div><strong>Sharpe:</strong> {{ reportData.risk?.sharpe_ratio }}</div>
              <div><strong>VaR 95%:</strong> {{ reportData.risk?.value_at_risk_95 }}</div>
              <div><strong>Max Drawdown:</strong> {{ reportData.risk?.max_drawdown }}</div>
              <div><strong>Volatility:</strong> {{ reportData.risk?.volatility }}</div>
            </div>
            <div class="border border-gray-200 p-3 rounded">
              <canvas ref="monthlyReturnsModalCanvasRef" width="400" height="200"></canvas>
            </div>
          </section>

          <!-- Stock Price -->
          <section>
            <h5 class="text-lg font-semibold text-gray-800 mb-2 flex items-center space-x-2 mt-4">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2"
                  d="M3 3h18M3 7h18M3 11h18M3 15h18M3 19h18"
                />
              </svg>
              <span>6-Month Weekly Stock Price</span>
            </h5>
            <div class="border border-gray-200 p-3 rounded">
              <canvas ref="stockPriceModalCanvasRef" width="400" height="200"></canvas>
            </div>
          </section>

          <!-- Comprehensive Summary -->
          <section>
            <h5 class="text-lg font-semibold text-gray-800 mb-2 mt-4">Comprehensive Summary</h5>
            <div class="text-sm text-gray-700 leading-relaxed" v-html="formattedSummary"></div>
          </section>
        </div>

        <!-- Modal Footer -->
        <div class="px-4 py-2 border-t border-gray-200 flex justify-end items-center space-x-3">
          <!-- Download PDF button -->
          <button
            @click="downloadPDF"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-700"
          >
            <svg
              class="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 4v16m8-8H4" />
            </svg>
            Download PDF
          </button>

          <!-- Close -->
          <button
            @click="$emit('close')"
            class="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import Chart from 'chart.js/auto'
import html2pdf from 'html2pdf.js'

// PROPS & Emits
const props = defineProps({
  open: { type: Boolean, default: false },
  reportData: { type: Object, required: true }
})
const emit = defineEmits(['close'])

// Format summary
const formattedSummary = computed(() => {
  if (!props.reportData?.comprehensive_summary) return ''
  const rawHtml = marked(props.reportData.comprehensive_summary)
  return DOMPurify.sanitize(rawHtml)
})

// Refs
const modalRootRef = ref(null)
let competitorModalChart = null
let quarterlyFundModalChart = null
let monthlyReturnsModalChart = null
let stockPriceModalChart = null

// Canvas refs
const competitorModalCanvasRef = ref(null)
const quarterlyFundModalCanvasRef = ref(null)
const monthlyReturnsModalCanvasRef = ref(null)
const stockPriceModalCanvasRef = ref(null)

// Lifecycle
onMounted(() => {
  setupCharts()
})
onBeforeUnmount(() => {
  destroyCharts()
})

// Whenever open changes, rebuild or destroy
watch(() => props.open, async (val) => {
  if (val) {
    await nextTick()
    setupCharts()
  } else {
    destroyCharts()
  }
}, { immediate: true })

/** Build or rebuild the charts */
function setupCharts() {
  if (!props.open) return
  destroyCharts()

  // 1) competitor
  if (
    competitorModalCanvasRef.value &&
    props.reportData?.competitor?.competitor_details?.length
  ) {
    const comps = props.reportData.competitor.competitor_details
    const names = comps.map(c => c.name)
    const mCaps = comps.map(c => parseFloat(c.market_cap || '0') / 1e9)
    const peRatios = comps.map(c => parseFloat(c.pe_ratio || '0'))

    competitorModalChart = new Chart(competitorModalCanvasRef.value, {
      type: 'bar',
      data: {
        labels: names,
        datasets: [
          {
            label: 'Market Cap (B)',
            data: mCaps,
            backgroundColor: 'rgba(99, 102, 241, 0.7)',
            yAxisID: 'y1'
          },
          {
            type: 'line',
            label: 'PE Ratio',
            data: peRatios,
            borderColor: 'rgba(255, 99, 132, 0.8)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            yAxisID: 'y2'
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y1: {
            type: 'linear',
            position: 'left',
            title: { display: true, text: 'Market Cap (B)' }
          },
          y2: {
            type: 'linear',
            position: 'right',
            grid: { drawOnChartArea: false },
            title: { display: true, text: 'PE Ratio' }
          }
        }
      }
    })
  }

  // 2) quarterly
  if (
    quarterlyFundModalCanvasRef.value &&
    props.reportData?.fundamental?.quarterly_fundamentals?.length
  ) {
    const qData = props.reportData.fundamental.quarterly_fundamentals.filter(
      q => q.total_revenue != null && q.net_income != null
    )
    if (qData.length > 0) {
      const labels = qData.map(q => q.date)
      const revs = qData.map(q => parseFloat(q.total_revenue || '0') / 1e9)
      const incs = qData.map(q => parseFloat(q.net_income || '0') / 1e9)

      quarterlyFundModalChart = new Chart(quarterlyFundModalCanvasRef.value, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              type: 'bar',
              label: 'Revenue (B)',
              data: revs,
              backgroundColor: 'rgba(59,130,246,0.7)',
              yAxisID: 'y1'
            },
            {
              type: 'bar',
              label: 'Net Income (B)',
              data: incs,
              backgroundColor: 'rgba(16,185,129,0.7)',
              yAxisID: 'y2'
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y1: {
              type: 'linear',
              position: 'left',
              title: { display: true, text: 'Revenue (B)' }
            },
            y2: {
              type: 'linear',
              position: 'right',
              grid: { drawOnChartArea: false },
              title: { display: true, text: 'Net Income (B)' }
            }
          }
        }
      })
    }
  }

  // 3) monthly returns
  if (
    monthlyReturnsModalCanvasRef.value &&
    props.reportData?.risk?.daily_returns?.length
  ) {
    const r = props.reportData.risk.daily_returns
    const xLabels = r.map(d => d.date)
    const yData = r.map(d => parseFloat(d.daily_return || '0') * 100)
    monthlyReturnsModalChart = new Chart(monthlyReturnsModalCanvasRef.value, {
      type: 'line',
      data: {
        labels: xLabels,
        datasets: [
          {
            label: 'Avg Monthly Return (%)',
            data: yData,
            borderColor: 'rgba(75,192,192,0.8)',
            backgroundColor: 'rgba(75,192,192,0.2)',
            tension: 0.2
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            title: { display: true, text: 'Return (%)' }
          },
          x: {
            title: { display: true, text: 'Month' }
          }
        }
      }
    })
  }

  // 4) stock price
  if (
    stockPriceModalCanvasRef.value &&
    props.reportData?.stock_price_data?.length
  ) {
    const sp = props.reportData.stock_price_data
    const xLabels = sp.map(d => d.date)
    const closePrices = sp.map(d => parseFloat(d.close || '0'))
    stockPriceModalChart = new Chart(stockPriceModalCanvasRef.value, {
      type: 'line',
      data: {
        labels: xLabels,
        datasets: [
          {
            label: 'Weekly Close',
            data: closePrices,
            borderColor: 'rgba(234,179,8,0.9)',
            backgroundColor: 'rgba(234,179,8,0.2)',
            tension: 0.2
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: { title: { display: true, text: 'Price (USD)' } },
          x: { title: { display: true, text: 'Week' } }
        }
      }
    })
  }
}

/** Destroy charts on close or unmount */
function destroyCharts() {
  if (competitorModalChart) {
    competitorModalChart.destroy()
    competitorModalChart = null
  }
  if (quarterlyFundModalChart) {
    quarterlyFundModalChart.destroy()
    quarterlyFundModalChart = null
  }
  if (monthlyReturnsModalChart) {
    monthlyReturnsModalChart.destroy()
    monthlyReturnsModalChart = null
  }
  if (stockPriceModalCanvasRef) {
    stockPriceModalChart?.destroy()
    stockPriceModalChart = null
  }
}

/** PDF Download */
async function downloadPDF() {
  if (!modalRootRef.value) return
  try {
    const opts = {
      margin: [10, 10],
      filename: 'financial_analysis_full_modal.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, letterRendering: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }
    await html2pdf().set(opts).from(modalRootRef.value).save()
  } catch(e) {
    console.error('Error generating PDF from modal:', e)
  }
}

/** Formatters */
function formatFloat(num, decimals=2) {
  if (!num || isNaN(num)) return '-'
  return parseFloat(num).toFixed(decimals)
}
function formatPct(num, decimals=2) {
  if (!num || isNaN(num)) return '-'
  const val = parseFloat(num) * 100
  return val.toFixed(decimals) + '%'
}
function formatBillion(num) {
  const n = parseFloat(num || '0')
  if (!num || isNaN(n) || n <= 0) return '-'
  const val = n / 1e9
  return val.toFixed(2) + 'B'
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity .2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ensure horizontal scroll on large charts if needed */
.chart-container {
  overflow-x: auto;
}
</style>
