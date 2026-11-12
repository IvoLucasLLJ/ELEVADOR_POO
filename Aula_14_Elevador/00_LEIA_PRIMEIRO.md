# Entrega parcial — Elevador POO — 12/11/2026

**Aluno:** Ivo Lucas de Lima Júnior\
**Curso:** Análise e Desenvolvimento de Sistemas — UniSenac\
**Disciplina:** Programação Orientada a Objetos\
**Atividade:** entrega parcial do Elevador, em 12 de novembro de 2026

## O que entregar e em que ordem ler

Esta pasta é **independente dos módulos das aulas 12 e 13**. Para avaliar a atividade, o professor pode seguir esta ordem:

1. **`00_LEIA_PRIMEIRO.md`** — orientações de execução, conceitos de POO e escopo da entrega parcial da Aula 14.
2. **`elevador_completo.py`** — aplicação funcional em arquivo único, organizada internamente por classes e responsabilidades.
3. **`requirements.txt`** — a única dependência externa da interface visual. O modo textual dispensa essa instalação.

## Como executar

Requer Python 3.10 ou superior. Dentro desta pasta:

**Opção A — interface visual no terminal Termux/POSIX:**

```sh
python -m pip install -r requirements.txt
python elevador_completo.py
```

**Opção B — interface textual sem bibliotecas externas:**

```sh
python elevador_completo.py --texto
```

Comandos de demonstração, digitados **um de cada vez**:

```text
externa 3 descer 2
iniciar
```

Espere a cabine chegar ao andar 3 e as duas pessoas embarcarem. Então:

```text
interna 0 1
interna 1 2
fechar
```

Na alternativa textual, também existem `status`, `pessoa ID`, `pausar`, `ajuda` e `sair`. O programa é interativo: depois de `iniciar`, o tempo avança mesmo sem enviar comandos. Pode-se registrar novas chamadas externas durante o movimento.

Para configurar o tempo de fechamento das portas nas paradas internas:

```sh
python elevador_completo.py --texto --tempo-portas 1.5
```

## Conceitos de POO demonstrados

| Conceito | Localização na implementação |
| --- | --- |
| Classes, objetos e construtores | `Andar`, `Pessoa`, `Elevador`, `Predio`, `Painel`, `InterfaceElevador`; `__init__` e `Predio()` |
| Atributos e métodos | `_andar_atual`, `_fila`, `_destinos`; `avancar_um_andar`, `registrar_destino_interno` |
| Encapsulamento | atributos com `_`, propriedades `@property`, tuplas e cópias de registros |
| Abstração e delegação | `Pessoa.selecionar_destino` delega ao `Elevador`; `Painel` coordena as interfaces |
| Composição | `Predio` cria 11 instâncias de `Andar` e uma de `Elevador` |
| Associação | `Pessoa` referencia um `Andar` ou `Elevador`; `Painel` referencia o `Predio` |
| Herança e polimorfismo | `InterfaceElevador(App)` herda do Textual e sobrescreve `compose()` — não há hierarquia entre as entidades do domínio |

## Escopo e verificações

- Exatamente 11 pavimentos (0–10), uma cabine e fila FIFO global.
- Cada chamada externa pode representar um grupo; uma pessoa pode registrar vários destinos.
- Várias pessoas podem compartilhar uma parada interna sem reordenar a fila.
- Embarque e desembarque condicionados a estados e validações.
- Comandos para iniciar, pausar, retomar, fechar portas e encerrar; fechamento temporizado nas paradas internas.
- Os dados permanecem somente em memória durante a sessão.

Na preparação desta entrega, foram verificadas a sintaxe do Python e a execução textual básica, incluindo chamada externa, embarque, destino interno, desembarque e encerramento. A interface visual Textual não foi validada nesta etapa. Essas verificações não substituem a demonstração ao professor.

## Integridade da organização

Esta pasta integra **a raiz do repositório `ELEVADOR_POO`**, lado a lado com `Aula_13_Predio/` e os arquivos originais da Aula 12. **Os arquivos e o histórico das aulas anteriores são preservados integralmente.** A entrega parcial da Aula 14 contém exclusivamente os três arquivos listados acima.
