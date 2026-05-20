🛡️ Network Anomaly Detection — Linear Regression SIEM Filter

A cybersecurity-focused machine learning model that detects network intrusions and anomalous traffic patterns using linear regression as a statistical baseline — the same first-pass anomaly filtering approach used by enterprise SIEM platforms like Splunk UBA and Elastic SIEM.

📌 Problem Statement
Modern networks generate millions of requests per minute. Manual monitoring is infeasible at scale. Attackers exploit this blind spot to launch:

DDoS attacks — overwhelming traffic spikes
Data exfiltration — sustained above-normal outbound traffic
Port scans — repeated low-level probes at irregular intervals
Brute-force attacks — spikes in authentication traffic

This model learns what "normal" traffic looks like for each hour of the day and raises a severity-graded alert the moment observed traffic deviates significantly from that baseline.

⚙️ How It Works
Raw Traffic Logs
      │
      ▼
┌─────────────────────────┐
│  1. Aggregate into      │  → 1-minute bins per hour
│     time windows        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  2. Fit linear          │  → ŷ = mx + b per hour
│     regression baseline │    (trained on past 6 days)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  3. Compute residuals   │  → residual = actual − predicted
│     and std deviation   │    std = σ of training residuals
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  4. Flag anomalies      │  → |residual| > threshold × σ
│     beyond ±2σ          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  5. Severity-graded     │  → LOW / MEDIUM / HIGH alert
│     alert log           │
└─────────────────────────┘
Why per-hour models?
Traffic at 3 AM and 3 PM have completely different baselines. A single model would predict an average that's wrong for almost every hour. Training one regression per hour captures the natural intraday pattern accurately.
Why linear regression?

✅ Fast — O(n) compute, runs in milliseconds per window
✅ Explainable — every alert has a clear mathematical justification
✅ Industry standard — mirrors Splunk's | anomalydetection and Elastic's ML detection jobs
✅ Self-calibrating — wider σ bands on noisy networks, tighter on stable ones


🚨 Severity Classification
DeviationSeverityMeaning> 2.0σ🟡 LOWStatistically unusual, warrants monitoring> 2.5σ🟠 MEDIUMLikely anomalous, investigate promptly> 3.0σ🔴 HIGHAlmost certainly malicious, immediate action

📊 Sample Output
======================================================================
NETWORK ANOMALY DETECTION — LINEAR REGRESSION BASELINE
Monitor day: 6  |  Sigma threshold: ±2.0σ
======================================================================

Hour    Actual  Predicted  Residual   Sigma  Severity
------------------------------------------------------------
15:00    280.0      169.9    +110.1  +17.33σ  HIGH     <-- ALERT
16:00    310.0      161.6    +148.4  +21.08σ  HIGH     <-- ALERT
17:00    265.0      180.3     +84.7   +9.35σ  HIGH     <-- ALERT

======================================================================
ALERT LOG  —  3 anomalies detected
======================================================================
  [HIGH]  Hour 15:00 | actual=280.0 req/min | predicted=169.9 | 17.33σ above baseline
  [HIGH]  Hour 16:00 | actual=310.0 req/min | predicted=161.6 | 21.08σ above baseline
  [HIGH]  Hour 17:00 | actual=265.0 req/min | predicted=180.3 | 9.35σ above baseline

  Correctly flagged : 3/3 injected attacks (100% recall)
======================================================================

🗂️ Project Structure
network-anomaly-detection/
│
├── Network_anomaly.py              # Main detection script
├── network_anomaly_detection.png   # Output visualization
├── requirements.txt                # Dependencies
└── README.md

🚀 Getting Started
Prerequisites

Python 3.8+
pip

Installation
bash# Clone the repository
git clone https://github.com/JoshYadav/network-anomaly-detection.git
cd network-anomaly-detection

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
Run
bashpython Network_anomaly.py

📦 Requirements
numpy
pandas
scikit-learn
matplotlib
Install all at once:
bashpip install numpy pandas scikit-learn matplotlib

🔬 Model Details
ParameterValueAlgorithmLinear Regression (OLS)Training window6 days × same hourAnomaly threshold±2σ (configurable)Models trained24 (one per hour)Mean R²0.218Mean std deviation7.36 req/minAttack recall3/3 (100%)

🧠 Real-World SIEM Mapping
This ProjectIndustry EquivalentPer-hour linear regressionSplunk | anomalydetection per time bucket±2σ thresholdElastic ML anomaly_score thresholdResidual flaggingIBM QRadar flow anomaly rulesSeverity gradingMicrosoft Sentinel alert severity levelsFirst-pass filterPre-filter before Isolation Forest / LSTM

⚠️ Limitations

Does not detect low-and-slow attacks (traffic stays within normal range)
Assumes a linear trend — does not model seasonality or weekly patterns
Each hour is modeled independently — no cross-hour correlation
Synthetic dataset — real-world deployment requires integration with live log sources (Filebeat, Splunk forwarder, etc.)


🔮 Future Improvements

 Replace linear regression with ARIMA or LSTM for time-series awareness
 Add multivariate features: bytes transferred, unique source IPs, failed login count
 Integrate Isolation Forest as second-pass filter
 Connect to live log sources via Filebeat or Splunk HEC
 Build a real-time dashboard with Grafana or Kibana


📚 References

Splunk Anomaly Detection Documentation
Elastic Machine Learning Anomaly Detection
NIST Cybersecurity Framework
Scikit-learn: LinearRegression


👤 Author
Josh Yadav
