#!/bin/bash
# Treasury Update Cron Wrapper
# Generated on Fri  1 Aug 2025 14:54:31 BST

cd "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
/usr/bin/python3 "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/us_treasury_yield_fetcher.py" >> "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/logs/treasury_updates.log" 2>&1

# Check if update was successful
if [ $? -eq 0 ]; then
    echo "[$(date)] ✅ Treasury yields updated successfully" >> "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/logs/treasury_updates.log"
else
    echo "[$(date)] ❌ Treasury yield update failed" >> "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/logs/treasury_updates.log"
    # Optional: Send alert email
    # echo "Treasury yield update failed on $(date)" | mail -s "Treasury Update Failed" admin@example.com
fi
