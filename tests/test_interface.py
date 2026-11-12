"""Integração dos botões e do temporizador da interface Textual real."""
import unittest

from textual.widgets import Button, Select
from Aula_13_Predio.interface import InterfaceElevador
from Aula_13_Predio.painel import Painel
from Aula_13_Predio.predio import Predio


class TestInterface(unittest.IsolatedAsyncioTestCase):
    def criar(self, intervalo=100):
        painel = Painel(Predio())
        return painel, InterfaceElevador(painel, intervalo=intervalo)

    async def test_cenario_a_com_botoes(self):
        painel, app = self.criar()
        async with app.run_test(size=(120, 50)) as pilot:
            self.assertTrue(app.query_one('#int-0', Button).disabled)
            self.assertTrue(await pilot.click('#ext-5'))
            self.assertTrue(await pilot.click('#descer'))
            self.assertTrue(await pilot.click('#iniciar'))
            for _ in range(5):
                app._tic()
            await pilot.pause()
            self.assertEqual(painel.elevador.andar_atual, 5)
            self.assertTrue(painel.elevador.portas_abertas)
            self.assertFalse(app.query_one('#int-0', Button).disabled)
            self.assertTrue(await pilot.click('#int-0'))
            self.assertTrue(await pilot.click('#fechar'))
            for _ in range(5):
                app._tic()
            await pilot.pause()
            self.assertEqual(painel.predio.pessoas[0].estado, 'fora')
            app._tic()  # fecha cabine vazia
            self.assertEqual(painel.elevador.consultar_fila(), [])
            self.assertTrue(app.is_running)
            await pilot.press('q')

    async def test_cenario_c_temporizador_e_entrada_durante_movimento(self):
        painel, app = self.criar(intervalo=0.5)
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.click('#ext-10')
            await pilot.click('#descer')
            await pilot.click('#iniciar')
            await pilot.pause(0.6)
            antes = painel.elevador.andar_atual
            self.assertGreater(antes, 0)
            self.assertLess(antes, 10)
            await pilot.click('#ext-3')
            await pilot.click('#subir')
            self.assertEqual(painel.elevador.solicitacoes, [10, 3])
            self.assertEqual(painel.elevador.consultar_fila()[0]['estado'], 'em_atendimento')
            await pilot.pause(0.6)
            self.assertGreater(painel.elevador.andar_atual, antes)
            self.assertEqual(painel.predio.pessoas[1].estado, 'aguardando')

    async def test_cenario_d_multiplos_destinos_por_botoes(self):
        painel, app = self.criar()
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.click('#subir')  # andar selecionado inicialmente = 0
            await pilot.click('#iniciar')
            app._tic()
            await pilot.pause()
            for andar in (4, 6, 9):
                self.assertTrue(await pilot.click(f'#int-{andar}'))
            pessoa = painel.predio.pessoas[0]
            self.assertEqual(pessoa.destinos, (4, 6, 9))
            self.assertEqual(len(painel.predio.pessoas), 1)
            await pilot.click('#fechar')
            for destino in (4, 6, 9):
                while not painel.elevador.portas_abertas:
                    app._tic()
                self.assertEqual(painel.elevador.andar_atual, destino)
                await pilot.click('#fechar')
            self.assertEqual(pessoa.destinos_atendidos, (4, 6, 9))
            self.assertEqual(pessoa.estado, 'fora')

    async def test_pausa_retoma_e_limites(self):
        painel, app = self.criar()
        async with app.run_test(size=(120, 50)) as pilot:
            self.assertTrue(app.query_one('#descer', Button).disabled)
            await pilot.click('#ext-10')
            self.assertTrue(app.query_one('#subir', Button).disabled)
            await pilot.click('#descer')
            await pilot.click('#iniciar')
            app._tic()
            await pilot.press('space')
            self.assertTrue(painel.pausado)
            app._tic()
            self.assertEqual(painel.elevador.andar_atual, 1)
            await pilot.click('#ext-3')
            await pilot.click('#subir')
            self.assertEqual(painel.elevador.solicitacoes, [10, 3])
            await pilot.click('#pausar')
            app._tic()
            self.assertEqual(painel.elevador.andar_atual, 2)

    async def test_tela_estreita_rolagem_e_teclado(self):
        painel, app = self.criar()
        async with app.run_test(size=(44, 32)) as pilot:
            self.assertTrue(app.has_class('estreita'))
            # Teclado continua acessível mesmo sem mouse ou toque no terminal.
            painel.chamar_externo(0, 'subir')
            await pilot.press('i')
            app._tic()
            await pilot.pause()
            botao = app.query_one('#int-4', Button)
            botao.focus()
            await pilot.pause()
            await pilot.press('enter')
            self.assertEqual(painel.predio.pessoas[0].destinos, (4,))
            await pilot.press('f')
            self.assertFalse(painel.elevador.portas_abertas)
            self.assertGreaterEqual(app.query_one('#acoes').region.y, 0)

    async def test_seletor_de_pessoas_preserva_contexto(self):
        painel, app = self.criar()
        async with app.run_test(size=(120, 50)) as pilot:
            painel.chamar_externo(0, 'subir')
            painel.chamar_externo(2, 'subir')
            painel.iniciar()
            app._tic()
            painel.escolher_destino(8)
            painel.fechar_portas()
            app._tic()
            app._tic()
            await pilot.pause()
            primeira, segunda = painel.elevador.passageiros
            seletor = app.query_one('#pessoa', Select)
            self.assertEqual(seletor.value, segunda.identificador)
            seletor.value = segunda.identificador
            await pilot.click('#int-9')
            self.assertEqual(primeira.destinos, (8,))
            self.assertEqual(segunda.destinos, (9,))
            self.assertEqual(len(painel.predio.pessoas), 2)
