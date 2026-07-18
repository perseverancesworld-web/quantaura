import pytest
from quantaura.core.vm import QuantauraVM, Bytecode

def test_push_store():
    vm = QuantauraVM()
    bc = [Bytecode('PUSH', 42), Bytecode('STORE', 'x')]
    vm.execute(bc)
    assert vm.memory['x'] == 42

def test_lux_halt():
    vm = QuantauraVM()
    bc = [Bytecode('LUX'), Bytecode('HALT')]
    result = vm.execute(bc)
    assert 'HALT' in str(result)  # Simplified