#!/bin/bash

# Documentation Monitoring Setup Script
# =====================================
# Sets up automated documentation maintenance monitoring

echo "📚 XTrillion API Documentation Monitoring Setup"
echo "==============================================="

# Make the agent executable
chmod +x doc_maintenance_agent.py

echo "✅ Documentation maintenance agent is ready!"
echo ""
echo "🔍 Usage Examples:"
echo "   python3 doc_maintenance_agent.py --check     # Run health check"
echo "   python3 doc_maintenance_agent.py --update    # Check and fix issues"
echo ""

# Test the agent
echo "🧪 Running initial documentation health check..."
python3 doc_maintenance_agent.py --check

echo ""
echo "⏰ Automated Monitoring Options:"
echo ""
echo "1. **Manual Schedule** (recommended for development):"
echo "   Run before important demos or client meetings:"
echo "   python3 doc_maintenance_agent.py --check"
echo ""
echo "2. **Cron Schedule** (for production):"
echo "   # Add to crontab for daily checks at 9 AM:"
echo "   0 9 * * * cd $(pwd) && python3 doc_maintenance_agent.py --check --api-base https://your-production-url.com"
echo ""
echo "3. **Pre-commit Hook** (for development):"
echo "   # Add to .git/hooks/pre-commit:"
echo "   echo '#!/bin/bash' > .git/hooks/pre-commit"
echo "   echo 'python3 doc_maintenance_agent.py --check --api-base http://localhost:8080' >> .git/hooks/pre-commit"
echo "   chmod +x .git/hooks/pre-commit"
echo ""
echo "4. **GitHub Actions** (for CI/CD):"
echo "   Create .github/workflows/doc-check.yml with documentation validation"
echo ""

# Create a sample cron entry file
cat > doc_monitoring_cron.txt << 'EOF'
# XTrillion API Documentation Monitoring
# Add these lines to your crontab with 'crontab -e'

# Daily documentation check at 9 AM (local development)
0 9 * * * cd /path/to/your/project && python3 doc_maintenance_agent.py --check

# Pre-deployment check (before business hours)
0 8 * * 1-5 cd /path/to/your/project && python3 doc_maintenance_agent.py --check --api-base https://your-production-url.com

# Weekly comprehensive check with performance measurement
0 7 * * 1 cd /path/to/your/project && python3 doc_maintenance_agent.py --check > weekly_doc_report.txt
EOF

echo "📁 Created 'doc_monitoring_cron.txt' with sample cron entries"
echo ""
echo "🎯 Next Steps:"
echo "   1. Review the initial health check results above"
echo "   2. Fix any critical issues found"
echo "   3. Choose a monitoring schedule that fits your workflow"
echo "   4. Set up automated alerts for documentation drift"
echo ""
echo "💡 Pro Tips:"
echo "   - Run before client demos to catch broken examples"
echo "   - Use --check before --update to see what will change"
echo "   - Monitor performance metrics for contract negotiations"
echo "   - Set up Slack/email alerts for failed checks in production"