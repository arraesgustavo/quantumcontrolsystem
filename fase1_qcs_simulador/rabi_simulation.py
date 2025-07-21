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