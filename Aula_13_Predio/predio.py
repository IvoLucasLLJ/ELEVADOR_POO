
from elevador import Elevador


class Predio:
    def __init__(self, total_andares=11):
        if total_andares < 1:
            raise ValueError("O prédio precisa ter pelo menos um andar.")

        self.total_andares = total_andares
        self.elevador = Elevador()

    def chamar_elevador(self, andar):
        if not 0 <= andar < self.total_andares:
            raise ValueError("Andar inexistente neste prédio.")

        self.elevador.chamar(andar)
        return self.elevador
