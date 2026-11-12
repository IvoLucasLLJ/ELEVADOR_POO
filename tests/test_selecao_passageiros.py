"""Regressão do embarque: o painel deve acompanhar a nova pessoa."""
import unittest

from textual.widgets import Button, Select, Static

from Aula_13_Predio.interface import InterfaceElevador
from Aula_13_Predio.painel import Painel
from Aula_13_Predio.predio import Predio


class TestSelecaoTextual(unittest.IsolatedAsyncioTestCase):
    async def test_novo_embarque_seleciona_segunda_pessoa(self):
        painel = Painel(Predio())
        app = InterfaceElevador(painel, intervalo=100)
        async with app.run_test(size=(120, 35)) as pilot:
            painel.chamar_externo(0, 'subir')
            painel.chamar_externo(2, 'subir')
            painel.iniciar()
            app._tic()
            await pilot.pause()
            self.assertTrue(await pilot.click('#int-8'))
            self.assertTrue(await pilot.click('#fechar'))
            app._tic()
            app._tic()
            await pilot.pause()
            primeira, segunda = painel.elevador.passageiros
            self.assertEqual(app.query_one('#pessoa', Select).value, segunda.identificador)
            self.assertTrue(await pilot.click('#int-9'))
            self.assertEqual(primeira.destinos, (8,))
            self.assertEqual(segunda.destinos, (9,))
            self.assertTrue(await pilot.click('#fechar'))
            self.assertFalse(painel.elevador.portas_abertas)

    async def selecionar(self, pilot, app, identificador):
        await pilot.click('#pessoa')
        # A primeira opção é o prompt vazio; as seguintes seguem a cabine.
        await pilot.press('home')
        ids = [p.identificador for p in app.painel.elevador.passageiros]
        await pilot.press(*(['down'] * (ids.index(identificador) + 1)), 'enter')
        await pilot.pause()
        self.assertEqual(app.query_one('#pessoa', Select).value, identificador)
        self.assertEqual(app.painel.pessoa_ativa.identificador, identificador)
        self.assertEqual(str(app.query_one('#pessoa-ativa', Static).content),
                         f'SELECIONANDO DESTINOS PARA: Pessoa {identificador}')

    async def test_grupo_destinos_individuais_alternancia_e_bloqueio(self):
        painel = Painel(Predio())
        app = InterfaceElevador(painel, intervalo=100)
        async with app.run_test(size=(120, 35)) as pilot:
            await pilot.click('#quantidade')
            await pilot.press('home', 'down', 'enter')  # Duas pessoas, uma chamada.
            self.assertTrue(await pilot.click('#ext-1'))
            self.assertTrue(await pilot.click('#subir'))
            self.assertTrue(await pilot.click('#iniciar'))
            app._tic()
            await pilot.pause()
            primeira, segunda = painel.elevador.passageiros
            self.assertEqual(primeira.origem, segunda.origem)
            self.assertEqual(app.query_one('#pessoa', Select).value, 2)
            self.assertEqual(str(app.query_one('#pessoa-ativa', Static).content),
                             'SELECIONANDO DESTINOS PARA: Pessoa 2')
            await pilot.press('f')
            mensagem = str(app.query_one('#mensagem', Static).content)
            self.assertIn('Pessoa 1', mensagem)
            self.assertIn('Pessoa 2', mensagem)
            self.assertTrue(painel.elevador.portas_abertas)
            self.assertTrue(await pilot.click('#int-1'))  # Mesmo andar é inválido.
            self.assertEqual(segunda.destinos, ())
            self.assertTrue(await pilot.click('#int-9'))
            self.assertTrue(await pilot.click('#int-7'))
            self.assertEqual(segunda.destinos, (9, 7))
            self.assertIn('Pessoa 1', str(app.query_one('#pendencias', Static).content))
            self.assertNotIn('Pessoa 2', str(app.query_one('#pendencias', Static).content))
            await pilot.press('f')
            self.assertIn('Pessoa 1', str(app.query_one('#mensagem', Static).content))
            self.assertTrue(painel.elevador.portas_abertas)
            await self.selecionar(pilot, app, 1)
            self.assertEqual(str(app.query_one('#int-9', Button).label), '9')
            self.assertTrue(await pilot.click('#int-6'))
            self.assertTrue(await pilot.click('#int-8'))
            for _ in range(3):
                app._tic()
            await pilot.pause()
            self.assertEqual(app.query_one('#pessoa', Select).value, 1)
            self.assertEqual(primeira.destinos, (6, 8))
            self.assertEqual(segunda.destinos, (9, 7))
            await self.selecionar(pilot, app, 2)
            self.assertEqual(str(app.query_one('#int-9', Button).label), '9*')
            self.assertEqual(str(app.query_one('#int-6', Button).label), '6')
            self.assertTrue(await pilot.click('#int-9'))  # Duplicata só desta pessoa.
            self.assertEqual(segunda.destinos, (9, 7))
            await self.selecionar(pilot, app, 1)
            self.assertTrue(await pilot.click('#fechar'))
            self.assertFalse(painel.elevador.portas_abertas)
            self.assertTrue(app.is_running)

    async def test_desembarque_fifo_fechamento_automatico_e_nova_viagem(self):
        painel = Painel(Predio(), tempo_portas=0.2)
        app = InterfaceElevador(painel, intervalo=100)
        async with app.run_test(size=(120, 35)) as pilot:
            painel.chamar_externo(1, 'subir', quantidade=2)
            await pilot.press('i')
            app._tic()
            await pilot.pause()
            primeira, segunda = painel.elevador.passageiros
            self.assertTrue(await pilot.click('#int-7'))  # Pessoa 2.
            await self.selecionar(pilot, app, 1)
            self.assertTrue(await pilot.click('#int-5'))
            self.assertTrue(await pilot.click('#int-7'))
            await self.selecionar(pilot, app, 2)
            await pilot.press('f')
            for _ in range(6):
                app._tic()
            await pilot.pause(0.5)  # Timer de portas real; motor está em 100 s.
            self.assertFalse(painel.elevador.portas_abertas)
            self.assertEqual(painel.elevador.andar_atual, 7)
            self.assertEqual(segunda.estado, 'fora')
            self.assertEqual(primeira.destinos, (5,))
            self.assertEqual(app.query_one('#pessoa', Select).value, 1)
            self.assertEqual(str(app.query_one('#pessoa-ativa', Static).content),
                             'SELECIONANDO DESTINOS PARA: Pessoa 1')
            app._tic()
            app._tic()
            await pilot.pause(0.5)
            self.assertEqual([r['andar'] for r in painel.elevador.historico], [1, 7, 5])
            self.assertEqual(primeira.destinos_atendidos, (7, 5))
            self.assertEqual(segunda.destinos_atendidos, (7,))
            self.assertEqual((primeira.estado, primeira.andar), ('fora', 5))
            self.assertEqual((segunda.estado, segunda.andar), ('fora', 7))
            self.assertTrue(app.query_one('#pessoa', Select).disabled)
            self.assertTrue(all(app.query_one(f'#int-{n}', Button).disabled for n in range(11)))
            self.assertEqual(painel.elevador.consultar_fila(), [])
            self.assertTrue(app.is_running)
            painel.chamar_externo(5, 'descer')
            app._tic()
            await pilot.pause()
            self.assertEqual(app.query_one('#pessoa', Select).value, 3)
            self.assertTrue(await pilot.click('#int-0'))
            await pilot.press('f')
            for _ in range(5):
                app._tic()
            await pilot.pause(0.5)
            self.assertEqual(painel.predio.pessoas[2].destinos_atendidos, (0,))
            self.assertFalse(painel.elevador.portas_abertas)
            self.assertEqual(painel.elevador.consultar_fila(), [])
            self.assertTrue(app.is_running)

    async def test_layout_horizontal_compacto_com_grupo(self):
        painel = Painel(Predio())
        app = InterfaceElevador(painel, intervalo=100)
        async with app.run_test(size=(120, 35)) as pilot:
            painel.chamar_externo(0, 'subir', quantidade=6)
            painel.iniciar()
            app._tic()
            await pilot.pause()
            for largura, altura in ((120, 35), (140, 30), (100, 32)):
                await pilot.resize_terminal(largura, altura)
                await pilot.pause()
                conteudo = app.query_one('#conteudo')
                self.assertEqual(conteudo.scroll_y, 0)
                self.assertEqual(app.query_one('#externo').region.y,
                                 app.query_one('#interno').region.y)
                for seletor in ('#quantidade', '#pessoa-ativa', '#pessoa', '#pendencias',
                                '#int-10', '#subir', '#fechar'):
                    regiao = app.query_one(seletor).region
                    self.assertGreater(regiao.height, 0)
                    self.assertGreaterEqual(regiao.x, 0)
                    self.assertLessEqual(regiao.right, largura)
                    self.assertLessEqual(regiao.bottom, altura - 2)
                if largura >= 110:
                    self.assertEqual(app.query_one('#grade-interna').region.height, 6)
                    self.assertLessEqual(app.query_one('#colunas').region.height, 18)

    async def test_pulsos_pendentes_apos_sair_nao_movem_ou_atualizam_widgets(self):
        painel = Painel(Predio())
        app = InterfaceElevador(painel, intervalo=100)
        async with app.run_test(size=(120, 35)) as pilot:
            painel.chamar_externo(10, 'descer')
            await pilot.press('i')
            app._tic()
            self.assertEqual(painel.elevador.andar_atual, 1)
            await pilot.press('q')
        antes = (painel.elevador.andar_atual, painel.elevador.eventos,
                 painel.elevador.consultar_fila())
        # Um callback já enfileirado pode chegar durante a desmontagem.
        app._tic()
        app._portas()
        self.assertEqual((painel.elevador.andar_atual, painel.elevador.eventos,
                          painel.elevador.consultar_fila()), antes)


class TestSelecaoDominio(unittest.TestCase):
    def setUp(self):
        self.agora = 0.0
        self.painel = Painel(Predio(), relogio=lambda: self.agora)
        self.e = self.painel.elevador
        self.painel.iniciar()

    def chegar(self):
        for _ in range(12):
            resultado = self.painel.atualizar()
            if resultado['evento'] == 'parada':
                return
        self.fail('Não chegou em 12 passos')

    def test_dois_andares_selecao_automatica_e_manual(self):
        self.painel.chamar_externo(0, 'subir')
        self.painel.chamar_externo(2, 'subir')
        self.chegar()
        primeira = self.painel.pessoa_ativa
        self.painel.escolher_destino(8)
        self.painel.escolher_destino(6)
        self.painel.fechar_portas()
        self.chegar()
        segunda = self.painel.pessoa_ativa
        self.assertEqual(segunda.identificador, 2)
        self.painel.escolher_destino(9)
        self.painel.selecionar_pessoa(1)
        self.painel.escolher_destino(10)
        for _ in range(3):
            self.painel.atualizar()
        self.assertIs(self.painel.pessoa_ativa, primeira)
        self.assertEqual(primeira.destinos, (8, 6, 10))
        self.assertEqual(segunda.destinos, (9,))
        self.painel.selecionar_pessoa(2)
        self.painel.escolher_destino(8)
        self.assertEqual(segunda.destinos, (9, 8))
        self.assertEqual(self.e.consultar_fila()[1]['pessoas'], (1, 2))

    def test_grupo_mesma_parada_destinos_validos_e_identificacao(self):
        self.painel.chamar_externo(5, 'descer', quantidade=3)
        self.chegar()
        self.assertEqual([p.identificador for p in self.e.passageiros], [1, 2, 3])
        self.assertEqual(self.painel.pessoa_ativa.identificador, 3)
        self.assertEqual(self.painel.predio.andares[5].pessoas, ())
        for pessoa in self.e.passageiros:
            self.assertEqual((pessoa.estado, pessoa.andar), ('dentro', 5))
        for andar in (5, 6, -1, 11, True, None):
            with self.subTest(andar=andar), self.assertRaises(ValueError):
                self.painel.escolher_destino(andar)
            self.assertEqual(self.e.passageiros[-1].destinos, ())
        self.painel.escolher_destino(0)
        self.agora = 1000
        for _ in range(3):
            self.assertEqual(self.painel.atualizar()['evento'], 'portas_abertas')
        antes = self.e.consultar_fila(), self.e.eventos
        with self.assertRaisesRegex(ValueError, 'Pessoa 1, Pessoa 2'):
            self.painel.fechar_portas()
        self.assertEqual((self.e.consultar_fila(), self.e.eventos), antes)
        self.painel.escolher_destino(1, 1)
        with self.assertRaisesRegex(ValueError, 'Pessoa 2'):
            self.painel.fechar_portas()
        self.painel.escolher_destino(2, 2)
        self.painel.fechar_portas()
        self.assertFalse(self.e.portas_abertas)

    def test_grupo_fifo_desembarque_selecao_restante_e_reutilizacao(self):
        self.painel.chamar_externo(1, 'subir', quantidade=2)
        self.chegar()
        primeira, segunda = self.e.passageiros
        self.painel.escolher_destino(7)  # Pessoa 2 inicia a fila.
        self.painel.escolher_destino(5, 1)
        self.painel.escolher_destino(7)
        self.painel.selecionar_pessoa(2)
        self.painel.fechar_portas()
        self.chegar()
        self.assertIs(self.painel.pessoa_ativa, primeira)
        self.assertEqual((primeira.estado, primeira.destinos), ('dentro', (5,)))
        self.assertEqual((segunda.estado, segunda.andar), ('fora', 7))
        self.agora += 1.5
        self.assertEqual(self.painel.atualizar(mover=False)['evento'], 'fechamento')
        self.chegar()
        self.assertIsNone(self.painel.pessoa_ativa)
        self.assertEqual((primeira.estado, primeira.andar), ('fora', 5))
        self.assertEqual(primeira.destinos_atendidos, (7, 5))
        self.agora += 1.5
        self.assertEqual(self.painel.atualizar(mover=False)['evento'], 'fechamento')
        self.assertEqual([r['andar'] for r in self.e.historico], [1, 7, 5])
        self.assertEqual([r['ordem'] for r in self.e.historico], [1, 2, 3])
        self.assertEqual(self.e.consultar_fila(), [])
        self.assertEqual(self.painel.atualizar()['evento'], 'ocioso')
        self.painel.chamar_externo(5, 'descer')
        self.chegar()
        self.assertEqual(self.painel.pessoa_ativa.identificador, 3)
        self.painel.escolher_destino(0)
        self.painel.fechar_portas()
        self.chegar()
        self.painel.atualizar()
        self.assertIsNone(self.painel.pessoa_ativa)
        self.assertEqual(self.e.consultar_fila(), [])
        self.assertEqual(self.painel.predio.pessoas[-1].destinos_atendidos, (0,))

    def test_quantidade_invalida_nao_cria_pessoas_ou_chamadas(self):
        for quantidade in (0, -1, True, None, 1.5, '2'):
            with self.subTest(quantidade=quantidade), self.assertRaises(ValueError):
                self.painel.chamar_externo(1, 'subir', quantidade)
            self.assertEqual(self.painel.predio.pessoas, ())
            self.assertEqual(self.e.consultar_fila(), [])
        self.painel.chamar_externo(1, 'subir', quantidade=2)
        antes = self.painel.predio.pessoas, self.e.consultar_fila(), self.e.eventos
        self.assertEqual(self.painel.chamar_externo(1, 'subir', 2)['resultado'], 'duplicada')
        self.assertEqual((self.painel.predio.pessoas, self.e.consultar_fila(), self.e.eventos), antes)

    def test_pessoa_invalida_nao_recebe_destinos_nem_altera_selecao(self):
        with self.assertRaises(ValueError):
            self.painel.selecionar_pessoa(1)
        self.assertIsNone(self.painel.pessoa_ativa)
        self.painel.chamar_externo(0, 'subir', quantidade=2)
        self.chegar()
        for identificador in (0, 3, True, '1', 1.0, Select.NULL):
            with self.subTest(identificador=identificador), self.assertRaises(ValueError):
                self.painel.escolher_destino(4, identificador)
            self.assertEqual(self.painel.pessoa_ativa.identificador, 2)
            self.assertTrue(all(not p.destinos for p in self.e.passageiros))

    def test_embarque_direto_no_dominio_tambem_atualiza_selecao(self):
        self.painel.chamar_externo(0, 'subir')
        self.painel.chamar_externo(2, 'subir')
        self.e.avancar_um_andar()
        self.assertEqual(self.painel.pessoa_ativa.identificador, 1)
        self.painel.escolher_destino(8)
        self.e.fechar_portas()
        self.e.avancar_um_andar()
        self.e.avancar_um_andar()
        self.assertEqual(self.painel.pessoa_ativa.identificador, 2)
        self.painel.escolher_destino(9)
        self.assertEqual([p.destinos for p in self.e.passageiros], [(8,), (9,)])


class TestSelecaoTexto(unittest.TestCase):
    def test_comandos_de_grupo_selecao_persistente_e_aviso(self):
        from contextlib import redirect_stdout
        import io
        from Aula_13_Predio.interface_texto import executar_comando, mostrar_estado

        painel = Painel(Predio())
        with redirect_stdout(io.StringIO()):
            executar_comando(painel, 'externa 0 subir 2')
            executar_comando(painel, 'iniciar')
            painel.atualizar()
            executar_comando(painel, 'interna 9')
            executar_comando(painel, 'pessoa 1')
            executar_comando(painel, 'interna 6')
            executar_comando(painel, 'interna 8')
        self.assertEqual([p.destinos for p in painel.elevador.passageiros], [(6, 8), (9,)])
        self.assertEqual(painel.pessoa_ativa.identificador, 1)
        with redirect_stdout(io.StringIO()) as saida:
            mostrar_estado(painel)
        self.assertIn('SELECIONANDO DESTINOS PARA: Pessoa 1', saida.getvalue())
        with redirect_stdout(io.StringIO()):
            executar_comando(painel, 'fechar')
        self.assertFalse(painel.elevador.portas_abertas)

    def test_pessoa_e_quantidade_invalidas_rejeitadas_pelos_comandos(self):
        from contextlib import redirect_stdout
        import io
        from Aula_13_Predio.interface_texto import executar_comando, mostrar_estado

        painel = Painel(Predio())
        with redirect_stdout(io.StringIO()):
            for comando in ('pessoa 1', 'pessoa x', 'externa 0 subir 0',
                            'externa 0 subir x', 'externa 0 subir 2 extra'):
                with self.subTest(comando=comando), self.assertRaises(ValueError):
                    executar_comando(painel, comando)
                self.assertEqual(painel.predio.pessoas, ())
                self.assertEqual(painel.elevador.consultar_fila(), [])
            executar_comando(painel, 'externa 0 subir 2')
            executar_comando(painel, 'iniciar')
            painel.atualizar()
        with redirect_stdout(io.StringIO()) as saida:
            mostrar_estado(painel)
        self.assertIn('FALTA DESTINO: Pessoa 1, Pessoa 2', saida.getvalue())
        with self.assertRaisesRegex(ValueError, 'Pessoa 1, Pessoa 2'):
            executar_comando(painel, 'fechar')
        self.assertTrue(painel.elevador.portas_abertas)
