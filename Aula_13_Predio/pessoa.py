class Pessoa:
    def __init__(self, nome, andar):
        self.nome = nome
        self.andar = andar
        self.estado = "fora"
        self.sentido = None
        self.destino = None

    def chamar_elevador(self, painel, sentido):
        if self.estado != "fora":
            print(f"{self.nome} já está em atendimento.")
            return False

        if painel.chamar_externo(self.andar, sentido):
            self.sentido = sentido.lower()
            self.estado = "aguardando"
            return True

        return False

    def embarcar(self, elevador):
        if self.estado != "aguardando":
            print(f"{self.nome} não está aguardando.")
            return False

        if elevador.andar_atual != self.andar:
            print("O elevador ainda não chegou.")
            return False

        self.estado = "dentro"
        print(f"{self.nome} entrou no elevador.")
        return True

    def escolher_destino(self, painel):
        if self.estado != "dentro":
            print("A pessoa precisa embarcar primeiro.")
            return None

        destino = painel.escolher_destino()

        if destino is not None:
            self.destino = destino

        return destino

    def desembarcar(self, elevador):
        if self.estado != "dentro":
            return False

        if self.destino is None:
            return False

        if elevador.andar_atual != self.destino:
            print("O elevador ainda não chegou ao destino.")
            return False

        self.andar = self.destino
        self.estado = "fora"
        self.sentido = None
        self.destino = None

        print(f"{self.nome} desembarcou no andar {self.andar}.")
        return True

    def mostrar_estado(self):
        print(f"\n{self.nome}")
        print(f"Andar: {self.andar}")
        print(f"Estado: {self.estado}")
        print(f"Sentido: {self.sentido}")
        print(f"Destino: {self.destino}")
