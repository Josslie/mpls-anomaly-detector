import networkx as nx
import matplotlib.pyplot as plt

class Network:
    def __init__(self):
        self.graph = nx.Graph()
        self.routing_tables = {}

    def add_node(self, name: str, role: str = "P"):
        self.graph.add_node(name, role=role)

    def add_link(self, a: str, b: str, bandwidth: int, delay: float, cost: int):
        self.graph.add_edge(a, b,
                            bandwidth=bandwidth,
                            delay=delay,
                            cost=cost)

    def compute_ospf(self):
        for node in self.graph.nodes:
            self.routing_tables[node] = {}
            for destination in self.graph.nodes:
                if node == destination:
                    continue
                try:
                    path = nx.shortest_path(
                        self.graph, node, destination, weight="cost"
                    )
                    cost = nx.shortest_path_length(
                        self.graph, node, destination, weight="cost"
                    )
                    next_hop = path[1] if len(path) > 1 else destination
                    self.routing_tables[node][destination] = {
                        "next_hop": next_hop,
                        "path": path,
                        "cost": cost
                    }
                except nx.NetworkXNoPath:
                    pass

    def print_routing_table(self, node: str):
        print(f"\nTable de routage OSPF — {node}")
        print("-" * 45)
        print(f"{'Destination':<12} {'Next Hop':<12} {'Cout':<8} {'Chemin'}")
        print("-" * 45)
        for dest, info in self.routing_tables[node].items():
            path_str = " -> ".join(info["path"])
            print(f"{dest:<12} {info['next_hop']:<12} {info['cost']:<8} {path_str}")

    def simulate_link_failure(self, a: str, b: str):
        print(f"\nCoupure du lien {a} <-> {b} !")
        self.graph.remove_edge(a, b)
        self.compute_ospf()
        print("Reconvergence OSPF effectuee.")

    def display(self):
        pos = nx.spring_layout(self.graph, seed=42)
        edge_labels = {
            (a, b): f"{d['delay']}ms / {d['bandwidth']}Mbps"
            for a, b, d in self.graph.edges(data=True)
        }
        colors = ["#185FA5" if self.graph.nodes[n]["role"] == "PE"
                  else "#888780" for n in self.graph.nodes]
        nx.draw(self.graph, pos, with_labels=True,
                node_color=colors, node_size=1200,
                font_color="white", font_weight="bold")
        nx.draw_networkx_edge_labels(self.graph, pos,
                                     edge_labels=edge_labels, font_size=7)
        plt.title("Topologie reseau IP/MPLS")
        plt.tight_layout()
        plt.savefig("reports/topologie.png", dpi=150)
        plt.show()


if __name__ == "__main__":
    net = Network()

    net.add_node("PE1", role="PE")
    net.add_node("PE2", role="PE")
    net.add_node("PE3", role="PE")
    net.add_node("P1",  role="P")
    net.add_node("P2",  role="P")

    net.add_link("PE1", "P1",  bandwidth=10000, delay=1.0, cost=10)
    net.add_link("PE2", "P1",  bandwidth=10000, delay=1.5, cost=10)
    net.add_link("PE3", "P2",  bandwidth=10000, delay=1.0, cost=10)
    net.add_link("P1",  "P2",  bandwidth=40000, delay=0.5, cost=5)
    net.add_link("PE1", "P2",  bandwidth=10000, delay=2.0, cost=20)

    # Calcul OSPF
    net.compute_ospf()

    # Afficher les tables de routage
    for node in ["PE1", "PE2", "P1"]:
        net.print_routing_table(node)

    # Simuler une coupure de lien
    print("\n--- Simulation coupure lien P1 <-> P2 ---")
    net.simulate_link_failure("P1", "P2")
    net.print_routing_table("PE1")

    # Afficher la topologie
    net.display()
