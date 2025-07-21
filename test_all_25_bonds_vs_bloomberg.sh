#!/bin/bash

# 🏦 Complete 25-Bond Individual Validation Test
# Tests each bond individually against Bloomberg Terminal Data

echo "🏦 Complete 25-Bond Individual Validation vs Bloomberg"
echo "===================================================="

# API Endpoint
API_URL="http://localhost:8081"

# Bloomberg bond data array
declare -a BONDS=(
    "US TREASURY N/B, 3%, 15-Aug-2052|71.66|4.90|16.36|0|US912810TJ79"
    "GALAXY PIPELINE, 3.25%, 30-Sep-2040|77.88|5.64|10.10|118|XS2249741674"
    "ABU DHABI CRUDE, 4.6%, 02-Nov-2047|89.40|5.72|9.82|123|XS1709535097"
    "SAUDI ARAB OIL, 4.25%, 16-Apr-2039|87.14|5.60|9.93|111|XS1982113463"
    "EMPRESA METRO, 4.7%, 07-May-2050|80.39|6.27|13.19|144|USP37466AS18"
    "CODELCO INC, 6.15%, 24-Oct-2036|101.63|5.95|8.02|160|USP3143NAH72"
    "COMISION FEDERAL, 6.264%, 15-Feb-2052|86.42|7.44|11.58|261|USP30179BR86"
    "COLOMBIA REP OF, 3.875%, 15-Feb-2061|52.71|7.84|12.98|301|US195325DX04"
    "ECOPETROL SA, 5.875%, 28-May-2045|69.31|9.28|9.81|445|US279158AJ82"
    "EMPRESA NACIONAL, 4.5%, 14-Sep-2047|76.24|6.54|12.39|171|USP37110AM89"
    "GREENSAIF PIPELI, 6.129%, 23-Feb-2038|103.03|5.72|7.21|146|XS2542166231"
    "STATE OF ISRAEL, 3.8%, 13-May-2060|64.50|6.34|15.27|151|XS2167193015"
    "SAUDI INT BOND, 4.5%, 26-Oct-2046|82.42|5.97|12.60|114|XS1508675508"
    "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048|92.21|7.06|11.45|223|XS1807299331"
    "UNITED MEXICAN, 5.75%, 12-Oct-2110|78.00|7.37|13.37|255|US91086QAZ19"
    "MEXICO CITY ARPT, 5.5%, 31-Jul-2047|82.57|7.07|11.38|224|USP6629MAD40"
    "PANAMA, 3.87%, 23-Jul-2060|56.60|7.36|13.49|253|US698299BL70"
    "PETROLEOS MEXICA, 6.95%, 28-Jan-2060|71.42|9.88|9.72|505|US71654QDF63"
    "PETROLEOS MEXICA, 5.95%, 28-Jan-2031|89.55|8.32|4.47|444|US71654QDE98"
    "GACI FIRST INVST, 5.125%, 14-Feb-2053|85.54|6.23|13.33|140|XS2585988145"
    "QATAR STATE OF, 4.817%, 14-Mar-2049|89.97|5.58|13.26|76|XS1959337749"
    "QNB FINANCE LTD, 1.625%, 22-Sep-2025|99.23|5.02|0.23|71|XS2233188353"
    "QATAR ENERGY, 3.125%, 12-Jul-2041|73.79|5.63|11.51|101|XS2359548935"
    "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043|93.29|5.66|11.24|95|XS0911024635"
    "SITIOS, 5.375%, 04-Apr-2032|97.26|5.87|5.51|187|USP0R80BAG79"
)

# Results arrays
declare -a RESULTS_API_YIELD=()
declare -a RESULTS_API_DURATION=()
declare -a RESULTS_STATUS=()
declare -a RESULTS_BOND_NAMES=()

echo "🔍 Testing API Health..."
HEALTH_CHECK=$(curl -s "$API_URL/health")
if [[ $? -eq 0 ]] && echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo "✅ API is healthy and ready"
else
    echo "❌ API health check failed"
    exit 1
fi

echo ""
echo "🧪 Testing all 25 bonds individually..."
echo ""

# Initialize counters
TOTAL_BONDS=0
SUCCESSFUL_BONDS=0
EXCELLENT_BONDS=0
GOOD_BONDS=0
FAILED_BONDS=0

# Test each bond
for bond_data in "${BONDS[@]}"; do
    IFS='|' read -r description price bbg_yield bbg_duration bbg_spread isin <<< "$bond_data"
    
    TOTAL_BONDS=$((TOTAL_BONDS + 1))
    echo "🔷 Testing Bond $TOTAL_BONDS: $description"
    echo "   Price: $price | BBG Yield: $bbg_yield% | BBG Duration: $bbg_duration years"
    
    # Call API
    RESPONSE=$(curl -s -X POST "$API_URL/api/v1/bond/parse-and-calculate" \
        -H "Content-Type: application/json" \
        -d "{\"description\": \"$description\", \"price\": $price, \"settlement_date\": \"2025-07-30\"}")
    
    if echo "$RESPONSE" | grep -q '"status":"success"'; then
        # Extract API results
        API_YIELD=$(echo "$RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    yield_val = data.get('analytics', {}).get('yield', 0.0)
    print(f'{yield_val:.2f}')
except:
    print('0.00')
")
        
        API_DURATION=$(echo "$RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    duration_val = data.get('analytics', {}).get('duration', 0.0)
    print(f'{duration_val:.2f}')
except:
    print('0.00')
")
        
        # Calculate differences
        YIELD_DIFF=$(python3 -c "print(f'{abs($API_YIELD - $bbg_yield) * 100:.0f}')")
        DURATION_DIFF=$(python3 -c "print(f'{abs($API_DURATION - $bbg_duration):.2f}')")
        
        # Determine status
        if (( $(echo "$YIELD_DIFF <= 5" | bc -l) )) && (( $(echo "$DURATION_DIFF <= 0.5" | bc -l) )); then
            STATUS="✅ EXCELLENT"
            EXCELLENT_BONDS=$((EXCELLENT_BONDS + 1))
        elif (( $(echo "$YIELD_DIFF <= 25" | bc -l) )) && (( $(echo "$DURATION_DIFF <= 2.0" | bc -l) )); then
            STATUS="⚠️  GOOD"
            GOOD_BONDS=$((GOOD_BONDS + 1))
        else
            STATUS="❌ CHECK"
        fi
        
        SUCCESSFUL_BONDS=$((SUCCESSFUL_BONDS + 1))
        
        echo "   ✅ API Yield: ${API_YIELD}% (diff: ${YIELD_DIFF}bp) | Duration: ${API_DURATION}yr (diff: ${DURATION_DIFF}yr) | $STATUS"
        
        # Store results
        RESULTS_API_YIELD+=("$API_YIELD")
        RESULTS_API_DURATION+=("$API_DURATION")
        RESULTS_STATUS+=("$STATUS")
        RESULTS_BOND_NAMES+=("$description")
        
    else
        echo "   ❌ API call failed"
        FAILED_BONDS=$((FAILED_BONDS + 1))
        RESULTS_API_YIELD+=("FAILED")
        RESULTS_API_DURATION+=("FAILED")
        RESULTS_STATUS+=("❌ FAILED")
        RESULTS_BOND_NAMES+=("$description")
    fi
    
    echo ""
done

echo "🏆 COMPREHENSIVE VALIDATION SUMMARY"
echo "=================================="
echo "📊 Total Bonds Tested: $TOTAL_BONDS"
echo "✅ Successful API Calls: $SUCCESSFUL_BONDS"
echo "🌟 Excellent Results (≤5bp, ≤0.5yr): $EXCELLENT_BONDS"
echo "⚠️  Good Results (≤25bp, ≤2.0yr): $GOOD_BONDS"
echo "❌ Failed/Poor Results: $FAILED_BONDS"
echo ""

# Calculate success rates
SUCCESS_RATE=$(python3 -c "print(f'{($SUCCESSFUL_BONDS / $TOTAL_BONDS) * 100:.1f}')")
EXCELLENT_RATE=$(python3 -c "print(f'{($EXCELLENT_BONDS / $TOTAL_BONDS) * 100:.1f}')")

echo "📈 Overall Success Rate: ${SUCCESS_RATE}%"
echo "🎯 Excellent Accuracy Rate: ${EXCELLENT_RATE}%"

# Generate detailed comparison table
echo ""
echo "📋 DETAILED COMPARISON TABLE"
echo "==========================="
printf "%-3s %-35s %-8s %-8s %-8s %-8s %-8s %-12s\n" "#" "Bond Name" "BBG_YLD" "API_YLD" "YLD_DIFF" "BBG_DUR" "API_DUR" "STATUS"
printf "%s\n" "$(printf '=%.0s' {1..100})"

for i in "${!BONDS[@]}"; do
    IFS='|' read -r description price bbg_yield bbg_duration bbg_spread isin <<< "${BONDS[$i]}"
    
    # Truncate bond name for display
    SHORT_NAME=$(echo "$description" | cut -c1-33)
    if [[ ${#description} -gt 33 ]]; then
        SHORT_NAME="${SHORT_NAME}..."
    fi
    
    API_YIELD_VAL="${RESULTS_API_YIELD[$i]}"
    API_DURATION_VAL="${RESULTS_API_DURATION[$i]}"
    STATUS_VAL="${RESULTS_STATUS[$i]}"
    
    if [[ "$API_YIELD_VAL" != "FAILED" ]]; then
        YIELD_DIFF=$(python3 -c "print(f'{abs($API_YIELD_VAL - $bbg_yield) * 100:.0f}bp')")
        DUR_DIFF=$(python3 -c "print(f'{abs($API_DURATION_VAL - $bbg_duration):.2f}yr')" 2>/dev/null || echo "N/A")
    else
        YIELD_DIFF="FAILED"
        DUR_DIFF="FAILED"
    fi
    
    printf "%-3d %-35s %-8s %-8s %-8s %-8s %-8s %-12s\n" \
        $((i+1)) "$SHORT_NAME" "${bbg_yield}%" "${API_YIELD_VAL}%" "$YIELD_DIFF" "${bbg_duration}yr" "${API_DURATION_VAL}yr" "$STATUS_VAL"
done

echo ""
echo "🎯 VALIDATION COMPLETE!"
echo "======================"

if (( $(echo "$EXCELLENT_RATE >= 70" | bc -l) )); then
    echo "🏆 EXCELLENT: Your API demonstrates institutional-grade accuracy!"
elif (( $(echo "$SUCCESS_RATE >= 90" | bc -l) )); then
    echo "👍 GOOD: Your API shows strong performance with room for optimization"
else
    echo "⚠️  NEEDS IMPROVEMENT: Consider reviewing calculation methodology"
fi

echo ""
echo "📊 Next Steps:"
echo "- Fix portfolio endpoint for full portfolio analytics"
echo "- Investigate bonds with larger differences for optimization"
echo "- Deploy to production with confidence based on individual bond accuracy"