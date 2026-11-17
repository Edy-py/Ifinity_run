# Corrida da Boa Alimentação 🏃‍♂️🍏🍔

**Corrida da Boa Alimentação** é um jogo 2D no estilo *Endless Runner* desenvolvido em Python com a biblioteca `pygame-ce`. O objetivo do jogo é promover a conscientização sobre hábitos alimentares de forma divertida e dinâmica.

Este projeto foi desenvolvido como parte de uma entrega acadêmica focada em boas práticas de engenharia de software, modularização, controle de versão (Git) e entrega contínua através de *sprints*.

## 🎮 Sobre o Jogo

Você controla um corredor em uma movimentada avenida de 3 faixas. Seu objetivo é manter a saúde em dia enquanto corre!
* **Colete alimentos saudáveis** (maçãs, brócolis, etc.) para ganhar pontos e reduzir seu peso.
* **Desvie de alimentos ultraprocessados** (hambúrgueres, donuts, etc.) que aumentam o seu peso rapidamente.
* Fique de olho no **Indicador de Peso** (HUD)! Se o marcador chegar à zona vermelha (excesso de peso máximo), é *Game Over*.
* A dificuldade aumenta progressivamente conforme você sobrevive.

## ⚙️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Motor Gráfico:** pygame-ce (Community Edition)
* **Empacotamento:** PyInstaller (para geração do executável `.exe`)
* **Arquitetura:** Orientação a Objetos, com separação de responsabilidades (Lógica, Entidades, UI, Estados).

## 📂 Estrutura do Projeto

```text
corrida_boa_alimentacao/
├── assets/                  # Arquivos de mídia (imagens, sons, fontes)
│   └── images/              # Sprites do jogador e comidas
├── src/                     # Código-fonte principal
│   ├── main.py              # Ponto de entrada e loop do jogo
│   ├── config.py            # Variáveis globais e configurações
│   ├── game_state.py        # Gerenciamento de estados e regras 
│   ├── entities/            # Classes dos objetos do jogo
│   │   ├── player.py        
│   │   ├── item.py          
│   │   └── spawner.py       
│   └── ui/                  # Interface de usuário
│       └── hud.py           
├── .gitignore               # Arquivos ignorados pelo Git
├── requirements.txt         # Dependências do projeto
└── README.md                # Este documento
```

## 🚀 Como Executar o Jogo

Existem duas formas de jogar: rodando através do código-fonte ou utilizando o executável final (Build).

### Opção 1: Código-Fonte (Recomendado para Desenvolvedores)

1. Certifique-se de ter o [Python](https://www.python.org/) instalado na sua máquina.
2. Clone este repositório ou baixe os arquivos.
3. Abra o terminal na pasta raiz do projeto.
4. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows (PowerShell):
   .\venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```
5. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
6. Execute o jogo:
   ```bash
   python src/main.py
   ```

### Opção 2: Executável (Windows)

1. Baixe o arquivo `.zip` da entrega final.
2. Extraia a pasta `CorridaBoaAlimentacao` em seu computador.
3. Certifique-se de que a pasta `assets` está no mesmo diretório do arquivo `.exe`.
4. Dê um duplo clique em `CorridaBoaAlimentacao.exe`.
*Nota: Caso o Windows SmartScreen bloqueie o jogo, clique em "Mais informações" e depois em "Executar mesmo assim", ou desative temporariamente o "Controle Inteligente de Aplicativos".*

## 🕹️ Controles

* **Seta para a Esquerda / Tecla A:** Move o personagem para a faixa da esquerda.
* **Seta para a Direita / Tecla D:** Move o personagem para a faixa da direita.
* **Barra de Espaço:** Inicia o jogo no Menu Principal / Reinicia a partida na tela de Game Over.
* **ESC:** Fecha o jogo.

## 📝 Notas Acadêmicas (Sprints)

O desenvolvimento seguiu uma metodologia ágil dividida em 3 entregas:
* **Sprint 1:** Protótipo jogável com movimentação Top-Down, faixas e colisões.
* **Sprint 2:** Implementação do sistema de pontuação, gerenciamento de peso progressivo e Game Over.
* **Sprint 3:** Polimento visual, Menu Inicial, substituição de placeholders por sprites gerados e compilação de Build (`.exe`).