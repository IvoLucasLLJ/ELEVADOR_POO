"""Entrada oficial: python -m Aula_13_Predio.main."""

import argparse
from .predio import Predio
from .painel import Painel


def main(argv=None):
    parser = argparse.ArgumentParser(description="Elevador POO: 11 pavimentos e fila FIFO.")
    parser.add_argument("--texto", action="store_true", help="interface de comandos sem Textual")
    parser.add_argument("--tempo-portas", type=float, default=1.5,
                        help="segundos de espera nas paradas internas (padrão: 1.5)")
    args = parser.parse_args(argv)
    try:
        painel = Painel(Predio(), tempo_portas=args.tempo_portas)
    except ValueError as erro:
        parser.error(str(erro))
    if args.texto:
        from .interface_texto import executar
        executar(painel)
    else:
        try:
            from .interface import InterfaceElevador
        except ModuleNotFoundError as erro:
            if erro.name and erro.name.startswith("textual"):
                parser.exit(1, "Instale: python -m pip install -r requirements.txt\nOu use: python -m Aula_13_Predio.main --texto\n")
            raise
        InterfaceElevador(painel).run()
    painel.mostrar_registros()


if __name__ == "__main__":
    main()
