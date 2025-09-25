# Keysight QCS API Mock & Quantum Simulator

**Um framework de simulação em Python que recria a arquitetura e a lógica da API do Quantum Control System (QCS) da Keysight para controle e simulação de experimentos quânticos.**

Este projeto foi desenvolvido como uma demonstração de domínio do ecossistema de software de controle quântico da Keysight, inspirado pelos excelentes datasheets e manuais técnicos fornecidos pela equipe da Keysight. O objetivo é simular o fluxo completo de um experimento quântico, desde a configuração do sistema até a execução da sequência de pulsos e a simulação da física do qubit, mimetizando a poderosa API do QCS.

## Visão Geral da Arquitetura

[cite\_start]Inspirado diretamente pela arquitetura modular do QCS e do software Labber[cite: 14886, 15078], este projeto foi dividido em três componentes principais:

1.  **Mock da API QCS (`qcs_api_mock.py`):**

      * Implementa as classes essenciais do sistema Keysight, como `System`, `Experiment`, `SequenceBuilder`, `TunableQubit` e `ReadoutResonator`.
      * O sistema é totalmente configurado via um arquivo `quantum_config.yaml`, que define os dispositivos quânticos, seus parâmetros e o mapeamento para os canais de controle, replicando a metodologia do QCS.
      * Inclui `PrintingBackend` e `PlottingBackend` funcionais que, assim como no software da Keysight, permitem inspecionar a sequência de pulsos de forma textual ou visual.

2.  **Simulador Físico (`physics_simulator.py`):**

      * Um backend customizado que utiliza a biblioteca **QuTiP** para simular a evolução temporal de um sistema quântico de dois níveis (qubit).
      * O Hamiltoniano do sistema é construído de forma dinâmica, utilizando o envelope de pulso gerado pelo `SequenceBuilder` como o termo de controle dependente do tempo (H\_drive).
      * Isso permite uma simulação realista de como os pulsos de controle, definidos na camada de abstração da API, afetam o estado quântico do qubit.

3.  **Experimento de Rabi (`rabi_simulation.py` e `experiments/rabi.py`):**

      * Implementa um experimento de Rabi completo como uma classe `RabiExperiment`, que herda da classe base `Experiment`, demonstrando a extensibilidade do framework.
      * O script `rabi_simulation.py` orquestra a simulação, varrendo a amplitude do pulso de Rabi e utilizando o `QuTiPSimulationBackend` para calcular a probabilidade de excitação do qubit em cada ponto.
      * Ao final, gera um gráfico da oscilação de Rabi, um resultado "canônico" em computação quântica, validando todo o fluxo do sistema.

## Como o Projeto Demonstra o Domínio das Tecnologias Keysight

Este simulador não é apenas uma implementação de um experimento quântico, mas uma recriação da **filosofia de design** do Quantum Control System da Keysight:

  * **Abstração do Hardware:** Assim como a API do QCS permite ao usuário programar em termos de qubits e ressonadores em vez de canais de AWG, este projeto utiliza classes como `TunableQubit` e `ReadoutResonator`, que são povoadas a partir de um arquivo de configuração YAML. A complexidade do controle é encapsulada, permitindo que o foco seja na física do experimento.

  * **Modularidade com Backends:** A utilização de `PrintingBackend` e `PlottingBackend` demonstra um claro entendimento da arquitetura de backends do QCS, que separa a definição da sequência da sua execução ou visualização. O `QuTiPSimulationBackend` é uma prova de conceito de como um backend customizado pode ser criado para interagir com diferentes hardwares ou, neste caso, com um simulador físico.

  * [cite\_start]**Fluxo de Trabalho de Experimentos:** A estrutura do código, com a classe `RabiExperiment` e o método `make_sequence`[cite: 4681, 14906], espelha exatamente o processo de programação de experimentos descrito na documentação do QCS. Isso mostra não apenas a capacidade de escrever código, mas de pensar e estruturar a automação de experimentos da maneira como a Keysight propõe.

## Como Executar

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio/fase1_qcs_simulador
    ```

2.  **Instale as dependências:**

    ```bash
    pip install numpy matplotlib pyyaml qutip
    ```

3.  **Execute a simulação:**

    ```bash
    python rabi_simulation.py
    ```

    Isso iniciará a varredura da amplitude do pulso, executará a simulação física para cada ponto e, ao final, exibirá o gráfico da oscilação de Rabi.

## Estrutura do Projeto

```
fase1_qcs_simulador/
│
├── config/
│   └── quantum_config.yaml     # Configuração do sistema quântico
│
├── experiments/
│   └── rabi.py                 # Definição do experimento de Rabi
│
├── utils/
│   └── converter.py            # Funções utilitárias (ex: conversão de pulso)
│
├── qcs_api_mock.py             # Mock da API do Quantum Control System
├── physics_simulator.py        # Backend de simulação com QuTiP
└── rabi_simulation.py          # Script principal para rodar a simulação
```

-----
