"""Testes oficiais run_test/Pilot: viagem, pausa, posição e redimensionamento."""
import asyncio
import json
from pathlib import Path
import time
import unittest

from textual.widgets import Button, RichLog, Static
from Aula_13_Predio.interface import InterfaceElevador
from Aula_13_Predio.painel import Painel
from Aula_13_Predio.predio import Predio

EVIDENCIAS = Path(__file__).resolve().parents[1] / 'evidencias'


class TestQualidadeInterface(unittest.IsolatedAsyncioTestCase):
    async def esperar(self, pilot, condicao, timeout=8):
        limite = time.monotonic() + timeout
        while not condicao() and time.monotonic() < limite:
            await pilot.pause(0.025)
        self.assertTrue(condicao(), 'Condição não ocorreu no tempo limite')

    async def test_viagem_real_1_5_6_7_somente_botoes_e_timers(self):
        painel = Painel(Predio())  # Prazo real padrão de 1,5 s.
        app = InterfaceElevador(painel, intervalo=0.2)
        async with app.run_test(size=(120, 42)) as pilot:
            self.assertTrue(await pilot.click('#ext-1'))
            self.assertTrue(await pilot.click('#subir'))
            self.assertTrue(await pilot.click('#iniciar'))
            await self.esperar(pilot, lambda: bool(painel.elevador.passageiros))
            pessoa = painel.elevador.passageiros[0]
            self.assertEqual((pessoa.estado, pessoa.origem), ('dentro', 1))
            for andar in (5, 6, 7):
                self.assertTrue(await pilot.click(f'#int-{andar}'))
            self.assertEqual(pessoa.destinos, (5, 6, 7))
            self.assertTrue(await pilot.click('#fechar'))  # Só no embarque.
            e = painel.elevador
            for andar, ordem in ((5, 2), (6, 3)):
                await self.esperar(pilot, lambda: e.portas_abertas and e.andar_atual == andar)
                self.assertEqual(pessoa.estado, 'dentro')
                self.assertEqual(str(app.query_one(f'#ext-{andar}', Button).label), f'>{andar}')
                self.assertEqual(str(app.query_one('#ext-1', Button).label), '1S')
                await self.esperar(pilot, lambda: any(r['ordem'] == ordem for r in e.historico))
                self.assertTrue(any(f'Portas fechadas; solicitação #{ordem} concluída.' == ev
                                    for ev in e.eventos))
            await self.esperar(pilot, lambda: pessoa.estado == 'fora' and not e.consultar_fila())
            self.assertEqual((e.andar_atual, pessoa.destinos_atendidos), (7, (5, 6, 7)))
            self.assertFalse(e.portas_abertas)
            self.assertTrue(app.is_running)
            # Continua aceitando e atendendo outra chamada no mesmo andar.
            self.assertTrue(await pilot.click('#ext-7'))
            self.assertTrue(await pilot.click('#descer'))
            await self.esperar(pilot, lambda: len(painel.predio.pessoas) == 2 and
                               painel.predio.pessoas[1].estado == 'dentro')
            self.assertEqual(painel.predio.pessoas[1].destinos, ())
            EVIDENCIAS.mkdir(exist_ok=True)
            (EVIDENCIAS / 'viagem_textual_eventos.log').write_text('\n'.join(e.eventos) + '\n')
            await pilot.press('q')

    async def test_pausa_na_abertura_aguarda_retomada(self):
        p = Painel(Predio(), tempo_portas=0.4)
        app = InterfaceElevador(p, intervalo=100)
        async with app.run_test(size=(120, 42)) as pilot:
            p.chamar_externo(1, 'subir')
            p.iniciar()
            app._tic()
            p.escolher_destino(5)
            p.escolher_destino(6)
            p.fechar_portas()
            for _ in range(4):
                app._tic()
            await pilot.press('space')
            self.assertTrue(p.pausado)
            await pilot.pause(0.7)
            self.assertTrue(p.elevador.portas_abertas)
            self.assertEqual(p.elevador.andar_atual, 5)
            await pilot.press('i')
            self.assertTrue(p.pausado)
            await pilot.press('space')
            await self.esperar(pilot, lambda: not p.elevador.portas_abertas)
            self.assertEqual(p.elevador.andar_atual, 5)  # Pulso de portas não move.
            app._tic()
            self.assertEqual(p.elevador.andar_atual, 6)

    async def test_estado_selecao_e_pendencias_usam_texto(self):
        p = Painel(Predio())
        app = InterfaceElevador(p, intervalo=100)
        async with app.run_test(size=(120, 42)) as pilot:
            await pilot.click('#ext-1')
            await pilot.click('#subir')
            await pilot.click('#ext-6')
            await pilot.click('#descer')
            self.assertEqual(str(app.query_one('#ext-0', Button).label), '>0')
            self.assertEqual(str(app.query_one('#ext-1', Button).label), '1*')
            self.assertEqual(str(app.query_one('#ext-6', Button).label), '6S*')
            await pilot.click('#iniciar')
            app._tic()
            await pilot.pause()
            self.assertTrue(app.query_one('#ext-1', Button).has_class('atual'))
            self.assertFalse(app.query_one('#ext-6', Button).has_class('atual'))
            self.assertIn('POSIÇÃO ATUAL: ANDAR 1', str(app.query_one('#estado', Static).content))

    async def test_redimensionamento_distribuicao_e_rolagem(self):
        app = InterfaceElevador(Painel(Predio()), intervalo=100)
        medidas = []
        async with app.run_test(size=(120, 50)) as pilot:
            for largura, altura in ((120, 50), (120, 35), (100, 24), (85, 28),
                                    (84, 28), (60, 24), (44, 32), (32, 20), (120, 50)):
                await pilot.resize_terminal(largura, altura)
                await pilot.pause()
                self.assertEqual(app.has_class('estreita'), largura < 85)
                self.assertEqual(app.has_class('mini'), largura < 40)
                acoes = app.query_one('#acoes').region
                for seletor in ('#iniciar', '#fechar', '#pausar', '#sair'):
                    b = app.query_one(seletor, Button)
                    r = b.region
                    self.assertGreaterEqual(r.y, acoes.y)
                    self.assertLessEqual(r.bottom, altura)
                    self.assertGreaterEqual(r.x, 0)
                    self.assertLessEqual(r.right, largura)
                    self.assertGreaterEqual(r.width, len(str(b.label)) + 2)
                externo = app.query_one('#externo').region
                interno = app.query_one('#interno').region
                if largura >= 85:
                    self.assertEqual(externo.y, interno.y)
                    self.assertEqual(externo.right, interno.x)
                    self.assertLessEqual(abs(externo.width - interno.width), 1)
                else:
                    self.assertLessEqual(externo.bottom, interno.y)
                eventos = app.query_one('#eventos', RichLog)
                if largura == 120 and altura == 50:
                    # O espaço livre pertence ao histórico e não fica vazio.
                    self.assertGreater(eventos.region.height, 6)
                eventos.scroll_visible(immediate=True)
                await pilot.pause()
                self.assertGreaterEqual(eventos.region.y, app.query_one('#conteudo').region.y)
                self.assertLess(eventos.region.y, acoes.y)
                medidas.append({'terminal': [largura, altura], 'acoes': list(acoes),
                                'eventos': list(eventos.region),
                                'rolagem_vertical': app.query_one('#conteudo').max_scroll_y})
                EVIDENCIAS.mkdir(exist_ok=True)
                app.save_screenshot(f'layout_{largura}x{altura}.svg', path=str(EVIDENCIAS))
            (EVIDENCIAS / 'layout_medidas.json').write_text(json.dumps(medidas, indent=2))

    async def test_erro_de_entrada_exibido_sem_encerrar(self):
        p = Painel(Predio())
        app = InterfaceElevador(p, intervalo=100)
        async with app.run_test(size=(100, 35)) as pilot:
            await pilot.press('f')
            self.assertIn('já estão fechadas', str(app.query_one('#mensagem', Static).content))
            await pilot.press('space')
            self.assertIn('Inicie', str(app.query_one('#mensagem', Static).content))
            self.assertTrue(app.is_running)

    async def test_encerrar_durante_viagem_cancela_timers_da_interface(self):
        p = Painel(Predio())
        app = InterfaceElevador(p, intervalo=0.2)
        async with app.run_test(size=(100, 35)) as pilot:
            p.chamar_externo(10, 'descer')
            await pilot.press('i')
            await self.esperar(pilot, lambda: 0 < p.elevador.andar_atual < 10)
            await pilot.press('q')
        antes = (p.elevador.andar_atual, p.elevador.eventos)
        await asyncio.sleep(0.3)
        self.assertEqual((p.elevador.andar_atual, p.elevador.eventos), antes)
        self.assertTrue(p.elevador.consultar_fila())
