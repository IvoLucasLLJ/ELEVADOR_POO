# Guia da Aula 15 — Elevador POO e SOLID

**Autor:** Ivo Lucas de Lima Júnior. Este guia foi produzido na preparação acadêmica da Aula 15, a partir de `elevador_completo.py` e do relatório fornecido. O programa permanece integralmente em um arquivo. Os nomes entre crases permitem localizar cada exemplo no código.

## 1. Da Aula 14 à Aula 15

O relatório histórico apresenta a Aula 14 como base funcional em arquivo único. A versão atual separa o estado e as operações da fila, da cabine e dos passageiros, introduz três protocolos e mantém um coordenador. As impressões aparecem em funções de apresentação, sem fazer as entidades dependerem da interface.

A organização atual pode ser observada diretamente. A equivalência com a implementação anterior é uma conclusão histórica do relatório: não foi refeita nesta preparação, pois não se usa aqui uma cópia original da Aula 14.

## 2. Classes, objetos e estado

Uma **classe** define dados e operações. `Predio` é uma classe; ao avaliar `Predio()` cria-se um **objeto**, com seus próprios andares, pessoas e elevador. `Painel(predio)` cria outro objeto, associado ao prédio recebido.

Em `Andar.__init__(self, numero, predio)`, `__init__` inicializa o objeto criado. `self` é a referência à instância que recebe a operação; `self._numero`, `self._predio` e `self._pessoas` são atributos daquela instância. Não é uma palavra reservada, mas uma convenção usada pelo programa.

Um **método** é uma função definida na classe. `Andar.chamar_elevador` usa os atributos do próprio andar para encaminhar o pedido. `Pessoa.selecionar_destino` usa a identidade daquela pessoa ao solicitar seu destino. `Predio.validar_andar` é um método estático: não usa estado de uma instância para aplicar a regra de pavimentos.

Exemplo executável em um interpretador, importando o programa sem abrir a interface:

```python
from elevador_completo import Predio, Painel
predio = Predio()
painel = Painel(predio)
painel.chamar_externo(0, "subir")
painel.iniciar()
painel.atualizar()  # Já está no andar 0: abre e embarca no mesmo pulso.
pessoa = predio.pessoas[0]
painel.escolher_destino(2, pessoa.identificador)
painel.fechar_portas()
painel.atualizar()  # Andar 1.
painel.atualizar()  # Andar 2: atende o destino e desembarca.
```

Esse é um exemplo de uso da API existente, não código adicional de produção. As chamadas explícitas a `atualizar()` representam os pulsos que as interfaces emitem durante a execução.

## 3. Encapsulamento e consultas

O prefixo `_` indica uso interno por convenção: Python não impede acesso direto a esses atributos. A API pública usa propriedades e métodos para consultar e validar operações.

`Pessoa.identificador`, `Pessoa.destinos`, `Elevador.andar_atual` e outras propriedades não têm setter. Atribuir `pessoa.destinos = (...)` é recusado. `Predio.andares`, `Predio.pessoas`, `Andar.pessoas`, `Elevador.passageiros` e os destinos são expostos como tuplas.

`FilaFIFO.consultar()` cria uma lista de cópias dos registros. `_resumir_solicitacao` troca as referências às pessoas por seus IDs nessas consultas. O histórico também contém cópias. Alterar uma lista ou um dicionário retornado não deve reescrever o registro interno; há teste local dessa proteção.

Essas medidas protegem a **estrutura das coleções**. Uma tupla de pessoas continua contendo referências a objetos vivos, que podem mudar por suas operações. Não há imutabilidade profunda ou privacidade absoluta.

## 4. Responsabilidades e relações

| Classe concreta | Estado ou responsabilidade | Relação observável |
|---|---|---|
| `Andar` | Número, prédio associado e pessoas fora da cabine. | É criado por `Predio`; encaminha chamadas a ele. |
| `Pessoa` | Identificador, local, origem, sentido e destinos pendentes/atendidos. | Seu local referencia um `Andar` ou a cabine; delega operações a `Elevador`. |
| `FilaFIFO` | Registros, sequência global e histórico de pedidos. | É recebida pelo coordenador; não decide sobre portas. |
| `ControladorMovimento` | Posição, direção e portas. | Executa o passo físico solicitado; não escolhe a fila. |
| `GerenciadorPassageiros` | Pessoas na cabine e transferências entre locais. | Recebe a função `obter_andar`; preserva os mesmos objetos. |
| `Elevador` | Coordenação dos colaboradores e eventos do atendimento. | Recebe fila, movimento, passageiros e criação de solicitantes. |
| `Predio` | Composição de andares, elevador e cadastro de pessoas. | Usa fábrica padrão ou fábrica recebida em `fabrica_elevador`. |
| `Painel` | Início/pausa, pessoa ativa e prazo de fechamento. | Usa o prédio recebido e um relógio injetável. |
| `InterfaceElevador` | Widgets, disposição e eventos da interface visual. | Herda de `App` do Textual e chama o painel. |

**Composição:** `Predio.__init__` cria onze `Andar` e utiliza uma fábrica para criar o elevador. `_montar_elevador` cria os colaboradores concretos. Cada instância de prédio tem seus próprios componentes.

**Associação:** `Painel` recebe um prédio pronto; `Pessoa` referencia seu local físico. Não é necessário herdar de uma classe para manter relação com seus objetos.

**Delegação:** `Pessoa.selecionar_destino` chama `Elevador.registrar_destino_interno`; `Elevador` delega a validação e a alteração de destinos ao gerenciador e os registros à fila.

**Herança:** com Textual instalado, `InterfaceElevador(App)` herda o ciclo de execução do framework. `compose()` sobrescreve o método que constrói a interface; `on_mount`, eventos e ações participam desse ciclo. Não há hierarquia de herança entre as entidades do domínio. Sem Textual, a definição usa `object` como base e o construtor da interface informa a dependência ausente.

As funções `mostrar_estado_pessoa`, `mostrar_fila` e `mostrar_registros` cuidam de saída de dados. A interface textual usa `executar_comando`, `mostrar_estado` e `executar`.

## 5. Protocolos e injeção de dependências

Os contratos são definidos com `typing.Protocol`:

- `FilaAtendimento`: localização, registro, vínculo, início, consulta e conclusão de solicitações.
- `MovimentoCabine`: consulta da posição/direção/portas e operações físicas da cabine.
- `ControlePassageiros`: consulta dos ocupantes, embarque, desembarque e operações de destinos.

O construtor de `Elevador` recebe objetos com essas operações, em vez de criá-los internamente. Também recebe `criar_solicitante`, uma função. `_montar_elevador` concentra a escolha de `FilaFIFO`, `ControladorMovimento` e `GerenciadorPassageiros`. `Predio` aceita a opção `fabrica_elevador`; `Painel` recebe `relogio`, cujo padrão é `time.monotonic`.

Isso é **injeção de dependências por construtor/função**, sem contêiner ou framework de injeção. O relógio manual dos testes locais utiliza esse ponto para simular passagem do tempo. Os protocolos descrevem interfaces estruturais; a anotação não valida automaticamente as regras de negócio em execução. Não foi executado um verificador estático de tipos.

## 6. SOLID aplicado com exemplos localizáveis

### S — Single Responsibility Principle

`FilaFIFO` controla solicitações; `ControladorMovimento` controla o estado físico; `GerenciadorPassageiros` controla ocupantes e destinos. `Elevador.avancar_um_andar` coordena as operações desses colaboradores. `Painel` trata comandos e temporização, enquanto as interfaces apresentam e encaminham entradas.

Essa divisão reduz os motivos de alteração de cada componente. O coordenador ainda conhece a sequência de atendimento e mantém dependências concretas com conceitos do domínio; não se afirma independência completa.

### O — Open/Closed Principle

Os parâmetros de `Elevador.__init__` e `Predio.__init__(..., fabrica_elevador=...)` permitem selecionar implementações sem reescrever o fluxo coordenador para cada montagem. O ponto padrão é `_montar_elevador`.

Uma extensão por esses pontos só é adequada se mantiver os contratos. Uma mudança de regra, como substituir FIFO por prioridade, pode exigir revisão do comportamento e dos testes. Esta entrega contém uma política FIFO e não demonstra uma segunda política pronta.

### L — Liskov Substitution Principle

Um colaborador substituto deve aceitar as operações esperadas e manter os resultados e invariantes do contrato: um movimento não salta andares; a fila não muda a ordem global; embarque/desembarque conservam identidade e localização; a conclusão ocorre no fechamento aceito.

Ter os nomes dos métodos não basta. Um objeto que ofereça `avancar_para` mas salte três andares violaria o contrato comportamental esperado. Esse exemplo explica o princípio; não é uma implementação adicionada ao projeto. A suíte atual verifica cenários da implementação concreta, sem provar a substituibilidade de todas as implementações possíveis.

### I — Interface Segregation Principle

Os três protocolos separam operações por responsabilidade. O controle de movimento não precisa implementar consultas de pessoas ou histórico de solicitações. O gerenciador recebe apenas a função para localizar um andar, em vez de receber uma interface ampla do prédio para todas as tarefas.

Esses contratos são os consumidos pelo coordenador. Não são uma promessa de que cada componente funciona isoladamente com qualquer entrada: algumas operações internas pressupõem validação anterior de `Elevador`.

### D — Dependency Inversion Principle

`Elevador` recebe colaboradores anotados pelos protocolos e a função de criar pessoas. O ponto de composição escolhe as classes concretas. `GerenciadorPassageiros` recebe `obter_andar` e `Painel` recebe o relógio.

A política de coordenação não instancia os três colaboradores no seu construtor. Ainda existem relações concretas com `Pessoa`, `Andar` e os dados dos registros; a inversão é localizada, não absoluta.

## 7. Percurso da chamada ao desembarque

Para a chamada `externa 0 subir 2`, seguida dos destinos 2 e 3:

1. `executar_comando` ou o evento da interface chama `Painel.chamar_externo`.
2. `Predio.chamar_elevador` e `Elevador.registrar_chamada_externa` validam o andar, sentido e quantidade. Uma duplicata ativa/pendente retorna sem criar outras pessoas.
3. A função de criação registra duas `Pessoa` no andar de origem. `FilaFIFO.registrar` cria um pedido externo com sequência global.
4. Após `Painel.iniciar`, cada atualização pode avançar até um andar. `Elevador` pega o primeiro pedido e pede o passo a `ControladorMovimento`.
5. Na chegada, o elevador abre as portas. Cada pessoa embarca por `GerenciadorPassageiros`: sai do andar e passa à cabine, mantendo o mesmo objeto.
6. `Painel.escolher_destino` escolhe a pessoa; o gerenciador valida o destino; a fila cria ou compartilha o pedido interno. Repetir o destino para a mesma pessoa não cria outra parada.
7. `Painel.fechar_portas` é aceito quando todos na cabine têm destino. A chamada externa é concluída e a fila segue em FIFO.
8. No destino 2, o destino da Pessoa 1 passa a atendido. Sem destinos restantes, ela desembarca e é adicionada ao andar 2. A Pessoa 2 continua na cabine.
9. O fechamento interno é temporizado; a fila então atende o andar 3 e a Pessoa 2 desembarca. Cada solicitação só entra no histórico no fechamento.
10. O encerramento apresenta `mostrar_registros`, incluindo pedidos restantes, se a sessão tiver sido interrompida.

Se uma pessoa tiver vários destinos, não desembarca no intermediário. A ordem é global, não uma rota individual ordenada por distância. Ao informar um ID válido e um destino inválido, a pessoa ativa pode mudar antes da rejeição; o programa não promete atomicidade da seleção.

## 8. Roteiro de apresentação e defesa

1. Apresente o objetivo: simular uma cabine com onze pavimentos e fila FIFO, evoluindo a organização da Aula 14.
2. Mostre a tabela de responsabilidades e localize `Elevador.__init__`, os três protocolos e `_montar_elevador`.
3. Explique por que separar a fila do movimento evita que uma classe concentre todos os estados. Mostre composição, delegação e a associação da pessoa ao local.
4. Execute a demonstração com duas pessoas indicada no README. Explique o bloqueio sem destino, a identidade dos objetos, o destino compartilhado e a conclusão no fechamento.
5. Execute `python -B -m unittest discover -s tests -v` e apresente as evidências locais, distinguindo-as dos números históricos.
6. Explique os limites: contratos não são prova formal de Liskov, tuplas não tornam objetos imutáveis, não houve nova comparação com a Aula 14 e a interface foi exercitada automaticamente sem inspeção física de toque.

Uma resposta à pergunta “por que um arquivo só?” é que a separação de responsabilidades existe nas classes e contratos internos; a organização da entrega preserva a implementação em arquivo único já pronta. Não foi introduzida outra arquitetura nesta preparação.
