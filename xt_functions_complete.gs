// XTrillion Bond Analytics - COMPLETE VERSION
// Version: 5.0 - All functions included (Array + Smart Cache + Legacy)
// This file combines all functionality in one place

var API_BASE = "https://future-footing-414610.uc.r.appspot.com";
var API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q";

// Cache for storing API responses
var responseCache = {};
// Persistent cache using Google Sheets Properties Service
var documentProperties = PropertiesService.getDocumentProperties();

// ============================================
// MAIN ARRAY FUNCTIONS (MOST COMMONLY USED)
// ============================================

/**
 * Process multiple bonds at once using the portfolio endpoint
 * THIS IS THE MAIN FUNCTION YOU WANT TO USE
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {string} settlement_date Optional settlement date (applies to all bonds)
 * @return {Array} 2D array with YTM, Duration, Spread for each bond
 * @customfunction
 */
function XT_ARRAY(bond_range, price_range, settlement_date) {
  // Handle both single cells and ranges
  var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
  var prices = Array.isArray(price_range) ? price_range : [[price_range]];
  
  // Flatten 2D arrays to 1D
  bonds = bonds.map(function(row) { return row[0]; }).filter(function(b) { return b; });
  prices = prices.map(function(row) { return row[0]; }).filter(function(p) { return p; });
  
  if (bonds.length === 0 || prices.length === 0) {
    return "No valid bonds provided";
  }
  
  // Ensure bonds and prices arrays are same length
  if (bonds.length !== prices.length) {
    return "Bond descriptions and prices must have same count";
  }
  
  // Build portfolio data for API
  var portfolio_data = [];
  for (var i = 0; i < bonds.length; i++) {
    if (bonds[i] && prices[i]) {
      portfolio_data.push({
        "description": String(bonds[i]),
        "CLOSING PRICE": Number(prices[i]),
        "WEIGHTING": 1.0 // Equal weight for simple calculation
      });
    }
  }
  
  if (portfolio_data.length === 0) {
    return "No valid bond data";
  }
  
  // Format settlement date if provided
  var formattedDate = settlement_date ? formatSettlementDate(settlement_date) : null;
  
  // Build request payload - using portfolio endpoint for bulk processing
  var payload = {
    "data": portfolio_data,
    "metrics": ["ytm", "duration", "spread"] // Request only needed metrics
  };
  
  if (formattedDate) {
    payload["settlement_date"] = formattedDate;
  }
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(API_BASE + "/api/v1/portfolio/analysis", options);
    
    if (response.getResponseCode() !== 200) {
      return "Service temporarily unavailable";
    }
    
    var data = JSON.parse(response.getContentText());
    
    // Extract results and format for spreadsheet
    if (data && data.bond_data) {
      var results = [];
      
      // Add header row
      results.push(["Bond", "YTM (%)", "Duration", "Spread (bps)"]);
      
      // Process each bond's results
      for (var i = 0; i < data.bond_data.length; i++) {
        var bond = data.bond_data[i];
        
        // API now returns raw numeric values - extract directly
        var ytm = bond.yield !== undefined && bond.yield !== null ? bond.yield : "N/A";
        var duration = bond.duration !== undefined && bond.duration !== null ? bond.duration : "N/A";
        var spread = bond.spread !== undefined && bond.spread !== null ? bond.spread : 0;
        
        results.push([
          bonds[i],  // Original bond description
          ytm,
          duration,
          spread
        ]);
      }
      
      return results;
    } else {
      return "Unable to process portfolio";
    }
    
  } catch (error) {
    return "API Error: " + error.toString();
  }
}

/**
 * Get specific metrics for multiple bonds (customizable)
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {string} metrics Comma-separated list of metrics (e.g., "ytm,duration,convexity,pvbp")
 * @param {string} settlement_date Optional settlement date
 * @return {Array} 2D array with requested metrics for each bond
 * @customfunction
 */
function XT_ARRAY_CUSTOM(bond_range, price_range, metrics, settlement_date) {
  // Handle both single cells and ranges
  var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
  var prices = Array.isArray(price_range) ? price_range : [[price_range]];
  
  // Flatten 2D arrays to 1D
  bonds = bonds.map(function(row) { return row[0]; }).filter(function(b) { return b; });
  prices = prices.map(function(row) { return row[0]; }).filter(function(p) { return p; });
  
  if (bonds.length === 0 || prices.length === 0) {
    return "No valid bonds provided";
  }
  
  // Parse metrics string
  var metricsList = metrics ? metrics.split(",").map(function(m) { return m.trim(); }) : ["ytm", "duration"];
  
  // Build portfolio data
  var portfolio_data = [];
  for (var i = 0; i < bonds.length; i++) {
    if (bonds[i] && prices[i]) {
      portfolio_data.push({
        "description": String(bonds[i]),
        "CLOSING PRICE": Number(prices[i]),
        "WEIGHTING": 1.0
      });
    }
  }
  
  var formattedDate = settlement_date ? formatSettlementDate(settlement_date) : null;
  
  var payload = {
    "data": portfolio_data,
    "metrics": metricsList
  };
  
  if (formattedDate) {
    payload["settlement_date"] = formattedDate;
  }
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(API_BASE + "/api/v1/portfolio/analysis", options);
    
    if (response.getResponseCode() !== 200) {
      return "Service temporarily unavailable";
    }
    
    var data = JSON.parse(response.getContentText());
    
    if (data && data.bond_data) {
      var results = [];
      
      // Add header row with metric names
      var headers = ["Bond"].concat(metricsList);
      results.push(headers);
      
      // Process each bond
      for (var i = 0; i < data.bond_data.length; i++) {
        var bond = data.bond_data[i];
        var row = [bonds[i]];
        
        // Extract each requested metric
        for (var j = 0; j < metricsList.length; j++) {
          var metric = metricsList[j];
          var value = extractMetricValue(bond, metric);
          row.push(value);
        }
        
        results.push(row);
      }
      
      return results;
    }
    
  } catch (error) {
    return "API Error: " + error.toString();
  }
}

// ============================================
// SMART CACHING FUNCTIONS
// ============================================

/**
 * Smart array function that only recalculates changed bonds
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {string} settlement_date Optional settlement date
 * @param {boolean} force_refresh Set to TRUE to force recalculation
 * @return {Array} 2D array with metrics for each bond
 * @customfunction
 */
function XT_SMART(bond_range, price_range, settlement_date, force_refresh) {
  // Handle both single cells and ranges
  var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
  var prices = Array.isArray(price_range) ? price_range : [[price_range]];
  
  // Flatten 2D arrays to 1D
  bonds = bonds.map(function(row) { return row[0]; }).filter(function(b) { return b; });
  prices = prices.map(function(row) { return row[0]; }).filter(function(p) { return p; });
  
  if (bonds.length !== prices.length) {
    return "Bond descriptions and prices must have same count";
  }
  
  // Get cached results
  var cache = getCachedResults();
  var needsUpdate = [];
  var results = [];
  
  // Add header row
  results.push(["Bond", "YTM (%)", "Duration", "Spread (bps)", "Status"]);
  
  // Check which bonds need updating
  for (var i = 0; i < bonds.length; i++) {
    var cacheKey = bonds[i] + "_" + prices[i] + "_" + (settlement_date || "default");
    
    if (!force_refresh && cache[cacheKey]) {
      // Use cached value
      var cachedData = cache[cacheKey];
      results.push([
        bonds[i],
        cachedData.ytm,
        cachedData.duration,
        cachedData.spread,
        "Cached"
      ]);
    } else {
      // Needs update
      needsUpdate.push({
        index: i,
        bond: bonds[i],
        price: prices[i],
        cacheKey: cacheKey
      });
      // Placeholder row
      results.push([bonds[i], "Updating...", "Updating...", "Updating...", "New"]);
    }
  }
  
  // If nothing needs updating, return cached results
  if (needsUpdate.length === 0) {
    return results;
  }
  
  // Process only bonds that need updating
  var updateResults = processBondBatch(needsUpdate, settlement_date);
  
  // Update cache and results
  for (var j = 0; j < updateResults.length; j++) {
    var update = updateResults[j];
    var resultIndex = update.index + 1; // +1 for header row
    
    results[resultIndex] = [
      update.bond,
      update.ytm,
      update.duration,
      update.spread,
      "Updated"
    ];
    
    // Update cache
    cache[update.cacheKey] = {
      ytm: update.ytm,
      duration: update.duration,
      spread: update.spread,
      timestamp: new Date().getTime()
    };
  }
  
  // Save updated cache
  saveCachedResults(cache);
  
  return results;
}

// ============================================
// INDIVIDUAL BOND FUNCTIONS (LEGACY SUPPORT)
// ============================================

/**
 * Calculate bond yield to maturity
 * @customfunction
 */
function xt_ytm(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, ["ytm"]);
    
    if (data && data.analytics && typeof data.analytics.ytm === 'number') {
      return data.analytics.ytm;
    } else {
      return "Unable to calculate yield for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate bond modified duration
 * @customfunction
 */
function xt_duration(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, ["duration"]);
    
    if (data && data.analytics && typeof data.analytics.duration === 'number') {
      return data.analytics.duration;
    } else {
      return "Unable to calculate duration for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate bond spread
 * @customfunction
 */
function xt_spread(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, ["spread"]);
    
    if (data && data.analytics) {
      return data.analytics.spread || 0;
    } else {
      return "Unable to calculate spread for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function formatSettlementDate(settlement_date) {
  if (!settlement_date) {
    return null;
  }
  
  try {
    var dateObj;
    
    if (settlement_date instanceof Date) {
      dateObj = settlement_date;
    } else if (typeof settlement_date === 'string') {
      var dateStr = settlement_date.trim();
      if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
        return dateStr;
      }
      dateObj = new Date(dateStr);
    } else if (typeof settlement_date === 'number') {
      var excelEpoch = new Date(1900, 0, 1);
      dateObj = new Date(excelEpoch.getTime() + (settlement_date - 2) * 24 * 60 * 60 * 1000);
    } else {
      return null;
    }
    
    if (dateObj && !isNaN(dateObj.getTime())) {
      var year = dateObj.getFullYear();
      var month = ('0' + (dateObj.getMonth() + 1)).slice(-2);
      var day = ('0' + dateObj.getDate()).slice(-2);
      return year + '-' + month + '-' + day;
    }
    
    return null;
  } catch (error) {
    return null;
  }
}

function callBondAPIOptimized(bond_description, price, settlement_date, metrics) {
  // Create cache key
  var cacheKey = bond_description + "_" + price + "_" + (settlement_date || "default") + "_" + (metrics || []).join(",");
  
  // Check cache first
  if (responseCache[cacheKey]) {
    return responseCache[cacheKey];
  }
  
  // Use new /bond/quick endpoint for better performance
  var url = API_BASE + "/api/v1/bond/quick";
  
  // Build optimized payload
  var payload = {
    "description": bond_description,
    "price": price
  };
  
  // Add settlement date if provided
  var formattedDate = formatSettlementDate(settlement_date);
  if (formattedDate) {
    payload["settlement_date"] = formattedDate;
  }
  
  // Add specific metrics if requested (otherwise defaults to ytm, duration, spread)
  if (metrics && metrics.length > 0) {
    payload["metrics"] = metrics;
  }
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(url, options);
    
    if (response.getResponseCode() !== 200) {
      throw new Error("Service temporarily unavailable");
    }
    
    var data = JSON.parse(response.getContentText());
    
    // Cache the response
    responseCache[cacheKey] = data;
    
    return data;
  } catch (error) {
    throw new Error("Unable to connect to bond analytics service");
  }
}

function extractMetricValue(bond, metric) {
  // Map metric names to bond data fields - API now returns raw numbers
  switch(metric.toLowerCase()) {
    case 'ytm':
    case 'yield':
      return bond.yield !== undefined && bond.yield !== null ? bond.yield : "N/A";
    
    case 'duration':
      return bond.duration !== undefined && bond.duration !== null ? bond.duration : "N/A";
    
    case 'spread':
      return bond.spread !== undefined && bond.spread !== null ? bond.spread : 0;
    
    case 'accrued_interest':
      return bond.accrued_interest !== undefined && bond.accrued_interest !== null ? bond.accrued_interest : "N/A";
    
    case 'price':
      return bond.price !== undefined && bond.price !== null ? bond.price : "N/A";
    
    default:
      return bond[metric] !== undefined && bond[metric] !== null ? bond[metric] : "N/A";
  }
}

function getCachedResults() {
  var cacheStr = documentProperties.getProperty('bond_cache');
  return cacheStr ? JSON.parse(cacheStr) : {};
}

function saveCachedResults(cache) {
  // Limit cache size to prevent quota issues
  var keys = Object.keys(cache);
  if (keys.length > 500) {
    // Remove oldest entries
    var sorted = keys.sort(function(a, b) {
      return (cache[a].timestamp || 0) - (cache[b].timestamp || 0);
    });
    
    for (var i = 0; i < 100; i++) {
      delete cache[sorted[i]];
    }
  }
  
  documentProperties.setProperty('bond_cache', JSON.stringify(cache));
}

function processBondBatch(bonds, settlement_date) {
  if (bonds.length === 0) return [];
  
  // Build portfolio data
  var portfolio_data = bonds.map(function(item) {
    return {
      "description": item.bond,
      "CLOSING PRICE": item.price,
      "WEIGHTING": 1.0
    };
  });
  
  var payload = {
    "data": portfolio_data,
    "metrics": ["ytm", "duration", "spread"]
  };
  
  if (settlement_date) {
    payload["settlement_date"] = formatSettlementDate(settlement_date);
  }
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(API_BASE + "/api/v1/portfolio/analysis", options);
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      
      if (data && data.bond_data) {
        return bonds.map(function(item, index) {
          var bondData = data.bond_data[index];
          return {
            index: item.index,
            bond: item.bond,
            cacheKey: item.cacheKey,
            ytm: bondData.yield !== undefined && bondData.yield !== null ? bondData.yield : "N/A",
            duration: bondData.duration !== undefined && bondData.duration !== null ? bondData.duration : "N/A",
            spread: bondData.spread !== null ? bondData.spread : 0
          };
        });
      }
    }
  } catch (error) {
    // Return error results
    return bonds.map(function(item) {
      return {
        index: item.index,
        bond: item.bond,
        cacheKey: item.cacheKey,
        ytm: "Error",
        duration: "Error",
        spread: "Error"
      };
    });
  }
  
  return [];
}

// ============================================
// DYNAMIC RANGE DETECTION
// ============================================

/**
 * Automatically detect and process all bonds starting from a range
 * More Google Sheets native - pass a range directly
 * 
 * @param {Array} starting_range The range starting with first bond (e.g., A2:C100)
 * @return {Array} 2D array with YTM, Duration, Spread for all detected bonds
 * @customfunction
 */
function XT_DYNAMIC(starting_range) {
  // If a single cell is passed, treat it as the start of bond column
  if (!Array.isArray(starting_range)) {
    starting_range = [[starting_range]];
  }
  
  // Check if this is a single column or multiple columns
  var numCols = starting_range[0].length;
  var bonds = [];
  var prices = [];
  var settlementDate = null;
  
  if (numCols >= 2) {
    // Multiple columns passed - extract bonds and prices
    for (var i = 0; i < starting_range.length; i++) {
      if (starting_range[i][0] && starting_range[i][0].toString().trim() !== "") {
        bonds.push([starting_range[i][0]]);
        prices.push([starting_range[i][1] || 0]);
        
        // Get settlement date from third column if present and if first row
        if (numCols >= 3 && i === 0 && starting_range[i][2]) {
          settlementDate = starting_range[i][2];
        }
      } else {
        break; // Stop at first empty bond cell
      }
    }
  } else {
    // Single column passed - this is just bonds, need to get prices from next column
    // This is tricky in custom functions, so return an error message
    return "Please select at least 2 columns (bonds and prices). Example: =XT_DYNAMIC(A2:B100)";
  }
  
  if (bonds.length === 0) {
    return "No valid bonds found in the range";
  }
  
  // Process using XT_ARRAY
  return XT_ARRAY(bonds, prices, settlementDate);
}

/**
 * Alternative dynamic function that takes separate ranges (more flexible)
 * 
 * @param {Array} bond_column First bond cell or range (e.g., A2:A)
 * @param {Array} price_column First price cell or range (e.g., B2:B)
 * @param {*} settlement Optional settlement date
 * @return {Array} 2D array with results
 * @customfunction
 */
function XT_AUTO(bond_column, price_column, settlement) {
  // This works more like standard Google Sheets functions
  // You can pass full columns and it will process until it hits empty cells
  
  if (!bond_column || !price_column) {
    return "Please provide bond and price columns";
  }
  
  // Convert to arrays if single cells
  if (!Array.isArray(bond_column)) {
    bond_column = [[bond_column]];
  }
  if (!Array.isArray(price_column)) {
    price_column = [[price_column]];
  }
  
  // Extract valid bonds and prices (stop at first empty)
  var bonds = [];
  var prices = [];
  
  var maxRows = Math.min(bond_column.length, price_column.length);
  
  for (var i = 0; i < maxRows; i++) {
    var bond = bond_column[i][0];
    var price = price_column[i][0];
    
    if (bond && bond.toString().trim() !== "" && price) {
      bonds.push([bond]);
      prices.push([price]);
    } else if (!bond || bond.toString().trim() === "") {
      break; // Stop at first empty bond
    }
  }
  
  if (bonds.length === 0) {
    return "No valid bond/price pairs found";
  }
  
  // Use XT_ARRAY to process
  return XT_ARRAY(bonds, prices, settlement);
}

/**
 * Process bonds with individual settlement dates for each bond
 * 
 * @param {Array} data_range Range containing bonds, prices, and dates in columns
 * @return {Array} 2D array with results for each bond
 * @customfunction
 */
function XT_ARRAY_WITH_DATES(data_range) {
  if (!data_range || !Array.isArray(data_range)) {
    return "Please provide a data range with bonds, prices, and dates";
  }
  
  var results = [];
  results.push(["Bond", "YTM (%)", "Duration", "Spread (bps)"]);
  
  // Process each row individually since dates differ
  for (var i = 0; i < data_range.length; i++) {
    var row = data_range[i];
    if (row[0] && row[1]) { // Has bond and price
      var bond = row[0];
      var price = row[1];
      var date = row[2] || null;
      
      // Call API for this bond
      try {
        var data = callBondAPIOptimized(bond, price, date, ["ytm", "duration", "spread"]);
        
        if (data && data.analytics) {
          results.push([
            bond,
            data.analytics.ytm || "N/A",
            data.analytics.duration || "N/A",
            data.analytics.spread || 0
          ]);
        } else {
          results.push([bond, "Error", "Error", "Error"]);
        }
      } catch (error) {
        results.push([bond, "Error", "Error", "Error"]);
      }
    }
  }
  
  return results;
}

/**
 * Process large portfolios in batches
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {number} batch_size Number of bonds per batch (default 100)
 * @param {string} settlement_date Optional settlement date
 * @return {Array} 2D array with results for all bonds
 * @customfunction
 */
function XT_BATCH_PROCESS(bond_range, price_range, batch_size, settlement_date) {
  // Set default batch size
  batch_size = batch_size || 100;
  
  // Handle both single cells and ranges
  var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
  var prices = Array.isArray(price_range) ? price_range : [[price_range]];
  
  // Flatten 2D arrays to 1D
  bonds = bonds.map(function(row) { return row[0]; }).filter(function(b) { return b; });
  prices = prices.map(function(row) { return row[0]; }).filter(function(p) { return p; });
  
  if (bonds.length !== prices.length) {
    return "Bond descriptions and prices must have same count";
  }
  
  var allResults = [];
  allResults.push(["Bond", "YTM (%)", "Duration", "Spread (bps)", "Batch"]);
  
  // Process in batches
  var numBatches = Math.ceil(bonds.length / batch_size);
  
  for (var b = 0; b < numBatches; b++) {
    var startIdx = b * batch_size;
    var endIdx = Math.min(startIdx + batch_size, bonds.length);
    
    var batchBonds = bonds.slice(startIdx, endIdx);
    var batchPrices = prices.slice(startIdx, endIdx);
    
    // Process this batch
    var batchResults = XT_ARRAY(batchBonds, batchPrices, settlement_date);
    
    // Skip header row from batch results and add batch number
    for (var i = 1; i < batchResults.length; i++) {
      var row = batchResults[i];
      row.push(b + 1); // Add batch number
      allResults.push(row);
    }
    
    // Add small delay between batches to avoid rate limiting
    if (b < numBatches - 1) {
      Utilities.sleep(100); // 100ms delay
    }
  }
  
  return allResults;
}

// ============================================
// PORTFOLIO ANALYSIS FUNCTIONS
// ============================================

/**
 * Calculate portfolio-level summary statistics
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {Array} weight_range Range containing portfolio weights
 * @param {string} settlement_date Optional settlement date
 * @return {Array} Portfolio summary statistics
 * @customfunction
 */
function XT_PORTFOLIO_SUMMARY(bond_range, price_range, weight_range, settlement_date) {
  // Handle ranges
  var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
  var prices = Array.isArray(price_range) ? price_range : [[price_range]];
  var weights = Array.isArray(weight_range) ? weight_range : [[weight_range]];
  
  // Flatten arrays
  bonds = bonds.map(function(row) { return row[0]; }).filter(function(b) { return b; });
  prices = prices.map(function(row) { return row[0]; }).filter(function(p) { return p; });
  weights = weights.map(function(row) { return row[0]; }).filter(function(w) { return w; });
  
  if (bonds.length !== prices.length || bonds.length !== weights.length) {
    return "All ranges must have the same number of elements";
  }
  
  // Normalize weights
  var totalWeight = weights.reduce(function(sum, w) { return sum + Number(w); }, 0);
  var normalizedWeights = weights.map(function(w) { return Number(w) / totalWeight; });
  
  // Build portfolio data
  var portfolio_data = [];
  for (var i = 0; i < bonds.length; i++) {
    portfolio_data.push({
      "description": String(bonds[i]),
      "CLOSING PRICE": Number(prices[i]),
      "WEIGHTING": normalizedWeights[i] * 100 // API expects percentage
    });
  }
  
  var payload = {
    "data": portfolio_data,
    "context": "portfolio"
  };
  
  if (settlement_date) {
    payload["settlement_date"] = formatSettlementDate(settlement_date);
  }
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(API_BASE + "/api/v1/portfolio/analysis", options);
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      
      if (data && data.portfolio_summary) {
        var summary = data.portfolio_summary;
        
        // Format as table for spreadsheet
        return [
          ["Metric", "Value"],
          ["Weighted Avg YTM", summary.weighted_avg_yield || "N/A"],
          ["Portfolio Duration", summary.portfolio_duration || "N/A"],
          ["Portfolio Convexity", summary.portfolio_convexity || "N/A"],
          ["Total Market Value", summary.total_market_value || "N/A"],
          ["Number of Bonds", bonds.length],
          ["Settlement Date", settlement_date || "Prior month-end"]
        ];
      }
    }
  } catch (error) {
    return "Error calculating portfolio summary: " + error.toString();
  }
  
  return "Unable to calculate portfolio summary";
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Get version information
 * @customfunction
 */
function XT_VERSION() {
  return "XTrillion v5.0 - Complete";
}

/**
 * Check API health status
 * @customfunction
 */
function XT_HEALTH_CHECK() {
  try {
    var response = UrlFetchApp.fetch(API_BASE + "/health", {
      "method": "GET",
      "muteHttpExceptions": true
    });
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      return "API Status: " + data.status + " | Databases: " + data.database_status;
    } else {
      return "API Status: Unavailable";
    }
  } catch (error) {
    return "API Status: Connection Error";
  }
}

/**
 * Get API usage statistics
 * @customfunction
 */
function XT_API_STATS() {
  var cache = getCachedResults();
  var cacheSize = Object.keys(cache).length;
  var sessionCacheSize = Object.keys(responseCache).length;
  
  return [
    ["Metric", "Value"],
    ["Cached Bonds", cacheSize],
    ["Session Cache", sessionCacheSize],
    ["API Endpoint", API_BASE],
    ["Last Updated", new Date().toLocaleString()]
  ];
}

// ============================================
// CACHE MANAGEMENT
// ============================================

/**
 * Clear all cached data
 * @customfunction
 */
function XT_CLEAR_CACHE() {
  responseCache = {};
  documentProperties.deleteAllProperties();
  return "Cache cleared successfully";
}

/**
 * Get cache statistics
 * @customfunction
 */
function XT_CACHE_SIZE() {
  var cache = getCachedResults();
  var count = Object.keys(cache).length;
  return count + " bonds cached";
}

// ============================================
// QUICK START GUIDE
// ============================================

/**
 * MAIN FUNCTIONS TO USE:
 * 
 * 1. XT_ARRAY(bond_range, price_range, settlement_date)
 *    - Process multiple bonds in ONE API call
 *    - Example: =XT_ARRAY(A2:A51, B2:B51)
 *    - Returns: YTM, Duration, Spread for all bonds
 * 
 * 2. XT_ARRAY_CUSTOM(bond_range, price_range, "metrics", settlement_date)
 *    - Choose which metrics to return
 *    - Example: =XT_ARRAY_CUSTOM(A2:A51, B2:B51, "ytm,duration,convexity")
 * 
 * 3. XT_SMART(bond_range, price_range, settlement_date, force_refresh)
 *    - Only recalculates changed bonds (uses cache)
 *    - Example: =XT_SMART(A2:A51, B2:B51, C2, FALSE)
 * 
 * INDIVIDUAL BOND FUNCTIONS (backward compatible):
 * - xt_ytm(bond, price, date)
 * - xt_duration(bond, price, date)
 * - xt_spread(bond, price, date)
 * 
 * CACHE MANAGEMENT:
 * - XT_CLEAR_CACHE() - Clear all cached data
 * - XT_CACHE_SIZE() - Show number of cached bonds
 * 
 * Version 5.0 - Complete implementation with all features
 */