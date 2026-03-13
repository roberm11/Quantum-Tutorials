"""
References:

[1] J. R. Busemeyer and P. D. Bruza, Quantum Models of Cognition and Decision: Principles and Applications, 2nd ed.
    Cambridge: Cambridge University Press, 2024, doi: https://doi.org/10.1017/9781009205351
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.providers import Backend
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler

from qiskit.circuit.library import StatePreparation

def build_circuit() -> QuantumCircuit:
    
    NUM_QUBITS = 3
    NUM_CBITS = 3
    
    # Initialize the qubit and classical registers
    #
    # We need 3 qubits to represent the 5 bases of a qupentrit
    #     Qubit:         Qutrit:
    #      |000>    ->    |0>
    #      |001>    ->    |1>
    #      |010>    ->    |2>
    #      |011>    ->    |3>
    #      |100>    ->    |4>
    
    qupentrit_0 = QuantumRegister(NUM_QUBITS, "qupentrit_0")
    qupentrit_0_result = ClassicalRegister(NUM_CBITS, "result")
    
    qc = QuantumCircuit(qupentrit_0, qupentrit_0_result)

    # We want to initialize a five dimensional state vector \psi from 2.2.3 of [1]
    #     \psi = [ sqrt(0.05)
    #              sqrt(0.26)
    #              sqrt(0.40)
    #              sqrt(0.16)
    #              sqrt(0.13) ]
    
    statevector = [0.05**0.5, 0.26**0.5, 0.4**0.5, 0.16**0.5, 0.13**0.5, 0, 0, 0] # Note: we need the padding with 0s, since this vector represents 3 qubits
    
    # Append the circuit with the gate that prepares this state
    qc.append(StatePreparation(params=statevector, normalize=True), qupentrit_0)
    
    qc.measure(qupentrit_0, qupentrit_0_result)
    
    return qc
  
def run(qc: QuantumCircuit, backend: Backend, circuit_filename: str, output_filename: str):
    # Transpile the circuit
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)
    
    # Draw the transpiled circuit
    isa_circuit.draw("mpl", idle_wires=False, filename=circuit_filename)
    
    sampler = Sampler(backend)
    result = sampler.run([isa_circuit], shots=4096).result()
    
    import matplotlib.pyplot as plt
    from qiskit.visualization import plot_histogram

    counts = result[0].data["result"].get_counts()
    plot_histogram(counts)
    plt.savefig(output_filename)

if __name__ == "__main__":
    
    qc = build_circuit()
    
    from qiskit_aer import AerSimulator
    
    # Run a simulation without noise
    # NOTE: Even a noiseless simulation is influenced by chance.
    backend = AerSimulator(method="statevector")
    run(qc, backend, "5_statevector_qc.png", "5_statevector_results.png")
    
    
    # If you have access to a physical backend, then you can run a simulation using a noise model of that backend
    system = "ibm_rensselaer"
    
    from qiskit_ibm_runtime import QiskitRuntimeService
    
    # Run a simulation with a noise model derived from a real quantum system
    service = QiskitRuntimeService()
    backend = service.backend(system)
    backend = AerSimulator.from_backend(backend)
    run(qc, backend, "5_backend_sim_qc.png", "5_backend_sim_results.png")  
    
    
    # Run on a real system
    service = QiskitRuntimeService()
    backend = service.backend(system)
    run(qc, backend, "5_real_system_qc.png", "5_real_system_results.png")
    



#




