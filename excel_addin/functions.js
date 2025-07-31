// Excel Custom Functions - Bond Calculator
// Professional bond analytics with institutional accuracy

/**
 * Calculate bond yield to maturity
 * @customfunction BOND.YIELD
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} [price=100] Bond price
 * @returns {number} Yield to maturity (%)
 */
function yield(bond_description, price = 100) {
  return callBondAPI('yield', bond_description, price);
}

/**
 * Calculate bond modified duration
 * @customfunction BOND.DURATION  
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} [price=100] Bond price
 * @returns {number} Modified duration (years)
 */
function duration(bond_description, price = 100) {
  return callBondAPI('duration', bond_description, price);
}

/**
 * Calculate bond credit spread
 * @customfunction BOND.SPREAD
 * @param {string} bond_description Bond description (e.g., "ECOPETROL SA, 5.875%, 28-May-2045")
 * @param {number} [price=100] Bond price  
 * @returns {number} Credit spread (basis points)
 */
function spread(bond_description, price = 100) {
  return callBondAPI('spread', bond_description, price);
}

/**
 * Calculate bond accrued interest
 * @customfunction BOND.ACCRUED
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} [price=100] Bond price
 * @returns {number} Accrued interest (%)
 */
function accrued(bond_description, price = 100) {
  return callBondAPI('accrued', bond_description, price);
}

/**
 * Calculate bond convexity
 * @customfunction BOND.CONVEXITY
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} [price=100] Bond price
 * @returns {number} Price convexity
 */
function convexity(bond_description, price = 100) {
  return callBondAPI('convexity', bond_description, price);
}

/**
 * Calculate Price Value of a Basis Point
 * @customfunction BOND.PVBP
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} [price=100] Bond price
 * @returns {number} PVBP (per $1M notional)
 */
function pvbp(bond_description, price = 100) {
  return callBondAPI('pvbp', bond_description, price);
}

/**
 * Analyze bond - returns yield (use other functions for specific metrics)
 * @customfunction BOND.ANALYZE
 * @param {string} bond_description Bond description (e.g., "T 3 15/08/52")
 * @param {number} [price=100] Bond price
 * @returns {number} Yield to maturity (%)
 */
function analyze(bond_description, price = 100) {
  return callBondAPI('yield', bond_description, price);
}

/**
 * Core API call function - connects to institutional-grade bond calculator
 * @param {string} metric The metric to calculate (yield, duration, spread, etc.)
 * @param {string} bond_description Bond description
 * @param {number} price Bond price
 * @returns {Promise<number>} Calculated value
 */
async function callBondAPI(metric, bond_description, price) {
  try {
    // Validate inputs
    if (!bond_description || bond_description.trim() === '') {
      throw new Error('Bond description is required');
    }
    
    if (typeof price !== 'number' || price <= 0) {
      throw new Error('Price must be a positive number');
    }
    
    // Build API URL
    const baseUrl = 'https://excel-bond-bridge.vercel.app/api/bond';
    const params = new URLSearchParams({
      metric: metric,
      bond: bond_description.trim(),
      price: price.toString()
    });
    
    const url = `${baseUrl}?${params.toString()}`;
    
    // Make API call with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Accept': 'text/plain',
          'User-Agent': 'Excel-Bond-AddIn/1.0'
        }
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`API returned ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.text();
      
      // Handle error responses
      if (result.startsWith('ERROR_')) {
        throw new Error(`Bond calculation failed: ${result}`);
      }
      
      // Parse and validate numeric result
      const numericResult = parseFloat(result);
      
      if (isNaN(numericResult)) {
        throw new Error(`Invalid numeric result: ${result}`);
      }
      
      return numericResult;
      
    } catch (fetchError) {
      clearTimeout(timeoutId);
      
      if (fetchError.name === 'AbortError') {
        throw new Error('Request timeout - bond calculation took too long');
      }
      
      throw fetchError;
    }
    
  } catch (error) {
    // Return Excel-friendly error
    console.error('Bond calculation error:', error);
    
    // For Excel, we can return special error values
    if (error.message.includes('timeout')) {
      return '#TIMEOUT!';
    } else if (error.message.includes('Bond description')) {
      return '#VALUE!';
    } else if (error.message.includes('Price')) {
      return '#NUM!';
    } else {
      return '#N/A';
    }
  }
}

// Register custom functions with Excel
if (typeof CustomFunctions !== 'undefined') {
  CustomFunctions.associate('YIELD', yield);
  CustomFunctions.associate('DURATION', duration);
  CustomFunctions.associate('SPREAD', spread);
  CustomFunctions.associate('ACCRUED', accrued);
  CustomFunctions.associate('CONVEXITY', convexity);
  CustomFunctions.associate('PVBP', pvbp);
  CustomFunctions.associate('ANALYZE', analyze);
}