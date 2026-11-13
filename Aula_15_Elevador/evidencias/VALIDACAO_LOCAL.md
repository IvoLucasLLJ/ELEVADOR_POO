# Validação local — preparação da Aula 15

Registro produzido em 2026-11-12T23:12:00.961607-03:00. Esta validação usa os testes escritos nesta preparação a partir dos dois arquivos disponíveis. Não recupera nem reproduz os 103 testes e as 5.137 operações do relatório histórico.

## Ambiente efetivamente utilizado

- Pasta: `/storage/emulated/0/Documents/POO/Aula_15_Elevador`.
- Termux/Android, arquitetura `aarch64`; identificação do Python: `Android-16-aarch64-64bit-ELF`.
- Python **3.13.13**, executável `/data/data/com.termux/files/usr/bin/python`.
- Textual **8.2.8**, Rich **15.0.0**, pip **26.1.2**; nenhum pacote instalado ou atualizado.
- Versões completas, hash inicial e resultados dos comandos Git: [ambiente_inicial.json](ambiente_inicial.json).

## Comandos executados e resultados

Os comandos foram executados na raiz da entrega:

```sh
python -B -m unittest discover -s tests -v
python -B -S -m unittest discover -s tests -v
```

| Execução | Resultado observado | Tempo informado por unittest | Evidência |
|---|---|---|---|
| Ambiente normal, Textual instalado | **28 testes aprovados**, zero falhas/erros/omissões; retorno 0. | 21.534 s | [saída integral](testes_termux.log), [comando e datas](execucao_testes.json) |
| Mesmo conjunto com `-S` | **27 aprovados e 1 omitido**, zero falhas/erros; retorno 0. | 3.732 s | [saída integral](testes_sem_pacotes.log), [comando e datas](execucao_sem_pacotes.json) |

A omissão com `-S` é esperada: o processo não carrega site-packages e não encontra Textual para executar a verificação visual. A biblioteca continua instalada no ambiente normal. Foi ajustado apenas o texto explicativo desse skip e repetida a execução com `-S`, sem modificar asserções. As duas execuções exercitam a mesma suíte; não representam 56 testes distintos. Não houve falha observada do programa ou dos testes nesta preparação.

## O que foi exercitado

| Arquivo | Cenários |
|---|---|
| `tests/test_dominio.py` | 19 testes: composição, limites, chamadas e validação sem mutação, FIFO, duplicações pendentes/ativas/concluídas, sentidos opostos, início, movimento, portas, identidade/localização, destinos individuais/compartilhados/múltiplos, fechamento bloqueado, pausa, preservação do prazo das portas, consultas protegidas, histórico e configuração. |
| `tests/test_execucao.py` | 8 testes: importação silenciosa em processo isolado que só recebe uma cópia do programa, sintaxe e gramática 3.10, ajuda, orientação sem Textual, argumentos inválidos, várias linhas/EOF, entradas rejeitadas e viagem textual real. |
| `tests/test_interface_visual.py` | 1 teste com dois tamanhos, **120×35** e **44×32**: montagem, disponibilidade inicial de controles, disposição horizontal/vertical e atalhos de início/pausa/retomada/saída, usando `Textual.run_test()`. |

A viagem textual roda um subprocesso com `-B -I -S -u`, entrada/saída por pipes POSIX e espera pelas mensagens reais antes de enviar os comandos seguintes. Verifica embarque no andar 0, destino 2, desembarque da mesma sessão, conclusão e fila vazia ao sair. Não é uma sessão com toque ou PTY.

Os testes de temporização do domínio usam `Painel(..., relogio=...)`, uma dependência já aceita pelo programa. Nenhum estado privado de produção é reescrito para obter aprovação. O módulo visual usa a API de teste do Textual já instalado.

## Integridade e conservação

SHA-256 inicial e final de `elevador_completo.py`:

```text
ed32ed76d2d4c5be1c2fea132bc8d5dd3b7a73c9f91f4231cf41d2b17f42de1f
```

O arquivo tem **48.664 bytes** e permaneceu idêntico, incluindo comentários, interface e implementação. A conferência detalhada e os hashes dos materiais desta entrega estão em [integridade_final.json](integridade_final.json). O texto recebido do relatório foi preservado integralmente entre uma nota de contextualização e a nova seção 9.

## Alcance e limites

- Os cenários novos não equivalem à suíte histórica, à matriz histórica completa, a uma medição de cobertura ou a uma prova de ausência de defeitos.
- Não foi usada uma referência original da Aula 14 nem executado auditor de comparação estrutural ou comportamental com ela. Não foram produzidas capturas ou recuperados logs antigos. As referências históricas a esses materiais no relatório não indicam que eles existam nesta pasta.
- A gramática Python 3.10 foi analisada, mas só houve execução real em Python 3.13.13 neste ambiente. Windows e outras versões não foram validados.
- A interface visual foi exercitada automaticamente sem tela física. Toque, teclado virtual, fonte do terminal e visibilidade completa em todos os tamanhos não foram inspecionados.
- O modo textual usa POSIX. O EOF encerra a sessão, mesmo havendo chamadas pendentes.
- As coleções públicas são protegidas por tuplas/cópias, mas os objetos contidos permanecem mutáveis. A seleção de pessoa pode ocorrer antes da rejeição de destino; o teste preserva esse comportamento.

## Preparação para Git

`git rev-parse --show-toplevel` e `git status --short` retornaram **128**: esta pasta não integra um repositório existente. Isso é uma situação de integração, não uma falha do simulador. Não há regras de um repositório ancestral a aplicar aqui. O `.gitignore` criado na entrega exclui `__pycache__`, `*.py[cod]`, `.venv`, `venv`, `env`, caches de ferramentas e temporários; logs, JSON, testes e Markdown continuam incluíveis.

A integração ao repositório existente continua sendo uma etapa posterior. Conferir o diff e as regras do repositório de destino antes de versionar. A entrega permaneceu nesta pasta, sem Git aninhado, alteração de outras aulas, commit ou push.
