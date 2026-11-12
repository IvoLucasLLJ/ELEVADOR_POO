# Correção da seleção de passageiros — 12/11/2026

A regressão final aprovou **92 testes, sem falhas, erros ou testes ignorados**,
com `python -B auditar_qualidade.py` (código de saída 0). A suíte levou
**81.542 s**; a auditoria inteira, **82.016 s**. Os **57 testes determinísticos**
sob `trace` também passaram. Sintaxe e compilação aprovadas pela auditoria.

| Grupo de testes (arquivos distintos) | Casos | Resultado |
| --- | ---: | --- |
| Aula 12, domínio e integração (`test_elevador`, `test_aula13`, `test_qualidade`, `TestSelecaoDominio`) | 63 | Aprovados |
| Textual/Pilot (`test_interface`, `test_qualidade_interface`, `TestSelecaoTextual`) | 17 | Aprovados |
| Execução/alternativa textual (`test_execucao`, `test_qualidade_texto`, `TestSelecaoTexto`) | 12 | Aprovados |
| Total | 92 | Aprovados |

## Causa e correções

O seletor mantinha o ID anterior sempre que essa pessoa ainda estava na cabine.
O novo teste reproduziu o defeito antes da alteração (`AssertionError: 1 != 2`).
O `Painel` agora controla a pessoa ativa: novos embarques selecionam a última
pessoa que entrou; a seleção manual permanece durante as atualizações e pode
registrar múltiplos destinos. No desembarque da pessoa ativa, a seleção passa
para alguém ainda na cabine, priorizando quem não tem destino, ou é limpa.

O painel exibe **SELECIONANDO DESTINOS PARA: Pessoa X**; botões internos e seus
marcadores correspondem exclusivamente à pessoa selecionada. Notificações
transitórias de reconstrução do seletor não alteram a escolha. Os destinos das
outras pessoas ficam preservados.

Chamadas aceitam quantidade opcional (padrão 1); a interface visual oferece
1 a 6 pessoas por chamada, e a API/comandos aceitam inteiros positivos. Cada
pessoa do grupo recebe identidade e destinos próprios, na mesma parada externa.
Chamadas duplicadas continuam sem criar novas pessoas nem modificar o FIFO.
As portas não fecham enquanto houver alguém sem destino válido; o aviso lista
os nomes de todas as pessoas pendentes. Destinos inválidos não removem o bloqueio.
O fechamento automático nas paradas internas continua condicionado à segurança.

Na primeira execução completa desta correção, ocorreu também um erro intermitente
de encerramento: um timer tentou atualizar `#estado` depois da desmontagem da tela.
Os timers agora são interrompidos na saída/desmontagem, e callbacks pendentes não
movem o domínio nem consultam widgets depois de encerrar. A regressão final inclui
um caso específico e passou sem esse erro.

Em 120×35, a área dos painéis foi reduzida de **20 para 17 linhas**; as grades
passaram de três para duas linhas de botões em larguras a partir de 110 colunas,
sem reduzir a altura de três linhas de cada botão. O histórico ocupa o espaço
restante (8 linhas na captura). Foram verificadas as telas de 120×35, 140×30 e
100×32 com passageiros, além dos redimensionamentos existentes até 32×20.
A validação visual foi feita em Textual headless, sem avaliação física de toque.

## Preservação

`elevador.py`, `simulador.py` e os dez testes da Aula 12 estão intactos, verificados
por SHA-256 antes/depois. Todos os cenários anteriores foram mantidos. A única
alteração nos testes existentes foi a expectativa obsoleta em
`test_seletor_de_pessoas_preserva_contexto`: a seleção após o segundo embarque
passou da primeira para a segunda pessoa. Os outros arquivos de testes existentes
estão idênticos aos encontrados no início desta tarefa. Foram adicionados 13 casos.
Não houve commit ou push; alterações locais anteriores foram preservadas.

## Evidências finais

- [Suíte completa](evidencias/suite_completa.log).
- [Resumo estruturado da auditoria](evidencias/auditoria.json).
- [Execução da auditoria](evidencias/correcao_passageiros_auditoria.log).
- [Testes determinísticos sob trace](evidencias/suite_cobertura_dominio.log).
- [Captura com Pessoa 2 selecionada e destinos independentes](evidencias/selecao_pessoa2_120x35.svg).
- [Medidas do layout](evidencias/selecao_layout.json).
- [Manifesto desta correção e hashes de preservação](evidencias/correcao_passageiros.json).

Executar o programa, na raiz do projeto:

```sh
python -m Aula_13_Predio.main
```

---

# Histórico da auditoria anterior

O texto abaixo foi preservado como histórico. Seus números correspondem à auditoria
anterior de 79 testes; os logs e capturas compartilhados foram atualizados pela
execução final de 92 testes descrita acima.

# ELEVADOR_POO — correções e auditoria de qualidade

Data: 12/11/2026. Ambiente: Termux/Android, Python 3.13.13 e Textual 8.2.8.

## Escopo e diagnóstico inicial

As duas fases foram executadas diretamente na pasta do projeto. Os arquivos já continham alterações locais anteriores ao trabalho. Elas foram preservadas; o diff em relação ao HEAD inclui essa implementação anterior e não representa somente esta correção. Nenhum commit, push ou publicação foi realizado.

A execução inicial dos **55 testes anteriores passou** (`Ran 55 tests in 21.835s; OK`). Mesmo assim, a reprodução direta do cenário informado terminou em `andar=5, portas=True, destinos=(6, 7)` após vinte atualizações adicionais. Isso confirmou uma lacuna nos testes: os fluxos de vários destinos fechavam as portas manualmente nas paradas intermediárias.

| Problema | Causa confirmada | Correção |
| --- | --- | --- |
| Travamento nos andares 5 e 6 | `Painel.atualizar` só fechava automaticamente a cabine **sem passageiros**. A pessoa corretamente permanecia dentro com destinos pendentes. | Prazo de fechamento nas paradas internas, independente de a cabine conter passageiros; as verificações de segurança continuam no domínio. |
| Destaque externo continuava no andar 1 | A variante visual dos botões dependia exclusivamente de `_andar_selecionado`, sem marcar a posição da cabine. | Cabeçalho explícito de posição e sinais textuais independentes para posição, seleção e pendências. |
| Área vazia entre painéis e controles | A área rolável ocupava o espaço restante, mas seu conteúdo tinha altura automática e o histórico ficava fora dela com altura fixa. | Histórico dentro da área rolável, ocupando o espaço livre; painéis com menor preenchimento e controles adaptáveis à largura. |
| Atalho Iniciar podia desfazer uma pausa | `iniciar()` sempre zerava o estado de pausa, mesmo depois do início. O botão desabilitado não impedia o atalho. | Início idempotente; a retomada acontece por Pausar/Retomar. |

## Comportamento corrigido

- No embarque externo, a pessoa precisa escolher ao menos um destino e usar **Fechar portas**. A espera permanece aberta para permitir várias escolhas; não há fechamento automático dessa etapa.
- Ao chegar a uma parada interna, o domínio abre as portas, registra o evento de atendimento e retira somente o destino atendido. A pessoa permanece dentro enquanto tiver destinos pendentes; desembarca no último destino.
- Nas paradas intermediárias, o prazo padrão é **1,5 segundo**, configurável por `--tempo-portas`. O prazo pertence à ordem da solicitação, não somente ao número do andar.
- As interfaces consultam as portas a cada aproximadamente 100 ms sem avançar o motor. O motor continua avançando no máximo um andar por atualização de movimento; no uso normal, uma vez por segundo. O prazo depende do escalonamento do terminal e não constitui garantia de tempo real.
- Fechar manualmente invalida o prazo. Uma parada posterior recebe outro prazo. Mudanças feitas diretamente pelo domínio também são reconhecidas pela identidade da solicitação na consulta seguinte.
- Pausar suspende movimento e fechamento automático. Retomar preserva o tempo que faltava para fechar. O fechamento manual continua permitido durante a pausa, sem retomar o motor.
- A conclusão da solicitação no histórico e sua remoção da fila continuam ocorrendo ao fechar as portas, preservando o contrato anterior. O atendimento do destino é registrado na chegada, antes da espera.
- Com cabine vazia, permanece o comportamento anterior de fechar na atualização seguinte do motor; o prazo de portas também pode concluir esse fechamento. Fila vazia mantém a aplicação disponível para outra chamada.

No painel, **POSIÇÃO ATUAL: ANDAR N** identifica a cabine. Nos botões, `>N` indica a posição atual, `S` indica a seleção externa e `*` indica solicitações pendentes. Exemplo durante a viagem: `1S`, `>5`, `6*`, `7*`. Os sinais podem coexistir e não dependem apenas de cores; o andar atual também recebe negrito e sublinhado.

## Alterações por arquivo nesta tarefa

| Arquivo | Alteração |
| --- | --- |
| `Aula_13_Predio/painel.py` | Tempo configurável validado, relógio monotônico injetável, prazo vinculado à solicitação, invalidação de prazo, suspensão durante pausa e pulsos sem movimento. Início idempotente. |
| `Aula_13_Predio/interface.py` | Consulta periódica das portas, posição e seleção distintas, marcadores de fila, histórico usando o espaço disponível, controles em grade e disposição adaptável. |
| `Aula_13_Predio/interface_texto.py` | Consulta das portas entre passos do motor, sem bloquear entrada; ajuda ajustada para o fechamento automático. |
| `Aula_13_Predio/main.py` | Argumento `--tempo-portas`, com erros de configuração tratados pelo parser. |
| `tests/test_qualidade.py` | 15 testes novos de domínio e integração, com relógio controlado. |
| `tests/test_qualidade_interface.py` | 6 testes novos com `App.run_test` e `Pilot`, incluindo botões, temporizadores reais, pausa e redimensionamento. |
| `tests/test_qualidade_texto.py` | 3 testes novos em subprocessos POSIX: viagem completa, configuração e entrada inválidas. |
| `auditar_qualidade.py` | Execução reproduzível da suíte, análise sintática e cobertura de linhas com ferramentas da biblioteca padrão. |
| `README.md` | Uso atualizado das portas, legenda visual, disposição da tela, configuração e comandos de auditoria. |
| `RELATORIO_QUALIDADE.md` e `evidencias/` | Relatório, logs, medições, capturas SVG e resultados estruturados. |

`Elevador`, `Pessoa`, `Predio` e `Andar` foram auditados e exercitados, sem alterações nesta tarefa: suas regras de FIFO, embarque, desembarque e destinos já realizavam as transições adequadas. A causa principal estava na coordenação automática.

Os quatro arquivos de testes anteriores não foram editados. `elevador.py` e `simulador.py` da Aula 12 foram comparados ao HEAD e continuam idênticos; os hashes estão em [analise_estatica.json](evidencias/analise_estatica.json).

## Testes executados

Resultado final: **79 testes aprovados, 0 falhas, 0 erros e 0 ignorados**. A suíte funcional completa levou **55.225 s** nesta execução. A auditoria inteira, incluindo a medição separada, levou **55.627 s**.

| Suíte | Casos | Resultado |
| --- | ---: | --- |
| `tests/test_elevador.py` — Aula 12 | 10 | Aprovados |
| `tests/test_aula13.py` — domínio e integração anteriores | 32 | Aprovados |
| `tests/test_execucao.py` — execução e alternativa textual anteriores | 7 | Aprovados |
| `tests/test_interface.py` — Textual anterior | 6 | Aprovados |
| `tests/test_qualidade.py` — domínio e integração novos | 15 | Aprovados |
| `tests/test_qualidade_interface.py` — funcionais e layout novos | 6 | Aprovados |
| `tests/test_qualidade_texto.py` — subprocessos novos | 3 | Aprovados |
| **Total** | **79** | **Todos aprovados** |

O log individual de cada teste está em [suite_completa.log](evidencias/suite_completa.log), e o resumo estruturado em [auditoria.json](evidencias/auditoria.json). Além da suíte completa, **57 testes determinísticos** de domínio/regressão foram executados sob `trace`, todos aprovados, em 0.065 s: [suite_cobertura_dominio.log](evidencias/suite_cobertura_dominio.log).

Os grupos por nível se sobrepõem: testes de domínio também exercitam integrações. A tabela acima contabiliza cada caso uma única vez por arquivo.

**Unitários:** inicialização de prédio, elevador, andares, pessoa e painel; validação de pavimentos, identificadores e duração; chamadas, duplicatas, sentidos, fila, portas, movimento por andar e destinos pendentes/atendidos. Operações inválidas são verificadas quanto à ausência de mutações.

**Integração:** `Pessoa → Elevador` na seleção, embarque e desembarque; `Painel → Pessoa → Elevador` no encaminhamento dos destinos; `Painel → Predio → Andar → Elevador` nas externas; pertencimento único de cada pessoa a um pavimento ou à cabine; UI Textual e alternativa textual acionando as mesmas regras do domínio.

**Funcionais:** a viagem **1 → 5 → 6 → 7** foi executada por cliques simulados nos botões oficiais do Textual e por comandos em processo POSIX real. Nos dois testes, somente o embarque usa fechamento manual. Os testes verificam os três destinos, atendimento em ordem, fechamentos automáticos intermediários, permanência da pessoa na cabine, desembarque no 7, fila vazia e atendimento de uma nova chamada no mesmo andar. O teste Textual utiliza o prazo padrão real de 1,5 segundo. Evidências:

- [Eventos da viagem no Textual](evidencias/viagem_textual_eventos.log).
- [Saída da viagem na alternativa textual](evidencias/viagem_alternativa_texto.log).
- [Inicialização e saída em pseudoterminal](evidencias/inicio_termux_pty.json), código de saída 0, posição inicial renderizada, saída por `q` e relatório da sessão exibido, sem traceback. O fluxo de bytes está em `inicio_termux_pty.log`.

**Regressão:** os 10 testes da Aula 12 e os 45 testes anteriores da Aula 13 foram executados sem alterações. Antes dos novos testes, a execução após a correção concluiu 55 casos em 39.461 s, todos aprovados: [regressao_apos_correcao.log](evidencias/regressao_apos_correcao.log). A Aula 12 mantém sua política original de proximidade/direção; a Aula 13 mantém FIFO global.

## Casos extremos e segurança das transições

| Cenário | Evidência / resultado |
| --- | --- |
| Destino interno igual ao andar atual | Rejeitado sem mutação; externa no andar atual atende sem deslocamento quando chega sua vez. |
| Externas duplicadas | Rejeitadas enquanto pendentes ou ativas, sem criar pessoa adicional; aceitas novamente após conclusão. |
| Chamadas opostas no mesmo andar | Solicitações distintas, atendidas conforme FIFO. |
| Entrada durante movimento | Testes com timer Textual e com entrada por descritor em subprocesso confirmam registro sem ultrapassar a solicitação ativa. |
| Entrada durante espera das portas | Acrescentada ao fim da fila, sem modificar o prazo nem os destinos existentes. |
| Entrada junto ao fechamento | Testes imediatamente antes e depois do fechamento verificam fila e continuidade. Fechar é uma operação síncrona atômica no laço da simulação; não existe animação nem estado físico intermediário de fechamento. |
| Fila vazia e nova chamada | Retorna a ocioso; registra e atende nova externa, inclusive após a viagem 1–5–6–7. |
| Pausa no movimento | Mantém posição/fila e aceita externas; retoma no próximo andar. |
| Pausa com portas abertas | Não fecha automaticamente durante a pausa; preserva a fração de prazo restante, inclusive após pausas repetidas. |
| Fechamento manual durante pausa | Fecha portas sem retomar o motor. |
| Destinos internos repetidos | Não duplicam destinos nem registros da mesma pessoa. Destino compartilhado vincula outra pessoa à parada existente. |
| Vários destinos e várias pessoas | Mantém identidade e localização; desembarque depende dos destinos de cada pessoa, respeitando a fila global. |
| Andares negativos ou superiores a 10 | Rejeitados no domínio e nos comandos. Também testados `bool`, texto, `None` e valores fracionários nas APIs numéricas. |
| Configuração inválida | Duração negativa, não numérica, infinita ou NaN rejeitada; CLI encerra com mensagem e código 2, sem traceback. |
| Entrada textual inválida e EOF parcial | Rejeita comandos inválidos e processa a última linha sem quebra de linha; EOF e Ctrl+C encerram corretamente. |
| Encerramento durante viagem | Saída Textual não continua movimentando após fechar a aplicação; relatório conserva destinos pendentes. Alternativa textual também trata interrupção. |
| Prazos obsoletos | Fechar manualmente e abrir outra parada não reutiliza o prazo anterior; também verificado com fechamento direto no domínio e em novo embarque. |
| Pulsos repetidos | Dez consultas após o prazo não duplicam histórico nem movimentam; os callbacks das duas interfaces são serializados, sem threads para fechar portas. |
| Portas abertas | Movimento impedido; os testes comparam posição e estado antes/depois de várias tentativas. |

## Layout e aproveitamento do terminal

Foram executadas nove etapas de tamanho, incluindo o retorno à disposição inicial: **120×50, 120×35, 100×24, 85×28, 84×28, 60×24, 44×32, 32×20 e 120×50**. As medidas são colunas × linhas, não pixels físicos do tablet.

Os testes verificam igualdade proporcional dos painéis quando lado a lado, empilhamento abaixo de 85 colunas, grade de três colunas abaixo de 40, limites dos controles inferiores, largura suficiente para seus rótulos e acesso ao histórico por rolagem. Em 120×50, o histórico ocupa **19 linhas** em vez das seis linhas fixas anteriores, sem rolagem externa. Em terminais baixos ou estreitos, a área central rola e os controles inferiores permanecem visíveis. A navegação por foco/Enter no painel interno de 44×32 também é coberta pela suíte anterior.

Há medições em [layout_medidas.json](evidencias/layout_medidas.json) e capturas SVG `evidencias/layout_LARGURAxALTURA.svg`. As capturas representam a renderização automatizada, incluindo a rolagem até o histórico. Não comprovam toque físico, escala de fonte ou aparência na tela real do tablet. Não foi estabelecido suporte para dimensões inferiores a 32×20.

## Análise estática e manutenibilidade

- **Sintaxe:** AST e compilação de 19 fontes aprovados, incluindo fontes da aplicação, testes e auditor. `compileall` também executado com sucesso; `git diff --check` sem erros.
- **Responsabilidades:** `Elevador` conserva estado físico e regras; `Pessoa` conserva identidade e destinos; `Painel` coordena comandos e tempo; interfaces recebem entrada e renderizam estado. A correção não duplicou regras de embarque, FIFO ou desembarque nas interfaces.
- **Encapsulamento:** coleções de consulta são tuplas ou cópias; propriedades não têm setters para estado crítico. Atributos internos entre entidades continuam usando a convenção `_`, apropriada ao exercício, sem alteração direta pela interface.
- **Duplicação:** há dois algoritmos de elevador por exigência das aulas, preservados como implementações independentes. Não se tentou unificá-los. A temporização fica em um único coordenador compartilhado pelas duas interfaces.
- **Complexidade:** o fechamento usa um identificador de solicitação e um prazo monotônico, sem criar callbacks descartáveis por parada. Métodos de atualização continuam curtos e não bloqueiam uma viagem inteira. Não foram introduzidas abstrações para satisfazer métricas.
- **Exceções:** entradas são tratadas por `ValueError`, configuração por `argparse`, ausência de Textual por `ModuleNotFoundError` específico e interrupção textual por `KeyboardInterrupt`. A análise AST não encontrou capturas genéricas de `Exception`/`BaseException` nos fontes da aplicação.
- **Dependências:** não foram instalados pacotes novos. Textual permanece fixado em 8.2.8. Seus requisitos ativos e transitivos foram conferidos pelos metadados instalados e estão satisfeitos: [dependencias_projeto.log](evidencias/dependencias_projeto.log).
- **Ambiente global:** `python -m pip check` retornou código 1 por incompatibilidade de plataforma dos pacotes globais `pycryptodomex`, `Brotli`, `numpy` e `scipy`. Eles não integram os requisitos ativos do aplicativo. O diagnóstico está em [dependencias_ambiente.log](evidencias/dependencias_ambiente.log); o ambiente global não é declarado íntegro.
- **Ferramentas disponíveis:** `coverage`, `ruff` e `pyflakes` não estavam instalados. Usaram-se `unittest`, AST, compilação, `trace` e os mecanismos oficiais de teste do Textual. Não foi executado um linter externo, nem feita análise formal de tipos.

## Cobertura de testes

A medição usa `trace` da biblioteca padrão, iniciada **antes dos imports do domínio**. Somente as três suítes determinísticas (`test_elevador`, `test_aula13`, `test_qualidade`) entram na instrumentação; a suíte completa, incluindo GUI e subprocessos, roda separadamente sem `trace`. Não há medição de ramos, condições ou código executado em processos filhos.

| Módulo medido | Linhas exercitadas / executáveis | Cobertura de linhas |
| --- | ---: | ---: |
| `Aula_13_Predio.andar` | 23 / 23 | 100.00% |
| `Aula_13_Predio.elevador` | 160 / 162 | 98.77% |
| `Aula_13_Predio.painel` | 111 / 113 | 98.23% |
| `Aula_13_Predio.pessoa` | 61 / 61 | 100.00% |
| `Aula_13_Predio.predio` | 39 / 39 | 100.00% |
| `elevador` | 43 / 54 | 79.63% |

O núcleo da Aula 13 (domínio e `Painel`) atingiu **98.99% (394/398 linhas)**. Somando o elevador legado da Aula 12, o conjunto medido atingiu **96.68% (437/452 linhas)**. Esses valores **não representam cobertura do sistema inteiro**, pois a apresentação e os pontos de entrada ficaram fora da medição.

Trechos não exercitados nas suítes instrumentadas:

- `Aula_13_Predio/elevador.py:54`: apresentação da situação com portas abertas; exercitada pelos testes funcionais fora da medição.
- `Aula_13_Predio/elevador.py:179`: rejeição de fechar portas já fechadas; exercitada pelo teste funcional `test_erro_de_entrada_exibido_sem_encerrar`, fora da medição.
- `Aula_13_Predio/painel.py:44,46`: textos de situação antes de iniciar e durante pausa; exercitados pela interface fora da medição.
- `elevador.py:58–71`: bloco de demonstração executado somente como programa principal da Aula 12. Os dez testes verificam sua classe; não executam essa demonstração.

As linhas de execução do núcleo responsáveis por movimento, FIFO, vínculo e conclusão de destinos, permanência/desembarque e prazos automáticos foram exercitadas. Os testes também verificam invariantes por asserções; os percentuais não substituem essas verificações.

`interface.py`, `interface_texto.py`, `main.py` e `simulador.py` não tiveram percentual medido. As duas interfaces e a entrada da Aula 13 têm testes funcionais reais, mas executados fora do instrumento de cobertura. `__init__.py` contém somente uma docstring, sem regras de negócio. Os percentuais de 100% em algumas classes são resultados de linhas, não comprovação de todas as combinações possíveis de estado.

Arquivos com contagem por linha e marcação `>>>>>>` das ausências: [cobertura/](evidencias/cobertura/). Resumo da ferramenta: [cobertura_resumo.txt](evidencias/cobertura_resumo.txt). Não foram acrescentados testes para executar demonstrações ou elevar artificialmente a porcentagem.

## Pendências e limites da evidência

- A interação física por toque no tablet, a configuração do Termux para traduzir toque em mouse e a legibilidade com a fonte real escolhida pelo usuário **não foram validadas**. Foram executados Pilot, teclado simulado, processos POSIX e pseudoterminal real do ambiente.
- A aplicação usa estados lógicos de portas abertas/fechadas. Não modela sensores, animação de portas nem controle de equipamento físico; chamadas junto ao fechamento são avaliadas na serialização dos comandos.
- A primeira tentativa de medir toda a GUI sob `trace` apresentou uma falha no teste de encerramento durante movimento e forte lentidão. Foi interrompida, sem ser contabilizada como suíte aprovada. Seu registro parcial está em [tentativa_trace_integral_parcial.log](evidencias/tentativa_trace_integral_parcial.log), e a interrupção intencional em [tentativa_trace_integral_diagnostico.log](evidencias/tentativa_trace_integral_diagnostico.log). A interferência da instrumentação é a explicação operacional; não há traceback final daquela asserção porque a execução foi interrompida. A suíte funcional final é executada sem `trace`; a cobertura é medida separadamente com relógio controlado.
- Os avisos de depuração do asyncio sobre tarefas acima de 100 ms aparecem nos logs do Termux, sobretudo com instrumentação. Não constituem reprovação por si só. Não foi feito benchmark de desempenho nem teste de carga prolongada.
- Dados e histórico permanecem somente em memória e não têm limite de retenção na sessão, conforme o projeto existente. Encerrar durante viagem conserva pendências no relatório, sem persistência para outra execução.
- A checagem global de pacotes continua com os avisos de plataforma descritos acima; não foi alterada uma instalação alheia ao aplicativo.

Nos cenários críticos executados, a versão final não apresentou falhas conhecidas. As limitações acima continuam explícitas e não foram convertidas em afirmações de validação física.

## Comandos para iniciar e repetir a validação

Na pasta do projeto:

```sh
cd /storage/emulated/0/Documents/POO/Aula_12_Elevador
python -m Aula_13_Predio.main
```

Configuração explícita do prazo ou alternativa sem Textual:

```sh
python -m Aula_13_Predio.main --tempo-portas 1.5
python -m Aula_13_Predio.main --texto --tempo-portas 1.5
```

Reprodução: selecione o andar externo 1, pressione SUBIR e Iniciar; aguarde o embarque; selecione 5, 6 e 7 no painel interno e pressione Fechar portas uma vez. As paradas internas prosseguem automaticamente.

```sh
python -B -m unittest discover -s tests -v
python auditar_qualidade.py
```

O primeiro comando executa a suíte completa. O segundo também produz logs, JSON e cobertura em `evidencias/`. A medição de cobertura é limitada às suítes determinísticas do domínio para preservar os tempos da validação da interface.

Referências dos mecanismos empregados: [testes oficiais do Textual](https://textual.textualize.io/guide/testing/) e [layout do Textual](https://textual.textualize.io/guide/layout/). A execução foi feita contra a versão instalada 8.2.8.
