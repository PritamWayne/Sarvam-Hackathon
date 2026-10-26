"""
Interactive Web Dashboard & Inspection GUI for Land Deed Verification.
Runs a zero-dependency local web server on port 8080.
Displays:
- Uploaded Scanned Document vs Deskewed/Enhanced Output
- Visual Authenticity Markers Overlay (Stamps, Signatures, Kaifiyat)
- Parsed Deed Metadata & Tabular Ownership Shares
- Live JSON Viewer with Copy/Export capability
"""

import os
import sys
import json
import cgi
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

from pipeline import LandDeedVerificationPipeline

PORT = 8080
PIPELINE = LandDeedVerificationPipeline()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sarvam Vision — Land Deed Ingestion & Verification</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --bg: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-green: #10b981;
            --accent-blue: #38bdf8;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.5;
            padding: 24px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--card-border);
            margin-bottom: 24px;
        }
        .logo-group h1 { font-size: 1.6rem; font-weight: 700; color: #fff; }
        .logo-group p { font-size: 0.9rem; color: var(--text-muted); margin-top: 4px; }
        .badge-sarvam {
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: #fff;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 16px;
        }
        .stat-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
        .stat-value { font-size: 1.5rem; font-weight: 700; margin-top: 6px; }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .pill-verified { background: rgba(16, 185, 129, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }
        .pill-flagged { background: rgba(245, 158, 11, 0.2); color: var(--accent-amber); border: 1px solid var(--accent-amber); }
        .main-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .card-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card-title { font-size: 1.05rem; font-weight: 600; }
        .card-body { padding: 20px; overflow-y: auto; max-height: 800px; }
        .img-preview-container {
            position: relative;
            background: #090d16;
            border-radius: 8px;
            padding: 8px;
            text-align: center;
            border: 1px solid var(--card-border);
        }
        .img-preview-container img {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        .legend-bar {
            display: flex;
            gap: 16px;
            margin-top: 12px;
            font-size: 0.8rem;
            justify-content: center;
        }
        .legend-item { display: flex; align-items: center; gap: 6px; }
        .legend-dot { width: 12px; height: 12px; border-radius: 3px; }
        .table-responsive { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 0.9rem; }
        .table-responsive th, .table-responsive td {
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid var(--card-border);
        }
        .table-responsive th { background: #162032; color: var(--text-muted); font-weight: 600; }
        pre.json-box {
            background: #0b1120;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 14px;
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            color: #38bdf8;
            overflow-x: auto;
            max-height: 480px;
        }
        .btn {
            background: var(--primary);
            color: #fff;
            padding: 8px 16px;
            border-radius: 6px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
            transition: background 0.2s;
        }
        .btn:hover { background: var(--primary-hover); }
        .tab-nav {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--card-border);
            padding: 12px 20px 0 20px;
        }
        .tab-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            padding: 8px 14px;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.9rem;
            border-bottom: 2px solid transparent;
        }
        .tab-btn.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
            font-weight: 600;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-group">
                <h1>Step 1: Land Deed Ingestion & Verification</h1>
                <p>Sarvam Vision (Doc-AI) Multilingual Layout, Ownership & Visual Authenticity Pipeline</p>
            </div>
            <div>
                <span class="badge-sarvam">Sarvam AI Powered</span>
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Document Status</div>
                <div class="stat-value">
                    <span class="status-pill pill-verified" id="authStatusPill">
                        ● VERIFIED
                    </span>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Mandatory Stamps</div>
                <div class="stat-value" id="stampStat" style="color: var(--accent-green);">PRESENT (2)</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Tehsildar/Patwari Signatures</div>
                <div class="stat-value" id="sigStat" style="color: var(--accent-blue);">VERIFIED</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Marginal Remarks (Kaifiyat)</div>
                <div class="stat-value" id="kaifiyatStat" style="color: var(--accent-amber);">DETECTED</div>
            </div>
        </div>

        <div class="main-layout">
            <!-- Left Panel: Scanned Document & Visual Markers Overlay -->
            <div class="card">
                <div class="tab-nav">
                    <button class="tab-btn active" onclick="switchView('overlayView', this)">Visual Verification Overlay</button>
                    <button class="tab-btn" onclick="switchView('enhancedView', this)">Enhanced / Deskewed</button>
                    <button class="tab-btn" onclick="switchView('originalView', this)">Original Raw Scan</button>
                </div>
                <div class="card-body">
                    <div id="overlayView" class="tab-content active img-preview-container">
                        <img src="/output/sample_land_deed_verified_overlay.png" alt="Visual Markers Overlay">
                        <div class="legend-bar">
                            <div class="legend-item"><div class="legend-dot" style="background:#22c55e;"></div> Official Stamps</div>
                            <div class="legend-item"><div class="legend-dot" style="background:#0ea5e9;"></div> Signatures</div>
                            <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div> Kaifiyat Remarks</div>
                        </div>
                    </div>
                    <div id="enhancedView" class="tab-content img-preview-container">
                        <img src="/output/preprocessed/sample_land_deed_enhanced.png" alt="Enhanced Preprocessed">
                    </div>
                    <div id="originalView" class="tab-content img-preview-container">
                        <img src="/sample_land_deed.png" alt="Original Scan">
                    </div>
                </div>
            </div>

            <!-- Right Panel: Extracted Deed Metadata & Tabular Ownership Data -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Extracted Deed Metadata & Ownership</span>
                    <a href="/output/sample_land_deed_verification_result.json" download class="btn">
                        Export JSON
                    </a>
                </div>
                <div class="card-body">
                    <h3 style="font-size: 1rem; margin-bottom: 8px; color: var(--accent-blue);">Land Parcel & Jurisdiction</h3>
                    <table class="table-responsive" style="margin-bottom: 20px;">
                        <tr><th>Deed Type</th><td id="deedType">Khatauni (अधिकार अभिलेख)</td></tr>
                        <tr><th>Khasra / Plot Numbers</th><td id="khasraNo">154/1, 154/2, 156</td></tr>
                        <tr><th>Khata Number</th><td id="khataNo">00184</td></tr>
                        <tr><th>Village / Tehsil</th><td id="jurisdiction">Khaspur (खासपुर), Mawana, Meerut, UP</td></tr>
                        <tr><th>Plot Area</th><td id="plotArea">3.75 Bigha (9,484.8 Sq. M / 0.9485 Hectares)</td></tr>
                        <tr><th>Marginal Kaifiyat Notes</th><td id="kaifiyatText" style="font-size:0.85rem; color:#fde68a;">आदेश दि० 12.09.2024 न्यायालय तहसीलदार, मवाना: दाखिल खारिज स्वीकार हुआ।</td></tr>
                    </table>

                    <h3 style="font-size: 1rem; margin-bottom: 8px; color: var(--accent-green);">Recorded Tenure Holders (Ownership Shares)</h3>
                    <table class="table-responsive" style="margin-bottom: 20px;">
                        <thead>
                            <tr>
                                <th>Owner / Tenure Holder</th>
                                <th>Parentage</th>
                                <th>Share %</th>
                                <th>Allocated Area</th>
                            </tr>
                        </thead>
                        <tbody id="tenureTable">
                            <tr>
                                <td>सुरेश कुमार (Suresh Kumar)</td>
                                <td>स्व० रामस्वरूप</td>
                                <td><span style="color: var(--accent-green); font-weight:600;">50.0% (1/2)</span></td>
                                <td>1.875 Bigha</td>
                            </tr>
                            <tr>
                                <td>महेश कुमार (Mahesh Kumar)</td>
                                <td>स्व० रामस्वरूप</td>
                                <td><span style="color: var(--accent-green); font-weight:600;">50.0% (1/2)</span></td>
                                <td>1.875 Bigha</td>
                            </tr>
                        </tbody>
                    </table>

                    <h3 style="font-size: 1rem; margin-bottom: 8px; color: var(--text-muted);">Complete Structured JSON Output</h3>
                    <pre class="json-box" id="jsonBox">Loading verified JSON data...</pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchView(tabId, btn) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }

        // Load JSON Result dynamically
        fetch('/output/sample_land_deed_verification_result.json')
            .then(res => res.json())
            .then(data => {
                document.getElementById('jsonBox').textContent = JSON.stringify(data, null, 2);
            })
            .catch(err => {
                console.error("Could not load result json", err);
            });
    </script>
</body>
</html>
"""


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path).path
        if parsed_path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return
        # Serve static assets from working directory
        return super().do_GET()


def run_dashboard():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, DashboardRequestHandler)
    print(f"\n" + "=" * 65)
    print(f" Land Deed Ingestion & Verification Web Dashboard is Live!")
    print(f" URL: http://127.0.0.1:{PORT}")
    print(f"=" * 65 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    run_dashboard()
