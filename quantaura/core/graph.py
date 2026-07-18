import networkx as nx

class SymbolGraph:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_node(self, name, **attrs):
        self.G.add_node(name, **attrs)

    def add_edge(self, u, v, **attrs):
        self.G.add_edge(u, v, **attrs)

    def illuminate(self, node):
        print(f'LUX on {node}: relations highlighted')
        # Add edges in real impl

    def status(self):
        return {'nodes': len(self.G.nodes), 'edges': len(self.G.edges)}

def run_graph_demo():
    g = SymbolGraph()
    g.add_node('PATTERN')
    g.illuminate('PATTERN')
    print('Graph:', g.status())
