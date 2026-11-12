"""Elevador POO completo: um elevador, 11 pavimentos e atendimento FIFO.

Execução visual: python elevador_completo.py
Execução textual (sem dependências externas): python elevador_completo.py --texto
Tempo das portas: acrescente --tempo-portas 1.5 (segundos, finito e >= 0).

Versão independente da Aula 13. Todas as regras e classes estão neste arquivo.
Ordem de leitura: entidades -> prédio -> controlador -> interfaces -> main.
Python 3.10+; a interface visual utiliza Textual 8.2.8. A textual usa POSIX/Termux.
"""

from __future__ import annotations

import argparse
import codecs
import math
import os
import select
import sys
import time

# Dependência opcional: as entidades e a interface textual funcionam sem Textual.
try:
    from textual.app import App, ComposeResult
    from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
    from textual.widgets import Button, Footer, Header, RichLog, Select, Static
except ModuleNotFoundError as erro:
    if not erro.name or not erro.name.startswith("textual"):
        raise
    _TEXTUAL_DISPONIVEL = False
    App = object  # Permite definir a classe; seu construtor exige a biblioteca visual.
else:
    _TEXTUAL_DISPONIVEL = True

# 1. Entidades do domínio

# Andar representa um pavimento e mantém as pessoas que estão fora da cabine.
# Responsabilidade: consultar a espera e encaminhar chamadas ao elevador do prédio.
# POO: abstração do pavimento e encapsulamento da lista de pessoas.
# Relações: é parte da composição de Predio e associa-se às pessoas presentes.
class Andar:  # Classe: define a estrutura e as operações de seus objetos.
    # Construtor __init__: inicializa cada objeto; self referencia essa instância.
    def __init__(self, numero, predio):
        predio.validar_andar(numero)
        # Atributos de instância: cada andar guarda seus próprios dados.
        self._numero = numero
        self._predio = predio
        self._pessoas = []

    # Encapsulamento: _ indica uso interno por convenção (não privacidade absoluta).
    # Propriedades sem setter e tuplas protegem o acesso público ao estado.
    @property
    def numero(self):
        return self._numero

    @property
    def pessoas(self):
        return tuple(self._pessoas)

    def aguardando(self, sentido):
        return tuple(p for p in self._pessoas
                     if p.estado == "aguardando" and p.sentido == sentido)

    # Método de instância: usa self para acessar o prédio associado.
    def chamar_elevador(self, sentido, quantidade=1):
        return self._predio.elevador.registrar_chamada_externa(self.numero, sentido, quantidade)

    def _adicionar(self, pessoa):
        if pessoa not in self._pessoas:
            self._pessoas.append(pessoa)

    def _retirar(self, pessoa):
        self._pessoas.remove(pessoa)


# Pessoa representa um passageiro com identidade, localização e viagem próprias.
# Responsabilidade: guardar seu estado e solicitar embarque, destinos e desembarque.
# POO: abstração e encapsulamento; a identidade do objeto persiste na viagem.
# Relações: associa-se a um Andar ou ao Elevador, conforme sua localização.
class Pessoa:
    def __init__(self, identificador, andar):
        if type(identificador) is not int or identificador < 1:
            raise ValueError("Identificador deve ser inteiro positivo.")
        self._identificador = identificador
        self._local = andar  # Associação: referência ao objeto de localização.
        self._origem = andar.numero
        self._estado = "fora"
        self._sentido = None
        self._destinos = []
        self._atendidos = []

    @property
    def identificador(self):
        return self._identificador

    @property
    def nome(self):
        return f"Pessoa {self.identificador}"

    @property
    def andar(self):
        return (self._local.andar_atual if self.estado == "dentro"
                else self._local.numero)

    @property
    def origem(self):
        return self._origem

    @property
    def estado(self):
        return self._estado

    @property
    def sentido(self):
        return self._sentido

    @property
    def destinos(self):
        return tuple(self._destinos)

    @property
    def destinos_atendidos(self):
        return tuple(self._atendidos)

    def embarcar(self, elevador):
        return elevador.embarcar(self)

    # Delegação: o elevador valida e registra a operação solicitada pela pessoa.
    def selecionar_destino(self, andar, elevador):
        return elevador.registrar_destino_interno(andar, self)

    def desembarcar(self, elevador):
        return elevador.desembarcar(self)

    def _aguardar(self, sentido):
        self._sentido = sentido
        self._estado = "aguardando"

    def _entrar(self, elevador):
        self._local = elevador
        self._estado = "dentro"

    def _adicionar_destino(self, andar):
        self._destinos.append(andar)

    def _atender_destino(self, andar):
        self._destinos.remove(andar)
        self._atendidos.append(andar)

    def _sair(self, andar):
        self._local = andar
        self._estado = "fora"
        self._sentido = None

    def mostrar_estado(self):
        print(f"{self.nome}: {self.estado}, andar {self.andar}, "
              f"destinos {self.destinos}, atendidos {self.destinos_atendidos}")


# Elevador representa a cabine e o atendimento físico das solicitações FIFO.
# Responsabilidade: mover, controlar portas, embarcar e desembarcar com validação.
# POO: abstração das operações e encapsulamento dos estados e registros.
# Relações: é um componente de Predio e associa-se às pessoas; Painel o coordena.
class Elevador:
    def __init__(self, predio):
        self._predio = predio
        self._andar_atual = 0
        self._direcao = "parado"
        self._portas_abertas = False
        self._fila = []
        self._passageiros = []
        self._historico = []
        self._eventos = []
        self._sequencia = 0

    @property
    def andar_atual(self):
        return self._andar_atual

    @property
    def direcao(self):
        return self._direcao

    @property
    def portas_abertas(self):
        return self._portas_abertas

    @property
    def total_andares(self):
        return self._predio.total_andares

    @property
    def passageiros(self):
        return tuple(self._passageiros)

    @property
    def eventos(self):
        return tuple(self._eventos)

    @property
    def historico(self):
        return tuple(self._copiar(r) for r in self._historico)

    @property
    def ultimo_atendimento(self):
        return self._copiar(self._historico[-1]) if self._historico else None

    @property
    def solicitacoes(self):
        return [r["andar"] for r in self._fila]

    @property
    def situacao(self):
        if self.portas_abertas:
            return "em atendimento"
        return "em deslocamento" if self.direcao != "parado" else "parado"

    @staticmethod
    def _copiar(registro):
        return {k: (tuple(p.identificador for p in v) if k == "pessoas" else v)
                for k, v in registro.items()}

    # Cópias dos registros evitam que a interface altere a fila encapsulada.
    def consultar_fila(self):
        return [self._copiar(r) for r in self._fila]

    def _registrar_evento(self, mensagem):
        self._eventos.append(mensagem)

    def _enfileirar(self, tipo, andar, pessoas, sentido=None):
        self._sequencia += 1
        registro = {"ordem": self._sequencia, "tipo": tipo, "andar": andar,
                    "estado": "pendente", "pessoas": pessoas}
        if sentido is not None:
            registro["sentido"] = sentido
        self._fila.append(registro)
        return registro

    def registrar_chamada_externa(self, andar, sentido, quantidade=1):
        self._predio.validar_andar(andar)
        if type(quantidade) is not int or quantidade < 1:
            raise ValueError("A quantidade de pessoas deve ser um inteiro positivo.")
        if not isinstance(sentido, str):
            raise ValueError("Escolha subir ou descer.")
        sentido = sentido.strip().lower()
        if sentido not in ("subir", "descer"):
            raise ValueError("Escolha subir ou descer.")
        if (andar == 0 and sentido == "descer") or (andar == 10 and sentido == "subir"):
            raise ValueError("Sentido impossível neste pavimento.")
        for r in self._fila:
            if r["tipo"] == "externa" and r["andar"] == andar and r["sentido"] == sentido:
                return {"resultado": "duplicada", "solicitacao": self._copiar(r)}
        pessoas = [self._predio._criar_solicitante(andar, sentido)
                   for _ in range(quantidade)]
        r = self._enfileirar("externa", andar, pessoas, sentido)
        nomes = ", ".join(p.nome for p in pessoas)
        self._registrar_evento(f"Externa #{r['ordem']}: andar {andar}, {sentido}; {nomes} aguardando.")
        return {"resultado": "registrada", "solicitacao": self._copiar(r)}

    def registrar_destino_interno(self, andar, pessoa):
        self._predio.validar_andar(andar)
        if pessoa not in self._passageiros or pessoa.estado != "dentro":
            raise ValueError("O painel interno exige uma pessoa embarcada.")
        if andar == self.andar_atual:
            raise ValueError("O elevador já está neste andar.")
        if andar in pessoa.destinos:
            return {"resultado": "duplicada", "solicitacao": None}
        # A primeira escolha respeita a chamada; as seguintes são etapas
        # da mesma viagem. A fila global continua sendo a autoridade.
        if not pessoa.destinos and not pessoa.destinos_atendidos:
            if ((pessoa.sentido == "subir" and andar < pessoa.origem)
                    or (pessoa.sentido == "descer" and andar > pessoa.origem)):
                raise ValueError("O primeiro destino deve respeitar o sentido da chamada.")
        existente = next((r for r in self._fila
                          if r["tipo"] == "interna" and r["andar"] == andar), None)
        pessoa._adicionar_destino(andar)
        if existente is not None:
            existente["pessoas"].append(pessoa)
            r, resultado = existente, "vinculada"
        else:
            r, resultado = self._enfileirar("interna", andar, [pessoa]), "registrada"
        self._registrar_evento(f"Interna #{r['ordem']}: destino {andar} para {pessoa.nome} ({resultado}).")
        return {"resultado": resultado, "solicitacao": self._copiar(r)}

    # Abstração: a interface pede um avanço sem manipular posição ou portas.
    def avancar_um_andar(self):
        if self.portas_abertas:
            return {"evento": "portas_abertas", "andar": self.andar_atual}
        if not self._fila:
            self._direcao = "parado"
            return {"evento": "ocioso", "andar": self.andar_atual}
        r = self._fila[0]
        r["estado"] = "em_atendimento"
        destino = r["andar"]
        if destino != self.andar_atual:
            self._direcao = "subindo" if destino > self.andar_atual else "descendo"
            self._andar_atual += 1 if destino > self.andar_atual else -1
            self._registrar_evento(f"Elevador {self.direcao}: andar {self.andar_atual}.")
        if self.andar_atual != destino:
            return {"evento": "movimento", "andar": self.andar_atual}
        self._direcao = "parado"
        self._portas_abertas = True
        self._registrar_evento(f"Portas abertas no andar {self.andar_atual} para #{r['ordem']} ({r['tipo']}).")
        if r["tipo"] == "externa":
            for pessoa in r["pessoas"]:
                pessoa.embarcar(self)
        else:
            for pessoa in r["pessoas"]:
                pessoa._atender_destino(destino)
                self._registrar_evento(f"{pessoa.nome}: destino {destino} atendido.")
                if not pessoa.destinos:
                    pessoa.desembarcar(self)
        return {"evento": "parada", "andar": self.andar_atual,
                "solicitacao": self._copiar(r)}

    def embarcar(self, pessoa):
        r = self._fila[0] if self._fila else None
        if (not self.portas_abertas or self.direcao != "parado" or r is None
                or r["tipo"] != "externa" or pessoa not in r["pessoas"]
                or pessoa.estado != "aguardando" or pessoa.andar != self.andar_atual
                or pessoa.sentido != r["sentido"]):
            raise ValueError("Embarque exige a chamada externa correspondente e portas abertas.")
        self._predio.obter_andar(pessoa.andar)._retirar(pessoa)
        self._passageiros.append(pessoa)
        pessoa._entrar(self)
        self._registrar_evento(f"{pessoa.nome} embarcou; painel interno disponível.")
        return True

    def desembarcar(self, pessoa):
        r = self._fila[0] if self._fila else None
        if (not self.portas_abertas or self.direcao != "parado" or r is None
                or r["tipo"] != "interna" or pessoa not in r["pessoas"]
                or pessoa not in self._passageiros or pessoa.destinos
                or not pessoa.destinos_atendidos
                or pessoa.destinos_atendidos[-1] != self.andar_atual):
            raise ValueError("Desembarque exige o último destino atendido e portas abertas.")
        local = self._predio.obter_andar(self.andar_atual)
        self._passageiros.remove(pessoa)
        local._adicionar(pessoa)
        pessoa._sair(local)
        self._registrar_evento(f"{pessoa.nome} desembarcou no andar {self.andar_atual}; viagem concluída.")
        return True

    def fechar_portas(self):
        if not self.portas_abertas:
            raise ValueError("As portas já estão fechadas.")
        sem_destino = [p.nome for p in self._passageiros if not p.destinos]
        if sem_destino:
            raise ValueError("Portas abertas: selecione um destino válido para "
                             + ", ".join(sem_destino) + ".")
        r = self._fila.pop(0)
        r["estado"] = "concluida"
        self._historico.append(r)
        self._portas_abertas = False
        self._registrar_evento(f"Portas fechadas; solicitação #{r['ordem']} concluída.")
        return self._copiar(r)


# 2. Composição do prédio

# Predio representa o conjunto de onze pavimentos e exatamente um elevador.
# Responsabilidade: construir esses componentes, validar andares e criar pessoas.
# POO: composição dos componentes e encapsulamento do cadastro da sessão.
# Relações: cria Andar, Elevador e Pessoa; é associado ao controlador Painel.
class Predio:
    def __init__(self, total_andares=11):
        if type(total_andares) is not int or total_andares != 11:
            raise ValueError("Este prédio possui 11 pavimentos (0 a 10).")
        # Composição: o próprio prédio cria e mantém seus componentes.
        self._andares = tuple(Andar(n, self) for n in range(11))
        self._elevador = Elevador(self)
        self._pessoas = []

    @property
    def total_andares(self):
        return 11

    @property
    def andares(self):
        return self._andares

    @property
    def elevador(self):
        return self._elevador

    @property
    def pessoas(self):
        return tuple(self._pessoas)

    @staticmethod
    def validar_andar(numero):
        if type(numero) is not int or not 0 <= numero <= 10:
            raise ValueError("Informe um andar inteiro de 0 a 10.")

    def obter_andar(self, numero):
        self.validar_andar(numero)
        return self.andares[numero]

    def chamar_elevador(self, andar, sentido, quantidade=1):
        return self.obter_andar(andar).chamar_elevador(sentido, quantidade)

    def _criar_solicitante(self, andar, sentido):
        local = self.obter_andar(andar)
        # Objeto: uma instância concreta da classe Pessoa, com identidade própria.
        pessoa = Pessoa(len(self._pessoas) + 1, local)
        local._adicionar(pessoa)
        self._pessoas.append(pessoa)
        pessoa._aguardar(sentido)
        return pessoa


# 3. Controlador compartilhado pelas duas interfaces

# Painel representa o controlador dos comandos e do andamento da simulação.
# Responsabilidade: iniciar/pausar, selecionar pessoas e temporizar portas internas.
# POO: abstração de comandos e associação com Predio; não herda das entidades.
# Relações: coordena o domínio para as interfaces visual e textual.
class Painel:
    def __init__(self, predio, tempo_portas=1.5, relogio=time.monotonic):
        if (isinstance(tempo_portas, bool) or not isinstance(tempo_portas, (int, float))
                or not math.isfinite(tempo_portas) or tempo_portas < 0):
            raise ValueError("O tempo das portas deve ser finito e não negativo.")
        self._predio = predio  # Associação: usa um prédio recebido, sem criá-lo.
        self._iniciado = False
        self._pausado = False
        self._tempo_portas = tempo_portas
        self._relogio = relogio
        self._parada_temporizada = None
        self._prazo_portas = None
        self._inicio_pausa = None
        self._pessoa_ativa = None
        self._passageiros_conhecidos = ()

    @property
    def tempo_portas(self):
        return self._tempo_portas

    @property
    def predio(self):
        return self._predio

    @property
    def elevador(self):
        return self.predio.elevador

    @property
    def iniciado(self):
        return self._iniciado

    @property
    def pausado(self):
        return self._pausado

    @property
    def situacao(self):
        if not self.iniciado:
            return "aguardando início"
        if self.pausado:
            return "pausado"
        return self.elevador.situacao

    def iniciar(self):
        # O atalho Iniciar não deve desfazer uma pausa em uma sessão ativa.
        if not self.iniciado:
            self._iniciado = True

    def alternar_pausa(self):
        if not self.iniciado:
            raise ValueError("Inicie o atendimento primeiro.")
        agora = self._relogio()
        if self.pausado:
            if self._prazo_portas is not None:
                self._prazo_portas += agora - self._inicio_pausa
            self._inicio_pausa = None
        else:
            self._inicio_pausa = agora
        self._pausado = not self.pausado
        return self.pausado

    def chamar_externo(self, andar, sentido, quantidade=1):
        return self.predio.chamar_elevador(andar, sentido, quantidade)

    @property
    def pessoa_ativa(self):
        """Novo embarque tem prioridade; atualizações comuns mantêm a escolha."""
        return self._sincronizar_pessoa_ativa()

    def _sincronizar_pessoa_ativa(self):
        passageiros = self.elevador.passageiros
        novos = [p for p in passageiros if p not in self._passageiros_conhecidos]
        if novos:
            self._pessoa_ativa = novos[-1]
        elif self._pessoa_ativa not in passageiros:
            self._pessoa_ativa = next((p for p in passageiros if not p.destinos),
                                      passageiros[-1] if passageiros else None)
        self._passageiros_conhecidos = passageiros
        return self._pessoa_ativa

    def selecionar_pessoa(self, identificador):
        if type(identificador) is not int:
            raise ValueError("Identificador inválido.")
        pessoa = next((p for p in self.elevador.passageiros
                       if p.identificador == identificador), None)
        if pessoa is None:
            raise ValueError("A pessoa selecionada não está na cabine.")
        # Reconhecer embarques antes de aplicar a escolha manual evita que
        # a próxima atualização desfaça a seleção feita pelo usuário.
        self._sincronizar_pessoa_ativa()
        self._pessoa_ativa = pessoa
        return pessoa

    def escolher_destino(self, andar, identificador=None):
        if not self.elevador.passageiros:
            raise ValueError("Embarque antes de usar o painel interno.")
        pessoa = (self.pessoa_ativa if identificador is None
                  else self.selecionar_pessoa(identificador))
        return pessoa.selecionar_destino(andar, self.elevador)

    def fechar_portas(self):
        resultado = self.elevador.fechar_portas()
        self._cancelar_fechamento()
        return resultado

    def _cancelar_fechamento(self):
        self._parada_temporizada = None
        self._prazo_portas = None

    def _temporizar_parada(self):
        """O prazo pertence à ordem da parada, nunca à abertura seguinte."""
        fila = self.elevador.consultar_fila()
        if not self.elevador.portas_abertas or not fila or fila[0]["tipo"] != "interna":
            self._cancelar_fechamento()
            return
        ordem = fila[0]["ordem"]
        if ordem != self._parada_temporizada:
            self._parada_temporizada = ordem
            self._prazo_portas = self._relogio() + self.tempo_portas

    def atualizar(self, mover=True):
        """Pulso curto: fecha quando seguro ou avança no máximo um andar.

        As interfaces podem consultar portas com mover=False entre os passos
        do motor. Não há callbacks de fechamento acumulados entre paradas.
        """
        if not self.iniciado or self.pausado:
            return {"evento": "aguardando"}
        self._temporizar_parada()
        if self.elevador.portas_abertas:
            # Embarque externo permanece manual para permitir várias escolhas.
            # Cabine vazia mantém o fechamento no próximo passo do motor.
            vazio = not self.elevador.passageiros and mover
            prazo = (self._prazo_portas is not None
                     and self._relogio() >= self._prazo_portas)
            seguros = all(p.destinos for p in self.elevador.passageiros)
            if seguros and (vazio or prazo):
                self.fechar_portas()
                return {"evento": "fechamento"}
            return {"evento": "portas_abertas", "andar": self.elevador.andar_atual}
        if not mover:
            return {"evento": "aguardando"}
        resultado = self.elevador.avancar_um_andar()
        self._sincronizar_pessoa_ativa()
        self._temporizar_parada()
        return resultado

    def mostrar_fila(self):
        for registro in self.elevador.consultar_fila():
            print(registro)

    def mostrar_registros(self):
        """Relatório da sessão, incluindo viagens concluídas e pendências."""
        print("\n=== RELATÓRIO DA SESSÃO ===")
        for registro in self.elevador.historico:
            print(f"#{registro['ordem']} {registro['tipo']}: "
                  f"andar {registro['andar']} {registro.get('sentido', '')} — concluída")
        for pessoa in self.predio.pessoas:
            print(f"{pessoa.nome}: origem {pessoa.origem}; "
                  f"destinos atendidos {pessoa.destinos_atendidos}; "
                  f"pendentes {pessoa.destinos}; {pessoa.estado} no andar {pessoa.andar}")
        print("Fila restante:", self.elevador.consultar_fila())


# 4. Interface visual Textual (CSS e widgets incluídos)

# InterfaceElevador representa a aplicação visual interativa no terminal.
# Responsabilidade: apresentar estado e encaminhar eventos de entrada ao Painel.
# POO: herança de App (com Textual instalado) e associação com Painel.
# Polimorfismo por sobrescrita: compose substitui o método de App; o framework
# chama a implementação desta subclasse ao montar seus widgets.
class InterfaceElevador(App):
    TITLE = "UniSenac · Elevador POO"
    BINDINGS = [("i", "iniciar", "Iniciar"),
                ("space", "pausar", "Pausar/retomar"),
                ("f", "fechar", "Fechar portas"), ("q", "sair", "Sair")]
    CSS = """
    Screen { background: #0b1220; color: #ecf2fa; }
    #estado { height: auto; min-height: 2; padding: 0 1; background: #16263c; }
    #conteudo { height: 1fr; }
    #colunas { height: auto; }
    #externo, #interno { width: 1fr; height: auto; border: round #355477; padding: 0 1; }
    .estreita #colunas { layout: vertical; }
    .estreita #externo, .estreita #interno { width: 100%; }
    .subtitulo { height: 1; color: #93c5fd; text-style: bold; }
    .ajuda { height: auto; color: #b6c8dc; }
    #grade-externa, #grade-interna { grid-size: 4; grid-gutter: 0 1; height: 9; margin: 0; }
    Button { min-width: 4; height: 3; }
    Grid Button { width: 1fr; }
    #setas { height: 3; }
    #acoes { grid-size: 4; grid-rows: 3; height: 3; }
    .estreita #acoes { grid-size: 2; height: 6; }
    #acoes Button { min-width: 0; padding: 0; }
    .mini #grade-externa, .mini #grade-interna { grid-size: 3; height: 12; }
    #setas Button, #acoes Button { width: 1fr; }
    .ampla #grade-externa, .ampla #grade-interna { grid-size: 6; height: 6; }
    #pessoa, #quantidade { height: 3; margin: 0; }
    #pessoa-ativa { height: auto; color: #93c5fd; text-style: bold; }
    #pendencias { height: auto; color: #fbbf24; }
    #fila { height: auto; min-height: 2; padding: 0 1; }
    #mensagem { height: auto; min-height: 1; color: #fbbf24; padding: 0 1; }
    #eventos { height: 1fr; min-height: 5; border: round #355477; }
    #selecionado { height: auto; }
    .atual { text-style: bold underline; }
    """

    def __init__(self, painel: Painel, intervalo=1.0):
        if not _TEXTUAL_DISPONIVEL:
            raise ModuleNotFoundError(
                "A interface visual requer Textual; use --texto ou instale textual==8.2.8.",
                name="textual",
            )
        super().__init__()  # Inicializa a parte herdada de App.
        self.painel = painel
        self.intervalo = intervalo
        self._andar_selecionado = 0
        self._eventos_lidos = 0
        self._opcoes_pessoas = None
        self._encerrando = False
        self._temporizadores = []

    # Sobrescrita (override) do contrato de App: polimorfismo na composição visual.
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("", id="estado")
        with VerticalScroll(id="conteudo"):
            with Horizontal(id="colunas"):
                with Vertical(id="externo"):
                    yield Static("PAINEL EXTERNO", classes="subtitulo")
                    yield Static("Andar + sentido · > atual · S seleção · * fila", classes="ajuda")
                    yield Static("Andar selecionado: 0", id="selecionado")
                    yield Select([(f"{n} {'pessoa' if n == 1 else 'pessoas'} nesta chamada", n) for n in range(1, 7)],
                                 value=1, allow_blank=False, id="quantidade")
                    with Grid(id="grade-externa"):
                        for andar in range(11):
                            yield Button(str(andar), id=f"ext-{andar}")
                    with Horizontal(id="setas"):
                        yield Button("SUBIR", id="subir", variant="success")
                        yield Button("DESCER", id="descer", variant="warning")
                with Vertical(id="interno"):
                    yield Static("PAINEL INTERNO", classes="subtitulo")
                    yield Static("Destinos por pessoa · paradas: portas automáticas.", classes="ajuda")
                    yield Static("SELECIONANDO DESTINOS PARA: —", id="pessoa-ativa", markup=False)
                    yield Select([], prompt="Pessoa na cabine", id="pessoa", disabled=True)
                    yield Static("Cabine vazia.", id="pendencias", markup=False)
                    with Grid(id="grade-interna"):
                        for andar in range(11):
                            yield Button(str(andar), id=f"int-{andar}", disabled=True)
            yield Static("", id="fila", markup=False)
            yield RichLog(id="eventos", wrap=True, markup=False)
        with Grid(id="acoes"):
            yield Button("Iniciar", id="iniciar", variant="primary")
            yield Button("Fechar portas", id="fechar")
            yield Button("Pausar", id="pausar")
            yield Button("Sair", id="sair", variant="error")
        yield Static("Escolha uma chamada externa e pressione Iniciar (i).", id="mensagem", markup=False)
        yield Footer()

    def on_mount(self):
        self._ajustar_layout(self.size.width)
        self._temporizadores = [self.set_interval(self.intervalo, self._tic),
                                self.set_interval(0.1, self._portas)]
        self._atualizar()

    def on_resize(self, event):
        self._ajustar_layout(event.size.width)

    def _ajustar_layout(self, largura):
        self.set_class(largura < 85, "estreita")
        self.set_class(largura < 40, "mini")
        self.set_class(largura >= 110, "ampla")

    def _executar(self, operacao):
        try:
            resultado = operacao()
            mensagem = (f"Solicitação {resultado['resultado']}."
                        if isinstance(resultado, dict) and "resultado" in resultado else "Comando executado.")
        except ValueError as erro:
            mensagem = str(erro)
        self.query_one("#mensagem", Static).update(mensagem)
        self._atualizar()

    def _tic(self):
        if self._encerrando or not self.is_running:
            return
        self.painel.atualizar()
        self._atualizar()

    def _portas(self):
        if self._encerrando or not self.is_running:
            return
        resultado = self.painel.atualizar(mover=False)
        if resultado["evento"] == "fechamento":
            self._atualizar()

    def _atualizar(self):
        elevador = self.painel.elevador
        portas = "ABERTAS" if elevador.portas_abertas else "FECHADAS"
        self.query_one("#estado", Static).update(
            f"POSIÇÃO ATUAL: ANDAR {elevador.andar_atual} | {elevador.direcao.upper()} | PORTAS {portas}\n"
            f"{self.painel.situacao.upper()} · 1 elevador · pavimentos 0 a 10")
        self.query_one("#selecionado", Static).update(f"Seleção externa: {self._andar_selecionado} (S)")
        fila = elevador.consultar_fila()
        linhas = [f"#{r['ordem']} {r['tipo']} {r['andar']} {r.get('sentido', '')} ({r['estado']})" for r in fila]
        self.query_one("#fila", Static).update("FILA FIFO\n" + (" | ".join(linhas) or "Vazia; aguardando novas chamadas."))
        ativa = self.painel.pessoa_ativa
        opcoes = tuple((f"{p.nome} · " + (f"destinos {p.destinos}" if p.destinos else "SEM DESTINO"),
                        p.identificador) for p in elevador.passageiros)
        seletor = self.query_one("#pessoa", Select)
        # set_options também gera Changed; essas notificações transitórias não
        # representam uma escolha manual e não podem restaurar um ID antigo.
        with seletor.prevent(Select.Changed):
            if opcoes != self._opcoes_pessoas:
                seletor.set_options(opcoes)
                self._opcoes_pessoas = opcoes
            valor = ativa.identificador if ativa is not None else Select.NULL
            if seletor.value != valor:
                seletor.value = valor
        seletor.disabled = ativa is None
        self.query_one("#pessoa-ativa", Static).update(
            f"SELECIONANDO DESTINOS PARA: {ativa.nome if ativa else '—'}")
        sem_destino = [p.nome for p in elevador.passageiros if not p.destinos]
        self.query_one("#pendencias", Static).update(
            "FALTA DESTINO: " + ", ".join(sem_destino) if sem_destino else
            "Destinos registrados. Pode fechar as portas." if elevador.portas_abertas and ativa else
            "* destinos da pessoa selecionada" if ativa else "Cabine vazia.")
        pendentes = {r["andar"] for r in fila if r["estado"] == "pendente"}
        for andar in range(11):
            atual = andar == elevador.andar_atual
            selecionado = andar == self._andar_selecionado
            pendente = andar in pendentes
            externo = self.query_one(f"#ext-{andar}", Button)
            externo.label = f"{'>' if atual else ''}{andar}{'S' if selecionado else ''}{'*' if pendente else ''}"
            externo.set_class(atual, "atual")
            externo.variant = "success" if atual else "primary" if selecionado else "default"
            interno = self.query_one(f"#int-{andar}", Button)
            interno.disabled = ativa is None
            destino_ativo = ativa is not None and andar in ativa.destinos
            interno.label = f"{'>' if atual else ''}{andar}{'*' if destino_ativo else ''}"
            interno.variant = "primary" if destino_ativo else "default"
            interno.set_class(atual, "atual")
        self.query_one("#subir", Button).disabled = self._andar_selecionado == 10
        self.query_one("#descer", Button).disabled = self._andar_selecionado == 0
        self.query_one("#fechar", Button).disabled = not elevador.portas_abertas
        self.query_one("#pausar", Button).disabled = not self.painel.iniciado
        self.query_one("#pausar", Button).label = "Retomar" if self.painel.pausado else "Pausar"
        self.query_one("#iniciar", Button).disabled = self.painel.iniciado
        eventos = elevador.eventos
        log = self.query_one("#eventos", RichLog)
        for mensagem in eventos[self._eventos_lidos:]:
            log.write(mensagem)
        self._eventos_lidos = len(eventos)

    def on_select_changed(self, event: Select.Changed):
        if event.select.id != "pessoa" or event.value != event.select.value:
            return
        if event.value is Select.NULL:
            self._atualizar()
            return
        self._executar(lambda: self.painel.selecionar_pessoa(event.value))

    def on_button_pressed(self, event: Button.Pressed):
        identificador = event.button.id or ""
        if identificador.startswith("ext-"):
            self._andar_selecionado = int(identificador[4:])
            self._atualizar()
        elif identificador in ("subir", "descer"):
            quantidade = self.query_one("#quantidade", Select).value
            self._executar(lambda: self.painel.chamar_externo(
                self._andar_selecionado, identificador, quantidade))
        elif identificador.startswith("int-"):
            pessoa = self.query_one("#pessoa", Select).value
            # Não há fallback para outra pessoa se a seleção estiver vazia.
            self._executar(lambda: self.painel.escolher_destino(int(identificador[4:]), pessoa))
        elif identificador == "iniciar":
            self.action_iniciar()
        elif identificador == "fechar":
            self.action_fechar()
        elif identificador == "pausar":
            self.action_pausar()
        elif identificador == "sair":
            self.action_sair()

    def action_iniciar(self):
        self._executar(self.painel.iniciar)

    def action_fechar(self):
        self._executar(self.painel.fechar_portas)

    def action_pausar(self):
        self._executar(self.painel.alternar_pausa)

    def _parar_temporizadores(self):
        self._encerrando = True
        for temporizador in self._temporizadores:
            temporizador.stop()

    def on_unmount(self):
        self._parar_temporizadores()

    def action_sair(self):
        self._parar_temporizadores()
        self.exit()


# 5. Interface textual: somente biblioteca padrão, com entrada não bloqueante

AJUDA = """PAINEL EXTERNO: externa ANDAR subir|descer [QUANTIDADE]
PAINEL INTERNO: interna DESTINO [ID] · pessoa ID para alternar a pessoa ativa
OPERAÇÕES: iniciar, fechar, pausar (também retoma), status, ajuda, sair
Exemplo: externa 5 descer -> iniciar -> aguarde embarque -> interna 0 -> fechar
Nas paradas internas as portas fecham automaticamente; o embarque exige fechar.
Chamadas externas continuam disponíveis durante o movimento. Confirme com Enter.
"""


def executar_comando(painel, linha):
    partes = linha.strip().lower().split()
    if not partes:
        return True
    comando, *args = partes
    if comando == "sair" and not args:
        return False
    if comando == "externa" and len(args) in (2, 3):
        print(painel.chamar_externo(int(args[0]), args[1],
                                   int(args[2]) if len(args) == 3 else 1)["resultado"])
    elif comando == "interna" and len(args) in (1, 2):
        print(painel.escolher_destino(int(args[0]), int(args[1]) if len(args) == 2 else None)["resultado"])
    elif comando == "pessoa" and len(args) == 1:
        painel.selecionar_pessoa(int(args[0]))
    elif comando == "iniciar" and not args:
        painel.iniciar()
    elif comando == "fechar" and not args:
        painel.fechar_portas()
    elif comando == "pausar" and not args:
        painel.alternar_pausa()
    elif comando == "ajuda" and not args:
        print(AJUDA)
    elif comando != "status" or args:
        raise ValueError("Comando inválido. Digite ajuda.")
    mostrar_estado(painel)
    return True


def mostrar_estado(painel):
    e = painel.elevador
    print(f"Andar {e.andar_atual} | {e.direcao} | portas "
          f"{'abertas' if e.portas_abertas else 'fechadas'} | {painel.situacao}")
    print("Fila FIFO:", e.consultar_fila())
    print("Cabine:", [(p.nome, p.destinos) for p in e.passageiros])
    ativa = painel.pessoa_ativa
    print("SELECIONANDO DESTINOS PARA:", ativa.nome if ativa else "—")
    sem_destino = [p.nome for p in e.passageiros if not p.destinos]
    if sem_destino:
        print("FALTA DESTINO:", ", ".join(sem_destino))


def executar(painel, intervalo=1.0):
    print(AJUDA)
    mostrar_estado(painel)
    proximo = time.monotonic() + intervalo
    lidos = 0
    pendente = ""
    decodificador = codecs.getincrementaldecoder(sys.stdin.encoding or "utf-8")()
    continuar = True
    try:
        while continuar:
            agora = time.monotonic()
            pronto, _, _ = select.select([sys.stdin], [], [], max(0, min(0.1, proximo - agora)))
            if pronto:
                # Ler o descritor evita comandos presos no buffer de readline
                # quando várias linhas chegam no mesmo evento de entrada.
                dados = os.read(sys.stdin.fileno(), 4096)
                pendente += decodificador.decode(dados, final=not dados)
                linhas = pendente.split("\n")
                pendente = linhas.pop()
                if not dados:
                    if pendente:
                        linhas.append(pendente)
                    continuar = False
                for linha in linhas:
                    try:
                        if not executar_comando(painel, linha):
                            continuar = False
                            break
                    except ValueError as erro:
                        print("Entrada rejeitada:", erro)
                if not continuar:
                    break
            agora = time.monotonic()
            if agora >= proximo:
                painel.atualizar()
                proximo = agora + intervalo
            else:
                painel.atualizar(mover=False)
            eventos = painel.elevador.eventos
            if len(eventos) > lidos:
                for mensagem in eventos[lidos:]:
                    print(mensagem)
                lidos = len(eventos)
                mostrar_estado(painel)
    except KeyboardInterrupt:
        pass
    print("Simulação encerrada; dados desta sessão não são persistidos.")


# 6. Ponto de entrada e seleção da interface

def main(argv=None):
    parser = argparse.ArgumentParser(description="Elevador POO: 11 pavimentos e fila FIFO.")
    parser.add_argument("--texto", action="store_true", help="interface de comandos sem Textual")
    parser.add_argument("--tempo-portas", type=float, default=1.5,
                        help="segundos de espera nas paradas internas (padrão: 1.5)")
    args = parser.parse_args(argv)
    try:
        # Objetos: instancia o prédio e o controlador associados nesta sessão.
        painel = Painel(Predio(), tempo_portas=args.tempo_portas)
    except ValueError as erro:
        parser.error(str(erro))
    if args.texto:
        executar(painel)
    else:
        try:
            interface = InterfaceElevador(painel)
        except ModuleNotFoundError as erro:
            if erro.name and erro.name.startswith("textual"):
                parser.exit(1, "Instale: python -m pip install textual==8.2.8\n"
                               "Ou use: python elevador_completo.py --texto\n")
            raise
        interface.run()
    painel.mostrar_registros()


if __name__ == "__main__":
    main()
