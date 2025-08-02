// XTrillion Bond Analytics - Professional Google Sheets Functions
// Version: 1.0 Production Ready
// Created: August 1, 2025

var API_BASE = "https://future-footing-414610.uc.r.appspot.com";
var API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q";

// Core API helper function
function callBondAPI(bond_description, price) {
  var url = API_BASE + "/api/v1/bond/analysis";
  var payload = JSON.stringify({
    "description": bond_description,
    "price": price
  });
  
  var options = {
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    "payload": payload,
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
 * @return {number} Yield to maturity (%)
 * @customfunction
 */
function xt_ytm(bond_description, price) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price);
    
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
 * @return {number} Modified duration (years)
 * @customfunction
 */
function xt_duration(bond_description, price) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price);
    
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
 * @return {number} Accrued interest (%)
 * @customfunction
 */
function xt_accrued_interest(bond_description, price) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price);
    
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
 * @return {number} Accrued interest per million
 * @customfunction
 */
function xt_accrued_pm(bond_description, price) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price);
    
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
 * @return {number} Spread (basis points)
 * @customfunction
 */
function xt_spread(bond_description, price) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price);
    
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
 * @return {number} Macaulay duration (years)
 * @customfunction
 */
function xt_macaulay_duration(bond_description, price) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price);
    
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
 * @return {number} Convexity
 * @customfunction
 */
function xt_convexity(bond_description, price) {
  if (!bond_description || !price) {
    return "Please provide bond description and price";
  }
  
  try {
    var data = callBondAPI(bond_description, price);
    
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
 * @return {number} Difference between XTrillion and Bloomberg
 * @customfunction
 */
function xt_accrued_compare(bond_description, price, bbg_accrued_per_million) {
  if (!bond_description || !price || typeof bbg_accrued_per_million !== 'number') {
    return "Please provide bond description, price, and Bloomberg value";
  }
  
  try {
    var xtrillion_accrued = xt_accrued_pm(bond_description, price);
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
 * @return {string} Match status (MATCH, CLOSE, MINOR_DIFF, MAJOR_DIFF)
 * @customfunction
 */
function xt_validation_status(bond_description, price, bbg_accrued_per_million) {
  if (!bond_description || !price || typeof bbg_accrued_per_million !== 'number') {
    return "Please provide bond description, price, and Bloomberg value";
  }
  
  try {
    var difference = xt_accrued_compare(bond_description, price, bbg_accrued_per_million);
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

// Professional bond analytics for Google Sheets
// Supports: US Treasuries, Corporate Bonds, Sovereign Bonds
// Usage: =xt_ytm("T 3 15/08/52", 71.66)
// Version: 1.0 Production Ready