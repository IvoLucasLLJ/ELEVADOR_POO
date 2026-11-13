# Aula 15 — Programação Orientada a Objetos

**Autor:** Ivo Lucas de Lima Júnior  
**Projeto:** Elevador POO — refatoração SOLID  
**Repositório de referência:** `IvoLucasLLJ/ELEVADOR_POO`

Simulador de um elevador em um prédio com onze pavimentos, numerados de 0 a 10. A Aula 15 reorganiza as responsabilidades da versão da Aula 14: fila, movimento e passageiros passam a colaboradores próprios, coordenados por `Elevador`. A apresentação dos dados fica em funções e nas interfaces. Toda a implementação de produção permanece em `elevador_completo.py`, preservado byte a byte nesta preparação.

A evolução descrita se baseia no código atual e no relatório histórico fornecido. Não foi feita nesta preparação uma comparação com uma versão original da Aula 14.

## Funcionamento

- Uma cabine, fila global FIFO e deslocamento de no máximo um andar por pulso do motor.
- Chamadas externas por andar e sentido, inclusive antes do início e durante o deslocamento. No térreo só é possível subir; no último andar, descer.
- Uma chamada pode representar um grupo. Repetir uma chamada externa ainda pendente ou em atendimento não cria outro pedido nem novas pessoas.
- Cada pessoa conserva sua identidade entre espera, cabine e desembarque; pode ter vários destinos. Pessoas diferentes podem compartilhar uma solicitação interna.
- Os destinos entram na fila global: a ordem de atendimento não é otimizada por proximidade.
- A chegada abre as portas e atende os passageiros no mesmo pulso. O pedido é concluído no fechamento das portas, quando entra no histórico.
- O fechamento é recusado se alguém na cabine estiver sem destino. O embarque exige fechamento manual; as paradas internas têm fechamento temporizado. A cabine vazia pode fechar no próximo pulso do motor.
- A pausa bloqueia a atualização automática e preserva o tempo restante das portas, permitindo registrar novas chamadas externas.
- Ao sair, o programa apresenta o relatório da sessão. Não há persistência em arquivo ou banco de dados.

## Classes e SOLID

| Classe | Responsabilidade principal |
|---|---|
| `Andar` | Representar um pavimento, consultar as pessoas presentes e encaminhar chamadas. |
| `Pessoa` | Manter identidade, localização e destinos; delegar pedidos ao elevador. |
| `FilaFIFO` | Manter sequência, registros de solicitações, vínculos e histórico. |
| `ControladorMovimento` | Manter posição, direção e portas; avançar um andar. |
| `GerenciadorPassageiros` | Validar destinos e transferir as mesmas pessoas entre cabine e andares. |
| `Elevador` | Coordenar fila, movimento e passageiros recebidos no construtor. |
| `Predio` | Compor onze andares e um elevador e cadastrar solicitantes. |
| `Painel` | Controlar início, pausa, seleção de pessoa e temporização das portas. |
| `InterfaceElevador` | Apresentar a interface de terminal Textual e encaminhar eventos ao painel. |

Os protocolos `FilaAtendimento`, `MovimentoCabine` e `ControlePassageiros` descrevem as operações consumidas por `Elevador`.

| Princípio | Aplicação e alcance |
|---|---|
| S — responsabilidade única | Fila, cabine e passageiros têm seus próprios donos de estado. |
| O — aberto/fechado | O construtor de `Elevador` e a fábrica aceita por `Predio` oferecem pontos de substituição. Uma política alternativa deve preservar os contratos; não foi implementada outra nesta entrega. |
| L — substituição de Liskov | Um substituto precisa manter FIFO, identidades, validações, passo físico e conclusão dos pedidos. `Protocol` sozinho não prova esse comportamento. |
| I — segregação de interfaces | Há três contratos focados em fila, movimento e passageiros, em vez de um contrato único para todas as funções. |
| D — inversão de dependência | `Elevador` recebe os colaboradores e a função de criação de solicitantes; `_montar_elevador` escolhe as implementações concretas. |

O [guia didático](Guia_Elevador_POO_SOLID.md) localiza os exemplos e explica as limitações dessa aplicação de SOLID.

## Ambiente e dependências

O programa indica **Python 3.10 ou superior** e **Textual 8.2.8** para a interface visual. O modo textual usa apenas biblioteca padrão, com entrada não bloqueante baseada em recursos **POSIX**, como `select.select` e `os.read`.

Nesta preparação foram encontrados e utilizados **Termux/Android aarch64, Python 3.13.13 e Textual 8.2.8**. Nenhum pacote foi instalado ou atualizado. Rich 15.0.0 estava presente como dependência do ambiente visual; não é uma importação direta do programa nem um requisito do modo textual.

Entre nesta pasta antes de executar os comandos:

```sh
cd /storage/emulated/0/Documents/POO/Aula_12_Elevador/Aula_15_Elevador
```

Para preparar futuramente um ambiente que ainda não tenha a dependência visual:

```sh
python -m pip install -r requirements.txt
```

Esse comando é uma instrução de instalação, não uma ação realizada nesta preparação. Se usar ambiente virtual no Termux, crie-o no armazenamento privado do Termux; o armazenamento compartilhado pode impedir os links e permissões necessários ao ambiente virtual.

## Interface visual

```sh
python elevador_completo.py
```

Selecione o andar no painel externo, a quantidade e o sentido. Pressione **Iniciar** ou `i`. Quando ocorrer o embarque, selecione a pessoa e os destinos no painel interno; registre destinos para todos antes de fechar as portas (`f`). Espaço pausa/retoma e `q` encerra. A interface oferece quantidades de 1 a 6; a API e o modo textual aceitam inteiros positivos sem esse limite do seletor.

Em terminais estreitos os painéis são empilhados e pode ser necessário rolar o conteúdo. A verificação local visual usa o modo de teste do Textual, sem capturas ou inspeção de toque no dispositivo.

## Interface textual

```sh
python elevador_completo.py --texto
python elevador_completo.py --texto --tempo-portas 1.5
```

`--tempo-portas` aceita segundos finitos e não negativos; o padrão é 1,5 segundo. A configuração também vale para o modo visual. `--help` mostra os argumentos.

Demonstração: digite as duas primeiras linhas e aguarde o embarque no andar 0:

```text
externa 0 subir 2
iniciar
```

Depois do embarque, digite uma linha por vez:

```text
interna 2 1
interna 3 2
fechar
```

A Pessoa 1 desembarca no andar 2 e a Pessoa 2 no andar 3. As portas nas paradas internas fecham automaticamente. Use `status` para consultar, `pessoa ID` para alternar a pessoa ativa, `pausar` para pausar/retomar, `ajuda` para listar comandos e `sair` para encerrar.

O relógio avança enquanto a entrada permanece aberta. Enviar toda uma viagem por um único pipe seguido de EOF não equivale a esperar os embarques: o EOF encerra a sessão. O teste de viagem textual sincroniza o envio com as mensagens reais do subprocesso.

## Testes

A suíte desta pasta foi **criada nesta preparação**, usando `unittest` da biblioteca padrão e somente o programa atual. Execute da raiz da entrega:

```sh
python -B -m unittest discover -s tests -v
```

Para executar os cenários de domínio e de entrada sem carregar pacotes externos:

```sh
python -B -S -m unittest discover -s tests -v
```

O segundo comando omite os testes visuais quando Textual não está disponível. Os testes de subprocesso também verificam o modo textual isolado com `-I -S`. O teste visual utiliza `run_test()` do Textual e não requer abrir outra janela de terminal. O relógio das portas é injetado nos testes de domínio; a viagem textual exercita o processo real.

Os resultados efetivamente executados, seus comandos, datas e limitações estão em [evidencias/VALIDACAO_LOCAL.md](evidencias/VALIDACAO_LOCAL.md). Os **103 testes e as 5.137 operações** descritos no relatório fornecido são **históricos de Linux/Python 3.12.14**. Não correspondem a esta nova suíte, não foram reproduzidos e não são somados a ela.

## Organização

```text
Aula_15_Elevador/
├── .gitignore
├── README.md
├── elevador_completo.py
├── requirements.txt
├── Guia_Elevador_POO_SOLID.md
├── Validacao_Final_Elevador_SOLID.md
├── tests/
│   ├── test_dominio.py
│   ├── test_execucao.py
│   └── test_interface_visual.py
└── evidencias/
    ├── VALIDACAO_LOCAL.md
    ├── ambiente_inicial.json
    ├── execucao_testes.json
    ├── testes_termux.log
    ├── execucao_sem_pacotes.json
    ├── testes_sem_pacotes.log
    ├── integridade_final.json
    ├── INTEGRACAO_GIT.md
    ├── execucao_integracao.json
    ├── integracao_testes_normal.log
    ├── integracao_testes_sem_pacotes.log
    └── integridade_integracao.json
```

Não há cópia da versão original, auditor estrutural histórico, capturas ou logs históricos nesta entrega. As referências a esses materiais nas seções antigas do relatório foram mantidas como registro histórico. A seção local do relatório descreve o conteúdo disponível agora.

## Limitações e versionamento

Os testes exercitam os cenários identificados no código; não constituem prova formal de ausência de defeitos ou de equivalência com a Aula 14. A análise da gramática Python 3.10 não é execução nessa versão. Windows, outras versões de Python, toque, teclado virtual e apresentação física do terminal não foram validados nesta preparação.

As tuplas protegem as coleções, mas não tornam os objetos `Pessoa` imutáveis. A seleção de uma pessoa válida pode ocorrer antes da rejeição de um destino inválido; esse efeito existente foi mantido e testado.

Esta cópia está integrada localmente à subpasta `Aula_15_Elevador/` do repositório `IvoLucasLLJ/ELEVADOR_POO`, na branch `main`, preparada para revisão e versionamento. A pasta original foi mantida intacta. O `.gitignore` local exclui caches, bytecode, ambientes virtuais e temporários, preservando documentação, testes e evidências. Não foi criado Git aninhado nem alterada outra aula. Não houve commit nem push; a Aula 15 ainda não foi publicada nesta etapa.

Os registros de preparação e o manifesto `evidencias/integridade_final.json` descrevem a pasta de origem na data daquela validação. Este README foi ajustado para a cópia integrada; os testes repetidos no destino e a integridade atual constam de [evidencias/INTEGRACAO_GIT.md](evidencias/INTEGRACAO_GIT.md) e `evidencias/integridade_integracao.json`.
