
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.providers import Backend
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler

from qiskit.circuit.library.data_preparation import UniformSuperpositionGate

def build_circuit() -> QuantumCircuit:
    
    NUM_QUBITS = 2
    NUM_CBITS = 2
    
    # Initialize the qubit and classical registers
    #
    # We need 2 qubits to represent the 3 bases of a qutrit
    #     Qubit:        Qutrit:
    #      |00>    ->    |A>
    #      |01>    ->    |B>
    #      |10>    ->    |C>
    
    qutrit_0 = QuantumRegister(NUM_QUBITS, "qutrit_0")
    qutrit_0_result = ClassicalRegister(NUM_CBITS, "result")
    
    qc = QuantumCircuit(qutrit_0, qutrit_0_result)

    # We will need to initialize this into a uniform superposition over the qutrit states.
    qc.append(UniformSuperpositionGate(3, 2), qutrit_0)
    
    qc.measure(qutrit_0, qutrit_0_result)
    
    return qc
  
def run(qc: QuantumCircuit, backend: Backend, circuit_filename: str, output_filename: str):
    # Transpile the circuit
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)
    
    # Draw the transpiled circuit
    isa_circuit.draw("mpl", idle_wires=False, filename=circuit_filename)
    
    sampler = Sampler(backend)
    result = sampler.run([isa_circuit], shots=1024).result()
    
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
    run(qc, backend, "statevector_qc.png", "statevector_results.png")
    
    
    # If you have access to a physical backend, then you can run a simulation using a noise model of that backend
    system = "ibm_rensselaer"
    
    from qiskit_ibm_runtime import QiskitRuntimeService
    
    # Run a simulation with a noise model derived from a real quantum system
    service = QiskitRuntimeService()
    backend = service.backend(system)
    backend = AerSimulator.from_backend(backend)
    run(qc, backend, "backend_sim_qc.png", "backend_sim_results.png")  
    
    '''
    # Run on a real system
    service = QiskitRuntimeService()
    backend = service.backend(system)
    run(qc, backend, "real_system_qc.png", "real_system_results.png")
    '''


#




