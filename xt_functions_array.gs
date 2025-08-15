// XTrillion Bond Analytics - ARRAY FORMULA Support for Google Sheets
// Version: 3.0 - Full array/range support for efficient bulk processing
// Created: August 12, 2025
// Performance: Process 100 bonds in 1 API call instead of 100 separate calls

var API_BASE = "https://future-footing-414610.uc.r.appspot.com";
var API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q";

// ============================================
// ARRAY FORMULA FUNCTIONS
// Process multiple bonds in a single API call
// ============================================

/**
 * Process multiple bonds at once using the portfolio endpoint
 * Accepts a range of bonds and returns all metrics efficiently
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

/**
 * Process bonds with individual settlement dates
 * Each row can have its own settlement date
 * 
 * @param {Array} data_range Range with columns: [Bond, Price, Settlement Date]
 * @return {Array} Array with [Bond, YTM, Duration, Spread] for each row
 * @customfunction
 */
function XT_ARRAY_WITH_DATES(data_range) {
  if (!Array.isArray(data_range) || data_range.length === 0) {
    return "Please select a range with bond data";
  }
  
  var results = [];
  results.push(["Bond", "YTM (%)", "Duration", "Spread (bps)"]);
  
  // Process in batches for efficiency
  var batchSize = 10;
  var batches = [];
  
  for (var i = 0; i < data_range.length; i += batchSize) {
    var batch = data_range.slice(i, i + batchSize);
    batches.push(batch);
  }
  
  // Process each batch
  for (var b = 0; b < batches.length; b++) {
    var batch = batches[b];
    var batchResults = processBatch(batch);
    results = results.concat(batchResults);
  }
  
  return results;
}

/**
 * Dynamic array formula that expands automatically
 * Place in top-left cell and it will fill the range
 * 
 * @param {string} start_cell Reference to the cell with first bond (e.g., "A2")
 * @return {Array} Dynamic array with all bond metrics
 * @customfunction
 */
function XT_DYNAMIC(start_cell) {
  // Get the sheet
  var sheet = SpreadsheetApp.getActiveSheet();
  
  // Parse the start cell reference
  var startRange = sheet.getRange(start_cell);
  var startRow = startRange.getRow();
  var bondColumn = startRange.getColumn();
  var priceColumn = bondColumn + 1; // Assume price is in next column
  
  // Find the last row with data
  var lastRow = sheet.getLastRow();
  var numRows = lastRow - startRow + 1;
  
  if (numRows <= 0) {
    return "No data found";
  }
  
  // Get the data ranges
  var bondRange = sheet.getRange(startRow, bondColumn, numRows, 1).getValues();
  var priceRange = sheet.getRange(startRow, priceColumn, numRows, 1).getValues();
  
  // Filter out empty rows
  var bonds = [];
  var prices = [];
  
  for (var i = 0; i < numRows; i++) {
    if (bondRange[i][0] && priceRange[i][0]) {
      bonds.push(bondRange[i][0]);
      prices.push(priceRange[i][0]);
    }
  }
  
  if (bonds.length === 0) {
    return "No valid bonds found";
  }
  
  // Call the array function
  return XT_ARRAY(bonds, prices, null);
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

function processBatch(batch) {
  var results = [];
  
  // Build portfolio data from batch
  var portfolio_data = [];
  
  for (var i = 0; i < batch.length; i++) {
    var row = batch[i];
    if (row[0] && row[1]) {  // Bond and price required
      var item = {
        "description": String(row[0]),
        "CLOSING PRICE": Number(row[1]),
        "WEIGHTING": 1.0
      };
      
      // Add settlement date if provided in third column
      if (row[2]) {
        item["settlement_date"] = formatSettlementDate(row[2]);
      }
      
      portfolio_data.push(item);
    }
  }
  
  if (portfolio_data.length === 0) {
    return results;
  }
  
  // Call API
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
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      
      if (data && data.bond_data) {
        for (var i = 0; i < data.bond_data.length; i++) {
          var bond = data.bond_data[i];
          results.push([
            batch[i][0],  // Original bond description
            bond.yield !== undefined && bond.yield !== null ? bond.yield : "N/A",
            bond.duration !== undefined && bond.duration !== null ? bond.duration : "N/A",
            bond.spread !== undefined && bond.spread !== null ? bond.spread : 0
          ]);
        }
      }
    }
  } catch (error) {
    // Return error rows
    for (var i = 0; i < batch.length; i++) {
      results.push([batch[i][0], "Error", "Error", "Error"]);
    }
  }
  
  return results;
}

// ============================================
// USAGE EXAMPLES
// ============================================

/**
 * EXAMPLE USAGE:
 * 
 * 1. Basic array formula for column of bonds:
 *    =XT_ARRAY(A2:A101, B2:B101)
 *    Returns YTM, Duration, Spread for all 100 bonds in ONE API call
 * 
 * 2. Custom metrics for portfolio:
 *    =XT_ARRAY_CUSTOM(A2:A50, B2:B50, "ytm,duration,convexity,pvbp")
 *    Returns specified metrics for all bonds
 * 
 * 3. With individual settlement dates:
 *    =XT_ARRAY_WITH_DATES(A2:C101)
 *    Where columns are: [Bond Description, Price, Settlement Date]
 * 
 * 4. Dynamic expansion (auto-detects range):
 *    =XT_DYNAMIC("A2")
 *    Automatically processes all bonds starting from A2
 * 
 * PERFORMANCE:
 * - Old way: 100 bonds × 3 metrics = 300 API calls
 * - New way: 1 API call for all 100 bonds
 * - Improvement: 300x fewer API calls
 */

// Version 3.0 - Full Array Formula Support
// Processes multiple bonds in single API call
// Dramatic performance improvement for portfolios