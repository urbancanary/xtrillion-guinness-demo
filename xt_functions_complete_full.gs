// XTrillion Bond Analytics - COMPLETE VERSION
// Version: 5.1 - All functions included (Array + Smart Cache + Legacy + XT_AUTO)
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
 * Most flexible function - works like native Google Sheets functions
 * RECOMMENDED FOR NEW USERS
 * 
 * @param {Array} bond_column Range containing bond descriptions (e.g., A2:A100 or A:A)
 * @param {Array} price_column Range containing bond prices (e.g., B2:B100 or B:B)
 * @param {string} settlement Optional settlement date
 * @return {Array} 2D array with YTM, Duration, Spread for each bond
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
 * Process multiple bonds at once - uses individual calls for full precision
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
        
        // Extract numeric values - preserve full precision
        var ytm = "N/A";
        var duration = "N/A";
        var spread = 0;
        
        // API now returns raw numeric values - extract directly
        if (bond.yield !== undefined && bond.yield !== null) {
          ytm = typeof bond.yield === 'number' ? bond.yield : parseFloat(bond.yield);
        }
        
        if (bond.duration !== undefined && bond.duration !== null) {
          duration = typeof bond.duration === 'number' ? bond.duration : parseFloat(bond.duration);
        }
        
        if (bond.spread !== undefined && bond.spread !== null) {
          spread = typeof bond.spread === 'number' ? bond.spread : parseFloat(bond.spread);
        }
        
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

/**
 * Automatically detect and process all bonds starting from a cell with a bond description
 * Pass a cell reference directly (e.g., A2) and it will find all bonds below it
 * 
 * @param {*} starting_value The first bond description (from cell reference like A2)
 * @return {Array} 2D array with YTM, Duration, Spread for all detected bonds
 * @customfunction
 */
function XT_DYNAMIC(starting_value) {
  var sheet = SpreadsheetApp.getActiveSheet();
  
  // If no value provided or empty
  if (!starting_value || starting_value === "") {
    return "Please select a cell containing a bond description";
  }
  
  // Convert to string and trim
  var searchValue = starting_value.toString().trim();
  
  // Find this value in the sheet to locate where to start
  var dataRange = sheet.getDataRange();
  var values = dataRange.getValues();
  var startRow = -1;
  var colNum = -1;
  
  // Search for the starting value in the sheet
  for (var r = 0; r < values.length; r++) {
    for (var c = 0; c < values[r].length; c++) {
      if (values[r][c] && values[r][c].toString().trim() === searchValue) {
        startRow = r + 1;  // Convert to 1-based row number
        colNum = c + 1;     // Convert to 1-based column number
        break;
      }
    }
    if (startRow > 0) break;
  }
  
  if (startRow === -1) {
    // Value not found in sheet - maybe it's the first of a series
    // Assume it's meant to start at A2 if not found
    return "Could not locate '" + searchValue + "' in the sheet. Please ensure the cell reference is correct.";
  }
  
  // Now we know where to start - get the data from this position
  var lastRow = sheet.getLastRow();
  
  if (lastRow < startRow) {
    return "No additional data found below the starting cell";
  }
  
  // Get all bonds starting from the found position
  var maxRows = lastRow - startRow + 1;
  var bondColumn = sheet.getRange(startRow, colNum, maxRows, 1).getValues();
  
  // Find where the bond data ends (first empty cell)
  var bonds = [];
  var rowCount = 0;
  
  for (var i = 0; i < bondColumn.length; i++) {
    if (bondColumn[i][0] && bondColumn[i][0].toString().trim() !== "") {
      bonds.push([bondColumn[i][0]]);
      rowCount++;
    } else {
      break; // Stop at first empty cell
    }
  }
  
  if (bonds.length === 0) {
    return "No valid bonds found";
  }
  
  // Get corresponding prices from the next column
  var prices = sheet.getRange(startRow, colNum + 1, rowCount, 1).getValues();
  
  // Check for settlement date in third column
  var settlementDate = null;
  try {
    var dateCell = sheet.getRange(startRow, colNum + 2).getValue();
    if (dateCell) {
      settlementDate = dateCell;
    }
  } catch (e) {
    // No third column available
  }
  
  // Process all bonds
  return XT_ARRAY(bonds, prices, settlementDate);
}

/**
 * Alternative dynamic function that works with ranges (like the new behavior)
 * 
 * @param {Array} starting_range The range starting with first bond (e.g., A2:C100)
 * @return {Array} 2D array with YTM, Duration, Spread for all detected bonds
 * @customfunction
 */
function XT_DYNAMIC_RANGE(starting_range) {
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
    return "Please select at least 2 columns (bonds and prices). Example: =XT_DYNAMIC_RANGE(A2:B100)";
  }
  
  if (bonds.length === 0) {
    return "No valid bonds found in the range";
  }
  
  // Process using XT_ARRAY
  return XT_ARRAY(bonds, prices, settlementDate);
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
// INDIVIDUAL BOND FUNCTIONS (LEGACY SUPPORT)
// ============================================

/**
 * Calculate bond yield to maturity
 * @customfunction
 */
function xt_ytm(bond_description, price, settlement_date) {
  // Convert inputs to ensure we handle them properly
  var bondStr = bond_description ? String(bond_description).trim() : "";
  var priceInput = price;
  
  // Show loading message for empty inputs (Google Sheets sometimes passes empty on initial load)
  if (!bondStr && (priceInput === null || priceInput === undefined || priceInput === "")) {
    return "Loading...";
  }
  
  // Check for bond description
  if (!bondStr) {
    return "Waiting for bond description...";
  }
  
  // Handle price - be more lenient with what we accept
  var numericPrice;
  if (priceInput === null || priceInput === undefined || priceInput === "") {
    return "Waiting for price...";
  } else {
    // Try to convert to number - handle various formats
    numericPrice = Number(priceInput);
    if (isNaN(numericPrice)) {
      // Try parsing as string in case it has formatting
      var priceStr = String(priceInput).replace(/[^0-9.-]/g, '');
      numericPrice = parseFloat(priceStr);
    }
    
    if (isNaN(numericPrice) || numericPrice <= 0) {
      // Debug: show what we received
      return "Invalid price: " + priceInput + " (type: " + typeof priceInput + ")";
    }
  }
  
  try {
    // Don't rely on cache for individual functions - get fresh data
    // Clear this specific cache entry to force refresh
    var cacheKey = bondStr + "_" + numericPrice + "_" + (settlement_date || "default") + "_ytm";
    if (responseCache[cacheKey]) {
      delete responseCache[cacheKey];
    }
    
    var data = callBondAPIOptimized(bondStr, numericPrice, settlement_date, ["ytm"]);
    
    // Check multiple possible locations for YTM value
    if (data) {
      // Priority 1: analytics.ytm
      if (data.analytics && typeof data.analytics.ytm === 'number') {
        return data.analytics.ytm;
      }
      // Priority 2: analytics.yield_to_maturity
      if (data.analytics && typeof data.analytics.yield_to_maturity === 'number') {
        return data.analytics.yield_to_maturity;
      }
      // Priority 3: direct ytm field
      if (typeof data.ytm === 'number') {
        return data.ytm;
      }
      // Priority 4: look in result
      if (data.result && data.result.analytics && typeof data.result.analytics.ytm === 'number') {
        return data.result.analytics.ytm;
      }
    }
    
    // If we got here, we couldn't find the YTM value
    return "Unable to calculate YTM";
  } catch (error) {
    // If it's a timeout or network error, show a friendlier message
    if (error.toString().indexOf("timeout") > -1 || error.toString().indexOf("timed out") > -1) {
      return "Loading... (may take a moment)";
    }
    if (error.toString().indexOf("Unable to connect") > -1) {
      return "Connection error - please retry";
    }
    // Show the actual error for debugging
    return "Error: " + error.toString();
  }
}

/**
 * Uppercase version for consistency
 * @customfunction
 */
function XT_YTM(bond_description, price, settlement_date) {
  return xt_ytm(bond_description, price, settlement_date);
}

/**
 * Calculate bond modified duration
 * @customfunction
 */
function xt_duration(bond_description, price, settlement_date) {
  // Convert inputs to ensure we handle them properly
  var bondStr = bond_description ? String(bond_description).trim() : "";
  var priceInput = price;
  
  // Show loading message for empty inputs
  if (!bondStr && !priceInput) {
    return "Loading...";
  }
  
  // Check for bond description
  if (!bondStr) {
    return "Waiting for bond description...";
  }
  
  // Handle price - be more lenient with what we accept
  var numericPrice;
  if (priceInput === null || priceInput === undefined || priceInput === "") {
    return "Waiting for price...";
  } else {
    // Try to convert to number - handle various formats
    numericPrice = Number(priceInput);
    if (isNaN(numericPrice)) {
      // Try parsing as string in case it has formatting
      var priceStr = String(priceInput).replace(/[^0-9.-]/g, '');
      numericPrice = parseFloat(priceStr);
    }
    
    if (isNaN(numericPrice) || numericPrice <= 0) {
      return "Invalid price: " + priceInput + " (type: " + typeof priceInput + ")";
    }
  }
  
  try {
    var data = callBondAPIOptimized(bondStr, numericPrice, settlement_date, ["duration", "modified_duration"]);
    
    if (data && data.analytics) {
      // Try different field names
      if (typeof data.analytics.modified_duration === 'number') {
        return data.analytics.modified_duration;
      } else if (typeof data.analytics.duration === 'number') {
        return data.analytics.duration;
      }
    }
    return "Calculating...";
  } catch (error) {
    if (error.toString().indexOf("timeout") > -1) {
      return "Loading... (may take a moment)";
    }
    return "Calculating... (retry in a moment)";
  }
}

function XT_DURATION(bond_description, price, settlement_date) {
  return xt_duration(bond_description, price, settlement_date);
}

/**
 * Calculate bond spread
 * @customfunction
 */
function xt_spread(bond_description, price, settlement_date) {
  if (bond_description === null || bond_description === undefined || bond_description === "") {
    return "Please provide bond description";
  }
  if (price === null || price === undefined || price === "") {
    return "Please provide price";
  }
  
  var numericPrice = Number(price);
  if (isNaN(numericPrice) || numericPrice <= 0) {
    return "Invalid price: " + price;
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, numericPrice, settlement_date, ["spread"]);
    
    if (data && data.analytics) {
      return data.analytics.spread !== null && data.analytics.spread !== undefined ? data.analytics.spread : 0;
    }
    return 0; // Default to 0 for spread if not available
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

function XT_SPREAD(bond_description, price, settlement_date) {
  return xt_spread(bond_description, price, settlement_date);
}

/**
 * Calculate bond convexity
 * @customfunction
 */
function xt_convexity(bond_description, price, settlement_date) {
  if (bond_description === null || bond_description === undefined || bond_description === "") {
    return "Please provide bond description";
  }
  if (price === null || price === undefined || price === "") {
    return "Please provide price";
  }
  
  var numericPrice = Number(price);
  if (isNaN(numericPrice) || numericPrice <= 0) {
    return "Invalid price: " + price;
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, numericPrice, settlement_date, ["convexity"]);
    
    if (data && data.analytics && typeof data.analytics.convexity === 'number') {
      return data.analytics.convexity;
    }
    return "Unable to calculate convexity for this bond";
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

function XT_CONVEXITY(bond_description, price, settlement_date) {
  return xt_convexity(bond_description, price, settlement_date);
}

/**
 * Calculate bond PVBP (Price Value of Basis Point)
 * @customfunction
 */
function xt_pvbp(bond_description, price, settlement_date) {
  if (bond_description === null || bond_description === undefined || bond_description === "") {
    return "Please provide bond description";
  }
  if (price === null || price === undefined || price === "") {
    return "Please provide price";
  }
  
  var numericPrice = Number(price);
  if (isNaN(numericPrice) || numericPrice <= 0) {
    return "Invalid price: " + price;
  }
  
  try {
    var data = callBondAPIOptimized(bond_description, numericPrice, settlement_date, ["pvbp"]);
    
    if (data && data.analytics && typeof data.analytics.pvbp === 'number') {
      return data.analytics.pvbp;
    }
    return "Unable to calculate PVBP for this bond";
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

function XT_PVBP(bond_description, price, settlement_date) {
  return xt_pvbp(bond_description, price, settlement_date);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Get version information
 * @customfunction
 */
function XT_VERSION() {
  return "XTrillion v5.1 - Complete with XT_AUTO";
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

/**
 * Debug function to test API connectivity
 * @customfunction
 */
function XT_DEBUG(bond_description, price, settlement_date) {
  try {
    var data = callBondAPIOptimized(bond_description, price, settlement_date);
    return JSON.stringify(data, null, 2);
  } catch (error) {
    return "Debug Error: " + error.toString();
  }
}

/**
 * Debug function for portfolio endpoint
 * @customfunction
 */
function XT_DEBUG_PORTFOLIO(bond1, price1, bond2, price2) {
  var portfolio_data = [];
  if (bond1 && price1) {
    portfolio_data.push({
      "description": String(bond1),
      "CLOSING PRICE": Number(price1),
      "WEIGHTING": 1.0
    });
  }
  if (bond2 && price2) {
    portfolio_data.push({
      "description": String(bond2),
      "CLOSING PRICE": Number(price2),
      "WEIGHTING": 1.0
    });
  }
  
  var payload = {
    "data": portfolio_data,
    "metrics": ["ytm", "duration", "spread"]
  };
  
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
    var data = JSON.parse(response.getContentText());
    
    // Show what we're getting from the API
    if (data && data.bond_data && data.bond_data.length > 0) {
      var firstBond = data.bond_data[0];
      var result = "First bond data structure:\n";
      result += "Keys: " + Object.keys(firstBond).join(", ") + "\n";
      
      // Check each potential location
      if (firstBond.analytics_data) {
        result += "analytics_data.ytm: " + firstBond.analytics_data.ytm + "\n";
      }
      if (firstBond.analytics) {
        result += "analytics.ytm: " + firstBond.analytics.ytm + "\n";
      }
      if (firstBond.ytm !== undefined) {
        result += "ytm: " + firstBond.ytm + " (type: " + typeof firstBond.ytm + ")\n";
      }
      if (firstBond.yield !== undefined) {
        result += "yield: " + firstBond.yield + " (type: " + typeof firstBond.yield + ")\n";
      }
      
      return result;
    }
    
    return JSON.stringify(data, null, 2);
  } catch (error) {
    return "Debug Error: " + error.toString();
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
  
  // Use bond analysis endpoint
  var url = API_BASE + "/api/v1/bond/analysis";
  
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
  
  // Add specific metrics if requested (otherwise defaults to all)
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
  // Map metric names to bond data fields - preserve full precision
  switch(metric.toLowerCase()) {
    case 'ytm':
    case 'yield':
      if (bond.yield) {
        if (typeof bond.yield === 'number') {
          return bond.yield;
        } else {
          return parseFloat(bond.yield.replace('%', ''));
        }
      }
      return "N/A";
    
    case 'duration':
      if (bond.duration) {
        if (typeof bond.duration === 'number') {
          return bond.duration;
        } else {
          return parseFloat(bond.duration.replace(' years', ''));
        }
      }
      return "N/A";
    
    case 'spread':
      return bond.spread !== null && bond.spread !== undefined ? bond.spread : 0;
    
    case 'convexity':
      return bond.convexity !== null && bond.convexity !== undefined ? bond.convexity : "N/A";
    
    case 'pvbp':
      return bond.pvbp !== null && bond.pvbp !== undefined ? bond.pvbp : "N/A";
    
    case 'accrued_interest':
      return bond.accrued_interest !== null && bond.accrued_interest !== undefined ? bond.accrued_interest : "N/A";
    
    case 'clean_price':
      return bond.clean_price !== null && bond.clean_price !== undefined ? bond.clean_price : "N/A";
    
    case 'dirty_price':
      return bond.dirty_price !== null && bond.dirty_price !== undefined ? bond.dirty_price : "N/A";
    
    case 'macaulay':
    case 'macaulay_duration':
      return bond.macaulay_duration !== null && bond.macaulay_duration !== undefined ? bond.macaulay_duration : "N/A";
    
    default:
      var value = bond[metric];
      return value !== null && value !== undefined ? value : "N/A";
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
          
          // Extract values with full precision - check all possible locations
          var ytmValue = "N/A";
          var durationValue = "N/A";
          var spreadValue = 0;
          
          // API now returns raw numeric values - extract directly
          if (bondData.yield !== undefined && bondData.yield !== null) {
            ytmValue = typeof bondData.yield === 'number' ? bondData.yield : parseFloat(bondData.yield);
          }
          
          if (bondData.duration !== undefined && bondData.duration !== null) {
            durationValue = typeof bondData.duration === 'number' ? bondData.duration : parseFloat(bondData.duration);
          }
          
          if (bondData.spread !== undefined && bondData.spread !== null) {
            spreadValue = typeof bondData.spread === 'number' ? bondData.spread : parseFloat(bondData.spread);
          }
          
          return {
            index: item.index,
            bond: item.bond,
            cacheKey: item.cacheKey,
            ytm: ytmValue,
            duration: durationValue,
            spread: spreadValue
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
// QUICK START GUIDE
// ============================================

/**
 * MAIN FUNCTIONS TO USE:
 * 
 * 1. XT_AUTO(bond_range, price_range, settlement_date) ⭐ RECOMMENDED
 *    - Works like native Google Sheets functions
 *    - Example: =XT_AUTO(A:A, B:B)
 *    - Example: =XT_AUTO(A2:A100, B2:B100, "2025-01-15")
 * 
 * 2. XT_ARRAY(bond_range, price_range, settlement_date)
 *    - Process multiple bonds in ONE API call
 *    - Example: =XT_ARRAY(A2:A51, B2:B51)
 *    - Returns: YTM, Duration, Spread for all bonds
 * 
 * 3. XT_ARRAY_CUSTOM(bond_range, price_range, "metrics", settlement_date)
 *    - Choose which metrics to return
 *    - Example: =XT_ARRAY_CUSTOM(A2:A51, B2:B51, "ytm,duration,convexity")
 * 
 * 4. XT_DYNAMIC(range)
 *    - Auto-detect from combined range
 *    - Example: =XT_DYNAMIC(A2:B100)
 * 
 * 5. XT_SMART(bond_range, price_range, settlement_date, force_refresh)
 *    - Only recalculates changed bonds (uses cache)
 *    - Example: =XT_SMART(A2:A51, B2:B51, C2, FALSE)
 * 
 * INDIVIDUAL BOND FUNCTIONS (backward compatible):
 * - xt_ytm(bond, price, date)
 * - xt_duration(bond, price, date)
 * - xt_spread(bond, price, date)
 * - xt_convexity(bond, price, date)
 * - xt_pvbp(bond, price, date)
 * 
 * PORTFOLIO FUNCTIONS:
 * - XT_PORTFOLIO_SUMMARY(bonds, prices, weights, date)
 * - XT_BATCH_PROCESS(bonds, prices, batch_size, date)
 * 
 * UTILITY FUNCTIONS:
 * - XT_VERSION() - Show version info
 * - XT_HEALTH_CHECK() - Check API status
 * - XT_API_STATS() - Show cache statistics
 * - XT_CLEAR_CACHE() - Clear all cached data
 * - XT_CACHE_SIZE() - Show number of cached bonds
 * - XT_DEBUG(bond, price, date) - Debug API responses
 * 
 * Version 5.1 - Complete implementation with XT_AUTO
 */