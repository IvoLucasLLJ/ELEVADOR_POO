> **Aula 15 — contextualização desta entrega:** as seções 1 a 8 abaixo reproduzem o relatório histórico recebido, referente à validação em Linux/Python 3.12.14. Seus 103 testes, 5.137 operações, capturas e caminhos de evidências não são resultados ou arquivos desta preparação. A validação local atual, com uma suíte nova e independente, está na seção 9 e em `evidencias/VALIDACAO_LOCAL.md`.

# Elevador SOLID — validação final da etapa 4

**Conclusão:** os 19 critérios de aceitação foram verificados e atendidos no escopo exercitado. O programa final conserva os mesmos bytes aprovados na etapa 3. A entrega mantém um único arquivo de produção e inclui guia didático, testes e evidências reproduzíveis.

**Referência de data:** 12/11/2026, horário de Brasília. A revisão não realizou alterações no GitHub nem substituiu a entrega anterior.

## 1. Base, objetivo e alterações desta etapa

A base funcional é o arquivo único da Aula 14, preservado em `referencia/elevador_original.py`. O V4 fornecido pelo professor e os materiais “POO — Princípios” e “Elevador — SOLID Exemplo” orientaram o diagnóstico e a divisão de responsabilidades. O V4 não substituiu a base funcional do aluno.

A etapa 3 implementou nove classes concretas e três protocolos: fila, movimento e passageiros receberam responsabilidades próprias; o elevador tornou-se o coordenador desses componentes; as impressões foram separadas das entidades e do painel. Continuam onze pavimentos, um elevador, FIFO, grupos, identidade das pessoas, múltiplos destinos, portas, pausa e as mesmas interfaces.

Na etapa 4 foram revisados código, contratos, testes e capturas; construída a matriz de aceitação; escrito o guia de explicação; e verificada uma cópia extraída do pacote. Não houve alteração de código de produção nem de testes nesta etapa. Não foi acrescentada funcionalidade.

## 2. Resultados consolidados

| Verificação | Resultado | Evidência |
|---|---|---|
| Suíte completa da etapa 3, aplicável aos mesmos bytes finais | 103 testes; 50,487 segundos; OK. | `evidencias/08_suite_final.log` |
| Comparação entre original e refatorado | 5.137 operações em dez sequências determinísticas, sem divergências observadas. | `tests/test_equivalencia.py`, `evidencias/equivalencia.json` |
| Critérios de aceitação | 19 associados a testes existentes e aprovados. | Matriz abaixo e `evidencias/matriz_aceitacao.json` |
| Preservação estrutural | Interface visual, três funções textuais e 18 métodos remanescentes do painel com AST idêntica à referência. | `evidencias/estrutura.json` e `estrutura_etapa4.json` |
| Inspeção das capturas | Oito tamanhos de terminal examinados; limites de telas pequenas registrados. | `evidencias/inspecao_visual/` |
| Execução a partir do pacote extraído | Sete testes de entrada/execução aprovados em 2,032 segundos; auditoria estrutural aprovada. | `evidencias/09_pacote_extraido.log`, `verificacao_pacote.json` |
| Integridade da entrega | Código comparado byte a byte com a etapa 3; arquivos identificados no manifesto; ZIP conferido. | `MANIFESTO_SHA256.json` |

Os sete testes da etapa 4 fazem parte dos 103; não devem ser somados para anunciar 110 cenários diferentes. As 5.137 operações também não representam testes independentes adicionais. A suíte completa não foi repetida porque código e testes permaneceram idênticos; a verificação suplementar tratou da execução após empacotamento.

Os logs de desenvolvimento foram preservados. Houve um erro de organização de testes durante a etapa 3 e uma chamada antiga de relatório em um subprocesso de teste. Ambos foram corrigidos antes da execução final aprovada. O relatório da etapa 3 registra esses episódios.

## 3. Matriz dos 19 critérios

Os nomes abaixo correspondem a métodos nos arquivos `tests/<módulo>.py`. Sua existência e aprovação foram conferidas contra o código dos testes e o log final. “Atendido” significa atendido pelos cenários, inspeções e ambiente registrados; não significa prova universal de correção.

| Critério | Resultado esperado | Evidências principais — módulo.método |
|---|---|---|
| **CA01 — atendido** | Composição inicial: um elevador, onze pavimentos, posição 0 e fila vazia. | `test_aula13.test_composicao_inicial`; `test_aula13.test_predio_rejeita_configuracoes_diferentes` |
| **CA02 — atendido** | Chamadas válidas antes do início e durante movimento. | `test_aula13.test_antes_do_inicio_nao_movimenta`; `test_aula13.test_cenario_c_chamada_durante_movimento`; `test_execucao.test_loop_real_aceita_comando_durante_movimento` |
| **CA03 — atendido** | Repetição externa pendente/ativa sem novos registros ou pessoas. | `test_aula13.test_cenario_e_duplicata_pendente_ativa_e_concluida`; `test_contratos_solid.test_duplicacao_ativa_nao_consume_ordem` |
| **CA04 — atendido** | Sentidos opostos no mesmo pavimento geram chamadas distintas. | `test_aula13.test_cenario_f_chamadas_opostas`; `test_contratos_solid.test_tipos_e_sentidos_definem_chaves_distintas` |
| **CA05 — atendido** | Passo máximo de um andar e limites 0 a 10. | `test_contratos_solid.test_subida_descida_e_chegada_no_proprio_pulso`; `test_contratos_solid.test_abertura_em_movimento_e_pavimentos_invalidos` |
| **CA06 — atendido** | Portas abertas e pausa bloqueiam deslocamento automático. | `test_aula13.test_portas_abertas_impedem_movimento`; `test_aula13.test_pausa_preserva_movimento_e_aceita_externas`; `test_qualidade.test_pulso_de_portas_nunca_move` |
| **CA07 — atendido** | Embarque das pessoas corretas, com identidade e localização preservadas. | `test_contrato_passageiros.test_embarque_exige_contexto_e_preserva_identidade`; `test_aula13.test_pertencimento_unico_em_fluxo_completo` |
| **CA08 — atendido** | Fechamento rejeitado enquanto houver passageiro sem destino. | `test_aula13.test_fechar_exige_destino_sem_mutacao`; `test_selecao_passageiros.test_grupo_destinos_individuais_alternancia_e_bloqueio` |
| **CA09 — atendido** | Vários destinos por pessoa e permanência nas etapas intermediárias. | `test_aula13.test_cenario_d_multiplos_destinos_mesma_identidade`; `test_contrato_passageiros.test_etapa_intermediaria_nao_autoriza_desembarque` |
| **CA10 — atendido** | Destino compartilhado em um registro interno e ordem global FIFO. | `test_aula13.test_destino_compartilhado_preserva_ambas_pessoas`; `test_equivalencia.test_parada_compartilhada_e_conclusao_no_fechamento` |
| **CA11 — atendido** | Resultados e erros preservados, inclusive seleção ativa antes da rejeição. | `test_aula13.test_duplicata_interna_nao_modifica_pessoa`; `test_equivalencia.test_selecao_em_erro_e_prioridade_das_validacoes_preservadas` |
| **CA12 — atendido** | Conclusão e histórico somente no fechamento aceito, uma vez por pedido. | `test_contratos_solid.test_ordem_fifo_e_conclusao_exatamente_uma_vez`; `test_equivalencia.test_parada_compartilhada_e_conclusao_no_fechamento` |
| **CA13 — atendido** | Desembarque no andar correto e pertencimento físico único. | `test_contrato_passageiros.test_desembarque_exige_portas_e_ultimo_andar`; `test_aula13.test_pertencimento_unico_em_fluxo_completo` |
| **CA14 — atendido** | Pausa conserva tempo restante; prazo antigo não fecha outra parada. | `test_qualidade.test_pausa_preserva_tempo_restante_e_nao_move`; `test_qualidade.test_prazo_antigo_nao_fecha_parada_posterior`; `test_qualidade.test_fechamento_direto_no_dominio_tambem_invalida_prazo` |
| **CA15 — atendido** | Consultas não expõem coleções e registros internos para alteração. | `test_contratos_solid.test_consultas_e_lista_de_entrada_nao_expoem_estado`; `test_aula13.test_propriedades_protegidas`; `test_contrato_passageiros.test_grupo_preserva_ordem_e_consulta_protegida` |
| **CA16 — atendido** | Seleção manual e prioridade dos novos embarques preservadas. | `test_selecao_passageiros.test_dois_andares_selecao_automatica_e_manual`; `test_selecao_passageiros.test_novo_embarque_seleciona_segunda_pessoa` |
| **CA17 — atendido** | Comandos, ações e disposição visual preservados. | `test_qualidade_interface.test_redimensionamento_distribuicao_e_rolagem`; `test_interface.test_tela_estreita_rolagem_e_teclado`; `test_selecao_passageiros.test_layout_horizontal_compacto_com_grupo` |
| **CA18 — atendido** | Encerramento para atualizações, gera relatório e não acrescenta persistência. | `test_qualidade_interface.test_encerrar_durante_viagem_cancela_timers_da_interface`; `test_selecao_passageiros.test_pulsos_pendentes_apos_sair_nao_movem_ou_atualizam_widgets`; `test_qualidade.test_saida_registra_viagem_incompleta` |
| **CA19 — atendido** | Arquivo único, importação segura e argumentos de execução válidos. | `test_execucao.test_importar_nao_executa_interface_nem_carrega_aula12`; `test_execucao.test_fallback_sem_site_packages_e_varias_linhas_eof`; `test_qualidade_texto.test_configuracao_cli_invalida_sem_traceback` |

CA17 também conta com comparação estrutural da interface e inspeção das capturas. Em CA18, a ausência de persistência adicional foi conferida na revisão do código e no fluxo de encerramento. Em CA19, a execução real foi feita em Python 3.12.14/Linux; a análise sintática para Python 3.10 não estende automaticamente essa validação a outros ambientes.

## 4. Revisão das fronteiras e dos contratos

`FilaFIFO` guarda registros, sequência e histórico. `ControladorMovimento` guarda posição, direção e portas. `GerenciadorPassageiros` guarda os passageiros e recebe a função de localizar um andar. `Elevador` mantém referências a esses colaboradores, a função de criação de solicitantes e os eventos; não duplica o estado físico ou as coleções dos colaboradores.

A fila oferece cópias dos registros, e a consulta pública usa IDs. As visões internas preservam referências às mesmas pessoas. Tuplas protegem a estrutura das coleções, sem tornar imutáveis os objetos contidos nelas. Métodos internos de registro e alteração de destinos pressupõem validação anterior pelo coordenador; não são apresentados como APIs independentes que aceitam qualquer entrada.

A substituição por contrato exige preservar comportamento: FIFO, identidades, rejeições, passo físico e conclusão correta. O teste com adaptadores de superfície restrita confirma que o coordenador usa as operações contratadas; ele envolve implementações existentes e não demonstra uma segunda política de atendimento. Os protocolos não são prova automática de Liskov nem foi executada análise estática de tipos.

O código conserva relações concretas entre as entidades. A melhoria SOLID é localizada e verificável; não se afirma desacoplamento absoluto nem que qualquer funcionalidade futura possa ser adicionada sem editar classes.

## 5. Inspeção visual e alcance

As capturas SVG foram produzidas pelo modo de teste do Textual. Na etapa 4, foram renderizadas para PNG e examinadas. As imagens são representações do terminal de teste, não fotografias ou capturas do tablet do aluno.

| Tamanhos em caracteres | Observação |
|---|---|
| 120 × 50 e 120 × 35 | Painéis lado a lado, ações visíveis e área de eventos ocupando o espaço disponível. Sem rolagem vertical do conteúdo nesses estados. |
| 100 × 24 e 85 × 28 | Painéis lado a lado; altura reduzida exige rolagem. As capturas mostram o conteúdo deslocado para exibir os eventos. |
| 84 × 28, 60 × 24 e 44 × 32 | Painéis organizados verticalmente e ações em duas linhas. Parte dos controles exige rolagem. |
| 32 × 20 | Ações principais permanecem visíveis; título abreviado e parte do rodapé/atalhos truncada. A área central é muito reduzida e exige rolagem. |

As capturas foram feitas depois de tornar a área de eventos visível; controles superiores fora da imagem não significam controles removidos. As verificações automáticas conferem posição e dimensões dos botões de ação, distribuição dos painéis e alcance dos eventos. Há teste adicional de navegação por foco e teclado em tela estreita.

A preservação do layout foi confirmada. A experiência de toque, o teclado virtual, a fonte e o tamanho efetivo do terminal no Android não foram examinados. A apresentação em 32 × 20 tem limitações de leitura já presentes no layout preservado; não foi tratada como uma tela em que tudo cabe ao mesmo tempo.

## 6. Compatibilidade e comportamentos explicitamente preservados

| Uso anterior | Uso nesta versão |
|---|---|
| `Predio()` e `Painel(Predio())` | Permanecem válidos. |
| Construção direta `Elevador(predio)` | Construtor recebe fila, movimento, passageiros e função de criar solicitantes; montagem padrão em `_montar_elevador`. |
| `pessoa.mostrar_estado()` | `mostrar_estado_pessoa(pessoa)` |
| `painel.mostrar_fila()` | `mostrar_fila(registros)` |
| `painel.mostrar_registros()` | `mostrar_registros(pessoas, historico, fila)` |

A API de apresentação teve essas migrações planejadas. Seus consumidores foram ajustados na etapa 3 sem remover as asserções correspondentes. As duas esperas de 0,2 segundo do teste de redimensionamento corrigem a sincronização do teste identificada na etapa 1; não alteram o CSS.

Permanece o efeito de seleção diante de erro: informar o ID válido de outra pessoa junto com destino inválido pode selecionar essa pessoa antes da rejeição. Não é uma promessa de atomicidade da seleção; é um comportamento original mantido e testado.

Uma chegada abre portas e atende passageiros no mesmo pulso. A conclusão da solicitação ocorre no fechamento. A fila global pode produzir 1 → 7 → 5 mesmo quando a Pessoa 1 escolheu 5 antes de 7, porque a parada 7 já estava registrada por outra pessoa.

## 7. Ambiente e limites

A validação real utilizou **Linux x86_64, Python 3.12.14 e Textual 8.2.8**. A alternativa textual foi exercitada também com `-S`, sem pacotes externos. Seus mecanismos de entrada continuam usando recursos POSIX, como na referência.

Não houve execução desta versão em Windows nem no tablet/Termux do aluno. A sintaxe foi analisada segundo a gramática do Python 3.10; não houve execução real nessa versão. Não se afirma compatibilidade universal com plataformas, versões ou tamanhos de terminal.

Os critérios e os testes sustentam a preservação nas situações exercitadas. Não constituem prova formal de ausência de defeitos. A transferência ao ambiente final e uma execução no dispositivo permanecem atividades locais posteriores à entrega deste pacote; não foram confundidas com verificações já realizadas.

## 8. Identificação da versão e entrega

| Referência | SHA-256 |
|---|---|
| Código original da Aula 14 | `5977ffb0b5190d57e979d5d68c0ae99fe02845cb54eda97ca5881aad3dfc59bf` |
| Código final refatorado | `ed32ed76d2d4c5be1c2fea132bc8d5dd3b7a73c9f91f4231cf41d2b17f42de1f` |

O manifesto lista os arquivos do pacote e seus hashes, excluindo o próprio manifesto. O programa da raiz é a versão de uso; os checkpoints são históricos. A auditoria e os testes podem gerar novas evidências em uma execução posterior, modificando hashes desses arquivos de saída.

As quatro etapas estão consolidadas: diagnóstico, projeto, implementação e revisão final. O código anterior foi preservado; a versão final está preparada para abrir no Acode e levar ao ambiente Python/Codex do aluno. Não foram feitos commit, push, criação de branch, publicação ou alteração no GitHub.

## 9. Validação local desta preparação — Aula 15

**Data local:** 2026-11-12T23:12:00.961607-03:00. **Autor da entrega:** Ivo Lucas de Lima Júnior.

A pasta de trabalho é `/storage/emulated/0/Documents/POO/Aula_15_Elevador`. O ponto de partida desta organização continha somente o programa e este relatório. A documentação e os testes atuais foram produzidos a partir desses arquivos; não dependem de uma referência original indisponível. O histórico das seções anteriores foi conservado, sem apresentar seus resultados como nova execução.

### 9.1 Materiais e preservação

Foram criados `README.md`, `requirements.txt`, `Guia_Elevador_POO_SOLID.md`, `.gitignore`, três módulos de testes em `tests/` e os registros reais em `evidencias/`. Não há diretórios vazios ou arquivos simulando materiais históricos.

`elevador_completo.py` manteve seus **48.664 bytes** e o SHA-256 inicial/final **`ed32ed76d2d4c5be1c2fea132bc8d5dd3b7a73c9f91f4231cf41d2b17f42de1f`**. Não houve alteração de funcionamento, classes, comentários, interface ou arquitetura.

### 9.2 Execuções atuais

Ambiente: **Termux/Android aarch64, Python 3.13.13, Textual 8.2.8**, com Rich 15.0.0 presente. Não foram instalados ou atualizados pacotes.

| Comando na raiz da entrega | Resultado local |
|---|---|
| `python -B -m unittest discover -s tests -v` | **28 testes aprovados**, zero falhas/erros/omissões; 21.534 s; retorno 0. |
| `python -B -S -m unittest discover -s tests -v` | Mesmos 28 descobertos: **27 aprovados e 1 omitido**, zero falhas/erros; 3.732 s; retorno 0. |

A omissão com `-S` ocorre porque site-packages não é carregado e o teste visual não encontra Textual nesse processo. O modo textual e o domínio foram exercitados sem a biblioteca visual. As execuções não devem ser somadas como conjuntos diferentes. O teste visual normal usa `run_test()` em 120×35 e 44×32, sem capturas ou inspeção de toque. O teste de viagem textual executa um subprocesso real e sincroniza entrada com embarque e desembarque.

Os nomes e resultados dos testes estão em `evidencias/testes_termux.log` e `evidencias/testes_sem_pacotes.log`; comandos, datas e retornos em `evidencias/execucao_testes.json` e `evidencias/execucao_sem_pacotes.json`; versões em `evidencias/ambiente_inicial.json`; integridade em `evidencias/integridade_final.json`. O detalhamento do alcance está em `evidencias/VALIDACAO_LOCAL.md`.

### 9.3 Limites e integração pendente

Os **103 testes e as 5.137 operações continuam sendo resultados históricos**, não reproduzidos aqui. Não se executou comparação com a Aula 14, auditor histórico, inspeção física de tela, análise estática de tipos, teste em Windows ou execução em Python 3.10. A análise da gramática 3.10 não amplia automaticamente a validação real. Os testes novos não são prova formal nem substituem as evidências históricas citadas nas seções 1 a 8, ausentes desta entrega.

Não houve falha observada na suíte local. O teste do efeito de seleção diante de destino inválido e o guia explicitam o comportamento existente; nenhuma asserção foi enfraquecida para aprovar o programa. O ajuste da mensagem de skip esclarece a indisponibilidade do Textual sob `-S`.

A pasta está fora de um repositório Git (retorno 128 na consulta). O `.gitignore` local protege contra caches, bytecode, ambientes virtuais e temporários e preserva documentação, testes e evidências. A inclusão no repositório existente permanece posterior; a entrega não foi movida e não se inicializou outro Git. **Não houve commit nem push.**
