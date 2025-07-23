import qutip as qt
import numpy as np

def simulate_qubit_evolution(
    pulse_envelope: np.ndarray, 
    t_list: np.ndarray, 
    qubit_params: dict
) -> float:
    
    #Simula a evolução de um qubit sob a influência de um pulso de controle usando QuTiP.

    #Args:
    #    pulse_envelope (np.ndarray): O envelope de amplitude do pulso de controle.
    #    t_list (np.ndarray): O array de tempo correspondente ao pulso.
    #    qubit_params (dict): Um dicionário com os parâmetros do qubit (ex: 'frequency').

    #Returns:
    #    float: A probabilidade final de encontrar o qubit no estado |1>.

    # Parâmetros
    VOLT_TO_RABI_HERTZ = 25e6
    qubit_freq_from_params = qubit_params.get('frequency', 5.0e9) # Pega do YAML, com um padrão
    
    if isinstance(qubit_freq_from_params, (list, tuple)):
        qubit_freq = float(qubit_freq_from_params[0])
    else:
        qubit_freq = float(qubit_freq_from_params)

    # Hamiltoniano: H = w0/2 * Z + Omega * cos(w_drive * t) * X

    # Definir o hamiltoniano na rotating frame

    # H_drive: O operador de controle (como o pulso afeta o qubit)
    H_drive = 0.5 * qt.sigmax() # Um drive no eixo X

    
    # Amplitude do envelope precisa ser convertida para frequencia angular
    rabi_freq_envelope = pulse_envelope * VOLT_TO_RABI_HERTZ
    angular_freq_envelope = 2 * np.pi * rabi_freq_envelope

    if len(t_list) != len(angular_freq_envelope):
        raise ValueError("t_list e envelope precisam ter o mesmo tamanho")

    # Montar o vetor [ [t0, a0], [t1, a1], ..., [tn, an] ]
    time_array = np.column_stack((t_list, angular_freq_envelope))

    # Parte tempo-dependente
    # H0 = 0
    def envelope_func(t, args=None):
        return np.interp(t, t_list, angular_freq_envelope)

    H = [[H_drive, envelope_func]]

    psi0 = qt.basis(2, 0)  # Qubit começa no estado |0> (estado fundamental)
    
    # Operador para medir a população no estado |1> (excitado)
    projection_operator_1 = qt.ket2dm(qt.basis(2, 1))

    print("Pulso shape:", pulse_envelope.shape)
    print("t_list shape:", t_list.shape)
    print("Hamil. dependente do tempo shape:", time_array.shape)
    print("Primeiros 5 valores do pulso:", angular_freq_envelope[:5])

    # Solução de Schrödinger
    result = qt.mesolve(H, psi0, t_list, c_ops=[], e_ops=[projection_operator_1])

    # Extrair o resultado final
    # A probabilidade de estar no estado |1> é o valor de expectação final do nosso operador.
    final_prob_1 = result.expect[0][-1]
    
    return final_prob_1