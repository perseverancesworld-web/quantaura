from .core.vm import run_demo as vm_demo
from .core.graph import run_graph_demo

def run_demo():
    print('Quantaura Runtime v0.9')
    vm_demo()
    run_graph_demo()
