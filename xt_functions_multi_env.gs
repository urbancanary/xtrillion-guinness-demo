// XTrillion Bond Analytics - MULTI-ENVIRONMENT VERSION
// Version: 6.0 - Full environment support (testing → maia_dev → production)
// Support for: testing, maia_dev, production (or alpha, beta, production)

// ============================================
// ENVIRONMENT CONFIGURATION
// ============================================

var ENVIRONMENTS = {
  "testing": {
    base: "http://localhost:8081",  // Your local testing server
    key: "gax10_demo_3j5h8m9k2p6r4t7w1q",
    name: "Local Testing"
  },
  "maia_dev": {
    base: "https://maia-dev-dot-future-footing-414610.uc.r.appspot.com", // Maia team testing
    key: "gax10_dev_4n8s6k2x7p9v5m8p1z",
    name: "Maia Development"
  },
  "production": {
    base: "https://future-footing-414610.uc.r.appspot.com", // Production
    key: "gax10_demo_3j5h8m9k2p6r4t7w1q",
    name: "Production"
  },
  // Alternative naming scheme
  "alpha": {
    base: "http://localhost:8081",
    key: "gax10_demo_3j5h8m9k2p6r4t7w1q", 
    name: "Alpha Testing"
  },
  "beta": {
    base: "https://maia-dev-dot-future-footing-414610.uc.r.appspot.com",
    key: "gax10_dev_4n8s6k2x7p9v5m8p1z",
    name: "Beta Testing"
  }
};

var DEFAULT_ENV = "production"; // Default when no environment specified

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
// MAIN ARRAY FUNCTIONS WITH ENVIRONMENT SUPPORT
// ============================================

/**
 * Process multiple bonds at once using the portfolio endpoint
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices  
 * @param {string} settlement_date Optional settlement date (applies to all bonds)
 * @param {string} environment Optional environment ("testing", "maia_dev", "production", "alpha", "beta")
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
  var apiUrl = getApiUrl(environment, "/api/v1/portfolio/analysis");
  var apiKey = getApiKey(environment);
  
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
      "X-API-Key": apiKey
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(apiUrl, options);
    
    if (response.getResponseCode() !== 200) {
      return "Service temporarily unavailable (" + config.name + ")";
    }
    
    var data = JSON.parse(response.getContentText());
    
    if (data && data.bond_data) {
      var results = [];
      
      // Add header row with environment info
      results.push(["Bond", "YTM (%)", "Duration", "Spread (bps)", "Environment"]);
      
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
 * Smart array function with environment support
 * 
 * @param {Array} bond_range Range containing bond descriptions
 * @param {Array} price_range Range containing bond prices
 * @param {string} settlement_date Optional settlement date
 * @param {boolean} force_refresh Set to TRUE to force recalculation
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with metrics for each bond
 * @customfunction
 */
function XT_SMART(bond_range, price_range, settlement_date, force_refresh, environment) {
  // Use XT_ARRAY with caching logic (simplified for now)
  return XT_ARRAY(bond_range, price_range, settlement_date, environment);
}

/**
 * Dynamic array function that expands automatically with environment support
 * 
 * @param {Array} starting_range The range starting with first bond (e.g., A2:C100)
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} Dynamic array with all bond metrics
 * @customfunction
 */
function XT_DYNAMIC(starting_range, environment) {
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
    return "Please select at least 2 columns (bonds and prices). Example: =XT_DYNAMIC(A2:B100, \"maia_dev\")";
  }
  
  if (bonds.length === 0) {
    return "No valid bonds found in the range";
  }
  
  return XT_ARRAY(bonds, prices, settlementDate, environment);
}

/**
 * Flexible range processing with environment support
 * 
 * @param {Array} bond_column Bond range or column
 * @param {Array} price_column Price range or column  
 * @param {*} settlement Optional settlement date
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {Array} 2D array with results
 * @customfunction
 */
function XT_AUTO(bond_column, price_column, settlement, environment) {
  if (!bond_column || !price_column) {
    return "Please provide bond and price columns";
  }
  
  if (!Array.isArray(bond_column)) {
    bond_column = [[bond_column]];
  }
  if (!Array.isArray(price_column)) {
    price_column = [[price_column]];
  }
  
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
      break;
    }
  }
  
  if (bonds.length === 0) {
    return "No valid bond/price pairs found";
  }
  
  return XT_ARRAY(bonds, prices, settlement, environment);
}

// ============================================
// INDIVIDUAL BOND FUNCTIONS WITH ENVIRONMENT SUPPORT
// ============================================

/**
 * Calculate bond yield to maturity with environment support
 * 
 * @param {string} bond_description Bond description or ISIN
 * @param {number} price Bond price
 * @param {*} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {number} Yield to maturity
 * @customfunction
 */
function xt_ytm(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
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
 * Calculate bond modified duration with environment support
 * 
 * @param {string} bond_description Bond description or ISIN
 * @param {number} price Bond price  
 * @param {*} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {number} Modified duration
 * @customfunction
 */
function xt_duration(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
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
 * Calculate bond spread with environment support
 * 
 * @param {string} bond_description Bond description or ISIN
 * @param {number} price Bond price
 * @param {*} settlement_date Optional settlement date  
 * @param {string} environment Optional environment ("testing", "maia_dev", "production")
 * @return {number} Spread in basis points
 * @customfunction
 */
function xt_spread(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
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

// ============================================
// HELPER FUNCTIONS
// ============================================

function callBondAPI(bond_description, price, settlement_date, environment) {
  var config = getEnvironmentConfig(environment);
  var url = getApiUrl(environment, "/api/v1/bond/analysis");
  
  // Build payload
  var payload = {
    "description": bond_description,
    "price": price
  };
  
  var formattedDate = formatSettlementDate(settlement_date);
  if (formattedDate) {
    payload["settlement_date"] = formattedDate;
  }
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": config.key
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
    return data;
  } catch (error) {
    throw new Error("Unable to connect to bond analytics service");
  }
}

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

// ============================================
// ENVIRONMENT UTILITY FUNCTIONS  
// ============================================

/**
 * Show available environments
 * @customfunction
 */
function XT_ENVIRONMENTS() {
  var envList = [];
  envList.push(["Environment", "URL", "Description"]);
  
  for (var key in ENVIRONMENTS) {
    var env = ENVIRONMENTS[key];
    envList.push([key, env.base, env.name]);
  }
  
  return envList;
}

/**
 * Test connectivity to specific environment
 * 
 * @param {string} environment Environment to test ("testing", "maia_dev", "production")
 * @return {string} Connection status
 * @customfunction
 */
function XT_TEST_ENV(environment) {
  var config = getEnvironmentConfig(environment);
  
  try {
    var response = UrlFetchApp.fetch(config.base + "/health", {
      "method": "GET",
      "muteHttpExceptions": true
    });
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      return config.name + ": ✅ " + data.status;
    } else {
      return config.name + ": ❌ Unavailable";
    }
  } catch (error) {
    return config.name + ": ❌ Connection Error";
  }
}

/**
 * Get current version info with environment
 * 
 * @param {string} environment Optional environment to check
 * @customfunction  
 */
function XT_VERSION_ENV(environment) {
  var config = getEnvironmentConfig(environment);
  return "XTrillion v6.0 Multi-Environment (" + config.name + ")";
}

// ============================================
// USAGE EXAMPLES WITH ENVIRONMENT SUPPORT
// ============================================

/**
 * EXAMPLE USAGE WITH ENVIRONMENTS:
 * 
 * 1. Testing locally:
 *    =XT_ARRAY(A2:A10, B2:B10, , "testing")
 *    =xt_ytm("T 3 15/08/52", 70, , "testing")
 * 
 * 2. Maia team development testing:
 *    =XT_ARRAY(A2:A10, B2:B10, , "maia_dev")  
 *    =xt_ytm("T 3 15/08/52", 70, , "maia_dev")
 * 
 * 3. Production (default - can omit environment):
 *    =XT_ARRAY(A2:A10, B2:B10)
 *    =XT_ARRAY(A2:A10, B2:B10, , "production")
 * 
 * 4. Alpha/Beta naming (alternative):
 *    =XT_ARRAY(A2:A10, B2:B10, , "alpha")    // Your testing
 *    =XT_ARRAY(A2:A10, B2:B10, , "beta")     // Maia testing
 * 
 * 5. Environment utilities:
 *    =XT_ENVIRONMENTS()           // Show all environments
 *    =XT_TEST_ENV("maia_dev")     // Test specific environment
 *    =XT_VERSION_ENV("testing")   // Version info for environment
 * 
 * THREE-TIER DEPLOYMENT STRATEGY:
 * testing (your local) → maia_dev → production
 * 
 * Once deployed to production, remove environment parameters from public functions
 */