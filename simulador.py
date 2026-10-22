"""Interface textual para usar a classe Elevador no terminal."""

from elevador import Elevador


def perguntar_sim_nao(pergunta):
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta == 'sim':
            return True
        if resposta in ('não', 'nao'):
            return False
        print('Responda sim ou não.')


def perguntar_destino(andar_atual, direcao):
    while True:
        try:
            destino = int(input('Qual é o andar de destino (0 a 10)? '))
        except ValueError:
            print('Digite um número inteiro de 0 a 10.')
            continue

        if not 0 <= destino <= 10:
            print('O andar deve estar entre 0 e 10.')
        elif direcao == 'subir' and destino <= andar_atual:
            print('Para subir, escolha um andar acima do andar atual.')
        elif direcao == 'descer' and destino >= andar_atual:
            print('Para descer, escolha um andar abaixo do andar atual.')
        else:
            return destino


def main():
    elevador = Elevador()
    print('Simulador de elevador — andares de 0 a 10.')
    print('Digite parar entre viagens para encerrar.')

    while True:
        print('\nAndar atual:', elevador.andar_atual)
        direcao = input('Subir, descer ou parar? ').strip().lower()
        if direcao == 'parar':
            print('Simulação encerrada.')
            return
        if direcao not in ('subir', 'descer'):
            print('Digite subir, descer ou parar.')
            continue
        if direcao == 'subir' and elevador.andar_atual == 10:
            print('Você já está no último andar. Escolha descer ou parar.')
            continue
        if direcao == 'descer' and elevador.andar_atual == 0:
            print('Você já está no térreo. Escolha subir ou parar.')
            continue

        while True:
            destino = perguntar_destino(elevador.andar_atual, direcao)
            if perguntar_sim_nao(f'Confirmar chamada para o andar {destino}? (sim/não) '):
                if destino in elevador.solicitacoes:
                    print('Esse andar já está nas paradas desta viagem.')
                else:
                    elevador.chamar(destino)
                    print('Chamada confirmada para o andar:', destino)
            else:
                print('Chamada cancelada.')

            if not perguntar_sim_nao('Adicionar outra parada antes do movimento? (sim/não) '):
                break

        if elevador.solicitacoes:
            print('\nAtendendo chamadas:')
            elevador.atender_solicitacoes()
            print('Todas as chamadas foram atendidas.')
        else:
            print('Nenhuma chamada confirmada.')


if __name__ == '__main__':
    main()
