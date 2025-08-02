#!/bin/bash
#
# Setup Daily Treasury Yield Updates
# ==================================
#
# This script sets up automatic daily updates of Treasury yields
# Runs at 6 PM ET (after Treasury publishes at ~4 PM ET)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="/usr/bin/python3"
UPDATE_SCRIPT="$SCRIPT_DIR/us_treasury_yield_fetcher.py"

echo "🏦 Setting up Daily Treasury Yield Updates"
echo "========================================="

# Check if update script exists
if [ ! -f "$UPDATE_SCRIPT" ]; then
    echo "❌ Error: Update script not found at $UPDATE_SCRIPT"
    exit 1
fi

# Create log directory
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Create wrapper script for cron
CRON_SCRIPT="$SCRIPT_DIR/cron_treasury_update.sh"
cat > "$CRON_SCRIPT" << EOF
#!/bin/bash
# Treasury Update Cron Wrapper
# Generated on $(date)

cd "$SCRIPT_DIR"
$PYTHON_PATH "$UPDATE_SCRIPT" >> "$LOG_DIR/treasury_updates.log" 2>&1

# Check if update was successful
if [ \$? -eq 0 ]; then
    echo "[\$(date)] ✅ Treasury yields updated successfully" >> "$LOG_DIR/treasury_updates.log"
else
    echo "[\$(date)] ❌ Treasury yield update failed" >> "$LOG_DIR/treasury_updates.log"
    # Optional: Send alert email
    # echo "Treasury yield update failed on \$(date)" | mail -s "Treasury Update Failed" admin@example.com
fi
EOF

chmod +x "$CRON_SCRIPT"

# Display cron entry
echo ""
echo "📋 Add this line to your crontab (crontab -e):"
echo ""
echo "# Update Treasury yields at 6 PM ET every weekday"
echo "0 18 * * 1-5 $CRON_SCRIPT"
echo ""
echo "Or for different timezones:"
echo "# 6 PM ET = 11 PM GMT = 3 PM PT"
echo "0 23 * * 1-5 $CRON_SCRIPT  # GMT"
echo "0 15 * * 1-5 $CRON_SCRIPT  # PT"
echo ""

# Create systemd timer alternative
SYSTEMD_DIR="$SCRIPT_DIR/systemd"
mkdir -p "$SYSTEMD_DIR"

# Create service file
cat > "$SYSTEMD_DIR/treasury-update.service" << EOF
[Unit]
Description=Update Treasury Yields
After=network.target

[Service]
Type=oneshot
ExecStart=$PYTHON_PATH $UPDATE_SCRIPT
WorkingDirectory=$SCRIPT_DIR
StandardOutput=append:$LOG_DIR/treasury_updates.log
StandardError=append:$LOG_DIR/treasury_updates.log
EOF

# Create timer file
cat > "$SYSTEMD_DIR/treasury-update.timer" << EOF
[Unit]
Description=Update Treasury Yields Daily
Requires=treasury-update.service

[Timer]
OnCalendar=Mon-Fri 18:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo "📋 Alternative: Use systemd timer (recommended for servers):"
echo ""
echo "sudo cp $SYSTEMD_DIR/treasury-update.* /etc/systemd/system/"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl enable treasury-update.timer"
echo "sudo systemctl start treasury-update.timer"
echo ""

echo "✅ Setup complete!"
echo ""
echo "📊 Manual test command:"
echo "   $PYTHON_PATH $UPDATE_SCRIPT"
echo ""
echo "📁 Logs will be saved to:"
echo "   $LOG_DIR/treasury_updates.log"