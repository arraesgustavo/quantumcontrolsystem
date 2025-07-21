from qcs_api_mock import Experiment, SequenceBuilder, TunableQubit

class RabiExperiment(Experiment):
    
    #Define um experimento de Rabi.
    #Esta classe irá gerar uma sequência que consiste em um pulso XY
    #com amplitude variável, seguido por uma medição.
    
    def __init__(self):
        # Esta parte permanece a mesma. O construtor do nosso mock
        # foi projetado para aceitar este caminho.
        super().__init__('config/quantum_config.yaml')

    def make_sequence(
        self,
        the_sequencer: SequenceBuilder, # O tipo agora aponta para nossa classe mock
        amplitude: float
    ):
        
        #Gera a sequência de pulsos para um único ponto de um sweep de Rabi.
        
        qubit = self.system.get_instances(TunableQubit)[0] # [cite: 4680]

        # Nenhuma alteração necessária aqui. A lógica está perfeita.
        # Adiciona o pulso de controle (Rabi) à sequência.
        the_sequencer.append(qubit.xy.play_pulse(amplitude=amplitude)) # [cite: 4681]

        # Adiciona o pulso de medição no final da sequência.
        the_sequencer.append(qubit.readout.measure())