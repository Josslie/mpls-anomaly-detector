import networkx as nx
import matplotlib.pyplot as plt

class Network:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, name: str, role: str = "P"):
        self.graph.add_node(name, role=role)

    def add_link(self, a: str, b: str, bandwidth: int, delay: float, cost: int):
        self.graph.add_edge(a, b,
                            bandwidth=bandwidth,
                            delay=delay,
                            cost=cost)

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
    net.display()
    print("Noeuds :", list(net.graph.nodes(data=True)))
    print("Liens  :", list(net.graph.edges(data=True)))