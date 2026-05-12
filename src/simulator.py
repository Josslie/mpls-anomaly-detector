import random
import pandas as pd
import sys
sys.path.insert(0, "src")
from network import Network
from flow import TrafficGenerator
from datetime import datetime, timedelta

class Simulator:
    def __init__(self):
        self.net = Network()
        self.net.add_node("PE1", role="PE")
        self.net.add_node("PE2", role="PE")
        self.net.add_node("PE3", role="PE")
        self.net.add_node("P1", role="P")
        self.net.add_node("P2", role="P")
        self.net.add_link("PE1", "P1", bandwidth=10000, delay=1.0, cost=10)
        self.net.add_link("PE2", "P1", bandwidth=10000, delay=1.5, cost=10)
        self.net.add_link("PE3", "P2", bandwidth=10000, delay=1.0, cost=10)
        self.net.add_link("P1", "P2", bandwidth=40000, delay=0.5, cost=5)
        self.net.add_link("PE1", "P2", bandwidth=10000, delay=2.0, cost=20)
        self.net.compute_ospf()
        self.records = []
        self.nodes = ["PE1", "PE2", "PE3", "P1", "P2"]
        self.start_time = datetime(2026, 5, 12, 8, 0, 0)

    def _inject_event(self, tick):
        event = "normal"
        if tick == 200:
            event = "link_failure"
        elif tick == 400:
            event = "traffic_spike"
        elif tick == 600:
            event = "link_degradation"
        return event

    def _compute_metrics(self, flows, event):
        base_latency = random.uniform(1.0, 5.0)
        if event == "link_failure":
            base_latency += random.uniform(10, 30)
        elif event == "traffic_spike":
            base_latency += random.uniform(5, 15)
        elif event == "link_degradation":
            base_latency += random.uniform(2, 8)
        jitter = random.uniform(0.1, 2.0)
        total_bw = sum(f.bandwidth for f in flows)
        utilization = min(total_bw / 10000 * 100, 100)
        loss = 0.0
        if utilization > 90:
            loss = random.uniform(0.1, 5.0)
        elif event == "link_failure":
            loss = random.uniform(5, 20)
        cpu = random.uniform(10, 40) + (20 if event != "normal" else 0)
        return round(base_latency, 2), round(jitter, 2), round(utilization, 2), round(loss, 2), round(cpu, 2)

    def run(self, ticks=1000):
        print("Simulation en cours...")
        gen = TrafficGenerator(self.nodes)
        for tick in range(ticks):
            gen.flows = []
            gen.generate(random.randint(5, 20))
            event = self._inject_event(tick)
            latency, jitter, utilization, loss, cpu = self._compute_metrics(gen.flows, event)
            timestamp = self.start_time + timedelta(seconds=tick)
            self.records.append({"tick": tick, "timestamp": str(timestamp), "latency_ms": latency, "jitter_ms": jitter, "utilization_pct": utilization, "loss_pct": loss, "cpu_pct": cpu, "active_flows": len(gen.flows), "event": event})
            if tick % 100 == 0:
                print("  tick " + str(tick) + "/" + str(ticks) + " | latence=" + str(latency) + "ms | event=" + event)
        print("Simulation terminee - " + str(ticks) + " ticks")
        return pd.DataFrame(self.records)

    def save(self, df, path="data/metrics.csv"):
        df.to_csv(path, index=False)
        print("Donnees sauvegardees dans " + path)

if __name__ == "__main__":
    sim = Simulator()
    df = sim.run(1000)
    sim.save(df)
    print("\nApercu des donnees:")
    print(df.head(10).to_string())
    print("\nStatistiques:")
    print(df.describe().to_string())
