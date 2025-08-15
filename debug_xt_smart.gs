/**
 * Debug version of XT_SMART to isolate the TypeError
 */
function DEBUG_XT_SMART(bond_range, price_range, settlement_date, force_refresh, environment) {
  try {
    // Step 1: Handle input parameters safely
    console.log("Step 1: Input validation");
    var bonds = Array.isArray(bond_range) ? bond_range : [[bond_range]];
    var prices = Array.isArray(price_range) ? price_range : [[price_range]];
    
    console.log("Bonds:", bonds);
    console.log("Prices:", prices);
    
    // Step 2: Initialize arrays early
    console.log("Step 2: Initialize arrays");
    var results = [];
    var needsUpdate = [];
    
    // Step 3: Settlement date detection
    console.log("Step 3: Settlement date detection");
    var detectedSettlement = null;
    
    // Check if price_range has multiple columns (price + settlement date)
    if (prices && prices.length > 0 && Array.isArray(prices[0]) && prices[0].length >= 2) {
      console.log("Multi-column input detected");
      var priceColumn = [];
      var settlementColumn = [];
      
      for (var i = 0; i < prices.length; i++) {
        if (prices[i] && prices[i][0]) priceColumn.push(prices[i][0]);
        if (prices[i] && prices[i][1]) settlementColumn.push(prices[i][1]);
      }
      
      prices = priceColumn;
      
      if (settlementColumn.length > 0 && settlementColumn[0]) {
        detectedSettlement = settlementColumn[0];
        console.log("Detected settlement:", detectedSettlement);
      }
    } else {
      console.log("Single column input");
      prices = prices.map(function(row) { 
        return Array.isArray(row) ? row[0] : row; 
      }).filter(function(p) { return p; });
    }
    
    // Step 4: Flatten bonds
    console.log("Step 4: Flatten bonds");
    bonds = bonds.map(function(row) { 
      return Array.isArray(row) ? row[0] : row; 
    }).filter(function(b) { return b; });
    
    console.log("Processed bonds:", bonds);
    console.log("Processed prices:", prices);
    
    // Step 5: Use detected settlement date
    if (!settlement_date && detectedSettlement) {
      settlement_date = detectedSettlement;
      console.log("Using detected settlement date:", settlement_date);
    }
    
    // Step 6: Validation
    if (bonds.length !== prices.length) {
      return "Bond descriptions and prices must have same count";
    }
    
    // Step 7: Add header row
    console.log("Step 7: Add header");
    results.push(["Bond", "YTM", "Duration", "Spread", "Status", "Environment"]);
    
    // Step 8: Test results array
    console.log("Step 8: Test results array");
    console.log("Results length:", results.length);
    console.log("First result:", results[0]);
    
    // Return debug info
    return [
      ["Debug Info", "Value", "", "", "", ""],
      ["Bonds count", bonds.length, "", "", "", ""],
      ["Prices count", prices.length, "", "", "", ""],
      ["Settlement", settlement_date || "None", "", "", "", ""],
      ["First bond", bonds[0] || "None", "", "", "", ""],
      ["First price", prices[0] || "None", "", "", "", ""]
    ];
    
  } catch (error) {
    console.log("Error caught:", error);
    return [["Error", error.toString(), "", "", "", ""]];
  }
}