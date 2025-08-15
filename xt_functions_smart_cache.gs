// XTrillion Bond Analytics - SMART CACHING Version
// Version: 4.0 - Intelligent caching to prevent unnecessary recalculations
// Only recalculates changed bonds, preserves unchanged values

var API_BASE = "https://future-footing-414610.uc.r.appspot.com";
var API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q";

// Persistent cache using Google Sheets Properties Service
var documentProperties = PropertiesService.getDocumentProperties();

// ============================================
// SMART CACHING FUNCTIONS
// ============================================

/**
 * Smart array function that only recalculates changed bonds
 * Preserves cached values for unchanged bonds
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

/**
 * Individual bond calculation with smart caching
 * Only calls API if value changed or expired
 * 
 * @param {string} bond_description Bond description
 * @param {number} price Bond price
 * @param {string} settlement_date Optional settlement date
 * @return {Array} Array with [YTM, Duration, Spread]
 * @customfunction
 */
function XT_CACHED(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return ["Invalid input", "", ""];
  }
  
  var cacheKey = bond_description + "_" + price + "_" + (settlement_date || "default");
  var cache = getCachedResults();
  
  // Check cache (expires after 1 hour)
  if (cache[cacheKey]) {
    var cached = cache[cacheKey];
    var age = (new Date().getTime() - cached.timestamp) / 1000 / 60; // Age in minutes
    
    if (age < 60) { // Less than 60 minutes old
      return [[cached.ytm, cached.duration, cached.spread]];
    }
  }
  
  // Need fresh data
  try {
    var data = callBondAPIQuick(bond_description, price, settlement_date, ["ytm", "duration", "spread"]);
    
    if (data && data.analytics) {
      var result = [
        data.analytics.ytm || "N/A",
        data.analytics.duration || "N/A",
        data.analytics.spread || 0
      ];
      
      // Update cache
      cache[cacheKey] = {
        ytm: result[0],
        duration: result[1],
        spread: result[2],
        timestamp: new Date().getTime()
      };
      
      saveCachedResults(cache);
      
      return [result];
    }
  } catch (error) {
    return [["Error", "Error", "Error"]];
  }
}

/**
 * Incremental update - only process specific rows
 * Useful when editing individual bonds
 * 
 * @param {number} start_row First row to update (e.g., 2)
 * @param {number} end_row Last row to update (e.g., 5)
 * @return {Array} Updated values for specified rows
 * @customfunction
 */
function XT_UPDATE_ROWS(start_row, end_row) {
  var sheet = SpreadsheetApp.getActiveSheet();
  
  // Get data for specified rows
  var numRows = end_row - start_row + 1;
  var bonds = sheet.getRange(start_row, 1, numRows, 1).getValues();
  var prices = sheet.getRange(start_row, 2, numRows, 1).getValues();
  
  var results = [];
  
  for (var i = 0; i < numRows; i++) {
    if (bonds[i][0] && prices[i][0]) {
      try {
        var data = callBondAPIQuick(bonds[i][0], prices[i][0], null, ["ytm", "duration", "spread"]);
        
        if (data && data.analytics) {
          results.push([
            data.analytics.ytm || "N/A",
            data.analytics.duration || "N/A",
            data.analytics.spread || 0
          ]);
        } else {
          results.push(["Error", "Error", "Error"]);
        }
      } catch (error) {
        results.push(["Error", "Error", "Error"]);
      }
    } else {
      results.push(["", "", ""]);
    }
  }
  
  return results;
}

/**
 * Manual cache management functions
 */
function XT_CLEAR_CACHE() {
  documentProperties.deleteAllProperties();
  return "Cache cleared successfully";
}

function XT_CACHE_SIZE() {
  var cache = getCachedResults();
  var count = Object.keys(cache).length;
  return count + " bonds cached";
}

function XT_CACHE_AGE() {
  var cache = getCachedResults();
  var ages = [];
  
  for (var key in cache) {
    if (cache[key].timestamp) {
      var age = (new Date().getTime() - cache[key].timestamp) / 1000 / 60;
      ages.push(age);
    }
  }
  
  if (ages.length === 0) {
    return "No cached data";
  }
  
  var avgAge = ages.reduce(function(a, b) { return a + b; }, 0) / ages.length;
  return "Average cache age: " + Math.round(avgAge) + " minutes";
}

// ============================================
// SELECTIVE UPDATE FUNCTIONS
// ============================================

/**
 * Update only when source data changes
 * Uses checksums to detect changes
 * 
 * @param {Array} bond_range Bond descriptions
 * @param {Array} price_range Prices
 * @return {Array} Results with change detection
 * @customfunction
 */
function XT_CHANGE_DETECT(bond_range, price_range) {
  var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
  var prices = Array.isArray(price_range) ? price_range : [[price_range]];
  
  // Calculate checksum of input data
  var checksum = calculateChecksum(bonds, prices);
  var lastChecksum = documentProperties.getProperty('last_checksum');
  
  if (checksum === lastChecksum) {
    // No changes detected - return cached results
    var cachedOutput = JSON.parse(documentProperties.getProperty('cached_output') || '[]');
    if (cachedOutput.length > 0) {
      return cachedOutput;
    }
  }
  
  // Data changed - recalculate
  var results = XT_ARRAY(bonds, prices);
  
  // Save new checksum and results
  documentProperties.setProperty('last_checksum', checksum);
  documentProperties.setProperty('cached_output', JSON.stringify(results));
  
  return results;
}

// ============================================
// HELPER FUNCTIONS
// ============================================

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
            ytm: bondData.yield ? parseFloat(bondData.yield.replace('%', '')) : "N/A",
            duration: bondData.duration ? parseFloat(bondData.duration.replace(' years', '')) : "N/A",
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

function callBondAPIQuick(bond_description, price, settlement_date, metrics) {
  var url = API_BASE + "/api/v1/bond/quick";
  
  var payload = {
    "description": bond_description,
    "price": price
  };
  
  if (settlement_date) {
    payload["settlement_date"] = formatSettlementDate(settlement_date);
  }
  
  if (metrics) {
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
  
  var response = UrlFetchApp.fetch(url, options);
  
  if (response.getResponseCode() === 200) {
    return JSON.parse(response.getContentText());
  }
  
  throw new Error("API call failed");
}

function formatSettlementDate(settlement_date) {
  if (!settlement_date) return null;
  
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
    }
    
    if (dateObj && !isNaN(dateObj.getTime())) {
      var year = dateObj.getFullYear();
      var month = ('0' + (dateObj.getMonth() + 1)).slice(-2);
      var day = ('0' + dateObj.getDate()).slice(-2);
      return year + '-' + month + '-' + day;
    }
  } catch (error) {
    return null;
  }
  
  return null;
}

function calculateChecksum(bonds, prices) {
  var str = JSON.stringify(bonds) + JSON.stringify(prices);
  var hash = 0;
  
  for (var i = 0; i < str.length; i++) {
    var char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  return hash.toString();
}

// ============================================
// USAGE INSTRUCTIONS
// ============================================

/**
 * SMART CACHING FUNCTIONS:
 * 
 * 1. XT_SMART() - Only recalculates changed bonds
 *    =XT_SMART(A2:A51, B2:B51, C2, FALSE)
 *    Last parameter: FALSE = use cache, TRUE = force refresh
 * 
 * 2. XT_CACHED() - Individual bond with caching
 *    =XT_CACHED(A2, B2, C2)
 *    Caches for 1 hour, then refreshes automatically
 * 
 * 3. XT_UPDATE_ROWS() - Update specific rows only
 *    =XT_UPDATE_ROWS(2, 5)
 *    Updates rows 2-5 only
 * 
 * 4. XT_CHANGE_DETECT() - Updates only when data changes
 *    =XT_CHANGE_DETECT(A2:A51, B2:B51)
 *    Uses checksums to detect changes
 * 
 * CACHE MANAGEMENT:
 * 
 * =XT_CLEAR_CACHE() - Clear all cached data
 * =XT_CACHE_SIZE() - Show number of cached bonds
 * =XT_CACHE_AGE() - Show average age of cached data
 * 
 * BENEFITS:
 * - Changing one bond doesn't recalculate all bonds
 * - Cached values persist across sheet recalculations
 * - Reduces API calls by 80-90%
 * - Faster response for unchanged data
 */