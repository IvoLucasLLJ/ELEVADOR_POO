from predio import Predio
from pessoa import Pessoa
from painel import Painel


def main():
    predio = Predio(11)
    elevador = predio.elevador
    painel = Painel(elevador, predio.total_andares)

    pessoas = []
    grupos = {}
    viagens = []

    print("=" * 44)
    print("       SISTEMA DE ELEVADOR")
    print("=" * 44)
    print("Prédio: 11 pavimentos (0 a 10)")
    print("Elevadores: 1")
    print("Atendimento: fila FIFO")

    # Registrar todas as chamadas externas
    iniciar = painel.registrar_chamadas_interativamente()

    if not iniciar:
        print("\nSimulação encerrada.")
        return

    # Criar as pessoas dos grupos registrados
    for chamada in elevador.consultar_fila():
        if chamada["tipo"] != "externa":
            continue

        andar = chamada["andar"]
        sentido = chamada["sentido"]
        quantidade = chamada["quantidade_pessoas"]

        integrantes = []

        for _ in range(quantidade):
            numero = len(pessoas) + 1
            pessoa = Pessoa(f"Pessoa {numero}", andar)

            pessoa.estado = "aguardando"
            pessoa.sentido = sentido

            pessoas.append(pessoa)
            integrantes.append(pessoa)

        grupos[(andar, sentido)] = integrantes

    print("\n=== PESSOAS REGISTRADAS ===")

    for pessoa in pessoas:
        print(
            f"{pessoa.nome}: andar {pessoa.andar}, "
            f"aguardando para {pessoa.sentido}"
        )

    # Atendimento FIFO: uma parada por vez
    while elevador.consultar_fila():
        print("\n" + "=" * 44)
        print("       PRÓXIMO ATENDIMENTO")
        print("=" * 44)

        proxima = elevador.consultar_fila()[0]

        elevador.atender_proxima_solicitacao()

        andar = elevador.andar_atual

        # Desembarcar quem chegou ao destino
        for pessoa in pessoas:
            if (
                pessoa.estado == "dentro"
                and pessoa.destino == andar
            ):
                origem = pessoa.andar
                destino = pessoa.destino

                if pessoa.desembarcar(elevador):
                    viagens.append({
                        "pessoa": pessoa.nome,
                        "origem": origem,
                        "destino": destino
                    })

        # Embarcar quem fez a chamada externa
        if proxima["tipo"] == "externa":
            chave = (
                proxima["andar"],
                proxima["sentido"]
            )

            integrantes = grupos.get(chave, [])

            embarcando = []

            for pessoa in integrantes:
                if pessoa.embarcar(elevador):
                    embarcando.append(pessoa)

            if embarcando:
                print(
                    f"\n{len(embarcando)} pessoa(s) "
                    f"embarcaram no andar {andar}."
                )

                primeiro_numero = int(
                    embarcando[0].nome.split()[-1]
                )

                destinos = painel.escolher_destinos_grupo(
                    quantidade_pessoas=len(embarcando),
                    sentido=proxima["sentido"],
                    primeiro_numero=primeiro_numero
                )

                for pessoa, registro in zip(
                    embarcando, destinos
                ):
                    pessoa.destino = registro["destino"]

        print("\nFila após atendimento:")
        painel.mostrar_fila()

    # Relatório final
    print("\n" + "=" * 44)
    print("       RELATÓRIO DE VIAGENS")
    print("=" * 44)

    for numero, viagem in enumerate(viagens, 1):
        print(
            f"{numero}. {viagem['pessoa']} | "
            f"{viagem['origem']} -> {viagem['destino']}"
        )

    print(f"\nTotal de pessoas: {len(pessoas)}")
    print(f"Viagens concluídas: {len(viagens)}")

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
