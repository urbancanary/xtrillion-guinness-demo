// XTrillion Bond Analytics - Enhanced Google Sheets Functions with Environment Support
// Version: 1.2 Multi-Environment Support
// Created: August 3, 2025

// Environment configurations
var ENVIRONMENTS = {
  "prod": {
    base: "https://future-footing-414610.uc.r.appspot.com",
    key: "gax10_demo_3j5h8m9k2p6r4t7w1q"
  },
  "dev": {
    base: "https://development-dot-future-footing-414610.uc.r.appspot.com",
    key: "gax10_dev_4n8s6k2x7p9v5m8p1z"
  }
};

// Default to production
var DEFAULT_ENV = "prod";

// Helper function to format settlement date
function formatSettlementDate(settlement_date) {
  if (!settlement_date) {
    return null;
  }
  
  try {
    var dateObj;
    
    // Handle Date objects from Google Sheets
    if (settlement_date instanceof Date) {
      dateObj = settlement_date;
    }
    // Handle string inputs
    else if (typeof settlement_date === 'string') {
      var dateStr = settlement_date.trim();
      
      // If already in YYYY-MM-DD format, return as-is
      if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
        return dateStr;
      }
      // Try to parse other formats
      dateObj = new Date(dateStr);
    }
    // Handle number inputs (Excel-style serial dates)
    else if (typeof settlement_date === 'number') {
      // Convert Excel serial date to JavaScript Date
      var excelEpoch = new Date(1900, 0, 1);
      dateObj = new Date(excelEpoch.getTime() + (settlement_date - 2) * 24 * 60 * 60 * 1000);
    }
    else {
      return null;
    }
    
    // Format to YYYY-MM-DD
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

// Core API helper function with environment support
function callBondAPI(bond_description, price, settlement_date, environment) {
  // Select environment
  var env = environment && ENVIRONMENTS[environment.toLowerCase()] ? environment.toLowerCase() : DEFAULT_ENV;
  var config = ENVIRONMENTS[env];
  
  // Use standard endpoint (not flexible) for dev compatibility
  var url = config.base + "/api/v1/bond/analysis";
  
  // Build payload object
  var payload = {
    "description": bond_description,
    "price": price
  };
  
  // Add settlement date if provided
  var formattedDate = formatSettlementDate(settlement_date);
  if (formattedDate) {
    payload.settlement_date = formattedDate;
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
    
    return JSON.parse(response.getContentText());
  } catch (error) {
    throw new Error("Unable to connect to bond analytics service");
  }
}

/**
 * Calculate bond yield to maturity
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("prod" or "dev", default: "prod")
 * @return {number} Yield to maturity (%)
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
    } else if (data && typeof data.ytm === 'number') {
      // Handle direct ytm response format
      return data.ytm;
    } else {
      return "Unable to calculate yield for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate bond modified duration
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("prod" or "dev", default: "prod")
 * @return {number} Modified duration
 * @customfunction
 */
function xt_duration(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
    if (data && data.analytics && typeof data.analytics.modified_duration === 'number') {
      return data.analytics.modified_duration;
    } else if (data && typeof data.duration === 'number') {
      // Handle direct duration response format
      return data.duration;
    } else {
      return "Unable to calculate duration for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate bond convexity
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("prod" or "dev", default: "prod")
 * @return {number} Convexity
 * @customfunction
 */
function xt_convexity(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
    if (data && data.analytics && typeof data.analytics.convexity === 'number') {
      return data.analytics.convexity;
    } else if (data && typeof data.convexity === 'number') {
      // Handle direct convexity response format
      return data.convexity;
    } else {
      return "Unable to calculate convexity for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate bond accrued interest
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("prod" or "dev", default: "prod")
 * @return {number} Accrued interest
 * @customfunction
 */
function xt_accrued(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
    if (data && data.analytics && typeof data.analytics.accrued_interest === 'number') {
      return data.analytics.accrued_interest;
    } else if (data && typeof data.accrued_interest === 'number') {
      // Handle direct accrued_interest response format
      return data.accrued_interest;
    } else {
      return "Unable to calculate accrued interest for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate bond accrued per million
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("prod" or "dev", default: "prod")
 * @return {number} Accrued per million
 * @customfunction
 */
function xt_accrued_per_million(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
    if (data && data.analytics && typeof data.analytics.accrued_per_million === 'number') {
      return data.analytics.accrued_per_million;
    } else if (data && typeof data.accrued_per_million === 'number') {
      // Handle direct accrued_per_million response format
      return data.accrued_per_million;
    } else {
      return "Unable to calculate accrued per million for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate bond PVBP (Price Value of a Basis Point)
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("prod" or "dev", default: "prod")
 * @return {number} PVBP
 * @customfunction
 */
function xt_pvbp(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
    if (data && data.analytics && typeof data.analytics.pvbp === 'number') {
      return data.analytics.pvbp;
    } else if (data && typeof data.pvbp === 'number') {
      // Handle direct pvbp response format
      return data.pvbp;
    } else {
      return "Unable to calculate PVBP for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Get all bond analytics in a single call
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @param {string} environment Optional environment ("prod" or "dev", default: "prod")
 * @return {Array} Array of [YTM, Duration, Convexity, Accrued, PVBP]
 * @customfunction
 */
function xt_bond_analytics(bond_description, price, settlement_date, environment) {
  if (!bond_description || !price) {
    return [["Please provide bond description and price", "", "", "", ""]];
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date, environment);
    
    // Extract values with fallback to direct fields
    var ytm = (data.analytics && data.analytics.ytm) || data.ytm || "N/A";
    var duration = (data.analytics && data.analytics.modified_duration) || data.duration || "N/A";
    var convexity = (data.analytics && data.analytics.convexity) || data.convexity || "N/A";
    var accrued = (data.analytics && data.analytics.accrued_interest) || data.accrued_interest || "N/A";
    var pvbp = (data.analytics && data.analytics.pvbp) || data.pvbp || "N/A";
    
    return [[ytm, duration, convexity, accrued, pvbp]];
  } catch (error) {
    return [["Service unavailable", "", "", "", ""]];
  }
}