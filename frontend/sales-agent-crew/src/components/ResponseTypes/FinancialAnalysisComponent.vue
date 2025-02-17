<template>
    <div class="container mx-auto p-4 w-full">
      <!-- Display an error message if present -->
      <div v-if="error" class="bg-red-100 text-red-700 p-2 rounded mb-4">
        {{ error }}
      </div>
      <!-- Render financial analysis if no error -->
      <div v-else>
        <!-- Basic Information -->
        <section class="mb-6">
          <h1 class="text-3xl font-bold mb-2">
            {{ parsed.data.company_name }} ({{ parsed.data.ticker }})
          </h1>
        </section>
  
        <!-- Competitor Analysis -->
        <section class="mb-6">
          <h2 class="text-2xl font-semibold mb-2">Competitor Analysis</h2>
          <div class="mb-4">
            <p>
              <strong>Competitor Tickers:</strong>
              <span v-if="parsed.data.competitor?.competitor_tickers">
                {{ parsed.data.competitor.competitor_tickers.join(', ') }}
              </span>
            </p>
          </div>
          <div class="overflow-x-auto w-full">
            <table class="w-full table-fixed border-collapse border border-gray-300 text-sm">
              <thead>
                <tr class="bg-gray-200">
                  <th class="border px-4 py-2 break-words">Ticker</th>
                  <th class="border px-4 py-2 break-words">Name</th>
                  <th class="border px-4 py-2 break-words">Market Cap</th>
                  <th class="border px-4 py-2 break-words">PE Ratio</th>
                  <th class="border px-4 py-2 break-words">PS Ratio</th>
                  <th class="border px-4 py-2 break-words">EBITDA Margins</th>
                  <th class="border px-4 py-2 break-words">Profit Margins</th>
                  <th class="border px-4 py-2 break-words">Revenue Growth</th>
                  <th class="border px-4 py-2 break-words">Earnings Growth</th>
                  <th class="border px-4 py-2 break-words">Short Ratio</th>
                  <th class="border px-4 py-2 break-words">Industry</th>
                  <th class="border px-4 py-2 break-words">Sector</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(competitor, index) in parsed.data.competitor.competitor_details"
                  :key="index"
                >
                  <td class="border px-4 py-2 break-words">{{ competitor.ticker }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.name }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.market_cap }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.pe_ratio }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.ps_ratio }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.ebitda_margins }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.profit_margins }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.revenue_growth }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.earnings_growth }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.short_ratio }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.industry }}</td>
                  <td class="border px-4 py-2 break-words">{{ competitor.sector }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
  
        <!-- Fundamental Analysis -->
        <section class="mb-6">
          <h2 class="text-2xl font-semibold mb-2">Fundamental Analysis</h2>
          <div class="overflow-x-auto w-full mb-4">
            <table class="w-full table-fixed border-collapse border border-gray-300 text-sm">
              <tbody>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Company Name</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.company_name }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Sector</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.sector }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Industry</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.industry }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Market Cap</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.market_cap }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">PE Ratio</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.pe_ratio }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Forward PE</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.forward_pe }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">PEG Ratio</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.peg_ratio || 'N/A' }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">PS Ratio</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.ps_ratio }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Price to Book</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.price_to_book }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Dividend Yield</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.dividend_yield }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Beta</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.beta }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">52 Week High</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.year_high }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">52 Week Low</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.year_low }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Analyst Recommendation</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.analyst_recommendation }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Target Price</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.target_price }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Earnings per Share</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.earnings_per_share }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Profit Margins</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.profit_margins }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Operating Margins</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.operating_margins }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">EBITDA Margins</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.ebitda_margins }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Short Ratio</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.short_ratio }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Return on Assets</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.return_on_assets }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Revenue Growth</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.revenue_growth }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Net Income Growth</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.net_income_growth }}</td>
                </tr>
              </tbody>
            </table>
          </div>
  
          <!-- Quarterly Fundamentals -->
          <h3 class="text-xl font-semibold mb-2">Quarterly Fundamentals</h3>
          <div class="overflow-x-auto w-full">
            <table class="w-full table-fixed border-collapse border border-gray-300 text-sm">
              <thead>
                <tr class="bg-gray-200">
                  <th class="border px-4 py-2 break-words">Date</th>
                  <th class="border px-4 py-2 break-words">Total Revenue</th>
                  <th class="border px-4 py-2 break-words">Net Income</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(qFund, index) in parsed.data.fundamental.quarterly_fundamentals"
                  :key="index"
                >
                  <td class="border px-4 py-2 break-words">{{ qFund.date }}</td>
                  <td class="border px-4 py-2 break-words">{{ qFund.total_revenue }}</td>
                  <td class="border px-4 py-2 break-words">{{ qFund.net_income }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
  
        <!-- Advanced Fundamentals -->
        <section class="mb-6">
          <h2 class="text-2xl font-semibold mb-2">Advanced Fundamentals</h2>
          <div class="overflow-x-auto w-full">
            <table class="w-full table-fixed border-collapse border border-gray-300 text-sm">
              <tbody>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Shares Outstanding</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.advanced_fundamentals.shares_outstanding }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Float Shares</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.advanced_fundamentals.float_shares }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Enterprise Value</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.advanced_fundamentals.enterprise_value }}</td>
                </tr>
                <tr>
                  <td class="border px-4 py-2 font-semibold break-words">Book Value</td>
                  <td class="border px-4 py-2 break-words">{{ parsed.data.fundamental.advanced_fundamentals.book_value }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
  
        <!-- Dividend History -->
        <section class="mb-6">
          <h2 class="text-2xl font-semibold mb-2">Dividend History</h2>
          <div v-if="parsed.data.fundamental.dividend_history && parsed.data.fundamental.dividend_history.length">
            <div class="overflow-x-auto w-full">
              <table class="w-full table-fixed border-collapse border border-gray-300 text-sm">
                <thead>
                  <tr class="bg-gray-200">
                    <th class="border px-4 py-2 break-words">Date</th>
                    <th class="border px-4 py-2 break-words">Dividend</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(dividend, index) in parsed.data.fundamental.dividend_history"
                    :key="index"
                  >
                    <td class="border px-4 py-2 break-words">{{ dividend.date }}</td>
                    <td class="border px-4 py-2 break-words">{{ dividend.dividend }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else>
            <p class="text-gray-500">No dividend history available.</p>
          </div>
        </section>
  
        <!-- Risk Analysis -->
        <section class="mb-6">
          <h2 class="text-2xl font-semibold mb-2">Risk Analysis</h2>
          <div class="mb-4 text-sm">
            <p><strong>Beta:</strong> {{ parsed.data.risk.beta }}</p>
            <p><strong>Sharpe Ratio:</strong> {{ parsed.data.risk.sharpe_ratio }}</p>
            <p><strong>Value at Risk (95%):</strong> {{ parsed.data.risk.value_at_risk_95 }}</p>
            <p><strong>Max Drawdown:</strong> {{ parsed.data.risk.max_drawdown }}</p>
            <p><strong>Volatility:</strong> {{ parsed.data.risk.volatility }}</p>
          </div>
          <h3 class="text-xl font-semibold mb-2">Daily Returns</h3>
          <div class="overflow-x-auto w-full">
            <table class="w-full table-fixed border-collapse border border-gray-300 text-sm">
              <thead>
                <tr class="bg-gray-200">
                  <th class="border px-4 py-2 break-words">Date</th>
                  <th class="border px-4 py-2 break-words">Daily Return</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(daily, index) in parsed.data.risk.daily_returns" :key="index">
                  <td class="border px-4 py-2 break-words">{{ daily.date }}</td>
                  <td class="border px-4 py-2 break-words">{{ daily.daily_return }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
  
        <!-- Stock Price Data -->
        <section class="mb-6">
          <h2 class="text-2xl font-semibold mb-2">Stock Price Data</h2>
          <div class="overflow-x-auto w-full">
            <table class="w-full table-fixed border-collapse border border-gray-300 text-sm">
              <thead>
                <tr class="bg-gray-200">
                  <th class="border px-4 py-2 break-words">Date</th>
                  <th class="border px-4 py-2 break-words">Open</th>
                  <th class="border px-4 py-2 break-words">High</th>
                  <th class="border px-4 py-2 break-words">Low</th>
                  <th class="border px-4 py-2 break-words">Close</th>
                  <th class="border px-4 py-2 break-words">Volume</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(stock, index) in parsed.data.stock_price_data" :key="index">
                  <td class="border px-4 py-2 break-words">{{ stock.date }}</td>
                  <td class="border px-4 py-2 break-words">{{ stock.open }}</td>
                  <td class="border px-4 py-2 break-words">{{ stock.high }}</td>
                  <td class="border px-4 py-2 break-words">{{ stock.low }}</td>
                  <td class="border px-4 py-2 break-words">{{ stock.close }}</td>
                  <td class="border px-4 py-2 break-words">{{ stock.volume }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
  
        <!-- Comprehensive Summary -->
        <section class="mb-6">
          <h2 class="text-2xl font-semibold mb-2">Comprehensive Summary</h2>
          <div class="bg-gray-100 p-4 rounded-lg shadow text-sm">
            <p class="whitespace-pre-line text-gray-800">
              {{ parsed.data.comprehensive_summary }}
            </p>
          </div>
        </section>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'FinancialAnalysis',
    props: {
      // The API response should be nested under parsed.data
      parsed: {
        type: Object,
        required: true,
      },
    },
    computed: {
      error() {
        // If an error message exists within parsed.data.error, display it.
        return this.parsed.data?.error || '';
      },
    },
  };
  </script>
  
  <style scoped>
  /* Additional scoped styles if needed */
  </style>
  