<template>
    <transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center"
      >
        <div class="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col relative">
          <!-- Modal Header -->
          <div class="flex items-center justify-between px-4 py-2 border-b border-gray-200">
            <h3 class="font-semibold text-lg text-gray-800">
              Full Financial Analysis
            </h3>
            <button
              @click="$emit('close')"
              class="text-gray-500 hover:text-gray-700 focus:outline-none"
            >
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
            ref="modalContentRef"
            class="p-4 overflow-y-auto space-y-6 flex-1"
            id="financial-modal-root"
          >
            <!-- Company Overview -->
            <section>
              <h4 class="text-md font-semibold text-gray-700 mb-2">
                Company: {{ reportData.company_name }} ({{ reportData.ticker }})
              </h4>
            </section>
  
            <!-- Competitor Chart + Table -->
            <section>
              <h5 class="font-semibold text-sm mb-2">Competitor Analysis</h5>
  
              <!-- Chart -->
              <div class="border border-gray-200 p-3 rounded-lg chart-container mb-3">
                <canvas ref="competitorModalCanvasRef" width="400" height="250"></canvas>
              </div>
  
              <!-- Table -->
              <table class="w-full border text-sm">
                <thead class="bg-gray-100 border-b text-left">
                  <tr>
                    <th class="px-2 py-1 border-r">Ticker</th>
                    <th class="px-2 py-1 border-r">Name</th>
                    <th class="px-2 py-1 border-r">Market Cap</th>
                    <th class="px-2 py-1 border-r">PE Ratio</th>
                    <th class="px-2 py-1 border-r">PS Ratio</th>
                    <th class="px-2 py-1 border-r">Rev Growth</th>
                    <th class="px-2 py-1">Earnings Growth</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(comp, cIdx) in reportData.competitor?.competitor_details || []"
                    :key="cIdx"
                    class="border-b"
                  >
                    <td class="px-2 py-1 border-r">{{ comp.ticker }}</td>
                    <td class="px-2 py-1 border-r">{{ comp.name }}</td>
                    <td class="px-2 py-1 border-r">{{ comp.market_cap }}</td>
                    <td class="px-2 py-1 border-r">{{ comp.pe_ratio }}</td>
                    <td class="px-2 py-1 border-r">{{ comp.ps_ratio }}</td>
                    <td class="px-2 py-1 border-r">{{ comp.revenue_growth }}</td>
                    <td class="px-2 py-1">{{ comp.earnings_growth }}</td>
                  </tr>
                </tbody>
              </table>
            </section>
  
            <!-- Fundamentals & margins donut -->
            <section>
              <h5 class="font-semibold text-sm mb-2 mt-4">Fundamentals & Margins</h5>
              <div class="text-sm text-gray-700 flex flex-wrap gap-6 mb-4">
                <p><strong>Market Cap:</strong> {{ reportData.fundamental?.market_cap }}</p>
                <p><strong>PE Ratio:</strong> {{ reportData.fundamental?.pe_ratio }}</p>
                <p><strong>Forward PE:</strong> {{ reportData.fundamental?.forward_pe }}</p>
                <p><strong>PS Ratio:</strong> {{ reportData.fundamental?.ps_ratio }}</p>
                <p><strong>Dividend Yield:</strong> {{ reportData.fundamental?.dividend_yield }}</p>
                <p><strong>Analyst Rec:</strong> {{ reportData.fundamental?.analyst_recommendation }}</p>
                <p><strong>Target Price:</strong> {{ reportData.fundamental?.target_price }}</p>
                <p><strong>Earnings/Share:</strong> {{ reportData.fundamental?.earnings_per_share }}</p>
              </div>
  
              <!-- donut chart for margins -->
              <div class="border border-gray-200 p-3 rounded-lg chart-container">
                <canvas ref="marginsModalCanvasRef" width="300" height="250"></canvas>
              </div>
            </section>
  
            <!-- Risk & daily returns chart -->
            <section>
              <h5 class="font-semibold text-sm mb-2 mt-4">Risk Profile & Daily Returns</h5>
              <div class="text-sm text-gray-700 flex flex-wrap gap-6 mb-4">
                <p><strong>Beta:</strong> {{ reportData.risk?.beta }}</p>
                <p><strong>Sharpe Ratio:</strong> {{ reportData.risk?.sharpe_ratio }}</p>
                <p><strong>VaR (95%):</strong> {{ reportData.risk?.value_at_risk_95 }}</p>
                <p><strong>Max Drawdown:</strong> {{ reportData.risk?.max_drawdown }}</p>
                <p><strong>Volatility:</strong> {{ reportData.risk?.volatility }}</p>
              </div>
  
              <div class="border border-gray-200 p-3 rounded-lg chart-container">
                <canvas ref="dailyReturnsModalCanvasRef" width="300" height="250"></canvas>
              </div>
            </section>
  
            <!-- Comprehensive Summary -->
            <section>
              <h5 class="font-semibold text-sm mb-2 mt-4">Comprehensive Summary</h5>
              <div class="text-sm text-gray-700 leading-relaxed" v-html="formattedSummary">
              </div>
            </section>
          </div>
  
          <!-- Modal Footer -->
          <div class="px-4 py-2 border-t border-gray-200 flex justify-end items-center space-x-3">
            <!-- Download PDF button -->
            <button
              @click="downloadPDF"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-700"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
  import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
  import DOMPurify from 'dompurify'
  import { marked } from 'marked'
  import Chart from 'chart.js/auto'
  import html2pdf from 'html2pdf.js'
  
  const props = defineProps({
    open: {
      type: Boolean,
      default: false
    },
    reportData: {
      type: Object,
      required: true
    }
  })
  
  const emit = defineEmits(['close'])
  
  const formattedSummary = computed(() => {
    return DOMPurify.sanitize(marked(props.reportData?.comprehensive_summary || ''))
  })
  
  // Refs for the chart canvases
  let competitorModalChart = null
  let marginsModalChart = null
  let dailyReturnsModalChart = null
  
  const competitorModalCanvasRef = ref(null)
  const marginsModalCanvasRef = ref(null)
  const dailyReturnsModalCanvasRef = ref(null)
  
  // The container we will convert to PDF
  const modalContentRef = ref(null)
  
  // Setup watchers + lifecycle
  onMounted(() => {
    setupCharts()
  })
  
  onBeforeUnmount(() => {
    destroyCharts()
  })
  
  watch(() => props.open, async (newVal) => {
    if (newVal) {
      // If the modal is opening, we might need to defer a bit 
      // so the DOM is painted before we create charts
      await nextTick()
      setupCharts()
    } else {
      destroyCharts()
    }
  })
  
  function destroyCharts() {
    if (competitorModalChart) {
      competitorModalChart.destroy()
      competitorModalChart = null
    }
    if (marginsModalChart) {
      marginsModalChart.destroy()
      marginsModalChart = null
    }
    if (dailyReturnsModalChart) {
      dailyReturnsModalChart.destroy()
      dailyReturnsModalChart = null
    }
  }
  
  async function setupCharts() {
    // Only build charts if open
    if (!props.open) return
  
    // Destroy existing first
    destroyCharts()
  
    // 1) competitor
    if (competitorModalCanvasRef.value && props.reportData?.competitor?.competitor_details?.length) {
      const competitorDetails = props.reportData.competitor.competitor_details
      const names = competitorDetails.map(c => c.name)
      const marketCaps = competitorDetails.map(c => {
        const mc = parseFloat(c.market_cap || '0')
        return mc > 0 ? mc / 1e9 : 0
      })
      const peRatios = competitorDetails.map(c => parseFloat(c.pe_ratio || '0'))
  
      competitorModalChart = new Chart(competitorModalCanvasRef.value, {
        data: {
          labels: names,
          datasets: [
            {
              type: 'bar',
              label: 'Market Cap (B)',
              data: marketCaps,
              backgroundColor: 'rgba(99, 102, 241, 0.8)',
              yAxisID: 'y1'
            },
            {
              type: 'line',
              label: 'PE Ratio',
              data: peRatios,
              borderColor: 'rgba(255, 99, 132, 0.8)',
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
  
    // 2) margins
    if (marginsModalCanvasRef.value && props.reportData?.fundamental) {
      const f = props.reportData.fundamental
      const pm = parseFloat(f.profit_margins || '0')
      const om = parseFloat(f.operating_margins || '0')
      const em = parseFloat(f.ebitda_margins || '0')
      // if at least one is > 0, we do chart
      if (pm !== 0 || om !== 0 || em !== 0) {
        marginsModalChart = new Chart(marginsModalCanvasRef.value, {
          type: 'doughnut',
          data: {
            labels: ['Profit Margin', 'Operating Margin', 'EBITDA Margin'],
            datasets: [
              {
                data: [pm, om, em],
                backgroundColor: [
                  'rgba(16, 185, 129, 0.7)',
                  'rgba(234, 179, 8, 0.7)',
                  'rgba(59, 130, 246, 0.7)'
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
  
    // 3) daily returns
    if (dailyReturnsModalCanvasRef.value && props.reportData?.risk?.daily_returns?.length) {
      const dailyData = props.reportData.risk.daily_returns
      const xLabels = dailyData.map(d => d.date)
      const returnsData = dailyData.map(d => parseFloat(d.daily_return || '0') * 100)
  
      dailyReturnsModalChart = new Chart(dailyReturnsModalCanvasRef.value, {
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
   * Download PDF from the modal content
   */
  async function downloadPDF() {
    if (!modalContentRef.value) {
      console.warn('No modalContentRef found for PDF generation.')
      return
    }
    const pdfOpts = {
      margin: [10, 10],
      filename: 'financial_full_report.pdf',
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
      await html2pdf().set(pdfOpts).from(modalContentRef.value).save()
    } catch (error) {
      console.error('Error generating PDF:', error)
    }
  }
  </script>
  
  <style scoped>
  .fade-enter-active, .fade-leave-active {
    transition: opacity .2s;
  }
  .fade-enter-from, .fade-leave-to {
    opacity: 0;
  }
  
  .chart-container {
    overflow-x: auto;
  }
  </style>
  