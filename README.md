# 🛡️ Network Anomaly Detection — Linear Regression SIEM Filter

> A cybersecurity-focused machine learning model that detects network intrusions and anomalous traffic patterns using **linear regression as a statistical baseline** — the same first-pass anomaly filtering approach used by enterprise SIEM platforms like **Splunk UBA** and **Elastic SIEM**.

---

## 📌 Problem Statement

Modern networks generate millions of requests per minute. Manual monitoring is infeasible at scale. Attackers exploit this blind spot to launch:

| Attack Type | Pattern |
|---|---|
| 🔴 DDoS | Overwhelming traffic spike in short window |
| 🟠 Data Exfiltration | Sustained above-normal outbound traffic |
| 🟡 Port Scan | Repeated low-level probes at irregular hours |
| 🟡 Brute Force | Spikes in authentication request count |

This model learns what **"normal" traffic looks like** for each hour of the day and raises a severity-graded alert the moment observed traffic deviates significantly from that baseline.

---

## ⚙️ How It Works

### Pipeline

**Step 1 — Ingest & Aggregate**
Raw packet/log streams are bucketed into fixed 1-minute time windows per hour of day.

**Step 2 — Fit Baseline (Linear Regression)**
A rolling window of historical data (past 6 days × same hour) is used to fit:

```
ŷ = mx + b
```

where `x` = day number, `ŷ` = predicted requests per minute.

**Step 3 — Compute Residuals**
```
residual  = actual − predicted
std (σ)   = standard deviation of training residuals
```

**Step 4 — Flag Anomalies**
```
if |residual| > threshold × σ  →  ALERT
```

**Step 5 — Severity Grading**

| Deviation | Severity |
|---|---|
| > 2.0σ | 🟡 LOW |
| > 2.5σ | 🟠 MEDIUM |
| > 3.0σ | 🔴 HIGH |

---

## 💡 Key Design Decisions

**Why one model per hour?**
Traffic at 3 AM and 3 PM have completely different baselines. A single model predicts an average that is wrong for almost every hour. Training one regression per hour captures the natural intraday pattern accurately.

**Why linear regression?**
- Fast — O(n) compute, runs in milliseconds per window
- Explainable — every alert has a clear mathematical reason
- Industry standard — mirrors Splunk `| anomalydetection` and Elastic ML jobs
- Self-calibrating — wider σ bands on noisy networks, tighter on stable ones

---

## 📊 Sample Output

```
======================================================================
NETWORK ANOMALY DETECTION — LINEAR REGRESSION BASELINE
Monitor day: 6  |  Sigma threshold: ±2.0σ
======================================================================

Hour    Actual  Predicted  Residual    Sigma  Severity
------------------------------------------------------------
00:00     84.6       87.9      -3.3   -0.85σ  NORMAL
06:00    112.5       98.3     +14.2   +2.20σ  LOW       <-- ALERT
12:00    190.7      162.6     +28.1   +6.59σ  HIGH      <-- ALERT
15:00    280.0      169.9    +110.1  +17.33σ  HIGH      <-- ALERT
16:00    310.0      161.6    +148.4  +21.08σ  HIGH      <-- ALERT
17:00    265.0      180.3     +84.7   +9.35σ  HIGH      <-- ALERT

======================================================================
ALERT LOG  —  7 anomalies detected
======================================================================

  [HIGH]  Hour 15:00 | actual=280.0 req/min | predicted=169.9 | 17.33σ above baseline
  [HIGH]  Hour 16:00 | actual=310.0 req/min | predicted=161.6 | 21.08σ above baseline
  [HIGH]  Hour 17:00 | actual=265.0 req/min | predicted=180.3 |  9.35σ above baseline

======================================================================
MODEL SUMMARY
======================================================================

  Total hours monitored  :  24
  Anomalies flagged      :  7
  Mean R²                :  0.2180
  Injected attack hours  :  15, 16, 17
  Correctly flagged      :  3 / 3  (100% recall)

======================================================================
```

---

## 🗂️ Project Structure

```
network-anomaly-detection/
│
├── Network_anomaly.py              # Main detection script
├── network_anomaly_detection.png   # Output visualization
├── requirements.txt                # Dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/JoshYadav/network-anomaly-detection.git
cd network-anomaly-detection
```

### 2. Create and activate virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install numpy pandas scikit-learn matplotlib
```

### 4. Run

```bash
python Network_anomaly.py
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `numpy` | Numerical computation |
| `pandas` | Data structuring and manipulation |
| `scikit-learn` | Linear regression model |
| `matplotlib` | Output visualization |

---

## 🔬 Model Summary

| Parameter | Value |
|---|---|
| Algorithm | Linear Regression (Ordinary Least Squares) |
| Training window | 6 days × same hour |
| Anomaly threshold | ±2σ (configurable) |
| Models trained | 24 (one per hour of day) |
| Mean R² | 0.218 |
| Mean std deviation | 7.36 req/min |
| Attack recall | 3/3 — 100% |

---

## 🧠 Real-World SIEM Mapping

| This Project | Industry Equivalent |
|---|---|
| Per-hour linear regression | Splunk `\| anomalydetection` per time bucket |
| ±2σ residual threshold | Elastic ML anomaly score threshold |
| Severity grading | Microsoft Sentinel alert severity levels |
| First-pass filter | Pre-filter before Isolation Forest / LSTM |

---

## ⚠️ Limitations

- Does not detect **low-and-slow attacks** where traffic stays within normal range
- Assumes a **linear trend** — does not model weekly seasonality
- Each hour is modeled **independently** — no cross-hour correlation
- Uses **synthetic data** — real deployment requires live log integration

---

## 🔮 Future Improvements

- [ ] Replace linear regression with **ARIMA** or **LSTM** for time-series awareness
- [ ] Add multivariate features: bytes transferred, unique IPs, failed login count
- [ ] Integrate **Isolation Forest** as a second-pass filter
- [ ] Connect to live sources via **Filebeat** or **Splunk HEC**
- [ ] Build a real-time dashboard with **Grafana** or **Kibana**

---

## 📚 References

- [Splunk Anomaly Detection](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Anomalydetection)
- [Elastic ML Anomaly Detection](https://www.elastic.co/guide/en/machine-learning/current/ml-ad-overview.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Scikit-learn LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)

---

## 👤 Author

**Josh Yadav**
