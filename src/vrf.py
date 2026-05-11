from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Route:
    prefix: str
    next_hop: str
    metric: int = 0
    rd: str = ""

class VRF:
    def __init__(self, name: str, rd: str, rt_export: str, rt_import: str):
        self.name = name
        self.rd = rd
        self.rt_export = rt_export
        self.rt_import = rt_import
        self.routes: Dict[str, Route] = {}

    def add_route(self, prefix: str, next_hop: str, metric: int = 0):
        self.routes[prefix] = Route(prefix=prefix, next_hop=next_hop, metric=metric, rd=self.rd)

    def get_route(self, prefix: str):
        return self.routes.get(prefix, None)

    def print_table(self):
        print("VRF: " + self.name + " | RD: " + self.rd + " | RT-export: " + self.rt_export + " | RT-import: " + self.rt_import)
        print("-" * 55)
        for prefix, route in self.routes.items():
            print("  " + prefix + " | next_hop=" + route.next_hop + " | metric=" + str(route.metric))

class VRFManager:
    def __init__(self):
        self.vrfs: Dict[str, VRF] = {}
        self.vpn_table: Dict[str, List[Route]] = {}

    def add_vrf(self, name: str, rd: str, rt_export: str, rt_import: str):
        self.vrfs[name] = VRF(name, rd, rt_export, rt_import)

    def add_route(self, vrf_name: str, prefix: str, next_hop: str, metric: int = 0):
        if vrf_name in self.vrfs:
            self.vrfs[vrf_name].add_route(prefix, next_hop, metric)

    def exchange_routes(self):
        for vrf in self.vrfs.values():
            for prefix, route in vrf.routes.items():
                vpn_key = vrf.rd + ":" + prefix
                if vpn_key not in self.vpn_table:
                    self.vpn_table[vpn_key] = []
                self.vpn_table[vpn_key].append(route)
        for vrf in self.vrfs.values():
            for other_vrf in self.vrfs.values():
                if other_vrf.name == vrf.name:
                    continue
                if other_vrf.rt_export == vrf.rt_import:
                    for prefix, route in other_vrf.routes.items():
                        if prefix not in vrf.routes:
                            vrf.add_route(prefix, route.next_hop, route.metric)

    def check_isolation(self, vrf1: str, vrf2: str):
        routes1 = set(self.vrfs[vrf1].routes.keys())
        routes2 = set(self.vrfs[vrf2].routes.keys())
        common = routes1.intersection(routes2)
        if common:
            print("Routes communes (import autorise): " + str(common))
        else:
            print("Isolation OK : " + vrf1 + " et " + vrf2 + " ne partagent pas de routes")

    def print_all(self):
        for vrf in self.vrfs.values():
            vrf.print_table()
            print()

if __name__ == "__main__":
    mgr = VRFManager()
    mgr.add_vrf("eMBB",  rd="65000:1", rt_export="65000:1", rt_import="65000:1")
    mgr.add_vrf("URLLC", rd="65000:2", rt_export="65000:2", rt_import="65000:2")
    mgr.add_route("eMBB",  "10.1.0.0/24", "PE1", 10)
    mgr.add_route("eMBB",  "10.1.1.0/24", "PE2", 10)
    mgr.add_route("URLLC", "10.2.0.0/24", "PE1", 10)
    mgr.add_route("URLLC", "10.2.1.0/24", "PE3", 10)
    print("=== Tables VRF avant echange ===")
    mgr.print_all()
    mgr.exchange_routes()
    print("=== Tables VRF apres echange ===")
    mgr.print_all()
    print("=== Verification isolation ===")
    mgr.check_isolation("eMBB", "URLLC")
