"""Domínio FIFO. Uma atualização percorre no máximo um andar."""

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
