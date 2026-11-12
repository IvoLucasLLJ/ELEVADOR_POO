"""Interface Textual, adaptada do painel visual local da Aula 13."""

from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, RichLog, Select, Static

from .painel import Painel


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
        super().__init__()
        self.painel = painel
        self.intervalo = intervalo
        self._andar_selecionado = 0
        self._eventos_lidos = 0
        self._opcoes_pessoas = None
        self._encerrando = False
        self._temporizadores = []

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
