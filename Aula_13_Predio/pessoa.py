"""Identidade preservada durante todas as etapas da viagem."""

class Pessoa:
    def __init__(self, identificador, andar):
        if type(identificador) is not int or identificador < 1:
            raise ValueError("Identificador deve ser inteiro positivo.")
        self._identificador = identificador
        self._local = andar
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
