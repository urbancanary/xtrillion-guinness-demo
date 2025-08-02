// XTrillion Bond Analytics - Professional Google Sheets Functions
// Version: 1.1 Production Ready with Settlement Date Support
// Created: August 1, 2025

var API_BASE = "https://future-footing-414610.uc.r.appspot.com";
var API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q";

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

// Core API helper function with settlement date support
function callBondAPI(bond_description, price, settlement_date) {
  // Use flexible endpoint for easier input handling
  var url = API_BASE + "/api/v1/bond/analysis/flexible";
  
  // Build array payload - endpoint auto-detects parameter types
  var payload = [bond_description, price];
  
  // Add settlement date if provided
  var formattedDate = formatSettlementDate(settlement_date);
  if (formattedDate) {
    payload.push(formattedDate);
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
 * @return {number} Yield to maturity (%)
 * @customfunction
 */
function xt_ytm(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date);
    
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
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @return {number} Modified duration (years)
 * @customfunction
 */
function xt_duration(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date);
    
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
 * Calculate bond accrued interest
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @return {number} Accrued interest (%)
 * @customfunction
 */
function xt_accrued_interest(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date);
    
    if (data && data.analytics && typeof data.analytics.accrued_interest === 'number') {
      return data.analytics.accrued_interest;
    } else {
      return "Unable to calculate accrued interest for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate accrued interest in Bloomberg format (per million)
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @return {number} Accrued interest per million
 * @customfunction
 */
function xt_accrued_pm(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date);
    
    if (data && data.analytics && typeof data.analytics.accrued_interest === 'number') {
      return data.analytics.accrued_interest * 10000;
    } else {
      return "Unable to calculate accrued interest for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate bond spread over government curve
 * @param {string} bond_description Bond description (e.g., "ECOPETROL SA, 5.875%, 28-May-2045")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @return {number} Spread (basis points)
 * @customfunction
 */
function xt_spread(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date);
    
    if (data && data.analytics) {
      return data.analytics.spread || 0;
    } else {
      return "Unable to calculate spread for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Calculate Macaulay duration
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} price Bond price
 * @param {any} settlement_date Optional settlement date
 * @return {number} Macaulay duration (years)
 * @customfunction
 */
function xt_macaulay_duration(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date);
    
    if (data && data.analytics && typeof data.analytics.macaulay_duration === 'number') {
      return data.analytics.macaulay_duration;
    } else {
      return "Unable to calculate Macaulay duration for this bond";
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
 * @return {number} Convexity
 * @customfunction
 */
function xt_convexity(bond_description, price, settlement_date) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price, settlement_date);
    
    if (data && data.analytics && typeof data.analytics.convexity === 'number') {
      return data.analytics.convexity;
    } else {
      return "Unable to calculate convexity for this bond";
    }
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Compare accrued interest with Bloomberg value
 * @param {string} bond_description Bond description
 * @param {number} price Bond price
 * @param {number} bbg_accrued_per_million Bloomberg accrued per million
 * @param {any} settlement_date Optional settlement date
 * @return {number} Difference between XTrillion and Bloomberg
 * @customfunction
 */
function xt_accrued_compare(bond_description, price, bbg_accrued_per_million, settlement_date) {
  if (!bond_description || !price || typeof bbg_accrued_per_million !== 'number') {
    return "Please provide bond description, price, and Bloomberg value";
  }
  
  try {
    var xtrillion_accrued = xt_accrued_pm(bond_description, price, settlement_date);
    if (typeof xtrillion_accrued === 'number') {
      return xtrillion_accrued - bbg_accrued_per_million;
    }
    return "Unable to compare - calculation failed";
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Get validation status compared to Bloomberg
 * @param {string} bond_description Bond description
 * @param {number} price Bond price
 * @param {number} bbg_accrued_per_million Bloomberg accrued per million
 * @param {any} settlement_date Optional settlement date
 * @return {string} Match status (MATCH, CLOSE, MINOR_DIFF, MAJOR_DIFF)
 * @customfunction
 */
function xt_validation_status(bond_description, price, bbg_accrued_per_million, settlement_date) {
  if (!bond_description || !price || typeof bbg_accrued_per_million !== 'number') {
    return "Please provide bond description, price, and Bloomberg value";
  }
  
  try {
    var difference = xt_accrued_compare(bond_description, price, bbg_accrued_per_million, settlement_date);
    if (typeof difference === 'number') {
      var abs_diff = Math.abs(difference);
      if (abs_diff < 1) return "MATCH";
      if (abs_diff < 100) return "CLOSE";
      if (abs_diff < 1000) return "MINOR_DIFF";
      return "MAJOR_DIFF";
    }
    return "Unable to validate - calculation failed";
  } catch (error) {
    return "Service temporarily unavailable - please try again";
  }
}

/**
 * Test settlement date formatting
 * @param {any} test_date Date to test
 * @return {string} Formatted date or error
 * @customfunction
 */
function xt_test_date(test_date) {
  var formatted = formatSettlementDate(test_date);
  return formatted ? "FORMATTED: " + formatted : "INVALID: " + test_date;
}

// Professional bond analytics for Google Sheets
// Supports: US Treasuries, Corporate Bonds, Sovereign Bonds
// Usage: =xt_ytm("T 3 15/08/52", 71.66)
// Usage with settlement date: =xt_ytm("T 3 15/08/52", 71.66, "2025-08-01")
// Version: 1.1 Production Ready with Settlement Date Support