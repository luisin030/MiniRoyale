# MiniRoyale

Protótipo educacional inspirado na estrutura de jogos de arena com cartas em tempo real.

> Objetivo: aprender Unity + C# construindo uma versão simples com arena, torres, elixir, cartas e tropas.

## MVP 0.1

- Arena 2D
- 1 torre de cada lado
- Elixir de 0 a 10
- Carta de Cavaleiro
- Clique para invocar tropa
- Tropa procura o alvo mais próximo
- Movimento automático
- Ataque e dano
- Destruição da torre
- Reinício da partida

## Estrutura

```text
Assets/
  Scripts/
    Core/
      GameManager.cs
      Team.cs
    Cards/
      CardData.cs
      CardSpawner.cs
      ElixirSystem.cs
    Units/
      Unit.cs
      UnitMovement.cs
      UnitCombat.cs
    Towers/
      Tower.cs
    UI/
      ElixirUI.cs
```

## Como começar no Unity

1. Crie um projeto **2D** vazio no Unity.
2. Copie a pasta `Assets/Scripts` deste repositório para a pasta `Assets` do projeto.
3. Crie uma cena chamada `Arena`.
4. Adicione:
   - uma torre azul;
   - uma torre vermelha;
   - um objeto `GameManager`;
   - um objeto `ElixirSystem`;
   - um Canvas com texto do elixir;
   - um botão/carta para o Cavaleiro.
5. Crie um prefab simples para a tropa usando um Sprite (por enquanto pode ser um quadrado).
6. Adicione `Collider2D` aos objetos que participam do combate.
7. Configure os campos públicos dos scripts pelo Inspector.

## Primeira meta

A primeira versão deve permitir:

1. selecionar a carta;
2. clicar na metade do jogador;
3. gastar elixir;
4. criar a tropa;
5. fazer a tropa andar até a torre inimiga;
6. atacar a torre;
7. vencer ao destruir a torre.

## Próximas versões

### 0.2
- quatro cartas;
- barra de vida;
- animações;
- cronômetro.

### 0.3
- duas torres laterais + torre principal;
- tropas contra tropas;
- ponte e caminhos.

### 0.4
- IA adversária;
- deck de 8 cartas;
- mão com 4 cartas.

### 0.5
- sons;
- partículas;
- menu;
- tela de vitória.

### Futuro
- multiplayer autoritativo;
- matchmaking;
- contas;
- ranking.

## Aviso

Este projeto é apenas inspirado em mecânicas gerais de jogos de arena com cartas. Use nomes, artes, sons, personagens e identidade visual próprios.
