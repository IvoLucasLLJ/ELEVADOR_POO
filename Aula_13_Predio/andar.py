"""Pavimento e localização das pessoas fora da cabine."""

class Andar:
    def __init__(self, numero, predio):
        predio.validar_andar(numero)
        self._numero = numero
        self._predio = predio
        self._pessoas = []

    @property
    def numero(self):
        return self._numero

    @property
    def pessoas(self):
        return tuple(self._pessoas)

    def aguardando(self, sentido):
        return tuple(p for p in self._pessoas
                     if p.estado == "aguardando" and p.sentido == sentido)

    def chamar_elevador(self, sentido, quantidade=1):
        return self._predio.elevador.registrar_chamada_externa(self.numero, sentido, quantidade)

    def _adicionar(self, pessoa):
        if pessoa not in self._pessoas:
            self._pessoas.append(pessoa)

    def _retirar(self, pessoa):
        self._pessoas.remove(pessoa)
