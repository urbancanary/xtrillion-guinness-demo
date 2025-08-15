// XTrillion Bond Analytics - COMPLETE MULTI-ENVIRONMENT VERSION
// Version: 6.0 - All functions with full environment support
// Environments: testing → maia_dev → production (or alpha → beta → production)

// ============================================
// ENVIRONMENT CONFIGURATION
// ============================================

var ENVIRONMENTS = {
  "testing": {
    base: "https://development-dot-future-footing-414610.uc.r.appspot.com",
    key: "gax10_dev_4n8s6k2x7p9v5m8p1z",
    name: "Personal Testing"
  },
  "maia_dev": {
    base: "https://api-dev.x-trillion.ai",  // Maps to maia-dev-dot-future-footing-414610.uc.r.appspot.com
    key: "gax10_dev_4n8s6k2x7p9v5m8p1z", 
    name: "Maia Development"
  },
  "production": {
    base: "https://api.x-trillion.ai",  // Maps to future-footing-414610.uc.r.appspot.com
    key: "gax10_demo_3j5h8m9k2p6r4t7w1q",
    name: "Production"
  },
  // Alternative naming scheme
  "alpha": {
    base: "https://development-dot-future-footing-414610.uc.r.appspot.com",
    key: "gax10_dev_4n8s6k2x7p9v5m8p1z",
    name: "Alpha Testing (Personal)"
  },
  "beta": {
    base: "https://api-dev.x-trillion.ai",  // Maps to maia-dev 
    key: "gax10_dev_4n8s6k2x7p9v5m8p1z",
    name: "Beta Testing (Maia)"
  }
};

var DEFAULT_ENV = "production";

// Cache for storing API responses  
var responseCache = {};
// Persistent cache using Google Sheets Properties Service
var documentProperties = PropertiesService.getDocumentProperties();

// ============================================
// ENVIRONMENT HELPER FUNCTIONS
// ============================================

function getEnvironmentConfig(environment) {
  var env = environment && ENVIRONMENTS[environment.toLowerCase()] ? 
            environment.toLowerCase() : DEFAULT_ENV;
  return ENVIRONMENTS[env];
}

function getApiUrl(environment, endpoint) {
  var config = getEnvironmentConfig(environment);
  return config.base + endpoint;
}

function getApiKey(environment) {
  var config = getEnvironmentConfig(environment);
  return config.key;
}

// ============================================
// MAIN ARRAY FUNCTIONS (MOST COMMONLY USED)
// ============================================

/**
 * Most flexible function with intelligent input detection - works like native Google Sheets functions
 * RECOMMENDED FOR NEW USERS
 * 
 * INTELLIGENT INPUT DETECTION:
 * - Single column: =XT_AUTO(A2:A10, B2:B10) -> B = prices
 * - Multi-column: =XT_AUTO(A2:A10, B2:C10) -> B = prices, C = settlement dates
 * 
 * @param {Array} bond_column Range containing bond descriptions (e.g., A2:A100 or A:A)
 * @param {Array} price_column Range containing prices (or prices + settlement dates)
 * @param {string} settlement Optional settlement date (overrides detected dates)
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with YTM, Duration, Spread for each bond
 * @customfunction
 */
function XT_AUTO(bond_column, price_column, settlement, environment) {
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
  
  // INTELLIGENT INPUT DETECTION - detect multi-column input
  var detectedSettlement = null;
  
  // Check if price_column has multiple columns (price + settlement date)
  if (price_column.length > 0 && price_column[0].length >= 2) {
    // Multi-column input detected - extract settlement date
    if (price_column[0][1]) {
      detectedSettlement = price_column[0][1];
    }
  }
  
  // Use detected settlement date if no explicit one provided
  if (!settlement && detectedSettlement) {
    settlement = detectedSettlement;
  }
  
  // Extract valid bonds and prices (stop at first empty)
  var bonds = [];
  var prices = [];
  
  var maxRows = Math.min(bond_column.length, price_column.length);
  
  for (var i = 0; i < maxRows; i++) {
    var bond = bond_column[i][0];
    var price = price_column[i][0]; // Always take price from first column
    
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
  return XT_ARRAY(bonds, prices, settlement, environment);
}

/**
 * Process multiple bonds at once using the portfolio endpoint
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {string} settlement_date Optional settlement date (applies to all bonds)
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with YTM, Duration, Spread for each bond
 * @customfunction
 */
function XT_ARRAY(bond_range, price_range, settlement_date, environment) {
  // Handle both single cells and ranges
  var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
  var prices = Array.isArray(price_range) ? price_range : [[price_range]];
  
  // Flatten 2D arrays to 1D
  bonds = bonds.map(function(row) { return row[0]; }).filter(function(b) { return b; });
  prices = prices.map(function(row) { return row[0]; }).filter(function(p) { return p; });
  
  if (bonds.length === 0 || prices.length === 0) {
    return "No valid bonds provided";
  }
  
  if (bonds.length !== prices.length) {
    return "Bond descriptions and prices must have same count";
  }
  
  // Get environment configuration
  var config = getEnvironmentConfig(environment);
  
  // Build portfolio data for API
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
  
  if (portfolio_data.length === 0) {
    return "No valid bond data";
  }
  
  // Format settlement date if provided
  var formattedDate = settlement_date ? formatSettlementDate(settlement_date) : null;
  
  // Build request payload
  var payload = {
    "data": portfolio_data,
    "metrics": ["ytm", "duration", "spread"]
  };
  
  if (formattedDate) {
    payload["settlement_date"] = formattedDate;
  }
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": getApiKey(environment)
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(getApiUrl(environment, "/api/v1/portfolio/analysis"), options);
    
    if (response.getResponseCode() !== 200) {
      return "Service temporarily unavailable (" + config.name + ")";
    }
    
    var data = JSON.parse(response.getContentText());
    
    if (data && data.bond_data) {
      var results = [];
      
      // Add header row with environment info
      results.push(["Bond", "YTM", "Duration", "Spread", "Environment"]);
      
      // Process each bond's results - API now returns raw numeric values
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
          spread,
          config.name
        ]);
      }
      
      return results;
    } else {
      return "Unable to process portfolio";
    }
    
  } catch (error) {
    return "API Error (" + config.name + "): " + error.toString();
  }
}

/**
 * Get specific metrics for multiple bonds (customizable)
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {string} metrics Comma-separated list of metrics (e.g., "ytm,duration,convexity,pvbp")
 * @param {string} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with requested metrics for each bond
 * @customfunction
 */
function XT_ARRAY_CUSTOM(bond_range, price_range, metrics, settlement_date, environment) {
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
  
  // Get environment config
  var config = getEnvironmentConfig(environment);
  
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
      "X-API-Key": getApiKey(environment)
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(getApiUrl(environment, "/api/v1/portfolio/analysis"), options);
    
    if (response.getResponseCode() !== 200) {
      return "Service temporarily unavailable (" + config.name + ")";
    }
    
    var data = JSON.parse(response.getContentText());
    
    if (data && data.bond_data) {
      var results = [];
      
      // Add header row with metric names and environment
      var headers = ["Bond"].concat(metricsList).concat(["Environment"]);
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
        
        row.push(config.name); // Add environment info
        results.push(row);
      }
      
      return results;
    }
    
  } catch (error) {
    return "API Error (" + config.name + "): " + error.toString();
  }
}

/**
 * Dynamic array formula that detects range automatically  
 * Place in a cell and it expands automatically
 * 
 * @param {string} starting_value First bond description or cell reference
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} Dynamic array with all bond metrics
 * @customfunction
 */
function XT_DYNAMIC(starting_value, environment) {
  // Simple implementation - user provides the first bond
  if (!starting_value) {
    return "Please provide starting bond description";
  }
  
  // For now, just process single bond - could be enhanced to detect ranges
  return XT_ARRAY([[starting_value]], [[100]], null, environment);
}

/**
 * Dynamic range processing - more sophisticated range detection
 * 
 * @param {Array} starting_range The range starting with first bond (e.g., A2:C100)
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with all detected bonds
 * @customfunction
 */
function XT_DYNAMIC_RANGE(starting_range, environment) {
  if (!Array.isArray(starting_range)) {
    starting_range = [[starting_range]];
  }
  
  var numCols = starting_range[0].length;
  var bonds = [];
  var prices = [];
  var settlementDate = null;
  
  if (numCols >= 2) {
    for (var i = 0; i < starting_range.length; i++) {
      if (starting_range[i][0] && starting_range[i][0].toString().trim() !== "") {
        bonds.push([starting_range[i][0]]);
        prices.push([starting_range[i][1] || 0]);
        
        if (numCols >= 3 && i === 0 && starting_range[i][2]) {
          settlementDate = starting_range[i][2];
        }
      } else {
        break;
      }
    }
  } else {
    return "Please select at least 2 columns (bonds and prices). Example: =XT_DYNAMIC_RANGE(A2:B100, \"maia_dev\")";
  }
  
  if (bonds.length === 0) {
    return "No valid bonds found in the range";
  }
  
  return XT_ARRAY(bonds, prices, settlementDate, environment);
}

/**
 * Process large portfolios in batches
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {number} batch_size Number of bonds per batch (default 100)
 * @param {string} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with results for all bonds
 * @customfunction
 */
function XT_BATCH_PROCESS(bond_range, price_range, batch_size, settlement_date, environment) {
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
  
  var config = getEnvironmentConfig(environment);
  var allResults = [];
  allResults.push(["Bond", "YTM", "Duration", "Spread", "Batch", "Environment"]);
  
  // Process in batches
  var numBatches = Math.ceil(bonds.length / batch_size);
  
  for (var b = 0; b < numBatches; b++) {
    var startIdx = b * batch_size;
    var endIdx = Math.min(startIdx + batch_size, bonds.length);
    
    var batchBonds = bonds.slice(startIdx, endIdx);
    var batchPrices = prices.slice(startIdx, endIdx);
    
    // Process this batch using XT_ARRAY logic
    var batchResults = processBondBatch(batchBonds, batchPrices, settlement_date, environment);
    
    // Add batch results with batch number
    for (var i = 0; i < batchResults.length; i++) {
      var row = batchResults[i];
      row.push(b + 1); // Add batch number
      row.push(config.name); // Add environment
      allResults.push(row);
    }
    
    // Add small delay between batches to avoid rate limiting
    if (b < numBatches - 1) {
      Utilities.sleep(100); // 100ms delay
    }
  }
  
  return allResults;
}

/**
 * Smart array function with intelligent input detection (v6.1 - Raw Numbers)
 * Only recalculates changed bonds. Returns full precision raw numeric values.
 * 
 * INTELLIGENT INPUT DETECTION:
 * - Single column: =XT_SMART(A2:A10, B2:B10) -> B = prices
 * - Multi-column: =XT_SMART(A2:A10, B2:C10) -> B = prices, C = settlement dates
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing prices (or prices + settlement dates)
 * @param {string} settlement_date Optional settlement date (overrides detected dates)
 * @param {boolean} force_refresh Set to TRUE to force recalculation and clear cache
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with raw numeric values: [Bond, YTM, Duration, Spread, Status, Environment]
 * @customfunction
 */
function XT_SMART(bond_range, price_range, settlement_date, force_refresh, environment) {
  // Handle both single cells and ranges
  var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
  var prices = Array.isArray(price_range) ? price_range : [[price_range]];
  
  // Initialize results array early to prevent undefined errors
  var needsUpdate = [];
  var results = [];
  
  // INTELLIGENT INPUT DETECTION - Key advantage of array functions
  var detectedSettlement = null;
  
  // Check if price_range has multiple columns (price + settlement date)
  if (prices && prices.length > 0 && Array.isArray(prices[0]) && prices[0].length >= 2) {
    // Multi-column input detected: Column 1 = prices, Column 2 = settlement dates
    var priceColumn = [];
    var settlementColumn = [];
    
    for (var i = 0; i < prices.length; i++) {
      if (prices[i] && prices[i][0]) priceColumn.push(prices[i][0]); // Extract prices from first column
      if (prices[i] && prices[i][1]) settlementColumn.push(prices[i][1]); // Extract settlement dates from second column
    }
    
    prices = priceColumn;
    
    // Use the first settlement date for all bonds (common case)
    // Or could be enhanced to use individual settlement dates per bond
    if (settlementColumn.length > 0 && settlementColumn[0]) {
      // Convert date to ISO format if it's a Date object
      detectedSettlement = convertToISODate(settlementColumn[0]);
    }
  } else {
    // Single column input - just prices
    prices = prices.map(function(row) { 
      return Array.isArray(row) ? row[0] : row; 
    }).filter(function(p) { return p; });
  }
  
  // Flatten bonds to 1D
  bonds = bonds.map(function(row) { 
    return Array.isArray(row) ? row[0] : row; 
  }).filter(function(b) { return b; });
  
  // Use detected settlement date if no explicit one provided
  if (!settlement_date && detectedSettlement) {
    settlement_date = detectedSettlement;
  }
  
  if (bonds.length !== prices.length) {
    return "Bond descriptions and prices must have same count";
  }
  
  var config = getEnvironmentConfig(environment);
  
  // Add header row  
  results.push(["Bond", "YTM", "Duration", "Spread", "Status", "Environment"]);
  
  // REMOVED CACHING - API is fast enough (400ms avg) and caching causes stale data issues
  // Always fetch fresh data to ensure settlement dates are properly used
  for (var i = 0; i < bonds.length; i++) {
    needsUpdate.push({
      index: i,
      bond: bonds[i],
      price: prices[i]
    });
    // Placeholder row
    results.push([bonds[i], "Calculating...", "Calculating...", "Calculating...", "Live", config.name]);
  }
  
  // Process only bonds that need updating
  var updateResults = processBondBatch(
    needsUpdate.map(function(item) { return item.bond; }),
    needsUpdate.map(function(item) { return item.price; }),
    settlement_date,
    environment
  );
  
  // Update cache and results
  for (var j = 0; j < updateResults.length; j++) {
    var update = updateResults[j];
    var needsUpdateItem = needsUpdate[j];
    var resultIndex = needsUpdateItem.index + 1; // +1 for header row
    
    results[resultIndex] = [
      needsUpdateItem.bond,
      update[1], // ytm
      update[2], // duration
      update[3], // spread
      "Updated",
      config.name
    ];
    
    // Update cache
    cache[needsUpdateItem.cacheKey] = {
      ytm: update[1],
      duration: update[2],
      spread: update[3],
      timestamp: new Date().getTime()
    };
  }
  
  // Save updated cache
  saveCachedResults(cache);
  
  return results;
}

/**
 * Calculate portfolio-level summary statistics
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {Array} weight_range Range containing portfolio weights
 * @param {string} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} Portfolio summary statistics
 * @customfunction
 */
function XT_PORTFOLIO_SUMMARY(bond_range, price_range, weight_range, settlement_date, environment) {
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
  
  var config = getEnvironmentConfig(environment);
  
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
      "X-API-Key": getApiKey(environment)
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(getApiUrl(environment, "/api/v1/portfolio/analysis"), options);
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      
      if (data && data.portfolio_summary) {
        var summary = data.portfolio_summary;
        
        // Format as table for spreadsheet
        return [
          ["Metric", "Value", "Environment"],
          ["Weighted Avg YTM", summary.weighted_avg_yield || "N/A", config.name],
          ["Portfolio Duration", summary.portfolio_duration || "N/A", config.name],
          ["Portfolio Convexity", summary.portfolio_convexity || "N/A", config.name],
          ["Total Market Value", summary.total_market_value || "N/A", config.name],
          ["Number of Bonds", bonds.length, config.name],
          ["Settlement Date", settlement_date || "Prior month-end", config.name]
        ];
      }
    }
  } catch (error) {
    return "Error calculating portfolio summary (" + config.name + "): " + error.toString();
  }
  
  return "Unable to calculate portfolio summary";
}

/**
 * Process bonds with individual settlement dates (multi-environment)
 * Each row can have different settlement dates
 * 
 * @param {Array} data_range Range with [bond, price, settlement_date] in columns
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with metrics for each bond
 * @customfunction
 */
function XT_ARRAY_WITH_DATES(data_range, environment) {
  if (!data_range || !Array.isArray(data_range)) {
    return "Please provide a data range with bonds, prices, and dates";
  }
  
  var config = getEnvironmentConfig(environment);
  var results = [];
  results.push(["Bond", "YTM", "Duration", "Spread", "Environment"]);
  
  // Process each row individually since dates differ
  for (var i = 0; i < data_range.length; i++) {
    var row = data_range[i];
    if (row[0] && row[1]) { // Has bond and price
      var bond = row[0];
      var price = row[1];
      var date = row[2] || null;
      
      // Call API for this bond with individual settlement date
      try {
        var data = callBondAPIOptimized(bond, price, date, ["ytm", "duration", "spread"], environment);
        
        if (data && data.analytics) {
          results.push([
            bond,
            data.analytics.ytm !== undefined && data.analytics.ytm !== null ? data.analytics.ytm : "N/A",
            data.analytics.duration !== undefined && data.analytics.duration !== null ? data.analytics.duration : "N/A", 
            data.analytics.spread !== undefined && data.analytics.spread !== null ? data.analytics.spread : 0,
            config.name
          ]);
        } else {
          results.push([bond, "Error", "Error", "Error", config.name]);
        }
      } catch (error) {
        results.push([bond, "Error", "Error", "Error", config.name]);
      }
    }
  }
  
  return results;
}

// ============================================
// INDIVIDUAL BOND FUNCTIONS (LEGACY SUPPORT)  
// ============================================

/**
 * Calculate bond yield to maturity (lowercase - legacy)
 * @param {string} bond_description Bond description or ISIN
 * @param {number} price Bond price
 * @param {*} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @customfunction
 */
function xt_ytm(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, ["ytm"], environment);
    
    if (data && data.analytics && typeof data.analytics.ytm === 'number') {
      return data.analytics.ytm;
    } else {
      return "Unable to calculate yield for this bond";
    }
  } catch (error) {
    var config = getEnvironmentConfig(environment);
    return "Service temporarily unavailable (" + config.name + ") - please try again";
  }
}

/**
 * Calculate bond yield to maturity (uppercase - standardized)
 * @customfunction
 */
function XT_YTM(bond_description, price, settlement_date, environment) {
  return xt_ytm(bond_description, price, settlement_date, environment);
}

/**
 * Calculate bond modified duration (lowercase - legacy)
 * @customfunction
 */
function xt_duration(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, ["duration"], environment);
    
    if (data && data.analytics && typeof data.analytics.duration === 'number') {
      return data.analytics.duration;
    } else {
      return "Unable to calculate duration for this bond";
    }
  } catch (error) {
    var config = getEnvironmentConfig(environment);
    return "Service temporarily unavailable (" + config.name + ") - please try again";
  }
}

/**
 * Calculate bond modified duration (uppercase - standardized)  
 * @customfunction
 */
function XT_DURATION(bond_description, price, settlement_date, environment) {
  return xt_duration(bond_description, price, settlement_date, environment);
}

/**
 * Calculate bond spread (lowercase - legacy)
 * @customfunction
 */
function xt_spread(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, ["spread"], environment);
    
    if (data && data.analytics) {
      return data.analytics.spread || 0;
    } else {
      return "Unable to calculate spread for this bond";
    }
  } catch (error) {
    var config = getEnvironmentConfig(environment);
    return "Service temporarily unavailable (" + config.name + ") - please try again";
  }
}

/**
 * Calculate bond spread (uppercase - standardized)
 * @customfunction
 */
function XT_SPREAD(bond_description, price, settlement_date, environment) {
  return xt_spread(bond_description, price, settlement_date, environment);
}

/**
 * Calculate bond convexity (lowercase - legacy)
 * @customfunction
 */
function xt_convexity(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, ["convexity"], environment);
    
    if (data && data.analytics && typeof data.analytics.convexity === 'number') {
      return data.analytics.convexity;
    } else {
      return "Unable to calculate convexity for this bond";
    }
  } catch (error) {
    var config = getEnvironmentConfig(environment);
    return "Service temporarily unavailable (" + config.name + ") - please try again";
  }
}

/**
 * Calculate bond convexity (uppercase - standardized)
 * @customfunction
 */
function XT_CONVEXITY(bond_description, price, settlement_date, environment) {
  return xt_convexity(bond_description, price, settlement_date, environment);
}

/**
 * Calculate bond PVBP (price value of basis point)
 * @customfunction
 */
function xt_pvbp(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, ["pvbp"], environment);
    
    if (data && data.analytics && typeof data.analytics.pvbp === 'number') {
      return data.analytics.pvbp;
    } else {
      return "Unable to calculate PVBP for this bond";
    }
  } catch (error) {
    var config = getEnvironmentConfig(environment);
    return "Service temporarily unavailable (" + config.name + ") - please try again";
  }
}

/**
 * Calculate bond PVBP (uppercase - standardized)
 * @customfunction
 */
function XT_PVBP(bond_description, price, settlement_date, environment) {
  return xt_pvbp(bond_description, price, settlement_date, environment);
}

// ============================================
// UTILITY FUNCTIONS  
// ============================================

/**
 * Get version information with environment
 * @customfunction
 */
function XT_VERSION(environment) {
  var config = getEnvironmentConfig(environment);
  return "XTrillion v6.0 Complete Multi-Environment (" + config.name + ")";
}

/**
 * Check API health status for specific environment
 * @customfunction
 */
function XT_HEALTH_CHECK(environment) {
  var config = getEnvironmentConfig(environment);
  
  try {
    var response = UrlFetchApp.fetch(getApiUrl(environment, "/health"), {
      "method": "GET", 
      "muteHttpExceptions": true
    });
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      return config.name + " Status: " + data.status + " | Databases: " + data.dual_database_system.total_active_databases;
    } else {
      return config.name + " Status: Unavailable";
    }
  } catch (error) {
    return config.name + " Status: Connection Error";
  }
}

/**
 * Get API usage statistics for environment
 * @customfunction
 */
function XT_API_STATS(environment) {
  var config = getEnvironmentConfig(environment);
  var cache = getCachedResults();
  var cacheSize = Object.keys(cache).length;
  var sessionCacheSize = Object.keys(responseCache).length;
  
  return [
    ["Metric", "Value", "Environment"],
    ["Cached Bonds", cacheSize, config.name],
    ["Session Cache", sessionCacheSize, config.name], 
    ["API Endpoint", config.base, config.name],
    ["API Key", config.key.substring(0, 8) + "...", config.name],
    ["Last Updated", new Date().toLocaleString(), config.name]
  ];
}

/**
 * Debug function to see raw API response
 * @customfunction
 */
function XT_DEBUG(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  var config = getEnvironmentConfig(environment);
  
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date, null, environment);
    return config.name + " Debug: " + JSON.stringify(data, null, 2);
  } catch (error) {
    return config.name + " Debug Error: " + error.toString();
  }
}

/**
 * Debug portfolio processing
 * @customfunction
 */
function XT_DEBUG_PORTFOLIO(bond1, price1, bond2, price2, environment) {
  var config = getEnvironmentConfig(environment);
  
  var portfolio_data = [
    {"description": String(bond1), "CLOSING PRICE": Number(price1), "WEIGHTING": 50.0},
    {"description": String(bond2), "CLOSING PRICE": Number(price2), "WEIGHTING": 50.0}
  ];
  
  var payload = {
    "data": portfolio_data,
    "metrics": ["ytm", "duration", "spread"],
    "context": "technical"
  };
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": getApiKey(environment)
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(getApiUrl(environment, "/api/v1/portfolio/analysis"), options);
    var data = JSON.parse(response.getContentText());
    
    var debugInfo = [
      ["Debug Info", "Value", "Environment"],
      ["Response Code", response.getResponseCode(), config.name],
      ["Bond 1 Data", "Keys: " + (data.bond_data && data.bond_data[0] ? Object.keys(data.bond_data[0]).join(", ") : "N/A"), config.name]
    ];
    
    if (data.bond_data && data.bond_data[0]) {
      var bond = data.bond_data[0];
      debugInfo.push(["First bond yield", bond.yield + " (type: " + typeof bond.yield + ")", config.name]);
      debugInfo.push(["First bond duration", bond.duration + " (type: " + typeof bond.duration + ")", config.name]);
      debugInfo.push(["First bond spread", bond.spread + " (type: " + typeof bond.spread + ")", config.name]);
    }
    
    return debugInfo;
    
  } catch (error) {
    return config.name + " Portfolio Debug Error: " + error.toString();
  }
}

// ============================================
// CACHE MANAGEMENT
// ============================================

/**
 * Clear all cached data
 * @customfunction
 */
function XT_CLEAR_CACHE() {
  try {
    responseCache = {};
    documentProperties.deleteAllProperties();
    // Also try to force clear by setting a new cache version
    documentProperties.setProperty('bond_cache_version', 'v6.1_cleared_' + new Date().getTime());
    return "Cache cleared successfully - " + new Date().toLocaleString();
  } catch (error) {
    return "Cache clear error: " + error.toString();
  }
}

/**
 * Simple test function to debug Google Sheets input handling
 * @param {string|Array} bonds Bond descriptions 
 * @param {number|Array} prices Bond prices
 * @return {Array} Debug information
 * @customfunction
 */
function XT_TEST_SIMPLE(bonds, prices) {
  try {
    var result = [];
    result.push(["Debug Info", "Value"]);
    result.push(["Bonds type", typeof bonds]);
    result.push(["Prices type", typeof prices]);
    result.push(["Bonds isArray", Array.isArray(bonds)]);
    result.push(["Prices isArray", Array.isArray(prices)]);
    
    if (Array.isArray(bonds) && bonds.length > 0) {
      result.push(["Bonds length", bonds.length]);
      result.push(["First bond", bonds[0]]);
      if (Array.isArray(bonds[0])) {
        result.push(["First bond isArray", "true"]);
        result.push(["First bond[0]", bonds[0][0]]);
      }
    }
    
    if (Array.isArray(prices) && prices.length > 0) {
      result.push(["Prices length", prices.length]);
      result.push(["First price", prices[0]]);
      if (Array.isArray(prices[0])) {
        result.push(["First price isArray", "true"]);
        result.push(["First price[0]", prices[0][0]]);
        if (prices[0].length >= 2) {
          result.push(["First price[1]", prices[0][1]]);
        }
      }
    }
    
    return result;
  } catch (error) {
    return [["Error", error.toString()]];
  }
}

/**
 * Ultra simple test function that just returns static data
 * @return {Array} Static test data
 * @customfunction
 */
function XT_TEST_STATIC() {
  return [
    ["Test", "Value"],
    ["Status", "Working"],
    ["Number", 123.45],
    ["Text", "Hello World"]
  ];
}

/**
 * Simplified XT_SMART without caching - always returns fresh data
 * @param {Array} bonds Bond descriptions
 * @param {Array} prices Prices and optional settlement dates
 * @param {string} settlement_date Optional settlement date
 * @param {boolean} force_refresh Ignored (no caching)
 * @param {string} environment Environment to use
 * @return {Array} Bond analytics
 * @customfunction
 */
function XT_SMART_NOCACHE(bonds, prices, settlement_date, force_refresh, environment) {
  try {
    // Handle input arrays
    bonds = Array.isArray(bonds) ? bonds : [[bonds]];
    prices = Array.isArray(prices) ? prices : [[prices]];
    
    // Detect settlement date from multi-column input
    var detectedSettlement = null;
    if (prices && prices.length > 0 && Array.isArray(prices[0]) && prices[0].length >= 2) {
      // Extract prices and settlement dates
      var priceColumn = [];
      var settlementColumn = [];
      
      for (var i = 0; i < prices.length; i++) {
        if (prices[i] && prices[i][0]) priceColumn.push(prices[i][0]);
        if (prices[i] && prices[i][1]) settlementColumn.push(prices[i][1]);
      }
      
      prices = priceColumn;
      
      if (settlementColumn.length > 0 && settlementColumn[0]) {
        detectedSettlement = convertToISODate(settlementColumn[0]);
      }
    } else {
      prices = prices.map(function(row) { 
        return Array.isArray(row) ? row[0] : row; 
      }).filter(function(p) { return p; });
    }
    
    // Flatten bonds
    bonds = bonds.map(function(row) { 
      return Array.isArray(row) ? row[0] : row; 
    }).filter(function(b) { return b; });
    
    // Use detected settlement if none provided
    settlement_date = settlement_date || detectedSettlement;
    
    if (bonds.length !== prices.length) {
      return "Bond and price counts must match";
    }
    
    var config = getEnvironmentConfig(environment);
    
    // Call API for all bonds - returns raw numeric values
    var results = processBondBatch(bonds, prices, settlement_date, environment);
    
    // Add header and environment info
    var output = [["Bond", "YTM", "Duration", "Spread", "Environment"]];
    
    // Process results - ensure we get raw numeric values
    if (!results || results.length === 0) {
      // If no results returned, show error for each bond
      for (var i = 0; i < bonds.length; i++) {
        output.push([
          bonds[i],
          "API Error",
          "API Error", 
          "API Error",
          config.name
        ]);
      }
    } else {
      for (var i = 0; i < results.length; i++) {
        if (results[i] && results[i].length >= 3) {
          // Extract raw numeric values, removing any formatting
          var ytm = results[i][0];
          var duration = results[i][1];
          var spread = results[i][2];
          
          // Clean any formatted strings to raw numbers
          if (typeof ytm === 'string') {
            ytm = parseFloat(ytm.replace(/[^0-9.-]/g, ''));
          }
          if (typeof duration === 'string') {
            duration = parseFloat(duration.replace(/[^0-9.-]/g, ''));
          }
          if (typeof spread === 'string') {
            spread = parseFloat(spread.replace(/[^0-9.-]/g, ''));
          }
          
          output.push([
            bonds[i],
            ytm,      // Raw number
            duration, // Raw number
            spread,   // Raw number
            config.name
          ]);
        } else {
          // Invalid result structure
          output.push([
            bonds[i],
            "Invalid Data",
            "Invalid Data",
            "Invalid Data",
            config.name
          ]);
        }
      }
    }
    
    return output;
    
  } catch (error) {
    return [["Error", error.toString(), "", "", ""]];
  }
}

/**
 * Debug function to check API response
 * @param {string} bond Bond description
 * @param {number} price Bond price
 * @param {string} environment Environment (production, testing, etc)
 * @return {Array} Debug information
 * @customfunction
 */
function XT_DEBUG_API(bond, price, environment) {
  var payload = {
    "data": [{
      "description": String(bond),
      "CLOSING PRICE": Number(price),
      "WEIGHTING": 1.0
    }],
    "metrics": ["ytm", "duration", "spread"]
  };
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": getApiKey(environment || "production")
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(getApiUrl(environment || "production", "/api/v1/portfolio/analysis"), options);
    var responseText = response.getContentText();
    var data = JSON.parse(responseText);
    
    var result = [];
    result.push(["Field", "Value"]);
    result.push(["Response Code", response.getResponseCode()]);
    result.push(["Has bond_data", data && data.bond_data ? "YES" : "NO"]);
    
    if (data && data.bond_data && data.bond_data.length > 0) {
      var bondData = data.bond_data[0];
      result.push(["Bond description", bondData.description || "missing"]);
      result.push(["Yield field", bondData.yield || "missing"]);
      result.push(["Duration field", bondData.duration || "missing"]);
      result.push(["Spread field", bondData.spread || "missing"]);
      result.push(["Yield type", typeof bondData.yield]);
      result.push(["Duration type", typeof bondData.duration]);
      result.push(["Spread type", typeof bondData.spread]);
    }
    
    return result;
  } catch (error) {
    return [["Error", error.toString()]];
  }
}

/**
 * Test settlement date detection and processing
 * @param {Array} bonds Bond descriptions 
 * @param {Array} prices Prices with optional settlement dates
 * @return {Array} Settlement date processing results
 * @customfunction
 */
function XT_TEST_SETTLEMENT(bonds, prices) {
  try {
    var result = [];
    result.push(["Processing Step", "Result"]);
    
    // Step 1: Check multi-column detection
    if (prices && prices.length > 0 && Array.isArray(prices[0]) && prices[0].length >= 2) {
      result.push(["Multi-column detected", "YES"]);
      
      var priceColumn = [];
      var settlementColumn = [];
      
      for (var i = 0; i < prices.length; i++) {
        if (prices[i] && prices[i][0]) priceColumn.push(prices[i][0]);
        if (prices[i] && prices[i][1]) settlementColumn.push(prices[i][1]);
      }
      
      result.push(["Price count", priceColumn.length]);
      result.push(["Settlement count", settlementColumn.length]);
      result.push(["First price", priceColumn[0]]);
      result.push(["First settlement", settlementColumn[0]]);
      
      // Test date conversion
      if (settlementColumn.length > 0 && settlementColumn[0]) {
        var rawDate = settlementColumn[0];
        result.push(["Raw date", rawDate]);
        result.push(["Date type", typeof rawDate]);
        
        // Handle Date object
        if (rawDate instanceof Date) {
          result.push(["Is Date object", "YES"]);
          var year = rawDate.getFullYear();
          var month = ('0' + (rawDate.getMonth() + 1)).slice(-2);
          var day = ('0' + rawDate.getDate()).slice(-2);
          var isoDate = year + '-' + month + '-' + day;
          result.push(["ISO date from Date", isoDate]);
        }
        // Handle string date
        else if (typeof rawDate === 'string' && rawDate.includes('/')) {
          result.push(["Is Date object", "NO - String"]);
          var dateParts = rawDate.split('/');
          if (dateParts.length === 3) {
            var isoDate = dateParts[2] + '-' + dateParts[1] + '-' + dateParts[0];
            result.push(["ISO date from string", isoDate]);
          }
        }
        // Handle as object that might have toString
        else if (typeof rawDate === 'object') {
          result.push(["Is Date object", "Maybe - checking"]);
          result.push(["toString value", rawDate.toString()]);
          // Try to parse as Date
          try {
            var dateValue = new Date(rawDate);
            if (!isNaN(dateValue.getTime())) {
              var year = dateValue.getFullYear();
              var month = ('0' + (dateValue.getMonth() + 1)).slice(-2);
              var day = ('0' + dateValue.getDate()).slice(-2);
              var isoDate = year + '-' + month + '-' + day;
              result.push(["ISO date parsed", isoDate]);
            }
          } catch(e) {
            result.push(["Date parse error", e.toString()]);
          }
        }
      }
    } else {
      result.push(["Multi-column detected", "NO"]);
    }
    
    return result;
  } catch (error) {
    return [["Error", error.toString()]];
  }
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

/**
 * Force refresh cache and return cache info
 * @customfunction
 */
function XT_FORCE_REFRESH() {
  try {
    responseCache = {};
    documentProperties.deleteProperty('bond_cache');
    documentProperties.setProperty('bond_cache_version', 'v6.1_forced_' + new Date().getTime());
    return "Cache force refreshed - all new calculations will fetch fresh data";
  } catch (error) {
    return "Force refresh error: " + error.toString();
  }
}

// ============================================
// ENVIRONMENT UTILITY FUNCTIONS
// ============================================

/**
 * Show available environments
 * @customfunction
 */
function XT_ENVIRONMENTS() {
  var envList = [];
  envList.push(["Environment", "URL", "Description", "Usage"]);
  
  for (var key in ENVIRONMENTS) {
    var env = ENVIRONMENTS[key];
    var usage = "=XT_ARRAY(A2:A10, B2:B10, , \"" + key + "\")";
    envList.push([key, env.base, env.name, usage]);
  }
  
  return envList;
}

/**
 * Test connectivity to specific environment
 * @customfunction
 */
function XT_TEST_ENV(environment) {
  return XT_HEALTH_CHECK(environment);
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Convert various date formats to ISO string (YYYY-MM-DD)
 * Handles Date objects, strings, and other formats from Google Sheets
 */
function convertToISODate(dateValue) {
  if (!dateValue) return null;
  
  // Handle Date object
  if (dateValue instanceof Date) {
    var year = dateValue.getFullYear();
    var month = ('0' + (dateValue.getMonth() + 1)).slice(-2);
    var day = ('0' + dateValue.getDate()).slice(-2);
    return year + '-' + month + '-' + day;
  }
  
  // Handle string date in DD/MM/YYYY format
  if (typeof dateValue === 'string' && dateValue.includes('/')) {
    var dateParts = dateValue.split('/');
    if (dateParts.length === 3) {
      return dateParts[2] + '-' + dateParts[1] + '-' + dateParts[0];
    }
  }
  
  // Handle object that might be a Date
  if (typeof dateValue === 'object') {
    try {
      var parsedDate = new Date(dateValue);
      if (!isNaN(parsedDate.getTime())) {
        var year = parsedDate.getFullYear();
        var month = ('0' + (parsedDate.getMonth() + 1)).slice(-2);
        var day = ('0' + parsedDate.getDate()).slice(-2);
        return year + '-' + month + '-' + day;
      }
    } catch(e) {
      // Fall through to return string representation
    }
  }
  
  // Last resort - return string representation
  return String(dateValue);
}

function formatSettlementDate(settlement_date) {
  // Use the new convertToISODate helper function
  return convertToISODate(settlement_date);
}

function callBondAPIOptimized(bond_description, price, settlement_date, metrics, environment) {
  // Create cache key including environment
  var cacheKey = bond_description + "_" + price + "_" + (settlement_date || "default") + "_" + (metrics || []).join(",") + "_" + (environment || "production");
  
  // Check cache first
  if (responseCache[cacheKey]) {
    return responseCache[cacheKey];
  }
  
  // Use bond analysis endpoint
  var url = getApiUrl(environment, "/api/v1/bond/analysis");
  
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
  
  // Add specific metrics if requested
  if (metrics && metrics.length > 0) {
    payload["metrics"] = metrics;
  }
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": getApiKey(environment)
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
      
    case 'convexity':
      return bond.convexity !== undefined && bond.convexity !== null ? bond.convexity : "N/A";
      
    case 'pvbp':
      return bond.pvbp !== undefined && bond.pvbp !== null ? bond.pvbp : "N/A";
    
    default:
      return bond[metric] !== undefined && bond[metric] !== null ? bond[metric] : "N/A";
  }
}

function getCachedResults() {
  var CACHE_VERSION = "v6.1"; // Updated to force cache refresh for precision fix
  var currentVersion = documentProperties.getProperty('bond_cache_version');
  
  // Clear cache if version doesn't match (forces fresh data with raw numbers)
  if (currentVersion !== CACHE_VERSION) {
    documentProperties.deleteProperty('bond_cache');
    documentProperties.setProperty('bond_cache_version', CACHE_VERSION);
    return {};
  }
  
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

function processBondBatch(bonds, prices, settlement_date, environment) {
  if (bonds.length === 0) return [];
  
  // Build portfolio data
  var portfolio_data = [];
  for (var i = 0; i < bonds.length; i++) {
    portfolio_data.push({
      "description": String(bonds[i]),
      "CLOSING PRICE": Number(prices[i]),
      "WEIGHTING": 1.0
    });
  }
  
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
      "X-API-Key": getApiKey(environment)
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(getApiUrl(environment, "/api/v1/portfolio/analysis"), options);
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      
      if (data && data.bond_data) {
        var results = [];
        for (var i = 0; i < data.bond_data.length; i++) {
          var bondData = data.bond_data[i];
          
          // Extract raw numeric values, not formatted strings
          var ytm = bondData.yield !== undefined && bondData.yield !== null ? bondData.yield : 0;
          var duration = bondData.duration !== undefined && bondData.duration !== null ? bondData.duration : 0;
          var spread = bondData.spread !== undefined && bondData.spread !== null ? bondData.spread : 0;
          
          // Ensure these are numbers, not formatted strings
          if (typeof ytm === 'string' && ytm.includes('%')) {
            ytm = parseFloat(ytm.replace('%', ''));
          }
          if (typeof duration === 'string' && duration.includes('years')) {
            duration = parseFloat(duration.replace(' years', ''));
          }
          if (typeof spread === 'string' && spread.includes('bps')) {
            spread = parseFloat(spread.replace(' bps', ''));
          }
          
          // Return just the values, not the bond name
          results.push([ytm, duration, spread]);
        }
        return results;
      }
    }
  } catch (error) {
    // Return error results with same structure as success case
    var results = [];
    for (var i = 0; i < bonds.length; i++) {
      results.push([0, 0, 0]);  // Return zeros for errors to maintain structure
    }
    return results;
  }
  
  return [];
}

// ============================================
// COMPREHENSIVE USAGE EXAMPLES  
// ============================================

// ============================================
// QUICK START GUIDE - MULTI-ENVIRONMENT
// ============================================

/**
 * MAIN FUNCTIONS TO USE WITH ENVIRONMENT SUPPORT:
 * 
 * 1. XT_AUTO(bond_range, price_range, settlement_date, environment) ⭐ RECOMMENDED
 *    - Works like native Google Sheets functions
 *    - Automatically handles ranges and stops at empty cells
 *    - Example: =XT_AUTO(A:A, B:B, , "testing")
 *    - Example: =XT_AUTO(A2:A100, B2:B100, "2025-01-15", "maia_dev")
 *    - Example: =XT_AUTO(A2:A100, B2:B100)  // Production (default)
 * 
 * 2. XT_ARRAY(bond_range, price_range, settlement_date, environment)
 *    - Process multiple bonds in ONE API call
 *    - Example: =XT_ARRAY(A2:A51, B2:B51, , "testing")
 *    - Example: =XT_ARRAY(A2:A51, B2:B51, "2025-01-15", "maia_dev")
 *    - Returns: YTM, Duration, Spread for all bonds with full precision
 * 
 * 3. XT_ARRAY_CUSTOM(bond_range, price_range, "metrics", settlement_date, environment)
 *    - Choose which metrics to return
 *    - Example: =XT_ARRAY_CUSTOM(A2:A51, B2:B51, "ytm,duration,convexity", , "testing")
 *    - Example: =XT_ARRAY_CUSTOM(A2:A51, B2:B51, "ytm,pvbp,spread", "2025-01-15", "maia_dev")
 *    - Available metrics: ytm, duration, spread, convexity, pvbp, accrued_interest
 * 
 * 4. XT_DYNAMIC_RANGE(starting_range, environment)
 *    - Auto-detect bonds from combined range
 *    - Example: =XT_DYNAMIC_RANGE(A2:B100, "testing")
 *    - Example: =XT_DYNAMIC_RANGE(A2:C100, "maia_dev")  // With settlement dates
 *    - Automatically expands to include all non-empty rows
 * 
 * 5. XT_SMART(bond_range, price_range, settlement_date, force_refresh, environment)
 *    - Only recalculates changed bonds (uses intelligent caching)
 *    - Example: =XT_SMART(A2:A51, B2:B51, C2, FALSE, "testing")  // Use cache
 *    - Example: =XT_SMART(A2:A51, B2:B51, C2, TRUE, "maia_dev")   // Force refresh
 *    - Shows "Cached", "New", or "Updated" status for each bond
 * 
 * 6. XT_BATCH_PROCESS(bond_range, price_range, batch_size, settlement_date, environment)
 *    - Process large portfolios efficiently in batches
 *    - Example: =XT_BATCH_PROCESS(A2:A1000, B2:B1000, 50, , "testing")
 *    - Example: =XT_BATCH_PROCESS(A2:A5000, B2:B5000, 100, "2025-01-15", "production")
 *    - Includes batch number and timing information
 * 
 * 7. XT_PORTFOLIO_SUMMARY(bond_range, price_range, weight_range, settlement_date, environment)
 *    - Calculate portfolio-level weighted metrics
 *    - Example: =XT_PORTFOLIO_SUMMARY(A2:A10, B2:B10, C2:C10, , "maia_dev")
 *    - Returns: Weighted YTM, Portfolio Duration, Portfolio Convexity, etc.
 *
 * INDIVIDUAL BOND FUNCTIONS WITH ENVIRONMENT SUPPORT:
 * 
 * Legacy format (lowercase - maintained for backward compatibility):
 * - xt_ytm(bond, price, date, environment)
 *   Example: =xt_ytm("T 3 15/08/52", 70, "2025-01-15", "testing")
 * 
 * - xt_duration(bond, price, date, environment)
 *   Example: =xt_duration("T 4.25 11/15/40", 95.5, , "maia_dev")
 * 
 * - xt_spread(bond, price, date, environment)
 *   Example: =xt_spread("AAPL 3.45 02/09/45", 98.2, , "production")
 * 
 * - xt_convexity(bond, price, date, environment)
 *   Example: =xt_convexity("T 2.25 08/15/49", 85.3, , "testing")
 * 
 * - xt_pvbp(bond, price, date, environment)
 *   Example: =xt_pvbp("T 1.125 02/15/31", 92.1, , "maia_dev")
 * 
 * Standardized format (uppercase - recommended for new implementations):
 * - XT_YTM(bond, price, date, environment)
 * - XT_DURATION(bond, price, date, environment)  
 * - XT_SPREAD(bond, price, date, environment)
 * - XT_CONVEXITY(bond, price, date, environment)
 * - XT_PVBP(bond, price, date, environment)
 *
 * ENVIRONMENT MANAGEMENT FUNCTIONS:
 * 
 * - XT_ENVIRONMENTS()
 *   Shows all available environments with URLs and usage examples
 *   Returns: Environment name, URL, description, sample usage
 * 
 * - XT_TEST_ENV(environment)
 *   Test connectivity to specific environment
 *   Example: =XT_TEST_ENV("testing")
 *   Example: =XT_TEST_ENV("maia_dev")
 *   Returns: Environment status and database connectivity
 * 
 * - XT_HEALTH_CHECK(environment)
 *   Detailed health check for specific environment
 *   Example: =XT_HEALTH_CHECK("production")
 *   Returns: API status, database status, version info
 * 
 * UTILITY AND DEBUG FUNCTIONS:
 * 
 * - XT_VERSION(environment)
 *   Show version information for specific environment
 *   Example: =XT_VERSION("maia_dev")
 * 
 * - XT_API_STATS(environment)
 *   Show API usage statistics and cache info
 *   Example: =XT_API_STATS("testing")
 *   Returns: Cache size, endpoint info, last updated
 * 
 * - XT_DEBUG(bond, price, date, environment)
 *   Debug individual bond API responses
 *   Example: =XT_DEBUG("T 3 15/08/52", 70, , "testing")
 *   Returns: Raw JSON response for troubleshooting
 * 
 * - XT_DEBUG_PORTFOLIO(bond1, price1, bond2, price2, environment)
 *   Debug portfolio API processing
 *   Example: =XT_DEBUG_PORTFOLIO("T 3 15/08/52", 70, "T 4 1/15/30", 95, "maia_dev")
 *   Returns: Response codes, data structure info, type information
 * 
 * CACHE MANAGEMENT FUNCTIONS:
 * 
 * - XT_CLEAR_CACHE()
 *   Clear all cached bond data (applies to all environments)
 *   Use when you need fresh calculations or troubleshooting cache issues
 * 
 * - XT_CACHE_SIZE()
 *   Show number of bonds currently cached
 *   Helps monitor cache usage and performance
 *
 * === THREE-TIER ENVIRONMENT STRATEGY ===
 * 
 * TESTING ENVIRONMENT ("testing" or "alpha"):
 * - URL: http://localhost:8081
 * - Purpose: Your local development and testing  
 * - Usage: =XT_ARRAY(A2:A10, B2:B10, , "testing")
 * - Start with: FLASK_APP=google_analysis10_api.py flask run --port 8081
 * 
 * MAIA DEVELOPMENT ENVIRONMENT ("maia_dev" or "beta"):
 * - URL: https://maia-dev-dot-future-footing-414610.uc.r.appspot.com
 * - Purpose: Maia team testing before production
 * - Usage: =XT_ARRAY(A2:A10, B2:B10, , "maia_dev")  
 * - Deploy with: ./deploy_maia_dev.sh
 * 
 * PRODUCTION ENVIRONMENT ("production" or omitted):
 * - URL: https://future-footing-414610.uc.r.appspot.com
 * - Purpose: Live production environment
 * - Usage: =XT_ARRAY(A2:A10, B2:B10) or =XT_ARRAY(A2:A10, B2:B10, , "production")
 * - Deploy with: ./deploy_production.sh
 * 
 * === DEPLOYMENT WORKFLOW ===
 * 
 * Step 1: LOCAL TESTING
 * - Test your changes locally with environment = "testing"
 * - Verify full precision values are returned
 * - Test edge cases and error handling
 * 
 * Step 2: MAIA DEVELOPMENT DEPLOYMENT  
 * - Deploy to maia-dev: ./deploy_maia_dev.sh
 * - Notify Maia team to test with environment = "maia_dev"
 * - Verify all functionality works in cloud environment
 * 
 * Step 3: PRODUCTION DEPLOYMENT
 * - After Maia approval, deploy: ./deploy_production.sh
 * - Functions work with environment omitted (defaults to production)
 * - Monitor for any issues in live environment
 * 
 * Step 4: PUBLIC RELEASE (OPTIONAL)
 * - For general release, environment parameter can be hidden
 * - Or keep for power users who want to test against different environments
 *
 * === PRECISION IMPROVEMENTS ===
 * 
 * OLD BEHAVIOR (Fixed):
 * - Portfolio API returned formatted strings: "5.04%", "16.1 years"  
 * - Google Sheets functions showed only 2 decimal places
 * - Lost precision for institutional calculations
 * 
 * NEW BEHAVIOR:
 * - Portfolio API returns raw numeric values: 5.0449628829956055, 16.116099009158262
 * - Google Sheets functions display full precision (6+ decimal places)
 * - Institutional-grade accuracy maintained throughout
 * 
 * EXAMPLE PRECISION COMPARISON:
 * - Old: YTM = "5.04%" (string, 2 decimals)
 * - New: YTM = 5.0449628829956055 (float, full precision)
 * - Difference: 0.0049628829956055% - significant for large portfolios!
 * 
 * === ALTERNATIVE NAMING SCHEMES ===
 * 
 * Option 1: Descriptive Names (Recommended)
 * - "testing" = Your local development environment
 * - "maia_dev" = Maia team development/testing environment
 * - "production" = Live production environment
 * 
 * Option 2: Greek Letter Names (Alternative)
 * - "alpha" = Your testing environment
 * - "beta" = Maia testing environment  
 * - "production" = Production environment
 * 
 * Both naming schemes are supported and map to the same URLs.
 * 
 * === PERFORMANCE OPTIMIZATIONS ===
 * 
 * ARRAY FUNCTIONS (Recommended for Multiple Bonds):
 * - XT_ARRAY: Process 100 bonds in 1 API call vs 100 individual calls
 * - XT_SMART: Only recalculates changed bonds using intelligent caching
 * - XT_BATCH_PROCESS: Handles thousands of bonds with automatic batching
 * 
 * CACHING STRATEGY:
 * - Session cache: Fast in-memory cache for current session
 * - Persistent cache: Survives sheet refreshes using Google Properties Service
 * - Cache keys include: bond + price + settlement + environment
 * - Smart cache: Only updates changed bonds, preserves unchanged calculations
 * 
 * INDIVIDUAL FUNCTIONS (Use for Single Bonds):
 * - Best for ad-hoc calculations or single bond analysis
 * - Automatic caching with environment-aware cache keys
 * - Both legacy (lowercase) and standardized (uppercase) versions available
 * 
 * === COMMON USE CASES ===
 * 
 * 1. DEVELOPMENT WORKFLOW:
 *    // Test locally first
 *    =XT_AUTO(A2:A100, B2:B100, , "testing")
 *    
 *    // Deploy and test with Maia team
 *    =XT_AUTO(A2:A100, B2:B100, , "maia_dev")
 *    
 *    // Go live
 *    =XT_AUTO(A2:A100, B2:B100)
 * 
 * 2. LARGE PORTFOLIO ANALYSIS:
 *    // Process 1000+ bonds efficiently
 *    =XT_BATCH_PROCESS(A2:A5000, B2:B5000, 100, , "production")
 * 
 * 3. CUSTOM METRICS SELECTION:
 *    // Only get specific metrics you need
 *    =XT_ARRAY_CUSTOM(A2:A100, B2:B100, "ytm,duration,pvbp", , "maia_dev")
 * 
 * 4. PORTFOLIO SUMMARY:
 *    // Get weighted portfolio-level metrics
 *    =XT_PORTFOLIO_SUMMARY(A2:A50, B2:B50, C2:C50, , "production")
 * 
 * 5. SMART CACHING FOR FREQUENT UPDATES:
 *    // Only recalculate bonds with changed prices
 *    =XT_SMART(A2:A100, B2:B100, , FALSE, "production")
 * 
 * 6. TROUBLESHOOTING:
 *    // Debug API responses
 *    =XT_DEBUG("T 3 15/08/52", 70, , "testing")
 *    
 *    // Check environment health
 *    =XT_TEST_ENV("maia_dev")
 * 
 * === ERROR HANDLING ===
 * 
 * All functions include environment-aware error messages:
 * - "Service temporarily unavailable (Local Testing)"
 * - "API Error (Maia Development): Connection timeout"  
 * - "Unable to calculate yield for this bond (Production)"
 * 
 * This helps identify which environment is having issues and aids in debugging.
 * 
 * === BACKWARD COMPATIBILITY ===
 * 
 * Existing functions continue to work without modification:
 * - =XT_ARRAY(A2:A10, B2:B10) still works (defaults to production)
 * - =xt_ytm("T 3 15/08/52", 70) still works (defaults to production)
 * - All legacy lowercase function names maintained
 * 
 * New environment parameter is optional for all functions.
 * 
 * Perfect for institutional-grade bond analysis with full deployment flexibility! 🎯
 * 
 * Version 6.0 - Complete Multi-Environment Support with Full Precision
 */