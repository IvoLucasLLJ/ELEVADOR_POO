from predio import Predio
from pessoa import Pessoa
from painel import Painel


def ler_numero(mensagem, minimo, maximo=None):
    while True:
        try:
            numero = int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro válido.")
            continue

        if numero < minimo or (
            maximo is not None and numero > maximo
        ):
            print("Número fora dos limites permitidos.")
            continue

        return numero


def escolher_sentido(andar, ultimo_andar):
    if andar == 0:
        return "subir"

    if andar == ultimo_andar:
        return "descer"

    while True:
        sentido = input(
            "Deseja subir ou descer? "
        ).strip().lower()

        if sentido in ("subir", "descer"):
            return sentido

        print("Digite subir ou descer.")


def main():
    predio = Predio(11)
    elevador = predio.elevador
    painel = Painel(elevador, predio.total_andares)

    pessoas = []
    viagens = []

    print("=== SISTEMA DE ELEVADOR ===")
    print("Prédio: 11 pavimentos")
    print("Atendimento: fila FIFO")

    quantidade = ler_numero(
        "\nQuantidade de pessoas: ", 1
    )

    # Registrar pessoas e chamadas externas
    for numero in range(1, quantidade + 1):
        nome = f"Pessoa {numero}"

        print(f"\n=== {nome} ===")

        andar = ler_numero(
            "Andar de origem: ",
            0,
            predio.total_andares - 1
        )

        pessoa = Pessoa(nome, andar)

        sentido = escolher_sentido(
            andar,
            predio.total_andares - 1
        )

        if pessoa.chamar_elevador(painel, sentido):
            pessoas.append(pessoa)
            pessoa.mostrar_estado()

    # Atender uma parada por vez, seguindo FIFO
    while elevador.solicitacoes:
        print("\n=== PRÓXIMO ATENDIMENTO ===")

        andar_atendido = (
            elevador.atender_proxima_solicitacao()
        )

        # Desembarcar pessoas que chegaram
        for pessoa in pessoas:
            if (
                pessoa.estado == "dentro"
                and pessoa.destino == andar_atendido
            ):
                origem = pessoa.andar
                destino = pessoa.destino

                if pessoa.desembarcar(elevador):
                    viagens.append({
                        "pessoa": pessoa.nome,
                        "origem": origem,
                        "destino": destino
                    })

        # Embarcar pessoas que estavam aguardando
        for pessoa in pessoas:
            if (
                pessoa.estado == "aguardando"
                and pessoa.andar == andar_atendido
            ):
                if pessoa.embarcar(elevador):
                    destino = None

                    while destino is None:
                        destino = pessoa.escolher_destino(
                            painel
                        )

        print("\nFila restante:", elevador.solicitacoes)

    # Relatório final
    print("\n=== RELATÓRIO DE VIAGENS ===")

    for numero, viagem in enumerate(viagens, 1):
        print(
            f"{numero}. {viagem['pessoa']}: "
            f"andar {viagem['origem']} "
            f"até {viagem['destino']}"
        )

    print(f"\nTotal de viagens: {len(viagens)}")

    print("\n=== ESTADO DAS PESSOAS ===")

    for pessoa in pessoas:
        pessoa.mostrar_estado()

    print("\n=== ESTADO DO ELEVADOR ===")
    print("Andar atual:", elevador.andar_atual)
    print("Direção:", elevador.direcao)
    print("Fila:", elevador.solicitacoes)

    painel.mostrar_registros()


if __name__ == "__main__":
    main()
