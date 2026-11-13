# ELEVADOR_POO — UniSenac

Projeto acadêmico de Programação Orientada a Objetos em Python, desenvolvido no Termux/Android. O repositório documenta a evolução do simulador em quatro etapas, mantendo as implementações anteriores para consulta e comparação:

1. **Aula 12 — algoritmo original de movimentação:** classe `Elevador` e simulador textual na raiz, com atendimento por proximidade e direção. Os dois arquivos-fonte e os dez testes originais foram preservados.
2. **Aula 13 — evolução modular:** pacote [Aula_13_Predio](Aula_13_Predio/), com prédio, pessoas, painéis externo e interno, portas e fila global FIFO para um elevador e onze pavimentos, de `0` a `10`.
3. **Aula 14 — versão completa em arquivo único:** aplicação independente dos módulos anteriores, preparada para a entrega parcial e **publicada em 12/11/2026**. A entrega publicada permanece disponível em [Aula_14_Elevador no GitHub](https://github.com/IvoLucasLLJ/ELEVADOR_POO/tree/main/Aula_14_Elevador).

4. **Aula 15 — refatoração SOLID em arquivo único:** **versão atual**, com fila, movimento e passageiros separados por responsabilidade, documentação, testes e evidências em [Aula_15_Elevador/README.md](Aula_15_Elevador/README.md).

## Navegação

- [Aula 15: versão atual, execução e testes](#aula-15-versão-atual)
- [Aula 14: entrega parcial publicada, execução e validação](#aula-14-versão-atual-e-entrega-parcial)
- [Aula 13: execução, regras, arquitetura e testes](#aula-13-evolução-modular)
- [Aula 12: algoritmo e simulador originais](#aula-12-algoritmo-original-de-movimentação)

## Aula 15: versão atual

A Aula 15 evolui a Aula 14 com **refatoração SOLID em um único arquivo Python**, mantendo toda a implementação em `Aula_15_Elevador/elevador_completo.py`. `Elevador` coordena os colaboradores de fila, movimento e passageiros por contratos, preservando uma cabine, onze pavimentos, FIFO e as interfaces visual e textual. O programa foi copiado sem alteração de bytes.

A entrega inclui [README da Aula 15](Aula_15_Elevador/README.md), [guia didático](Aula_15_Elevador/Guia_Elevador_POO_SOLID.md), testes e evidências. É a **versão atual** do projeto. As aulas anteriores e seus links são preservados abaixo.

### Execução da Aula 15 a partir da raiz

Requer Python 3.10 ou superior. A interface visual usa **Textual 8.2.8**, já encontrado no ambiente validado; nenhum pacote foi instalado ou atualizado nesta integração.

```sh
python Aula_15_Elevador/elevador_completo.py
python Aula_15_Elevador/elevador_completo.py --texto
python Aula_15_Elevador/elevador_completo.py --texto --tempo-portas 1.5
```

O modo textual usa somente biblioteca padrão e recursos POSIX/Termux. As orientações para preparar um ambiente visual novo estão no README da Aula 15.

### Testes e evidências da Aula 15

Os testes da Aula 15 importam seu próprio arquivo de produção. Para executá-los a partir da raiz do repositório, entre na subpasta no mesmo comando, evitando importar o `elevador_completo.py` preexistente na raiz:

```sh
(cd Aula_15_Elevador && python -B -m unittest discover -s tests -v)
(cd Aula_15_Elevador && python -B -S -m unittest discover -s tests -v)
```

No Termux/Android aarch64, com **Python 3.13.13 e Textual 8.2.8**, os resultados locais são **28 testes aprovados**; com `-S`, são **27 aprovados e 1 teste visual omitido**, pois site-packages não é carregado. O teste visual utiliza o modo headless do Textual em 120×35 e 44×32; não é inspeção física de toque ou tela.

Essa suíte foi produzida para a preparação acadêmica atual. Os **103 testes e as 5.137 operações** do relatório SOLID são resultados históricos de Linux/Python 3.12.14, sem nova execução ou comparação com a Aula 14 nesta integração. Os conjuntos não devem ser somados.

Consulte as [evidências da preparação](Aula_15_Elevador/evidencias/VALIDACAO_LOCAL.md) e o [registro da integração e dos testes no destino](Aula_15_Elevador/evidencias/INTEGRACAO_GIT.md). A descoberta geral de `tests/` na raiz continua pertencendo às suítes ali existentes; use os comandos acima para a Aula 15.

## Aula 14: versão atual e entrega parcial

A entrega de **12 de novembro de 2026** reúne as entidades, o controlador e as interfaces em `Aula_14_Elevador/elevador_completo.py`. Ela mantém um elevador, onze pavimentos, pessoas com destinos próprios e atendimento FIFO. Cada chamada externa pode representar um grupo, e uma pessoa pode registrar vários destinos. Os dados permanecem em memória durante a sessão.

A pasta publicada contém exclusivamente:

- [`00_LEIA_PRIMEIRO.md`](Aula_14_Elevador/00_LEIA_PRIMEIRO.md): orientações da entrega, conceitos de POO e escopo.
- [`elevador_completo.py`](Aula_14_Elevador/elevador_completo.py): aplicação completa em arquivo único.
- [`requirements.txt`](Aula_14_Elevador/requirements.txt): dependência da interface visual, fixada em `textual==8.2.8`.

A publicação foi realizada no commit [838c271 — Adiciona entrega parcial do elevador - Aula 14](https://github.com/IvoLucasLLJ/ELEVADOR_POO/commit/838c27158d9c671afa47b5c3e9beb551c0a4db11).

### Execução da Aula 14

Requer **Python 3.10 ou superior**. No Termux, caso o Python ainda não esteja instalado, execute `pkg install python`. Entre na pasta da versão da Aula 14:

```sh
cd /storage/emulated/0/Documents/POO/Aula_12_Elevador/Aula_14_Elevador
```

Para instalar a dependência e iniciar a **interface visual Textual**:

```sh
python -m pip install -r requirements.txt
python elevador_completo.py
```

Para iniciar a **interface textual**, na mesma pasta, sem instalar bibliotecas externas:

```sh
python elevador_completo.py --texto
```

A alternativa textual utiliza recursos POSIX disponíveis no Termux. O tempo de fechamento das portas nas paradas internas pode ser configurado em qualquer uma das interfaces; por exemplo:

```sh
python elevador_completo.py --texto --tempo-portas 1.5
```

Na interface textual, digite cada comando separadamente:

```text
externa 3 descer 2
iniciar
```

Aguarde a chegada ao andar 3 e o embarque das duas pessoas. Em seguida, registre os destinos individuais e feche as portas:

```text
interna 0 1
interna 1 2
fechar
```

Os comandos `status`, `pessoa ID`, `pausar`, `ajuda` e `sair` permitem acompanhar e controlar a sessão. Depois de `iniciar`, o movimento avança mesmo sem novos comandos. As instruções completas estão em [00_LEIA_PRIMEIRO.md](Aula_14_Elevador/00_LEIA_PRIMEIRO.md).

### Validação da entrega parcial

Na preparação da Aula 14, foram aprovadas a verificação de sintaxe do Python e a execução textual básica: chamada externa no andar 3, embarque de duas pessoas, destinos 0 e 1, desembarques, fila final vazia e encerramento sem erros. **A interface visual da Aula 14 não foi validada nessa etapa.** Os 92 testes históricos apresentados na seção da Aula 13 pertencem às implementações das aulas 12 e 13.

## Aula 13: evolução modular

Esta seção preserva a documentação técnica do pacote `Aula_13_Predio/`. Seus comandos partem da raiz do repositório e executam a versão modular; a Aula 14 é iniciada pelo arquivo e pelo diretório indicados na seção anterior.

### Instalação e execução da Aula 13 no Termux

Requer Python **3.10 ou superior**. Desenvolvimento e testes realizados com Python **3.13.13** no Termux Android/aarch64. A interface visual utiliza **Textual 8.2.8**, fixado em `requirements.txt`.

Se o Python ainda não estiver instalado no Termux:

```sh
pkg install python
```

Na pasta do projeto:

```sh
cd /storage/emulated/0/Documents/POO/Aula_12_Elevador
python -m pip install --user -r requirements.txt
python -m Aula_13_Predio.main
```

O caminho equivalente `~/storage/shared/Documents/POO/Aula_12_Elevador` pode ser usado se o acesso ao armazenamento compartilhado já estiver configurado no Termux. Não execute `main.py` como arquivo avulso: os imports relativos pertencem ao pacote da Aula 13.

Textual já estava instalado no ambiente usado na implementação; não foi necessário instalar ou atualizar pacotes. O comando de instalação acima é a orientação para ambientes novos, não uma afirmação de instalação limpa verificada.

#### Uso da interface visual

1. No **painel externo**, selecione um andar e pressione **SUBIR** ou **DESCER**. A quantidade padrão é uma pessoa; para embarcar um grupo na mesma parada, escolha a quantidade antes de chamar. Os identificadores são automáticos.
2. Registre outras chamadas se desejar e pressione **Iniciar** (`i`). O atendimento avança automaticamente, um andar por segundo.
3. O painel externo continua disponível durante o movimento. Novas chamadas entram no fim da fila.
4. Ao atender uma externa, o elevador abre as portas e embarca automaticamente as pessoas correspondentes. O **painel interno** fica disponível.
5. Selecione um ou vários destinos antes de pressionar **Fechar portas** (`f`). Cada novo embarque seleciona automaticamente a última pessoa que entrou e exibe **SELECIONANDO DESTINOS PARA: Pessoa X**. O seletor permite alternar entre pessoas da cabine sem perder os destinos já registrados. Todos os botões internos atribuem destinos exclusivamente à pessoa selecionada; `*` marca somente os destinos dela. As portas permanecem abertas enquanto alguém estiver sem destino válido, com indicação dos nomes pendentes.
6. No embarque, escolha um ou vários destinos e use **Fechar portas**. Nas paradas internas intermediárias, as portas fecham automaticamente após **1,5 segundo**, mantendo a pessoa dentro enquanto houver destinos pendentes. O botão manual continua disponível.
7. Quando a cabine estiver vazia, as portas fecham automaticamente na atualização seguinte. Fila vazia deixa o sistema ocioso e disponível para novas chamadas.
8. **Pausar/Retomar** (barra de espaço) suspende o movimento e o fechamento automático, preservando a fila e o tempo restante das portas. O painel externo permanece disponível durante a pausa.
9. **Sair** (`q`) encerra a sessão e exibe no terminal o relatório de solicitações concluídas, destinos atendidos e pendências. Os dados são mantidos somente em memória e não são persistidos.

O painel mostra **POSIÇÃO ATUAL: ANDAR N**. Nos botões, `>N` marca a cabine, `S` indica a seleção externa e `*` indica solicitações pendentes no painel externo; os sinais podem coexistir. A seleção externa não acompanha a cabine. Também mostra direção, portas, situação operacional, fila FIFO e histórico de eventos, que aproveita o espaço livre. A fila inclui a solicitação em atendimento até concluir o serviço e fechar as portas.

Use Tab/Shift+Tab para navegar e Enter para acionar botões; os controles também aceitam eventos de mouse quando oferecidos pelo terminal. O suporte a toque como mouse depende da configuração do Termux/Android e não foi validado fisicamente nesta implementação. A disposição muda para uma coluna em terminais estreitos, com rolagem. Os painéis ficam lado a lado a partir de 85 colunas e empilhados em larguras menores; a partir de 110 colunas, as grades usam seis colunas e duas linhas para reduzir a altura dos painéis; abaixo de 40 colunas, usam três colunas. Os controles inferiores ficam em duas linhas nas telas estreitas. A rolagem permite consultar painéis, fila e histórico em terminais baixos.

#### Alternativa funcional sem Textual

```sh
python -m Aula_13_Predio.main --texto
```

Essa alternativa usa apenas a biblioteca padrão e entrada POSIX, disponível no Termux. Confirme cada comando com Enter; o movimento continua enquanto se aguarda uma linha completa. Exemplos:

```text
externa 5 descer
iniciar
```

Aguarde os eventos de chegada ao andar 5 e embarque; então digite:

```text
interna 0
fechar
```

Comandos disponíveis:

| Comando | Operação |
| --- | --- |
| `externa ANDAR subir\|descer [QUANTIDADE]` | Acionar o painel externo, inclusive durante movimento; quantidade opcional, padrão 1. |
| `interna DESTINO` | Destino para a pessoa ativa; novos embarques selecionam a última pessoa que entrou. |
| `pessoa ID` | Alternar a pessoa ativa sem alterar os destinos. |
| `interna DESTINO ID` | Selecionar uma pessoa específica e registrar seu destino, pelo ID automático exibido. |
| `iniciar` | Iniciar o atendimento automático. |
| `fechar` | Concluir a parada e fechar as portas, quando permitido. |
| `pausar` | Alternar pausa/retomada. |
| `status` | Mostrar estado, fila e pessoas na cabine. |
| `ajuda` | Mostrar os comandos. |
| `sair` | Encerrar voluntariamente. |

EOF (Ctrl+D) e Ctrl+C encerram essa alternativa sem traceback. `select` aguarda entrada ou o próximo intervalo; não há laço de espera ocupada. Essa interface alternativa é voltada a Termux/POSIX, não ao console nativo do Windows.

### Regras da Aula 13

- São exatamente onze pavimentos, com índices `0..10`; `Predio` rejeita configurações diferentes.
- Há uma única instância de elevador criada pelo prédio.
- Externa: andar e sentido. Interna: destino, associado às pessoas interessadas. Não existe `quantidade_pessoas` nos registros.
- Cada externa distinta cria automaticamente um ou mais objetos `Pessoa`, conforme a quantidade informada (padrão 1), como solicitantes didáticos. Isso não representa cadastro ou cálculo de lotação.
- Cada solicitação nova recebe ordem crescente e estado `pendente`, `em_atendimento` ou `concluida`. O histórico conserva as concluídas.
- FIFO é global: a solicitação ativa não pode ser ultrapassada. Passar por um andar solicitado posteriormente não o atende antecipadamente.
- Repetir uma externa pendente/ativa do mesmo andar e sentido não cria parada ou pessoa. Sentidos opostos são distintos. Após concluir a solicitação, sua chave pode ser registrada novamente.
- Repetir um destino já pendente para a mesma pessoa é rejeitado como duplicata. Se outra pessoa selecionar um destino já na fila, ela é vinculada à mesma parada, sem reordená-la.
- Solicitação no andar atual abre atendimento sem movimento quando chegar sua vez no FIFO. Destino interno igual ao andar atual é rejeitado sem alteração de estado.
- Portas abertas impedem movimento. Embarque exige a externa correspondente, mesmo andar e sentido. Desembarque exige destino efetivamente atendido e portas abertas.
- A **primeira escolha interna** respeita o sentido da chamada original. As seguintes podem representar outras etapas da mesma viagem; não reordenam a fila global.
- A pessoa ativa é controlada pelo `Painel`: novos embarques selecionam a última pessoa que entrou; uma escolha manual persiste até outro embarque ou o desembarque da pessoa selecionada. Ao desembarcar, a seleção passa para alguém ainda na cabine, priorizando quem não tem destino, ou é limpa se a cabine estiver vazia.
- Uma pessoa pode ter vários destinos pendentes. Em uma parada intermediária, remove apenas o destino atendido e permanece dentro. Desembarca ao atender seu último destino pendente, mantendo identidade e histórico.
- Enquanto está na cabine, a posição da pessoa acompanha o elevador; sua origem permanece disponível separadamente.
- Andares negativos, acima de 10, valores não inteiros (incluindo `bool` nas APIs numéricas), sentidos inválidos e operações fora de contexto são rejeitados sem alterar o domínio.

FIFO pode produzir trajetos maiores e inversões de movimento, inclusive enquanto há pessoas na cabine. Isso é parte do exercício, que não otimiza o percurso pelo sentido solicitado.

### Arquitetura e conceitos de POO da Aula 13

| Módulo / classe | Responsabilidade |
| --- | --- |
| `main.py` | Entrada, argumentos e composição da aplicação; importa a interface escolhida sob demanda. |
| `predio.py` / `Predio` | Compõe onze objetos `Andar` e seu único `Elevador`; cria os solicitantes automaticamente. |
| `andar.py` / `Andar` | Localiza pessoas fora da cabine, permite consultar espera por sentido e encaminha chamadas. |
| `elevador.py` / `Elevador` | Autoridade sobre posição, direção, portas, fila, solicitação ativa, passageiros, eventos e histórico. |
| `pessoa.py` / `Pessoa` | Identidade automática, origem, localização, estados, destinos pendentes e atendidos; operações de embarque, seleção e desembarque. |
| `painel.py` / `Painel` | Coordena acionamentos, início, pausa e atualizações; usa métodos do domínio. |
| `interface.py` / `InterfaceElevador` | Controles Textual, eventos de entrada, temporizador e apresentação. |
| `interface_texto.py` | Alternativa de comandos sem dependências externas. |

**Classes e objetos:** as classes descrevem entidades e comportamentos; `Predio()` constrói a composição concreta da sessão. **Construtores** estabelecem estados iniciais válidos. **Atributos e métodos** reúnem os dados e as operações das entidades.

**Encapsulamento:** propriedades públicas permitem leitura; mudanças passam por métodos que verificam as regras. Coleções são devolvidas como tuplas ou cópias. Atributos com `_` são internos por convenção Python; não constituem uma barreira de segurança contra código que deliberadamente ignore essa convenção. A interface não escreve neles.

**Composição:** o prédio cria e organiza seus andares e seu elevador. **Associação:** a mesma pessoa se relaciona com um andar ou com a cabine, e os registros de destino se associam às pessoas interessadas. Mover uma pessoa atualiza essas relações, sem duplicar sua identidade.

**Distribuição de responsabilidades:** o domínio decide se uma operação é válida; `Painel` coordena comandos; a interface mostra o resultado e recebe eventos. O temporizador chama uma atualização curta, sem executar toda a viagem em um laço bloqueante.

Não há hierarquia de herança entre as entidades do domínio nem demonstração acadêmica de polimorfismo entre elas. `InterfaceElevador` herda de `textual.app.App` e implementa os métodos de integração exigidos pelo framework; essa herança de infraestrutura não foi introduzida nas entidades apenas para demonstrar o conceito.

### Testes e validação das aulas 12 e 13

As suítes desta seção exercitam o algoritmo da Aula 12 e a implementação modular da Aula 13. Elas não constituem validação automática da versão em arquivo único da Aula 14. Execute a partir da raiz, após instalar as dependências da interface da Aula 13:

```sh
python -B -m unittest discover -s tests -v
```

A descoberta geral executa todos os arquivos de teste presentes em `tests/`. Para selecionar apenas as suítes publicadas das aulas 12 e 13, use os comandos específicos abaixo:

```sh
python -B -m unittest discover -s tests -p test_elevador.py -v
python -B -m unittest discover -s tests -p test_aula13.py -v
python -B -m unittest discover -s tests -p test_interface.py -v
python -B -m unittest discover -s tests -p test_execucao.py -v
python -B -m unittest discover -s tests -p test_selecao_passageiros.py -v
python -B -m unittest discover -s tests -p test_qualidade.py -v
python -B -m unittest discover -s tests -p test_qualidade_interface.py -v
python -B -m unittest discover -s tests -p test_qualidade_texto.py -v
```

- `test_elevador.py`: os **10 testes originais**, sem alteração, para a Aula 12.
- `test_aula13.py`: **32 testes** de domínio e fluxos integrados, incluindo os cenários A, B, C, D, E, F, G e H.
- `test_selecao_passageiros.py`: **13 testes** de regressão do embarque individual e em grupo, destinos independentes, alternância, bloqueio com identificação, FIFO, desembarque, fechamento automático, reutilização da sessão e layout horizontal e callbacks após o encerramento.
- `test_interface.py`: **6 testes** da interface Textual em modo headless, com eventos de botões/teclado, temporizador real, seleção de pessoa e tela estreita de 44×32.
- `test_execucao.py`: **7 testes** de entrada/imports, comandos, alternativa sem site-packages, loop em processo separado durante movimento e saída por interrupção.
- `test_qualidade.py`: **15 testes** adicionais de portas, prazos, pausa, construtores, FIFO e identidade das pessoas.
- `test_qualidade_interface.py`: **6 testes** adicionais com Pilot, incluindo a viagem real **1 → 5 → 6 → 7**, posição/seleção, pausa e nove etapas de redimensionamento.
- `test_qualidade_texto.py`: **3 testes** adicionais em subprocessos POSIX, incluindo a mesma viagem e entradas inválidas.

A auditoria histórica registrou **92 testes aprovados: 10 da Aula 12 e 82 da Aula 13** (79 cenários anteriores e 13 regressões de passageiros e encerramento). Na evolução do seletor da Aula 13, foi corrigida apenas a expectativa após o novo embarque: passou a selecionar a segunda pessoa. Os demais testes existentes foram preservados integralmente. A regressão da Aula 12 corresponde ao cenário I. Os testes da interface exigem Textual; os de domínio e da alternativa textual não dependem dele. Os testes por subprocesso/descritor usam recursos POSIX compatíveis com o ambiente Termux.

Os cenários verificam: chamada no 5 para descer; externas `3/descer, 0/subir, 10/descer, 8/descer` em FIFO; entrada durante percurso; destinos `4,6,9` da mesma pessoa; duplicatas antes/depois da conclusão; sentidos opostos; rejeições atômicas; ociosidade e nova chamada. Testes headless validam a aplicação real, mas não substituem avaliação física de toque e legibilidade no tablet.

A espera das portas pode ser configurada nas duas interfaces:

```sh
python -m Aula_13_Predio.main --tempo-portas 1.5
python -m Aula_13_Predio.main --texto --tempo-portas 1.5
```

Para repetir a suíte com medição de linhas pelo `trace` da biblioteca padrão:

```sh
python auditar_qualidade.py
```

O comando gera evidências locais em `evidencias/` e descobre todos os testes presentes em `tests/`; arquivos adicionais podem alterar o total executado. Consulte [RELATORIO_QUALIDADE.md](RELATORIO_QUALIDADE.md) para os resultados históricos das aulas 12 e 13, cobertura, causas dos defeitos e limites da validação. As referências desse relatório à ausência de commit ou push descrevem a etapa local de preparação; os códigos e testes dessas aulas já estão publicados.

### Preservação e referências

As fontes `elevador.py`, `simulador.py` e o teste legado `tests/test_elevador.py` permanecem com o conteúdo original. A política de proximidade da Aula 12 continua independente do FIFO da Aula 13. Os módulos da Aula 13 e suas suítes de testes estão versionados e publicados no repositório; a entrega parcial da Aula 14 foi acrescentada em pasta própria, preservando esses materiais e seu histórico.

As referências locais `Elevador_v3.zip` e `Elevador_v4.zip` do professor foram consideradas como material didático para movimento incremental e integração entre entidades. Não substituem o projeto. O painel visual local anterior foi reaproveitado conceitualmente, com controles Textual, disposição responsiva e temporizador; as regras e invariantes foram concentradas no domínio.

Não há banco de dados, rede, capacidade máxima, persistência, múltiplos elevadores ou otimização de percurso.

---

## Aula 12: algoritmo original de movimentação

**Instituição:** UniSenac
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)  
**Disciplina:** Programação Orientada a Objetos (POO)  
**Aula:** 12 — Algoritmo do Elevador  
**Data:** 22 de outubro de 2026  
**Linguagem:** Python

### 1. Objetivo

Simular, em Python, o atendimento de chamadas de um elevador. O exercício aplica os fundamentos de Programação Orientada a Objetos para representar o elevador, armazenar suas solicitações e controlar os deslocamentos entre andares.

O programa foi desenvolvido de maneira incremental: primeiro a classe e os atributos, depois o registro de chamadas, a movimentação, as paradas intermediárias, a remoção de solicitações atendidas e, por fim, a escolha da ordem de atendimento.

### 2. Funcionalidades implementadas

- Criar um elevador inicialmente no andar `0`, com direção `parado` e lista de solicitações vazia.
- Registrar chamadas por andar, evitando duplicatas.
- Subir ou descer um andar por vez, exibindo o movimento no terminal.
- Reconhecer e anunciar paradas em andares solicitados durante o percurso.
- Remover da lista cada solicitação atendida.
- Escolher a chamada inicialmente mais próxima; em caso de empate na distância, priorizar o andar superior.
- Após escolher um sentido, percorrer até a solicitação mais distante naquele sentido, atendendo as chamadas intermediárias; inverter a direção quando necessário.
- Atender uma chamada no andar atual sem deslocamento.
- Encerrar com a direção `parado` quando o deslocamento termina.

### 3. Estrutura do programa

O projeto está organizado em dois arquivos: `elevador.py` contém a classe `Elevador` e uma demonstração do algoritmo; `simulador.py` oferece uma interface interativa de terminal e importa essa classe. Cada arquivo executa seu fluxo principal somente quando é iniciado diretamente.

#### Classe `Elevador`

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

#### Como a escolha do trajeto funciona

O método `atender_solicitacoes()` verifica inicialmente se há chamada para o andar atual e, nesse caso, a atende sem mover o elevador.

Enquanto houver solicitações pendentes:

1. Identifica a solicitação com a menor distância absoluta em relação ao andar atual, usando `min()` e uma função `lambda`.
2. Em caso de empate entre distâncias, escolhe o andar **mais alto**: isso favorece a subida quando há uma opção acima e outra abaixo à mesma distância.
3. Se a chamada escolhida está acima da posição atual, define como destino o **maior andar solicitado**; caso contrário, o **menor andar solicitado**.
4. Chama `mover_para(destino)`. Ao percorrer os andares, esse método atende e remove as solicitações encontradas no caminho.
5. Repete a decisão até esvaziar a lista.

Essa é uma **heurística simples de atendimento por direção**, não uma garantia matemática do menor trajeto possível em todos os cenários. As chamadas são consideradas conforme a lista existente durante a execução sequencial da demonstração.

### 4. Desenvolvimento em seis etapas

| Etapa | Implementação | Conceitos praticados |
| --- | --- | --- |
| 1 | Criação da classe e inicialização dos atributos. | Classe, objeto, `__init__`, `self`, atributos. |
| 2 | Método `chamar()` para registrar solicitações sem duplicação. | Métodos, parâmetros, manipulação do estado. |
| 3 | Método `mover_para()` para subida e descida andar a andar. | Comportamento do objeto, condicionais, `while`. |
| 4 | Detecção e mensagem de paradas intermediárias. | Consulta aos atributos, decisões a partir do estado. |
| 5 | Remoção de solicitações atendidas. | Atualização do estado e consistência dos dados. |
| 6 | Método `atender_solicitacoes()` para definir a ordem das viagens. | Separação de responsabilidades e reutilização de métodos. |

### 5. Exemplo de execução

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

### 6. Conceitos de Programação Orientada a Objetos

**Classe e objeto.** `Elevador` é a classe que descreve como um elevador funciona; `elevador = Elevador()` cria um objeto concreto dessa classe.

**Atributos.** `andar_atual`, `direcao` e `solicitacoes` armazenam o estado de cada instância. A lista é criada dentro de `__init__`, de modo que objetos diferentes possuam listas próprias.

**Métodos.** `chamar()`, `mover_para()` e `atender_solicitacoes()` definem comportamentos que atuam sobre os atributos do elevador.

**`self`.** É a referência à própria instância. Ao escrever `self.andar_atual`, o método acessa o andar daquele objeto específico.

**Inicialização.** `__init__` estabelece o estado inicial quando o objeto é criado.

**Abstração.** A movimentação física do elevador é representada por mudanças nos atributos e mensagens de texto, sem necessidade de motor, sensores ou interface gráfica.

**Organização de responsabilidades.** `atender_solicitacoes()` decide para onde ir, enquanto `mover_para()` executa o trajeto e as paradas. Essa divisão evita repetir a lógica de deslocamento.

**Encapsulamento (parcial).** As ações principais são organizadas em métodos, mas os atributos continuam públicos e podem ser alterados diretamente, como acontece na demonstração com `elevador.andar_atual = 4`. Portanto, o projeto **não** implementa encapsulamento restritivo com atributos privados ou propriedades.

**Ainda não utilizados na Aula 12:** herança e polimorfismo. Esses recursos não são necessários para o escopo dessa versão.

As estruturas `if`, `while`, listas, `min()`, `max()` e `lambda` fazem parte da lógica de programação em Python e são empregadas dentro dos métodos da classe.

### 7. Como executar

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

#### Execução da interface interativa

Para utilizar o elevador por meio de perguntas e respostas no terminal, execute na pasta do projeto:

```bash
python simulador.py
```

Essa execução cria um elevador no andar `0` e permite registrar chamadas interativamente. Já `python elevador.py` permanece como demonstração do algoritmo com as chamadas predefinidas da seção 5. Não são necessárias bibliotecas externas.

### 8. Interface interativa de terminal

A interface de `simulador.py` conduz o usuário pelas seguintes etapas:

1. Exibe o andar atual e solicita uma opção: `subir`, `descer` ou `parar`.
2. Para subir ou descer, pede um andar de destino entre `0` e `10`, compatível com o sentido escolhido.
3. Solicita confirmação com `sim` ou `não`. Uma resposta negativa cancela apenas a chamada que está sendo confirmada.
4. Pergunta se o usuário deseja adicionar outra parada antes do movimento. É possível registrar várias paradas no mesmo sentido; uma chamada já registrada é informada e não é duplicada.
5. Ao terminar o registro, atende todas as chamadas confirmadas por meio da classe `Elevador`. Se nenhuma chamada foi confirmada, informa essa condição e volta ao menu.
6. Retorna ao menu para uma nova viagem, preservando o andar em que terminou o atendimento anterior. A opção `parar` encerra a simulação entre viagens.

As paradas são coletadas antes do deslocamento, sempre em relação ao andar atual. A ordem de digitação não determina a ordem de atendimento: a classe aplica o algoritmo descrito na seção 3. Não é possível inserir novas chamadas ou interromper o movimento pelo menu durante o atendimento.

#### Validação de entradas e tratamento de exceções

- Os comandos do menu e as respostas de confirmação passam por `strip()` e `lower()`, que removem espaços nas extremidades e normalizam letras maiúsculas para minúsculas.
- O menu aceita somente `subir`, `descer` e `parar`. Outras entradas produzem uma orientação e repetem a pergunta.
- As confirmações aceitam `sim`, `não` e `nao`. Qualquer outra resposta faz a pergunta ser repetida.
- O destino é convertido com `int()`. O bloco `try/except ValueError` trata entradas que não podem ser convertidas em número inteiro, como `abc` ou `2.5`, e solicita uma nova entrada.
- Após a conversão, o destino deve estar no intervalo inclusivo de `0` a `10`. Para subir, deve ser maior que o andar atual; para descer, menor. O próprio andar atual não é aceito como destino nessa interface.
- No térreo (`0`), a opção descer é recusada; no último andar (`10`), a opção subir é recusada.

Essas verificações pertencem ao simulador. A classe `Elevador` não valida o intervalo de andares nem o tipo das chamadas recebidas diretamente por seus métodos.

#### Funções e separação de responsabilidades

| Função de `simulador.py` | Responsabilidade |
| --- | --- |
| `perguntar_sim_nao(pergunta)` | Repete a pergunta até receber uma resposta válida e retorna `True` para `sim` ou `False` para `não`/`nao`. É reutilizada na confirmação da chamada e na inclusão de outra parada. |
| `perguntar_destino(andar_atual, direcao)` | Lê e valida um destino inteiro de `0` a `10`, coerente com o andar atual e com a opção `subir` ou `descer`. Retorna o destino validado. |
| `main()` | Cria a instância de `Elevador`, apresenta o menu, coordena as perguntas, registra chamadas confirmadas e solicita o atendimento. Mantém o ciclo de viagens até o comando `parar`. |

A integração ocorre por `from elevador import Elevador`. A função `main()` utiliza `elevador.chamar(destino)` para registrar solicitações e `elevador.atender_solicitacoes()` para executar o atendimento, sem reproduzir o algoritmo de movimentação.

Essa organização separa a interação e a validação de entradas, concentradas em `simulador.py`, do estado e do comportamento do elevador, definidos em `elevador.py`. A mesma classe é reutilizada tanto na demonstração quanto no simulador. A classe ainda imprime mensagens de movimento e parada, portanto a saída textual não está totalmente separada da lógica do elevador.

O bloco `if __name__ == '__main__':` de `simulador.py` chama `main()` apenas na execução direta. Da mesma forma, importar `Elevador` não executa a demonstração de `elevador.py`.

#### Exemplo de interação no terminal

No exemplo, o usuário confirma duas paradas, nos andares `2` e `4`, e encerra após o atendimento:

```text
Simulador de elevador — andares de 0 a 10.
Digite parar entre viagens para encerrar.

Andar atual: 0
Subir, descer ou parar? subir
Qual é o andar de destino (0 a 10)? 2
Confirmar chamada para o andar 2? (sim/não) sim
Chamada confirmada para o andar: 2
Adicionar outra parada antes do movimento? (sim/não) sim
Qual é o andar de destino (0 a 10)? 4
Confirmar chamada para o andar 4? (sim/não) sim
Chamada confirmada para o andar: 4
Adicionar outra parada antes do movimento? (sim/não) não

Atendendo chamadas:
Elevador subindo - andar: 1
Elevador subindo - andar: 2
Elevador parou no 2º andar
Elevador subindo - andar: 3
Elevador subindo - andar: 4
Elevador parou no 4º andar
Elevador chegou ao andar: 4
Todas as chamadas foram atendidas.

Andar atual: 4
Subir, descer ou parar? parar
Simulação encerrada.
```

#### Relação com os conceitos de POO

O simulador utiliza uma **instância** de `Elevador` durante toda a execução: seus **atributos** preservam o estado entre viagens, e seus **métodos** registram e atendem chamadas. A interface reutiliza a **abstração** do elevador por meio desses métodos, mantendo a separação de responsabilidades apresentada na seção 6.

As funções de entrada são funções de módulo, não métodos da classe. Seu uso complementa a organização orientada a objetos, sem introduzir herança ou polimorfismo. O encapsulamento permanece parcial, pois a interface consulta diretamente os atributos públicos `andar_atual` e `solicitacoes`.

### 9. Limitações e possibilidades de evolução

**Não fazem parte da versão da Aula 12:**

- Botões externos separados para solicitar subida ou descida.
- Distinção entre chamada no andar e escolha do destino dentro da cabine.
- Limite de capacidade ou lotação.
- Validação de intervalo e tipo de andar na própria classe `Elevador`; o intervalo de `0` a `10` é validado somente pela interface.
- Interface gráfica ou controle físico do elevador.
- Inclusão de chamadas durante o movimento ou interrupção do trajeto pelo comando `parar`, que é aceito somente no menu entre viagens.
- Tratamento de encerramento da entrada (`EOFError`) ou interrupção por teclado (`KeyboardInterrupt`); o `try/except` existente trata apenas `ValueError` na conversão do destino.
- Persistência dos dados: cada nova execução do simulador começa no andar `0`.
- Múltiplos elevadores, sensores ou simulação de chamadas simultâneas.

Essas possibilidades foram discutidas como evoluções futuras. O foco da Aula 12 é compreender e implementar a lógica inicial de chamadas, movimento, paradas e atendimento, aplicando os fundamentos de POO.

---

**Repositório:** [IvoLucasLLJ/ELEVADOR_POO](https://github.com/IvoLucasLLJ/ELEVADOR_POO)
