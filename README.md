# ELEVADOR_POO — Algoritmo do Elevador

**Instituição:** Senac  
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)  
**Disciplina:** Programação Orientada a Objetos (POO)  
**Aula:** 12 — Algoritmo do Elevador  
**Data:** 22 de outubro de 2026  
**Linguagem:** Python

## 1. Objetivo

Simular, em Python, o atendimento de chamadas de um elevador. O exercício aplica os fundamentos de Programação Orientada a Objetos para representar o elevador, armazenar suas solicitações e controlar os deslocamentos entre andares.

O programa foi desenvolvido de maneira incremental: primeiro a classe e os atributos, depois o registro de chamadas, a movimentação, as paradas intermediárias, a remoção de solicitações atendidas e, por fim, a escolha da ordem de atendimento.

## 2. Funcionalidades implementadas

- Criar um elevador inicialmente no andar `0`, com direção `parado` e lista de solicitações vazia.
- Registrar chamadas por andar, evitando duplicatas.
- Subir ou descer um andar por vez, exibindo o movimento no terminal.
- Reconhecer e anunciar paradas em andares solicitados durante o percurso.
- Remover da lista cada solicitação atendida.
- Escolher a chamada inicialmente mais próxima; em caso de empate na distância, priorizar o andar superior.
- Após escolher um sentido, percorrer até a solicitação mais distante naquele sentido, atendendo as chamadas intermediárias; inverter a direção quando necessário.
- Atender uma chamada no andar atual sem deslocamento.
- Encerrar com a direção `parado` quando o deslocamento termina.

## 3. Estrutura do programa

O arquivo principal é `elevador.py`, que contém a classe `Elevador` e uma demonstração de uso executada somente quando o arquivo é iniciado diretamente.

### Classe `Elevador`

A classe representa o elevador como um objeto que reúne **estado** (atributos) e **comportamento** (métodos).

| Elemento | Papel no programa |
| --- | --- |
| `__init__(self)` | Inicializa os atributos de cada novo elevador. |
| `self.andar_atual` | Guarda o andar em que o elevador está; começa em `0`. |
| `self.direcao` | Guarda o estado do movimento: `parado`, `subindo` ou `descendo`. |
| `self.solicitacoes` | Lista dos andares solicitados e ainda não atendidos. |
| `chamar(self, andar)` | Adiciona o andar à lista, se ele ainda não estiver nela. |
| `mover_para(self, andar_destino)` | Move o elevador andar a andar, anuncia as paradas e remove solicitações atendidas. |
| `atender_solicitacoes(self)` | Decide a sequência de atendimento e chama `mover_para()` para executar os deslocamentos. |

### Como a escolha do trajeto funciona

O método `atender_solicitacoes()` verifica inicialmente se há chamada para o andar atual e, nesse caso, a atende sem mover o elevador.

Enquanto houver solicitações pendentes:

1. Identifica a solicitação com a menor distância absoluta em relação ao andar atual, usando `min()` e uma função `lambda`.
2. Em caso de empate entre distâncias, escolhe o andar **mais alto**: isso favorece a subida quando há uma opção acima e outra abaixo à mesma distância.
3. Se a chamada escolhida está acima da posição atual, define como destino o **maior andar solicitado**; caso contrário, o **menor andar solicitado**.
4. Chama `mover_para(destino)`. Ao percorrer os andares, esse método atende e remove as solicitações encontradas no caminho.
5. Repete a decisão até esvaziar a lista.

Essa é uma **heurística simples de atendimento por direção**, não uma garantia matemática do menor trajeto possível em todos os cenários. As chamadas são consideradas conforme a lista existente durante a execução sequencial da demonstração.

## 4. Desenvolvimento em seis etapas

| Etapa | Implementação | Conceitos praticados |
| --- | --- | --- |
| 1 | Criação da classe e inicialização dos atributos. | Classe, objeto, `__init__`, `self`, atributos. |
| 2 | Método `chamar()` para registrar solicitações sem duplicação. | Métodos, parâmetros, manipulação do estado. |
| 3 | Método `mover_para()` para subida e descida andar a andar. | Comportamento do objeto, condicionais, `while`. |
| 4 | Detecção e mensagem de paradas intermediárias. | Consulta aos atributos, decisões a partir do estado. |
| 5 | Remoção de solicitações atendidas. | Atualização do estado e consistência dos dados. |
| 6 | Método `atender_solicitacoes()` para definir a ordem das viagens. | Separação de responsabilidades e reutilização de métodos. |

## 5. Exemplo de execução

No trecho demonstrativo do arquivo, é criada uma instância de `Elevador` e seu andar atual é definido como `4`. Depois são registradas as chamadas para os andares `7`, `2`, `5` e `1`.

```python
elevador = Elevador()
elevador.andar_atual = 4

elevador.chamar(7)
elevador.chamar(2)
elevador.chamar(5)
elevador.chamar(1)

elevador.atender_solicitacoes()
```

**Sequência de paradas:** `5 → 7 → 2 → 1`.

O elevador sobe do 4º ao 7º andar, parando no 5º; depois desce até o 1º, parando no 2º. Ao final, o **estado do objeto** é: `andar_atual = 1`, `direcao = "parado"` e `solicitacoes = []`. O programa exibe a lista vazia; para mostrar também os dois primeiros atributos ao final, seria necessário acrescentar comandos `print()`, o que não foi feito nesta versão.

**Observação:** `__init__` começa no andar `0`. A atribuição `elevador.andar_atual = 4` é feita apenas para configurar o cenário da demonstração.

## 6. Conceitos de Programação Orientada a Objetos

**Classe e objeto.** `Elevador` é a classe que descreve como um elevador funciona; `elevador = Elevador()` cria um objeto concreto dessa classe.

**Atributos.** `andar_atual`, `direcao` e `solicitacoes` armazenam o estado de cada instância. A lista é criada dentro de `__init__`, de modo que objetos diferentes possuam listas próprias.

**Métodos.** `chamar()`, `mover_para()` e `atender_solicitacoes()` definem comportamentos que atuam sobre os atributos do elevador.

**`self`.** É a referência à própria instância. Ao escrever `self.andar_atual`, o método acessa o andar daquele objeto específico.

**Inicialização.** `__init__` estabelece o estado inicial quando o objeto é criado.

**Abstração.** A movimentação física do elevador é representada por mudanças nos atributos e mensagens de texto, sem necessidade de motor, sensores ou interface gráfica.

**Organização de responsabilidades.** `atender_solicitacoes()` decide para onde ir, enquanto `mover_para()` executa o trajeto e as paradas. Essa divisão evita repetir a lógica de deslocamento.

**Encapsulamento (parcial).** As ações principais são organizadas em métodos, mas os atributos continuam públicos e podem ser alterados diretamente, como acontece na demonstração com `elevador.andar_atual = 4`. Portanto, o projeto **não** implementa encapsulamento restritivo com atributos privados ou propriedades.

**Ainda não utilizados:** herança e polimorfismo. Esses recursos não são necessários para o escopo atual.

As estruturas `if`, `while`, listas, `min()`, `max()` e `lambda` fazem parte da lógica de programação em Python e são empregadas dentro dos métodos da classe.

## 7. Como executar

É necessário ter Python instalado. Abra um terminal na pasta do projeto e execute:

```bash
python elevador.py
```

No Termux, caso o projeto esteja na pasta de Documentos usada durante a aula:

```bash
cd ~/storage/shared/Documents/POO/Aula_12_Elevador
python elevador.py
```

O bloco `if __name__ == '__main__':` permite executar essa demonstração quando o arquivo é iniciado diretamente, sem executá-la automaticamente caso a classe seja importada por outro arquivo.

## 8. Limitações e possibilidades de evolução

**Não fazem parte da versão atual:**

- Botões externos separados para solicitar subida ou descida.
- Distinção entre chamada no andar e escolha do destino dentro da cabine.
- Limite de capacidade ou lotação.
- Validação de um intervalo mínimo e máximo de andares.
- Interface de usuário, entrada interativa de chamadas ou controle físico do elevador.
- Múltiplos elevadores, sensores ou simulação de chamadas simultâneas.

Essas possibilidades foram discutidas como evoluções futuras. O foco da Aula 12 é compreender e implementar a lógica inicial de chamadas, movimento, paradas e atendimento, aplicando os fundamentos de POO.

---

**Repositório:** [IvoLucasLLJ/ELEVADOR_POO](https://github.com/IvoLucasLLJ/ELEVADOR_POO)
