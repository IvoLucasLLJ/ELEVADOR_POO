"""Alternativa POSIX/Termux sem dependências e sem bloquear o movimento."""

import codecs
import os
import select
import sys
import time

AJUDA = """PAINEL EXTERNO: externa ANDAR subir|descer [QUANTIDADE]
PAINEL INTERNO: interna DESTINO [ID] · pessoa ID para alternar a pessoa ativa
OPERAÇÕES: iniciar, fechar, pausar (também retoma), status, ajuda, sair
Exemplo: externa 5 descer -> iniciar -> aguarde embarque -> interna 0 -> fechar
Nas paradas internas as portas fecham automaticamente; o embarque exige fechar.
Chamadas externas continuam disponíveis durante o movimento. Confirme com Enter.
"""


def executar_comando(painel, linha):
    partes = linha.strip().lower().split()
    if not partes:
        return True
    comando, *args = partes
    if comando == "sair" and not args:
        return False
    if comando == "externa" and len(args) in (2, 3):
        print(painel.chamar_externo(int(args[0]), args[1],
                                   int(args[2]) if len(args) == 3 else 1)["resultado"])
    elif comando == "interna" and len(args) in (1, 2):
        print(painel.escolher_destino(int(args[0]), int(args[1]) if len(args) == 2 else None)["resultado"])
    elif comando == "pessoa" and len(args) == 1:
        painel.selecionar_pessoa(int(args[0]))
    elif comando == "iniciar" and not args:
        painel.iniciar()
    elif comando == "fechar" and not args:
        painel.fechar_portas()
    elif comando == "pausar" and not args:
        painel.alternar_pausa()
    elif comando == "ajuda" and not args:
        print(AJUDA)
    elif comando != "status" or args:
        raise ValueError("Comando inválido. Digite ajuda.")
    mostrar_estado(painel)
    return True


def mostrar_estado(painel):
    e = painel.elevador
    print(f"Andar {e.andar_atual} | {e.direcao} | portas "
          f"{'abertas' if e.portas_abertas else 'fechadas'} | {painel.situacao}")
    print("Fila FIFO:", e.consultar_fila())
    print("Cabine:", [(p.nome, p.destinos) for p in e.passageiros])
    ativa = painel.pessoa_ativa
    print("SELECIONANDO DESTINOS PARA:", ativa.nome if ativa else "—")
    sem_destino = [p.nome for p in e.passageiros if not p.destinos]
    if sem_destino:
        print("FALTA DESTINO:", ", ".join(sem_destino))


def executar(painel, intervalo=1.0):
    print(AJUDA)
    mostrar_estado(painel)
    proximo = time.monotonic() + intervalo
    lidos = 0
    pendente = ""
    decodificador = codecs.getincrementaldecoder(sys.stdin.encoding or "utf-8")()
    continuar = True
    try:
        while continuar:
            agora = time.monotonic()
            pronto, _, _ = select.select([sys.stdin], [], [], max(0, min(0.1, proximo - agora)))
            if pronto:
                # Ler o descritor evita comandos presos no buffer de readline
                # quando várias linhas chegam no mesmo evento de entrada.
                dados = os.read(sys.stdin.fileno(), 4096)
                pendente += decodificador.decode(dados, final=not dados)
                linhas = pendente.split("\n")
                pendente = linhas.pop()
                if not dados:
                    if pendente:
                        linhas.append(pendente)
                    continuar = False
                for linha in linhas:
                    try:
                        if not executar_comando(painel, linha):
                            continuar = False
                            break
                    except ValueError as erro:
                        print("Entrada rejeitada:", erro)
                if not continuar:
                    break
            agora = time.monotonic()
            if agora >= proximo:
                painel.atualizar()
                proximo = agora + intervalo
            else:
                painel.atualizar(mover=False)
            eventos = painel.elevador.eventos
            if len(eventos) > lidos:
                for mensagem in eventos[lidos:]:
                    print(mensagem)
                lidos = len(eventos)
                mostrar_estado(painel)
    except KeyboardInterrupt:
        pass
    print("Simulação encerrada; dados desta sessão não são persistidos.")
