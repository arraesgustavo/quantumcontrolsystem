"""
Módulo Mock da API QCS da Keysight.

Este módulo fornece uma implementação simulada das classes e funcionalidades
essenciais da API Quantum Control System (QCS), permitindo o desenvolvimento
e teste de sequências de experimentos quânticos sem a necessidade da biblioteca
proprietária ou de uma licença.

Funcionalidades implementadas:
- Carregamento de configuração de sistema a partir de arquivos YAML.
- Classes base para Experimentos, Dispositivos Quânticos e Canais.
- Um SequenceBuilder para a criação de sequências de pulsos.
- Backends funcionais para impressão (console) e plotagem (Matplotlib).
"""

import yaml
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# --- Classes de Operação (Estruturas de Dados) ---
# Usamos dataclasses para armazenar as informações de cada operação de forma limpa.

@dataclass
class PulseOperation:
    channel_path: str
    duration: float = 40e-9 # Duração padrão do pulso
    amplitude: float = 0.0
    frequency: float = 0.0
    phase: float = 0.0
    shape: str = 'gaussian'

@dataclass
class DelayOperation:
    duration: float

@dataclass
class MeasureOperation:
    channel_path: str
    integration_time: float

# --- Classes de Canal ---
# Representam os canais de controle físicos (emulados). Seus métodos
# criam e retornam os objetos de Operação.

class BaseChannel:
    def __init__(self, path):
        self.path = path

class XYChannel(BaseChannel):
    def play_pulse(self, amplitude=0.5, duration=40e-9):
        print(f"DEBUG: Criando pulso no canal {self.path} com amplitude {amplitude}")
        return PulseOperation(channel_path=self.path, amplitude=amplitude, duration=duration)

class ZChannel(BaseChannel):
    def play_pulse(self, amplitude=0.1, duration=100e-9):
        # Pulsos Z geralmente têm formas e durações diferentes
        return PulseOperation(channel_path=self.path, amplitude=amplitude, duration=duration, shape='square')

class ReadoutChannel(BaseChannel):
    def __init__(self, path, integration_time):
        super().__init__(path)
        self.integration_time = integration_time
        
    def measure(self):
        return MeasureOperation(channel_path=self.path, integration_time=self.integration_time)

# --- Classes de Dispositivos Quânticos ---
# Essas classes são instanciadas com base no seu arquivo YAML.

class TunableQubit:
    def __init__(self, name, system_config):
        self.name = name
        self.parameters = system_config.get('parameters', {})
        
        # Mapeia os canais lógicos para as classes de canal
        channels = system_config.get('channels', {})
        self.xy = XYChannel(f"{name}.xy")
        self.z = ZChannel(f"{name}.z")
        self.readout = None # Será linkado pelo System

class ReadoutResonator:
    def __init__(self, name, system_config):
        self.name = name
        self.parameters = system_config.get('parameters', {})
        
        # Mapeia os canais lógicos para as classes de canal
        channels = system_config.get('channels', {})
        self.drive = XYChannel(f"{name}.drive")
        self.acquisition = None # Não realiza ação, apenas informativo
        
        # Cria o canal de medição com o tempo de integração do YAML
        self.measure_channel = ReadoutChannel(f"{name}.measure", self.parameters.get('integration_time', 1e-6))


# --- Classes Centrais da API ---

class System:
    # Carrega e gerencia todo o sistema definido no arquivo YAML.
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.quantum_devices = {}
        self._load_devices()

    def _load_devices(self):
        device_map = {
            'TunableQubit': TunableQubit,
            'ReadoutResonator': ReadoutResonator
        }
        for name, config in self.config.get('quantum_devices', {}).items():
            device_class = device_map.get(config['type'])
            if device_class:
                self.quantum_devices[name] = device_class(name, config)

        # Linkar readout dos qubits aos ressoadores
        for device in self.quantum_devices.values():
            if isinstance(device, TunableQubit):
                readout_name = self.config['quantum_devices'][device.name]['channels']['readout']
                if readout_name in self.quantum_devices:
                    resonator = self.quantum_devices[readout_name]
                    device.readout = resonator.measure_channel

    def get_instances(self, device_type):
        return [dev for dev in self.quantum_devices.values() if isinstance(dev, device_type)]

class SequenceBuilder:
    # Coleta operações em uma lista para serem executadas por um backend.
    def __init__(self):
        self.operations = []

    def append(self, operation):
        self.operations.append(operation)

    def delay(self, duration):
        self.operations.append(DelayOperation(duration=duration))

class Experiment:
    # Classe base para todos os experimentos. Carrega o sistema e executa sequências.
    def __init__(self, config_path):
        self.system = System(config_path)

    def make_sequence(self, the_sequencer: SequenceBuilder, **kwargs):
        # Método a ser implementado pela classe filha (ex: RabiExperiment).
        raise NotImplementedError("Você deve implementar o método 'make_sequence' no seu experimento.")

    def run(self, backend, **kwargs):
        builder = SequenceBuilder()
        # Chama a implementação do usuário para construir a sequência
        self.make_sequence(builder, **kwargs)
        # Passa a sequência construída para o backend executar
        return backend.execute(builder.operations)

# --- Backends ---

class BaseBackend:
    def execute(self, operations):
        raise NotImplementedError

class PrintingBackend(BaseBackend):
    # Um backend que imprime a sequência de operações no console.
    def execute(self, operations):
        print("\n--- [PrintingBackend] Sequência de Operações ---")
        for i, op in enumerate(operations):
            print(f"  Passo {i+1}: {op}")
        print("----------------------------------------------\n")

class PlottingBackend(BaseBackend):
    # Um backend que usa Matplotlib para visualizar as formas de onda da sequência.
    
    def _generate_waveform(self, op: PulseOperation, sample_rate=1e9):
        # Helper para criar a forma de onda numérica a partir da operação de pulso.
        n_points = int(op.duration * sample_rate)
        t = np.linspace(0, op.duration, n_points)
        
        if op.shape == 'gaussian':
            sigma = op.duration / 4
            envelope = op.amplitude * np.exp(-0.5 * ((t - op.duration / 2) / sigma)**2)
        elif op.shape == 'square':
            envelope = op.amplitude * np.ones(n_points)
        else:
            envelope = np.zeros(n_points)
            
        return t, envelope

    def execute(self, operations):
        print("\n--- [PlottingBackend] Gerando gráfico da sequência ---")
        
        fig, axs = plt.subplots(3, 1, sharex=True, figsize=(10, 6))
        fig.suptitle("Visualização da Sequência de Pulsos (Mock)")
        axs[0].set_ylabel("Controle XY (V)")
        axs[1].set_ylabel("Controle Z (V)")
        axs[2].set_ylabel("Leitura (V)")
        axs[2].set_xlabel("Tempo (s)")

        current_time = 0.0
        
        for op in operations:
            if isinstance(op, PulseOperation):
                t, envelope = self._generate_waveform(op)
                time_axis = t + current_time
                
                if 'xy' in op.channel_path:
                    axs[0].plot(time_axis, envelope, label=op.channel_path)
                elif 'z' in op.channel_path:
                    axs[1].plot(time_axis, envelope, label=op.channel_path)
                elif 'drive' in op.channel_path:
                    axs[2].plot(time_axis, envelope, label=op.channel_path)
                
                current_time += op.duration

            elif isinstance(op, DelayOperation):
                current_time += op.duration
            
            elif isinstance(op, MeasureOperation):
                # Emula um pulso de leitura simples
                readout_op = PulseOperation(
                    channel_path=op.channel_path,
                    duration=op.integration_time,
                    amplitude=0.2, # Amplitude fixa para visualização
                    shape='square'
                )
                t, envelope = self._generate_waveform(readout_op)
                time_axis = t + current_time
                axs[2].plot(time_axis, envelope, label=op.channel_path, linestyle='--', color='gray')
                current_time += op.integration_time

        for ax in axs:
            if ax.has_data():
                ax.legend(fontsize='small')
            ax.grid(True)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()