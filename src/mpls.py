from typing import Dict, List

class MPLSTable:
    def __init__(self):
        self.table = {}
        self.label_counter = 100

    def _new_label(self):
        self.label_counter += 10
        return self.label_counter

    def build_lsp(self, path, destination):
        labels = [self._new_label() for _ in path]
        for i, node in enumerate(path):
            if node not in self.table:
                self.table[node] = {}
            if i == 0:
                self.table[node][destination] = {'operation': 'PUSH', 'label_in': None, 'label_out': labels[i], 'next_hop': path[i+1]}
            elif i == len(path) - 1:
                self.table[node][destination] = {'operation': 'POP', 'label_in': labels[i-1], 'label_out': None, 'next_hop': destination}
            else:
                self.table[node][destination] = {'operation': 'SWAP', 'label_in': labels[i-1], 'label_out': labels[i], 'next_hop': path[i+1]}

    def forward_packet(self, source, destination):
        print('Trajet MPLS : ' + source + ' -> ' + destination)
        print('-' * 50)
        current = source
        label_stack = []
        while current != destination:
            if current not in self.table or destination not in self.table[current]:
                print('Pas de LSP sur ' + current)
                break
            entry = self.table[current][destination]
            op = entry['operation']
            next_hop = entry['next_hop']
            if op == 'PUSH':
                label_stack.append(entry['label_out'])
                print('  ' + current + ' | PUSH | label=' + str(entry['label_out']) + ' | -> ' + next_hop)
            elif op == 'SWAP':
                old = label_stack[-1]
                label_stack[-1] = entry['label_out']
                print('  ' + current + ' | SWAP | ' + str(old) + ' -> ' + str(entry['label_out']) + ' | -> ' + next_hop)
            elif op == 'POP':
                old = label_stack.pop()
                print('  ' + current + ' | POP | label=' + str(old) + ' retire | -> ' + next_hop)
            current = next_hop
        print('  ' + destination + ' | ARRIVE | paquet delivre')

    def print_table(self, node):
        print('Table MPLS - ' + node)
        print('-' * 55)
        for dest, entry in self.table.get(node, {}).items():
            lin = str(entry['label_in']) if entry['label_in'] else '-'
            lout = str(entry['label_out']) if entry['label_out'] else '-'
            print('  ' + dest + ' | ' + entry['operation'] + ' | IN:' + lin + ' | OUT:' + lout + ' | -> ' + entry['next_hop'])

if __name__ == '__main__':
    import sys
    sys.path.insert(0, 'src')
    from network import Network
    net = Network()
    net.add_node('PE1', role='PE')
    net.add_node('PE2', role='PE')
    net.add_node('PE3', role='PE')
    net.add_node('P1', role='P')
    net.add_node('P2', role='P')
    net.add_link('PE1', 'P1', bandwidth=10000, delay=1.0, cost=10)
    net.add_link('PE2', 'P1', bandwidth=10000, delay=1.5, cost=10)
    net.add_link('PE3', 'P2', bandwidth=10000, delay=1.0, cost=10)
    net.add_link('P1', 'P2', bandwidth=40000, delay=0.5, cost=5)
    net.add_link('PE1', 'P2', bandwidth=10000, delay=2.0, cost=20)
    net.compute_ospf()
    mpls = MPLSTable()
    mpls.build_lsp(['PE1', 'P1', 'P2', 'PE3'], 'PE3')
    mpls.build_lsp(['PE2', 'P1', 'PE1'], 'PE1')
    for node in ['PE1', 'P1', 'P2', 'PE3']:
        mpls.print_table(node)
    mpls.forward_packet('PE1', 'PE3')
    mpls.forward_packet('PE2', 'PE1')
