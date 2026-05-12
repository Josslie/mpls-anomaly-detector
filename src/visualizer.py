import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.insert(0, "src")

class Visualizer:
    def __init__(self, csv_path="data/metrics.csv"):
        self.df = pd.read_csv(csv_path)
        self.events = self.df[self.df["event"] != "normal"]

    def plot_latency(self):
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(self.df["tick"], self.df["latency_ms"], color="#185FA5", linewidth=0.8, label="Latence ms")
        for _, row in self.events.iterrows():
            color = "#D85A30" if row["event"] == "link_failure" else "#EF9F27" if row["event"] == "traffic_spike" else "#534AB7"
            ax.axvline(x=row["tick"], color=color, linestyle="--", linewidth=1.5, alpha=0.8)
            ax.text(row["tick"]+5, ax.get_ylim()[1]*0.85, row["event"], fontsize=7, color=color, rotation=90)
        ax.set_title("Evolution de la latence reseau dans le temps")
        ax.set_xlabel("Tick")
        ax.set_ylabel("Latence (ms)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("reports/latency.png", dpi=150)
        plt.close()
        print("Graphique latence sauvegarde")

    def plot_utilization(self):
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.fill_between(self.df["tick"], self.df["utilization_pct"], color="#1D9E75", alpha=0.6, label="Utilisation %")
        ax.axhline(y=90, color="#D85A30", linestyle="--", linewidth=1, label="Seuil critique 90%")
        ax.set_title("Utilisation des liens dans le temps")
        ax.set_xlabel("Tick")
        ax.set_ylabel("Utilisation (%)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("reports/utilization.png", dpi=150)
        plt.close()
        print("Graphique utilisation sauvegarde")

    def plot_distributions(self):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        normal = self.df[self.df["event"] == "normal"]["latency_ms"]
        anomaly = self.df[self.df["event"] != "normal"]["latency_ms"]
        axes[0].hist(normal, bins=30, color="#185FA5", alpha=0.7, label="Normal")
        axes[0].hist(anomaly, bins=10, color="#D85A30", alpha=0.7, label="Anomalie")
        axes[0].set_title("Distribution des latences")
        axes[0].set_xlabel("Latence (ms)")
        axes[0].legend()
        axes[1].bar(["Normal", "link_failure", "traffic_spike", "link_degradation"],
            [len(self.df[self.df["event"] == "normal"]), len(self.df[self.df["event"] == "link_failure"]),
             len(self.df[self.df["event"] == "traffic_spike"]), len(self.df[self.df["event"] == "link_degradation"])],
            color=["#185FA5", "#D85A30", "#EF9F27", "#534AB7"])
        axes[1].set_title("Nombre de ticks par evenement")
        axes[1].set_ylabel("Nombre de ticks")
        plt.tight_layout()
        plt.savefig("reports/distributions.png", dpi=150)
        plt.close()
        print("Graphique distributions sauvegarde")

    def plot_all(self):
        self.plot_latency()
        self.plot_utilization()
        self.plot_distributions()
        print("Tous les graphiques sont dans reports/")

if __name__ == "__main__":
    viz = Visualizer()
    viz.plot_all()
