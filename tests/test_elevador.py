import io
import unittest
from contextlib import redirect_stdout

from elevador import Elevador


class TestElevador(unittest.TestCase):
    def setUp(self):
        self.elevador = Elevador()

    def executar_com_saida(self, metodo, *args):
        with redirect_stdout(io.StringIO()) as saida:
            metodo(*args)
        return saida.getvalue().splitlines()

    def registrar_chamadas(self, *andares):
        for andar in andares:
            self.elevador.chamar(andar)

    def verificar_paradas(self, linhas, andares):
        self.assertEqual(
            [linha for linha in linhas if linha.startswith('Elevador parou no ')],
            [f'Elevador parou no {andar}º andar' for andar in andares],
        )

    def test_estado_inicial(self):
        self.assertEqual(self.elevador.andar_atual, 0)
        self.assertEqual(self.elevador.direcao, 'parado')
        self.assertEqual(self.elevador.solicitacoes, [])

    def test_chamadas_sem_duplicacao(self):
        self.registrar_chamadas(3, 5, 8, 3, 5, 8)
        self.assertEqual(self.elevador.solicitacoes, [3, 5, 8])

    def test_subida_e_descida(self):
        for destino, direcao, percurso in (
            (5, 'subindo', [1, 2, 3, 4, 5]),
            (2, 'descendo', [4, 3, 2]),
        ):
            with self.subTest(destino=destino):
                linhas = self.executar_com_saida(self.elevador.mover_para, destino)
                self.assertEqual(
                    linhas,
                    [f'Elevador {direcao} - andar: {andar}' for andar in percurso]
                    + [f'Elevador chegou ao andar: {destino}'],
                )
                self.assertEqual(self.elevador.andar_atual, destino)
                self.assertEqual(self.elevador.direcao, 'parado')

    def test_ordem_de_atendimento(self):
        self.elevador.andar_atual = 4
        self.registrar_chamadas(7, 2, 5, 1)
        linhas = self.executar_com_saida(self.elevador.atender_solicitacoes)
        self.verificar_paradas(linhas, [5, 7, 2, 1])
        self.assertEqual(self.elevador.andar_atual, 1)
        self.assertEqual(self.elevador.direcao, 'parado')
        self.assertEqual(self.elevador.solicitacoes, [])

    def test_remocao_das_solicitacoes_atendidas(self):
        self.registrar_chamadas(3, 5, 8)
        linhas = self.executar_com_saida(self.elevador.mover_para, 5)
        self.verificar_paradas(linhas, [3, 5])
        self.assertEqual(self.elevador.solicitacoes, [8])
        linhas = self.executar_com_saida(self.elevador.mover_para, 8)
        self.verificar_paradas(linhas, [8])
        self.assertEqual(self.elevador.solicitacoes, [])

    def test_empate_prioriza_subida(self):
        self.elevador.andar_atual = 4
        self.registrar_chamadas(2, 6, 1, 8)
        linhas = self.executar_com_saida(self.elevador.atender_solicitacoes)
        self.verificar_paradas(linhas, [6, 8, 2, 1])
        self.assertEqual(self.elevador.solicitacoes, [])

    def test_chamada_no_andar_atual(self):
        self.elevador.andar_atual = 4
        self.elevador.chamar(4)
        linhas = self.executar_com_saida(self.elevador.atender_solicitacoes)
        self.assertEqual(linhas, [
            'Elevador já está no andar: 4',
            'Elevador parou no 4º andar',
        ])
        self.assertEqual(self.elevador.andar_atual, 4)
        self.assertEqual(self.elevador.direcao, 'parado')
        self.assertEqual(self.elevador.solicitacoes, [])

    def test_lista_vazia(self):
        self.elevador.andar_atual = 4
        linhas = self.executar_com_saida(self.elevador.atender_solicitacoes)
        self.assertEqual(linhas, [])
        self.assertEqual(self.elevador.andar_atual, 4)
        self.assertEqual(self.elevador.direcao, 'parado')
        self.assertEqual(self.elevador.solicitacoes, [])

    def test_destino_igual_ao_andar_atual_sem_chamada(self):
        linhas = self.executar_com_saida(self.elevador.mover_para, 0)
        self.assertEqual(linhas, ['Elevador já está no andar: 0'])
        self.assertEqual(self.elevador.andar_atual, 0)
        self.assertEqual(self.elevador.direcao, 'parado')

    def test_independencia_entre_instancias(self):
        outro = Elevador()
        self.elevador.chamar(3)
        outro.chamar(7)
        self.assertIsNot(self.elevador.solicitacoes, outro.solicitacoes)
        self.executar_com_saida(self.elevador.atender_solicitacoes)
        self.assertEqual(self.elevador.andar_atual, 3)
        self.assertEqual(self.elevador.solicitacoes, [])
        self.assertEqual(outro.andar_atual, 0)
        self.assertEqual(outro.direcao, 'parado')
        self.assertEqual(outro.solicitacoes, [7])


if __name__ == '__main__':
    unittest.main()
