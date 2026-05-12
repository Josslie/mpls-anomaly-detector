import pandas as pd
import sys
sys.path.insert(0, "src")

class KPIAnalyzer:
    def __init__(self, csv_path="data/metrics.csv"):
        self.df = pd.read_csv(csv_path)

    def summary(self):
        print("=== KPIs globaux ===")
        print("-" * 45)
        print("Latence moyenne  : " + str(round(self.df["latency_ms"].mean(), 2)) + " ms")
        print("Latence max      : " + str(round(self.df["latency_ms"].max(), 2)) + " ms")
        print("Gigue moyenne    : " + str(round(self.df["jitter_ms"].mean(), 2)) + " ms")
        print("Perte moyenne    : " + str(round(self.df["loss_pct"].mean(), 2)) + " %")
        print("Utilisation moy  : " + str(round(self.df["utilization_pct"].mean(), 2)) + " %")
        print("CPU moyen        : " + str(round(self.df["cpu_pct"].mean(), 2)) + " %")
        print("Flux actifs moy  : " + str(round(self.df["active_flows"].mean(), 1)))

    def by_event(self):
        print("\n=== KPIs par type d evenement ===")
        print("-" * 45)
        grouped = self.df.groupby("event")[["latency_ms","jitter_ms","loss_pct","cpu_pct"]].mean().round(2)
        print(grouped.to_string())

    def anomalies(self):
        print("\n=== Ticks anormaux (latence > 10ms) ===")
        print("-" * 45)
        anomalies = self.df[self.df["latency_ms"] > 10]
        print("Nombre de ticks anormaux : " + str(len(anomalies)))
        print(anomalies[["tick","timestamp","latency_ms","event"]].to_string())

    def export_kpis(self, path="data/kpis.csv"):
        kpis = self.df.groupby("event")[["latency_ms","jitter_ms","loss_pct","cpu_pct","utilization_pct"]].agg(["mean","max","min"]).round(2)
        kpis.to_csv(path)
        print("\nKPIs exportes dans " + path)

if __name__ == "__main__":
    kpi = KPIAnalyzer()
    kpi.summary()
    kpi.by_event()
    kpi.anomalies()
    kpi.export_kpis()
