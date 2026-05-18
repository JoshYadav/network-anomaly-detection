import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ─── 1. Generate synthetic 7-day traffic dataset ───────────────────────────
np.random.seed(42)

HOURS_PER_DAY = 24
DAYS = 7

# Realistic intraday pattern (req/min baseline)
hourly_pattern = np.array([
    82, 74, 68, 65, 70, 85, 110, 148, 162, 170, 168, 165,
    172, 168, 160, 158, 165, 170, 162, 148, 130, 115, 102, 90
])

records = []
for day in range(DAYS):
    for hour in range(HOURS_PER_DAY):
        noise = np.random.normal(0, 10)
        val = hourly_pattern[hour] + noise
        records.append({"day": day, "hour": hour, "requests": round(val, 2)})

df = pd.DataFrame(records)

# ─── 2. Inject attacks on day 6 (the "live" day we monitor) ────────────────
attack_hours = {15: 280, 16: 310, 17: 265}  # DDoS spike
for h, val in attack_hours.items():
    df.loc[(df.day == 6) & (df.hour == h), "requests"] = val

# ─── 3. Per-hour regression baseline (rolling 7-day window per hour) ───────
SIGMA_THRESHOLD = 2.0
MONITOR_DAY = 6

results = []

for hour in range(HOURS_PER_DAY):
    # Training data: all days EXCEPT the day being monitored
    train = df[(df.hour == hour) & (df.day < MONITOR_DAY)].copy()
    live  = df[(df.hour == hour) & (df.day == MONITOR_DAY)].copy()

    X_train = train[["day"]].values
    y_train = train["requests"].values
    X_live  = live[["day"]].values
    y_live  = live["requests"].values[0]

    # Fit linear regression on historical days
    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_live)[0]
    residuals_train = y_train - model.predict(X_train)
    std_dev = np.std(residuals_train)
    r2 = r2_score(y_train, model.predict(X_train))

    residual = y_live - y_pred
    deviation_sigma = residual / std_dev if std_dev > 0 else 0
    is_anomaly = abs(deviation_sigma) > SIGMA_THRESHOLD

    severity = (
        "HIGH"   if abs(deviation_sigma) > 3.0 else
        "MEDIUM" if abs(deviation_sigma) > 2.5 else
        "LOW"    if is_anomaly else
        "NORMAL"
    )

    results.append({
        "hour":            hour,
        "actual":          round(y_live, 1),
        "predicted":       round(y_pred, 1),
        "residual":        round(residual, 1),
        "deviation_sigma": round(deviation_sigma, 2),
        "std_dev":         round(std_dev, 2),
        "r2_score":        round(r2, 4),
        "anomaly":         is_anomaly,
        "severity":        severity,
    })

results_df = pd.DataFrame(results)

# ─── 4. Display full results ────────────────────────────────────────────────
print("=" * 70)
print("NETWORK ANOMALY DETECTION — LINEAR REGRESSION BASELINE")
print(f"Monitor day: {MONITOR_DAY}  |  Sigma threshold: ±{SIGMA_THRESHOLD}σ")
print("=" * 70)
print(f"\n{'Hour':<6} {'Actual':>8} {'Predicted':>10} {'Residual':>10} {'Sigma':>7} {'Severity':<10}")
print("-" * 60)

for _, row in results_df.iterrows():
    flag = " <-- ALERT" if row["anomaly"] else ""
    print(
        f"{int(row['hour']):02d}:00  "
        f"{row['actual']:>8.1f}  "
        f"{row['predicted']:>9.1f}  "
        f"{row['residual']:>+9.1f}  "
        f"{row['deviation_sigma']:>+6.2f}σ  "
        f"{row['severity']:<10}"
        f"{flag}"
    )

# ─── 5. Alert log ───────────────────────────────────────────────────────────
alerts = results_df[results_df["anomaly"]]
print("\n" + "=" * 70)
print(f"ALERT LOG  —  {len(alerts)} anomal{'y' if len(alerts)==1 else 'ies'} detected")
print("=" * 70)

if alerts.empty:
    print("  No anomalies — system nominal.")
else:
    for _, a in alerts.iterrows():
        direction = "above" if a["residual"] > 0 else "below"
        print(
            f"  [{a['severity']}]  Hour {int(a['hour']):02d}:00 | "
            f"actual={a['actual']} req/min | "
            f"predicted={a['predicted']} req/min | "
            f"{abs(a['deviation_sigma'])}σ {direction} baseline"
        )

# ─── 6. Summary statistics ──────────────────────────────────────────────────
print("\n" + "=" * 70)
print("MODEL SUMMARY")
print("=" * 70)
print(f"  Total hours monitored : {len(results_df)}")
print(f"  Anomalies flagged     : {alerts['anomaly'].sum()}")
print(f"  Detection rate        : {len(alerts)/len(results_df)*100:.1f}%")
print(f"  Mean R² (per-hour)    : {results_df['r2_score'].mean():.4f}")
print(f"  Mean std deviation    : {results_df['std_dev'].mean():.2f} req/min")
print(f"  Injected attack hours : {list(attack_hours.keys())} (ground truth)")
print(f"  Correctly flagged     : {sum(h in alerts['hour'].values for h in attack_hours)}/{len(attack_hours)}")

# ─── 7. Generate simple visualizations ─────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

hours = results_df['hour'].values
actual = results_df['actual'].values
predicted = results_df['predicted'].values
sigma = results_df['deviation_sigma'].values
is_anomaly = results_df['anomaly'].values

# Plot 1: Actual vs Predicted Traffic
ax1 = axes[0]
ax1.plot(hours, actual, 'b-', linewidth=2, label='Actual')
ax1.plot(hours, predicted, 'g--', linewidth=2, label='Predicted')
ax1.scatter(hours[is_anomaly], actual[is_anomaly], color='red', s=100, marker='X', label='Anomaly', zorder=5)
ax1.set_xlabel('Hour of Day')
ax1.set_ylabel('Requests/min')
ax1.set_title('Actual vs Predicted Traffic')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xticks(range(0, 24, 2))

# Plot 2: Sigma Deviations with Threshold
ax2 = axes[1]
colors = ['red' if anom else 'blue' for anom in is_anomaly]
ax2.bar(hours, sigma, color=colors, alpha=0.6)
ax2.axhline(y=SIGMA_THRESHOLD, color='orange', linestyle='--', linewidth=2, label=f'Threshold')
ax2.axhline(y=-SIGMA_THRESHOLD, color='orange', linestyle='--', linewidth=2)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax2.set_xlabel('Hour of Day')
ax2.set_ylabel('Sigma Deviations')
ax2.set_title('Anomaly Detection (Sigma Deviations)')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_xticks(range(0, 24, 2))

plt.tight_layout()
plt.savefig('network_anomaly_detection.png', dpi=100, bbox_inches='tight')
print("\n" + "=" * 70)
print("Visualization saved as: network_anomaly_detection.png")
print("=" * 70)