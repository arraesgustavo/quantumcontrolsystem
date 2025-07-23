import numpy as np
from qcs_api_mock import PulseOperation

def pulse_to_waveform(op: PulseOperation, sample_rate: float = 1e9) -> tuple[np.ndarray, np.ndarray]:
    
    #Converte um objeto PulseOperation em uma forma de onda numérica (envelope).

    #Args:
    #    op (PulseOperation): O objeto de pulso da sequência.
    #    sample_rate (float): A taxa de amostragem para a geração da forma de onda (padrão: 1 GSa/s).

    #Returns:
    #    tuple[np.ndarray, np.ndarray]: Uma tupla contendo o array de tempo e o array de amplitude (envelope).
    
    n_points = max(int(op.duration * sample_rate), 2)  # Evita erros com <2 pontos
    t = np.linspace(0, op.duration, n_points, endpoint=False)

    if op.shape == 'gaussian':
        sigma = op.duration / 4
        center = op.duration / 2
        envelope = op.amplitude * np.exp(-0.5 * ((t - center) / sigma)**2)
    elif op.shape == 'square':
        envelope = op.amplitude * np.ones(n_points)
    else:
        envelope = np.zeros(n_points)  # fallback

    return t, envelope