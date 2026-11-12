"""Composição: onze pavimentos e exatamente um elevador."""

from .andar import Andar
from .elevador import Elevador
from .pessoa import Pessoa


class Predio:
    def __init__(self, total_andares=11):
        if type(total_andares) is not int or total_andares != 11:
            raise ValueError("Este prédio possui 11 pavimentos (0 a 10).")
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
        pessoa = Pessoa(len(self._pessoas) + 1, local)
        local._adicionar(pessoa)
        self._pessoas.append(pessoa)
        pessoa._aguardar(sentido)
        return pessoa
