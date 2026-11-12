"""Coordena comandos; o estado físico pertence ao domínio."""

import math
import time


class Painel:
    def __init__(self, predio, tempo_portas=1.5, relogio=time.monotonic):
        if (isinstance(tempo_portas, bool) or not isinstance(tempo_portas, (int, float))
                or not math.isfinite(tempo_portas) or tempo_portas < 0):
            raise ValueError("O tempo das portas deve ser finito e não negativo.")
        self._predio = predio
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
