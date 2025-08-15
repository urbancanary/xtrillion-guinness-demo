/**
 * Test the performance difference between cached and non-cached API calls
 * @return {Array} Performance comparison results
 * @customfunction
 */
function XT_TEST_CACHE_PERFORMANCE() {
  var results = [];
  results.push(["Test Type", "Time (ms)", "Description"]);
  
  var testBond = "T 3 15/08/52";
  var testPrice = 71.66;
  var testSettlement = "2025-06-30";
  var environment = "testing";
  
  // Test 1: First call (no cache) - simulating cache miss
  var start1 = new Date().getTime();
  var config = getEnvironmentConfig(environment);
  
  try {
    // Simulate API call
    var url = config.base + "/api/v1/bond/analysis";
    var payload = {
      "description": testBond,
      "price": testPrice,
      "settlement_date": testSettlement
    };
    
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'headers': {
        'X-API-Key': config.key
      },
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true
    };
    
    var response = UrlFetchApp.fetch(url, options);
    var end1 = new Date().getTime();
    var time1 = end1 - start1;
    
    results.push(["First Call (Cache Miss)", time1, "API call required"]);
    
    // Store in cache for next test
    var cacheKey = testBond + "_" + testPrice + "_" + testSettlement;
    var cache = PropertiesService.getScriptProperties();
    
    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      cache.setProperty(cacheKey, JSON.stringify({
        ytm: data.analytics.ytm,
        duration: data.analytics.duration,
        spread: data.analytics.spread,
        timestamp: new Date().getTime()
      }));
    }
    
    // Test 2: Second call (with cache) - simulating cache hit
    var start2 = new Date().getTime();
    var cachedData = cache.getProperty(cacheKey);
    if (cachedData) {
      var parsed = JSON.parse(cachedData);
      // Just parse the cached data
      var ytm = parsed.ytm;
      var duration = parsed.duration;
      var spread = parsed.spread;
    }
    var end2 = new Date().getTime();
    var time2 = end2 - start2;
    
    results.push(["Second Call (Cache Hit)", time2, "Using cached data"]);
    
    // Calculate speedup
    var speedup = Math.round(time1 / time2);
    results.push(["Cache Speedup", speedup + "x faster", "Cache hit vs miss"]);
    
    // Test 3: Batch of 10 bonds without cache
    var start3 = new Date().getTime();
    for (var i = 0; i < 10; i++) {
      // Simulate different bonds
      var bondDesc = "T " + (i+1) + " 15/08/52";
      var bondPrice = 70 + i;
      
      payload = {
        "description": bondDesc,
        "price": bondPrice,
        "settlement_date": testSettlement
      };
      
      options.payload = JSON.stringify(payload);
      UrlFetchApp.fetch(url, options);
    }
    var end3 = new Date().getTime();
    var time3 = end3 - start3;
    
    results.push(["10 Bonds (No Cache)", time3, "10 API calls"]);
    results.push(["Average per Bond", Math.round(time3/10), "No cache avg"]);
    
    // Test 4: Batch of 10 bonds with 50% cache hit
    var start4 = new Date().getTime();
    for (var i = 0; i < 10; i++) {
      if (i % 2 === 0) {
        // Cache hit - just read from cache
        var fakeCacheRead = cache.getProperty("fake_key_" + i) || "{}";
        JSON.parse(fakeCacheRead);
      } else {
        // Cache miss - make API call
        payload = {
          "description": "T " + (i+1) + " 15/08/52",
          "price": 70 + i,
          "settlement_date": testSettlement
        };
        options.payload = JSON.stringify(payload);
        UrlFetchApp.fetch(url, options);
      }
    }
    var end4 = new Date().getTime();
    var time4 = end4 - start4;
    
    results.push(["10 Bonds (50% Cache)", time4, "5 cached, 5 API"]);
    results.push(["Average per Bond", Math.round(time4/10), "Mixed cache avg"]);
    
    // Summary
    results.push(["", "", ""]);
    results.push(["SUMMARY", "", ""]);
    
    if (time2 < 10) {
      results.push(["Cache Performance", "EXCELLENT", "<10ms cache reads"]);
      results.push(["Recommendation", "USE CACHE", "Significant speedup"]);
    } else if (time2 < 50 && speedup > 10) {
      results.push(["Cache Performance", "GOOD", "Fast cache, good speedup"]);
      results.push(["Recommendation", "USE CACHE", "Worth the complexity"]);
    } else if (speedup > 5) {
      results.push(["Cache Performance", "MODERATE", "Decent speedup"]);
      results.push(["Recommendation", "OPTIONAL", "Consider simpler no-cache"]);
    } else {
      results.push(["Cache Performance", "POOR", "Minimal speedup"]);
      results.push(["Recommendation", "NO CACHE", "Not worth complexity"]);
    }
    
    // Cache staleness warning
    results.push(["", "", ""]);
    results.push(["⚠️ WARNING", "", ""]);
    results.push(["Cache Issue", "STALE DATA", "Settlement dates ignored"]);
    results.push(["Impact", "WRONG RESULTS", "16.26 vs 16.35 duration"]);
    
  } catch (error) {
    results.push(["Error", error.toString(), ""]);
  }
  
  return results;
}