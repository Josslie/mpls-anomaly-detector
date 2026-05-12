import sys
sys.path.insert(0, "src")
from simulator import Simulator
import pandas as pd

class DatasetBuilder:
    def __init__(self):
        self.sim = Simulator()

    def build(self, ticks=50000):
        print("Generation du dataset " + str(ticks) + " ticks...")
        self.sim.records = []
        import random
        from datetime import timedelta
        from flow import TrafficGenerator
        nodes = ["PE1","PE2","PE3","P1","P2"]
        gen = TrafficGenerator(nodes)
        events_schedule = {}
        for t in range(0, ticks, 500):
            events_schedule[t+100] = "link_failure"
            events_schedule[t+250] = "traffic_spike"
            events_schedule[t+400] = "link_degradation"
        for tick in range(ticks):
            gen.flows = []
            gen.generate(random.randint(5, 20))
            event = events_schedule.get(tick, "normal")
            latency, jitter, utilization, loss, cpu = self.sim._compute_metrics(gen.flows, event)
            timestamp = self.sim.start_time + timedelta(seconds=tick)
            self.sim.records.append({"tick": tick, "timestamp": str(timestamp), "latency_ms": latency, "jitter_ms": jitter, "utilization_pct": utilization, "loss_pct": loss, "cpu_pct": cpu, "active_flows": len(gen.flows), "event": event})
            if tick % 5000 == 0:
                print("  " + str(tick) + "/" + str(ticks) + " ticks...")
        df = pd.DataFrame(self.sim.records)
        df.to_csv("data/dataset.csv", index=False)
        print("Dataset sauvegarde : data/dataset.csv")
        print("Taille : " + str(len(df)) + " lignes")
        print("Evenements : " + str(df["event"].value_counts().to_dict()))
        return df

if __name__ == "__main__":
    builder = DatasetBuilder()
    df = builder.build(50000)
