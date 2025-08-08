#!/usr/bin/env python3
"""
Test Results Viewer and Runner
Provides a simple web interface to view test results and run tests on demand
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
import datetime
import subprocess
from pathlib import Path

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>XTrillion API Test Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }
        .card .value {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .success { color: #27ae60; }
        .warning { color: #f39c12; }
        .danger { color: #e74c3c; }
        .test-results {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .passed {
            background-color: #d4edda;
            color: #155724;
        }
        .failed {
            background-color: #f8d7da;
            color: #721c24;
        }
        .controls {
            margin-bottom: 20px;
            text-align: right;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background-color: #2980b9;
        }
        button:disabled {
            background-color: #95a5a6;
            cursor: not-allowed;
        }
        .loading {
            display: none;
            margin-left: 10px;
        }
        .details {
            font-size: 12px;
            color: #666;
            max-width: 400px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .response-time {
            font-family: monospace;
            color: #666;
        }
        .history-section {
            margin-top: 30px;
        }
        .file-list {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .file-item {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        .file-item:hover {
            background-color: #f8f9fa;
        }
        .file-link {
            color: #3498db;
            text-decoration: none;
        }
        .file-link:hover {
            text-decoration: underline;
        }
        .timestamp {
            color: #666;
            font-size: 12px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 XTrillion API Test Dashboard</h1>
            <p>Monitor and run API tests</p>
        </div>

        <div class="controls">
            <button id="runTests" onclick="runTests()">
                Run All Tests
            </button>
            <span class="loading" id="loading">⏳ Running tests...</span>
        </div>

        <div id="currentResults">
            <!-- Current results will be loaded here -->
        </div>

        <div class="history-section">
            <h2>📁 Test History</h2>
            <div id="historyList" class="file-list">
                <!-- History will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        function formatTimestamp(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleString();
        }

        function formatResponseTime(seconds) {
            if (seconds === 0) return 'N/A';
            return `${(seconds * 1000).toFixed(0)}ms`;
        }

        function displayResults(data) {
            const successRate = data.success_rate || 0;
            const rateClass = successRate === 100 ? 'success' : successRate >= 80 ? 'warning' : 'danger';
            
            const html = `
                <div class="summary-cards">
                    <div class="card">
                        <h3>Success Rate</h3>
                        <div class="value ${rateClass}">${successRate.toFixed(1)}%</div>
                    </div>
                    <div class="card">
                        <h3>Tests Passed</h3>
                        <div class="value success">${data.passed}</div>
                    </div>
                    <div class="card">
                        <h3>Tests Failed</h3>
                        <div class="value danger">${data.failed}</div>
                    </div>
                    <div class="card">
                        <h3>Total Duration</h3>
                        <div class="value">${data.duration_seconds.toFixed(1)}s</div>
                    </div>
                </div>

                <div class="test-results">
                    <h2>Test Results - ${data.environment}</h2>
                    <p style="color: #666;">Last run: ${formatTimestamp(data.timestamp)}</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Test Name</th>
                                <th>Status</th>
                                <th>Response Time</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.results.map(result => `
                                <tr>
                                    <td>${result.test_name}</td>
                                    <td>
                                        <span class="status-badge ${result.passed ? 'passed' : 'failed'}">
                                            ${result.passed ? 'PASSED' : 'FAILED'}
                                        </span>
                                    </td>
                                    <td class="response-time">${formatResponseTime(result.response_time)}</td>
                                    <td class="details">${result.details}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            document.getElementById('currentResults').innerHTML = html;
        }

        function loadLatestResults() {
            fetch('/api/latest-results')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('currentResults').innerHTML = 
                            '<div class="test-results"><p style="color: #e74c3c;">No test results found. Run tests to generate results.</p></div>';
                    } else {
                        displayResults(data);
                    }
                })
                .catch(error => {
                    console.error('Error loading results:', error);
                });
        }

        function loadHistory() {
            fetch('/api/test-history')
                .then(response => response.json())
                .then(files => {
                    const html = files.map(file => `
                        <div class="file-item">
                            <a href="/api/results/${file.name}" class="file-link" 
                               onclick="loadHistoricalResult('${file.name}'); return false;">
                                ${file.name}
                            </a>
                            <span class="timestamp">${formatTimestamp(file.modified)}</span>
                        </div>
                    `).join('');
                    
                    document.getElementById('historyList').innerHTML = html || '<p style="color: #666;">No historical results found.</p>';
                })
                .catch(error => {
                    console.error('Error loading history:', error);
                });
        }

        function loadHistoricalResult(filename) {
            fetch(`/api/results/${filename}`)
                .then(response => response.json())
                .then(data => displayResults(data))
                .catch(error => {
                    console.error('Error loading historical result:', error);
                });
        }

        function runTests() {
            const button = document.getElementById('runTests');
            const loading = document.getElementById('loading');
            
            button.disabled = true;
            loading.style.display = 'inline';
            
            fetch('/api/run-tests', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayResults(data.results);
                        loadHistory(); // Refresh history
                    } else {
                        alert('Error running tests: ' + data.error);
                    }
                })
                .catch(error => {
                    alert('Error running tests: ' + error);
                })
                .finally(() => {
                    button.disabled = false;
                    loading.style.display = 'none';
                });
        }

        // Load initial data
        loadLatestResults();
        loadHistory();
        
        // Refresh every 30 seconds
        setInterval(() => {
            loadLatestResults();
            loadHistory();
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/latest-results')
def get_latest_results():
    """Get the most recent test results"""
    try:
        # Find the most recent test results file
        result_files = list(Path('.').glob('test_results_production_*.json'))
        if not result_files:
            return jsonify({'error': 'No test results found'}), 404
        
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-history')
def get_test_history():
    """Get list of all test result files"""
    try:
        result_files = list(Path('.').glob('test_results_*.json'))
        files = []
        
        for file in sorted(result_files, key=lambda f: f.stat().st_mtime, reverse=True):
            files.append({
                'name': file.name,
                'modified': datetime.datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                'size': file.stat().st_size
            })
        
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<filename>')
def get_specific_result(filename):
    """Get a specific test result file"""
    try:
        file_path = Path(filename)
        if not file_path.exists() or not filename.startswith('test_results_'):
            return jsonify({'error': 'File not found'}), 404
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    """Run the test suite"""
    try:
        # Run the test suite
        result = subprocess.run(
            ['python3', 'daily_test_suite.py'],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            # Load the results that were just generated
            result_files = list(Path('.').glob('test_results_production_*.json'))
            latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_file, 'r') as f:
                test_results = json.load(f)
            
            return jsonify({
                'success': True,
                'results': test_results,
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or 'Tests failed',
                'output': result.stdout
            })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Test execution timed out'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)