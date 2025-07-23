# Simulador base:
"""
import numpy as np
from experiments.rabi import RabiExperiment

# Importa os backends do nosso arquivo mock
from qcs_api_mock import PlottingBackend, PrintingBackend

# 1. Instancia o seu experimento.
exp = RabiExperiment()

# 2. Define o parâmetro que será varrido.
amplitudes = np.linspace(0, 1.0, 3) # Vamos usar 3 pontos para um teste rápido

print("--- Iniciando Simulação de Sequência de Rabi com API Mock ---")

# 3. Itera sobre os parâmetros e executa o experimento para cada um.
for i, amp in enumerate(amplitudes):
    print(f"\n--- Ponto {i+1}/{len(amplitudes)}: Amplitude = {amp:.2f} ---")
    
    # Executa com o PrintingBackend para ver a lista de instruções.
    exp.run(backend=PrintingBackend(), amplitude=amp)
    
    # Executa com o PlottingBackend para visualizar a forma de onda.
    exp.run(backend=PlottingBackend(), amplitude=amp)

print("\n--- Simulação de Sequência Concluída ---")
"""
import numpy as np
import matplotlib.pyplot as plt

# Classes do projeto
from experiments.rabi import RabiExperiment
from qcs_api_mock import BaseBackend, PulseOperation, TunableQubit
from utils.converter import pulse_to_waveform
from physics_simulator import simulate_qubit_evolution

class QuTiPSimulationBackend(BaseBackend):

    # Um backend customizado que executa a simulação física com QuTiP.
    # Ele conecta a sequência de pulsos gerada pela QCS com o simulador.

    def __init__(self, experiment_instance):
        self.experiment = experiment_instance

    def execute(self, operations):
        control_pulse_op = next((op for op in operations if isinstance(op, PulseOperation) and 'xy' in op.channel_path), None)
        
        if control_pulse_op is None:
            return 0.0 

        # Conversor
        t_list, envelope = pulse_to_waveform(control_pulse_op)
        
        # Parametros
        qubit = self.experiment.system.get_instances(TunableQubit)[0]
        qubit_params = qubit.parameters

        final_prob = simulate_qubit_evolution(envelope, t_list, qubit_params)
        
        return final_prob

if __name__ == "__main__":
    exp = RabiExperiment()
    sim_backend = QuTiPSimulationBackend(exp)

    amplitudes = np.linspace(0, 1.5, 101) 
    results = []

    print("--- Iniciando Simulação de Rabi com Integração QuTiP ---")

    for i, amp in enumerate(amplitudes):
        prob_1 = exp.run(backend=sim_backend, amplitude=amp)
        results.append(prob_1)
        print(f"Ponto {i+1}/{len(amplitudes)}: Amp={amp:.3f} -> P(|1>)={prob_1:.4f}")

    print("--- Simulação Concluída ---")

    plt.figure(figsize=(10, 6))
    plt.plot(amplitudes, results, 'o-', label='Resultado da Simulação QuTiP')
    plt.title("Oscilação de Rabi Simulada")
    plt.xlabel("Amplitude do Pulso (V)")
    plt.ylabel("Probabilidade do Estado |1⟩")
    plt.grid(True)
    plt.legend()
    plt.show()