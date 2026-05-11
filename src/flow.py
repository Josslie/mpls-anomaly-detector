from dataclasses import dataclass
import random

DSCP_MAP = {
    "EF": {"priority": 1, "name": "URLLC - Expedited Forwarding"},
    "AF41": {"priority": 2, "name": "eMBB - Assured Forwarding"},
    "BE": {"priority": 3, "name": "Best Effort"},
}

@dataclass
class Flow:
    src: str
    dst: str
    dscp: str
    bandwidth: float
    vrf: str

    def priority(self):
        return DSCP_MAP.get(self.dscp, {}).get("priority", 99)

    def __str__(self):
        return self.src + " -> " + self.dst + " | DSCP=" + self.dscp + " | " + str(self.bandwidth) + "Mbps | VRF=" + self.vrf

class TrafficGenerator:
    def __init__(self, nodes):
        self.nodes = nodes
        self.flows = []

    def generate(self, count=10):
        dscp_choices = ["EF", "AF41", "BE"]
        vrf_map = {"EF": "URLLC", "AF41": "eMBB", "BE": "eMBB"}
        for _ in range(count):
            src = random.choice(self.nodes)
            dst = random.choice([n for n in self.nodes if n != src])
            dscp = random.choice(dscp_choices)
            bw = round(random.uniform(1, 100), 1)
            self.flows.append(Flow(src=src, dst=dst, dscp=dscp, bandwidth=bw, vrf=vrf_map[dscp]))
        self.flows.sort(key=lambda f: f.priority())

    def print_flows(self):
        print("=== Flux generes par priorite QoS ===")
        print("-" * 55)
        for f in self.flows:
            print("  " + str(f))

    def link_utilization(self):
        util = {}
        for f in self.flows:
            key = f.src + "->" + f.dst
            util[key] = util.get(key, 0) + f.bandwidth
        print("\n=== Utilisation des liens (Mbps) ===")
        print("-" * 55)
        for link, bw in sorted(util.items(), key=lambda x: -x[1]):
            print("  " + link + " : " + str(round(bw, 1)) + " Mbps")

if __name__ == "__main__":
    nodes = ["PE1", "PE2", "PE3", "P1", "P2"]
    gen = TrafficGenerator(nodes)
    gen.generate(15)
    gen.print_flows()
    gen.link_utilization()
