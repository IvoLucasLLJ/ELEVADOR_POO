class Elevador:
    def __init__(self):
        self.andar_atual = 0
        self.direcao = 'parado'
        self.solicitacoes = []

    def chamar(self, andar):
        if andar not in self.solicitacoes:
            self.solicitacoes.append(andar)

    def mover_para(self, andar_destino):
        if andar_destino == self.andar_atual:
            self.direcao = 'parado'
            print('Elevador já está no andar:', self.andar_atual)
            if self.andar_atual in self.solicitacoes:
                print(f'Elevador parou no {self.andar_atual}º andar')
                self.solicitacoes.remove(self.andar_atual)
            return

        if andar_destino > self.andar_atual:
            self.direcao = 'subindo'
        else:
            self.direcao = 'descendo'

        while self.andar_atual != andar_destino:
            if self.direcao == 'subindo':
                self.andar_atual += 1
            else:
                self.andar_atual -= 1
            print('Elevador', self.direcao, '- andar:', self.andar_atual)
            if self.andar_atual in self.solicitacoes:
                print(f'Elevador parou no {self.andar_atual}º andar')
                self.solicitacoes.remove(self.andar_atual)

        print('Elevador chegou ao andar:', self.andar_atual)
        self.direcao = 'parado'

    def atender_solicitacoes(self):
        if self.andar_atual in self.solicitacoes:
            self.mover_para(self.andar_atual)

        while self.solicitacoes:
            mais_proximo = min(
                self.solicitacoes,
                key=lambda andar: (
                    abs(andar - self.andar_atual),
                    -andar,
                ),
            )
            if mais_proximo > self.andar_atual:
                destino = max(self.solicitacoes)
            else:
                destino = min(self.solicitacoes)
            self.mover_para(destino)


if __name__ == '__main__':
    elevador = Elevador()
    elevador.andar_atual = 4

    elevador.chamar(7)
    elevador.chamar(2)
    elevador.chamar(5)
    elevador.chamar(1)

    print('Andar atual:', elevador.andar_atual)
    print('Direção:', elevador.direcao)
    print('Solicitações:', elevador.solicitacoes)

    elevador.atender_solicitacoes()
    print('Solicitações:', elevador.solicitacoes)
