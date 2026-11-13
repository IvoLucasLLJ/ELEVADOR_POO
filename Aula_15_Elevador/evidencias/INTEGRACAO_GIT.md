# Integração local da Aula 15 ao repositório

**Data:** 2026-11-12T23:21:01.154802-03:00. A Aula 15 foi copiada, sem apagar ou alterar a origem. Esta etapa prepara a revisão e o versionamento; não houve commit, push ou publicação.

## Origem e destino

- Origem intacta: `/storage/emulated/0/Documents/POO/Aula_15_Elevador` (16 arquivos, conferidos por SHA-256 antes/depois).
- Raiz do repositório existente: `/storage/emulated/0/Documents/POO/Aula_12_Elevador`.
- Destino: `/storage/emulated/0/Documents/POO/Aula_12_Elevador/Aula_15_Elevador`.
- Branch: `main`.
- Remoto `origin` (fetch/push): `https://github.com/IvoLucasLLJ/ELEVADOR_POO.git`.
- O destino não existia antes da cópia. Não houve substituição de uma entrega anterior.

O README principal apresenta a Aula 15 como a versão mais recente preparada, com link relativo, comandos e resultados. Seus links e conteúdos das aulas anteriores foram preservados; os demais arquivos preexistentes do repositório mantiveram os hashes anteriores. O README da cópia foi ajustado para o novo caminho e para a situação dentro do repositório. Código, requirements, testes e evidências da preparação foram copiados integralmente, com exclusão prevista de caches, ambientes virtuais, temporários e metadados Git; esses artefatos não constam da cópia.

O programa de produção não foi editado. SHA-256 idêntico na origem e no destino:

```text
ed32ed76d2d4c5be1c2fea132bc8d5dd3b7a73c9f91f4231cf41d2b17f42de1f
```

## Testes realmente repetidos no destino

Executados a partir da raiz do repositório, com a mudança de diretório no próprio comando:

```sh
(cd Aula_15_Elevador && python -B -m unittest discover -s tests -v)
(cd Aula_15_Elevador && python -B -S -m unittest discover -s tests -v)
```

| Execução | Resultado | Tempo informado por unittest | Saída real |
|---|---|---|---|
| Normal | **28 aprovados**, sem falhas/erros/omissões, retorno 0. | 5.497 s | [integracao_testes_normal.log](integracao_testes_normal.log) |
| Com `-S` | **27 aprovados, 1 visual omitido**, sem falhas/erros, retorno 0. | 3.684 s | [integracao_testes_sem_pacotes.log](integracao_testes_sem_pacotes.log) |

Ambiente: Termux/Android aarch64, Python 3.13.13, Textual 8.2.8. Nenhum pacote foi instalado ou atualizado. Com `-S`, site-packages não é carregado e o processo não encontra o Textual instalado. A suíte é a mesma nos dois comandos; os números não representam conjuntos distintos adicionais. A verificação visual é headless, sem inspeção física do dispositivo.

[execucao_integracao.json](execucao_integracao.json) registra comandos, diretórios, horários, versões e retornos. Os **103 testes e as 5.137 operações** são resultados históricos, não reproduzidos nesta etapa. Não houve comparação com uma versão original da Aula 14.

## Evidências anteriores e integridade atual

Os arquivos `ambiente_inicial.json`, `execucao_testes.json`, `execucao_sem_pacotes.json`, `testes_termux.log`, `testes_sem_pacotes.log`, `VALIDACAO_LOCAL.md` e `integridade_final.json` foram copiados sem mudanças. Seus caminhos absolutos e seu manifesto descrevem a preparação na **origem**, antes da integração. A seção 9 de `Validacao_Final_Elevador_SOLID.md` também se refere àquela preparação. A indicação de que a pasta estava fora do Git é histórica e não descreve a presente cópia integrada.

Como o README desta cópia foi ajustado, seus bytes atuais diferem dos registrados no manifesto da origem. A conferência atual está em [integridade_integracao.json](integridade_integracao.json), que registra a preservação da origem, dos arquivos preexistentes, dos materiais copiados, as regras de ignore e os links locais desta cópia. O manifesto atual exclui a si próprio.

## Git e limites da alteração

O `.gitignore` da raiz foi inspecionado e preservado; o `.gitignore` da Aula 15 complementa a proteção desta subpasta. `git check-ignore --no-index --quiet` confirmou 12 cenários: caches/bytecode, ambientes virtuais e temporários ignorados; programa, requirements, README, testes, logs e JSON preservados para versionamento.

Antes desta tarefa já existiam estes itens não rastreados, que permaneceram intactos e não foram adicionados à área de preparação:

```text
?? RELATORIO_ARQUIVO_UNICO.md
?? elevador_completo.py
?? evidencias/
?? tests/test_elevador_completo.py
```

O escopo da integração é somente **`README.md` na raiz e a nova pasta `Aula_15_Elevador/`**. Não houve alteração de arquivos de outras aulas, inicialização de repositório aninhado, `git add`, commit ou push. A revisão e o versionamento da Aula 15 permanecem posteriores.
