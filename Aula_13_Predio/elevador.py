class Elevador:
    def __init__(self, total_andares=None):
        if total_andares is not None:
            if type(total_andares) is not int or total_andares < 1:
                raise ValueError(
                    "O número de pavimentos deve ser positivo."
                )

        self.total_andares = total_andares
        self.andar_atual = 0
        self.direcao = "parado"
        self._fila = []
        self.ultimo_atendimento = None

    @property
    def solicitacoes(self):
        return [
            chamada["andar"]
            for chamada in self._fila
        ]

    def _validar_andar(self, andar):
        if type(andar) is not int or andar < 0:
            raise ValueError(
                "Informe um andar inteiro a partir do térreo."
            )

        if (
            self.total_andares is not None
            and andar >= self.total_andares
        ):
            raise ValueError(
                "Andar inexistente neste prédio."
            )

    def chamar(self, andar):
        # Compatibilidade com a chamada simples anterior
        self._validar_andar(andar)

        if andar in self.solicitacoes:
            print(f"Andar {andar} já está na fila.")
            return False

        self._fila.append({
            "tipo": "simples",
            "andar": andar
        })

        print(f"Chamada registrada: andar {andar}")
        return True

    def registrar_chamada_externa(
        self, andar, sentido, quantidade_pessoas=1
    ):
        self._validar_andar(andar)

        if not isinstance(sentido, str):
            raise ValueError("Sentido inválido.")

        sentido = sentido.strip().lower()

        if sentido not in ("subir", "descer"):
            raise ValueError(
                "O sentido deve ser subir ou descer."
            )

        if (
            type(quantidade_pessoas) is not int
            or quantidade_pessoas < 1
        ):
            raise ValueError(
                "A quantidade de pessoas deve ser positiva."
            )

        if andar == 0 and sentido == "descer":
            raise ValueError(
                "No térreo só é possível subir."
            )

        if (
            self.total_andares is not None
            and andar == self.total_andares - 1
            and sentido == "subir"
        ):
            raise ValueError(
                "No último andar só é possível descer."
            )

        # Agrupa pessoas que chamaram no mesmo andar
        # e solicitaram o mesmo sentido.
        for chamada in self._fila:
            if (
                chamada["tipo"] == "externa"
                and chamada["andar"] == andar
                and chamada["sentido"] == sentido
            ):
                chamada["quantidade_pessoas"] += quantidade_pessoas

                print(
                    f"Chamada agrupada no andar {andar}. "
                    f"Total: {chamada['quantidade_pessoas']} pessoas."
                )

                return chamada.copy()

        chamada = {
            "tipo": "externa",
            "andar": andar,
            "sentido": sentido,
            "quantidade_pessoas": quantidade_pessoas
        }

        self._fila.append(chamada)

        print(
            f"Chamada externa: andar {andar}, "
            f"sentido {sentido}, "
            f"{quantidade_pessoas} pessoa(s)."
        )

        return chamada.copy()

    def registrar_destino_interno(
        self, andar, quantidade_pessoas=1
    ):
        self._validar_andar(andar)

        if (
            type(quantidade_pessoas) is not int
            or quantidade_pessoas < 1
        ):
            raise ValueError(
                "A quantidade de pessoas deve ser positiva."
            )

        if andar == self.andar_atual:
            raise ValueError(
                "O elevador já está neste andar."
            )

        # Mesmo destino: uma parada para várias pessoas
        for parada in self._fila:
            if (
                parada["tipo"] == "interna"
                and parada["andar"] == andar
            ):
                parada["quantidade_pessoas"] += quantidade_pessoas

                print(
                    f"Destino {andar} já registrado. "
                    "Passageiros agrupados."
                )

                return parada.copy()

        parada = {
            "tipo": "interna",
            "andar": andar,
            "quantidade_pessoas": quantidade_pessoas
        }

        self._fila.append(parada)

        print(
            f"Destino interno: andar {andar}, "
            f"{quantidade_pessoas} pessoa(s)."
        )

        return parada.copy()

    def consultar_fila(self):
        return [
            chamada.copy()
            for chamada in self._fila
        ]

    def mover_para(self, andar_destino):
        self._validar_andar(andar_destino)

        if andar_destino == self.andar_atual:
            self.direcao = "parado"

            print(
                f"Elevador já está no andar {self.andar_atual}."
            )
            return

        if andar_destino > self.andar_atual:
            self.direcao = "subindo"
        else:
            self.direcao = "descendo"

        while self.andar_atual != andar_destino:
            if self.direcao == "subindo":
                self.andar_atual += 1
            else:
                self.andar_atual -= 1

            print(
                f"Elevador {self.direcao} - "
                f"andar: {self.andar_atual}"
            )

        print(
            f"Elevador chegou ao andar {self.andar_atual}."
        )

        self.direcao = "parado"

    def atender_proxima_solicitacao(self):
        if not self._fila:
            print("Nenhuma chamada pendente.")
            return None

        proxima = self._fila[0]

        print(
            f"\nPróximo atendimento: "
            f"andar {proxima['andar']} "
            f"({proxima['tipo']})"
        )

        self.mover_para(proxima["andar"])

        self.ultimo_atendimento = self._fila.pop(0).copy()

        print(
            f"Atendimento concluído: andar {proxima['andar']}."
        )

        return proxima["andar"]

    def atender_solicitacoes(self):
        while self._fila:
            self.atender_proxima_solicitacao()

        print("\nTodas as solicitações foram atendidas.")
