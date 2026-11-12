"""Regressões da auditoria: relógio controlado e integração do domínio."""
import contextlib
import io
import unittest

from Aula_13_Predio.andar import Andar
from Aula_13_Predio.painel import Painel
from Aula_13_Predio.pessoa import Pessoa
from Aula_13_Predio.predio import Predio


class Relogio:
    def __init__(self):
        self.agora = 0.0

    def __call__(self):
        return self.agora


class TestQualidade(unittest.TestCase):
    def setUp(self):
        self.relogio = Relogio()
        self.predio = Predio()
        self.p = Painel(self.predio, relogio=self.relogio)
        self.e = self.p.elevador
        self.p.iniciar()

    def chegar(self):
        for _ in range(12):
            r = self.p.atualizar()
            if r['evento'] == 'parada':
                return r
        self.fail('Não chegou em 12 passos')

    def embarcar(self, destinos=(5, 6, 7)):
        self.p.chamar_externo(1, 'subir')
        self.chegar()
        pessoa = self.e.passageiros[0]
        for andar in destinos:
            self.p.escolher_destino(andar, pessoa.identificador)
        return pessoa

    def primeira_parada_interna(self):
        pessoa = self.embarcar()
        self.p.fechar_portas()
        self.chegar()
        self.assertEqual(self.e.andar_atual, 5)
        return pessoa

    def test_construtores_e_configuracao(self):
        self.assertEqual(self.p.tempo_portas, 1.5)
        self.assertFalse(self.p.pausado)
        self.assertEqual(self.p.situacao, 'parado')
        for tempo in (-1, True, '1.5', None, float('nan'), float('inf')):
            with self.subTest(tempo=tempo), self.assertRaises(ValueError):
                Painel(self.predio, tempo_portas=tempo)
        self.assertEqual(Painel(self.predio, tempo_portas=0).tempo_portas, 0)
        for identificador in (0, -1, True, '1', 1.5):
            with self.subTest(identificador=identificador), self.assertRaises(ValueError):
                Pessoa(identificador, self.predio.andares[0])
        for numero in (-1, 11, True, '1'):
            with self.subTest(numero=numero), self.assertRaises(ValueError):
                Andar(numero, self.predio)

    def test_1_5_6_7_sem_fechamento_manual_intermediario(self):
        pessoa = self.embarcar()
        self.assertEqual(pessoa.estado, 'dentro')
        self.assertEqual(pessoa.destinos, (5, 6, 7))
        self.p.fechar_portas()  # Somente no embarque.
        for destino, restantes in ((5, (6, 7)), (6, (7,)), (7, ())):
            r = self.chegar()
            self.assertEqual(r['andar'], destino)
            self.assertTrue(self.e.portas_abertas)
            self.assertEqual(pessoa.destinos, restantes)
            self.assertEqual(pessoa.estado, 'dentro' if restantes else 'fora')
            self.relogio.agora += 1.5
            self.assertEqual(self.p.atualizar()['evento'], 'fechamento')
            self.assertFalse(self.e.portas_abertas)
            self.assertEqual(self.e.ultimo_atendimento['andar'], destino)
        self.assertEqual(pessoa.destinos_atendidos, (5, 6, 7))
        self.assertEqual(self.e.consultar_fila(), [])
        self.assertEqual(self.p.atualizar()['evento'], 'ocioso')
        self.p.chamar_externo(7, 'descer')
        self.assertEqual(self.p.atualizar()['evento'], 'parada')
        self.assertEqual(len(self.e.passageiros), 1)

    def test_prazo_real_de_1_5_segundo(self):
        self.primeira_parada_interna()
        self.relogio.agora = 1.499
        self.assertEqual(self.p.atualizar()['evento'], 'portas_abertas')
        self.assertEqual(self.e.andar_atual, 5)
        self.relogio.agora = 1.5
        self.assertEqual(self.p.atualizar(mover=False)['evento'], 'fechamento')
        self.assertEqual(self.e.andar_atual, 5)
        self.assertEqual(self.p.atualizar()['evento'], 'parada')
        self.assertEqual(self.e.andar_atual, 6)

    def test_configuracao_altera_prazo(self):
        self.p = Painel(self.predio, tempo_portas=3, relogio=self.relogio)
        self.p.iniciar()
        self.primeira_parada_interna()
        self.relogio.agora = 1.5
        self.assertEqual(self.p.atualizar()['evento'], 'portas_abertas')
        self.relogio.agora = 3
        self.assertEqual(self.p.atualizar()['evento'], 'fechamento')

    def test_embarque_aguarda_escolha_e_fechamento_manual(self):
        self.embarcar(destinos=())
        self.relogio.agora = 100
        for _ in range(3):
            self.assertEqual(self.p.atualizar()['evento'], 'portas_abertas')
        with self.assertRaises(ValueError):
            self.p.fechar_portas()
        self.p.escolher_destino(5)
        self.relogio.agora = 200
        self.assertEqual(self.p.atualizar()['evento'], 'portas_abertas')
        self.p.fechar_portas()
        self.assertFalse(self.e.portas_abertas)

    def test_pausa_preserva_tempo_restante_e_nao_move(self):
        self.primeira_parada_interna()
        self.relogio.agora = 0.5
        self.p.alternar_pausa()
        antes = (self.e.consultar_fila(), self.e.eventos, self.e.andar_atual)
        self.relogio.agora = 100
        for _ in range(5):
            self.assertEqual(self.p.atualizar()['evento'], 'aguardando')
            self.p.atualizar(mover=False)
        self.assertEqual((self.e.consultar_fila(), self.e.eventos, self.e.andar_atual), antes)
        self.assertTrue(self.e.portas_abertas)
        self.p.iniciar()
        self.assertTrue(self.p.pausado)  # Atalho não contorna a pausa.
        self.p.alternar_pausa()
        self.relogio.agora = 100.999
        self.assertEqual(self.p.atualizar()['evento'], 'portas_abertas')
        self.relogio.agora = 101
        self.assertEqual(self.p.atualizar()['evento'], 'fechamento')

    def test_pausas_repetidas_nao_acumulam_prazos_obsoletos(self):
        self.primeira_parada_interna()
        for inicio, fim in ((0.25, 10.25), (10.5, 30.5)):
            self.relogio.agora = inicio
            self.p.alternar_pausa()
            self.relogio.agora = fim
            self.p.alternar_pausa()
        self.relogio.agora = 31.499
        self.assertEqual(self.p.atualizar()['evento'], 'portas_abertas')
        self.relogio.agora = 31.5
        self.assertEqual(self.p.atualizar()['evento'], 'fechamento')

    def test_prazo_antigo_nao_fecha_parada_posterior(self):
        self.primeira_parada_interna()
        self.relogio.agora = 1
        self.p.fechar_portas()
        self.chegar()
        self.assertEqual(self.e.andar_atual, 6)
        self.relogio.agora = 1.5  # Prazo que pertencia ao andar 5.
        self.assertEqual(self.p.atualizar(mover=False)['evento'], 'portas_abertas')
        self.assertTrue(self.e.portas_abertas)
        self.relogio.agora = 2.5
        self.assertEqual(self.p.atualizar(mover=False)['evento'], 'fechamento')
        # Pulsos concorrentes são serializados; só um fechamento é registrado.
        for _ in range(10):
            self.p.atualizar(mover=False)
        self.assertEqual([r['andar'] for r in self.e.historico], [1, 5, 6])
        self.assertEqual(self.e.andar_atual, 6)

    def test_fechamento_direto_no_dominio_tambem_invalida_prazo(self):
        self.primeira_parada_interna()
        self.relogio.agora = 1
        self.e.fechar_portas()
        self.e.avancar_um_andar()
        self.relogio.agora = 1.5
        self.assertEqual(self.p.atualizar(mover=False)['evento'], 'portas_abertas')
        self.assertEqual(self.e.andar_atual, 6)
        self.relogio.agora = 3
        self.assertEqual(self.p.atualizar(mover=False)['evento'], 'fechamento')

    def test_nova_externa_durante_prazo_preserva_fifo(self):
        pessoa = self.primeira_parada_interna()
        self.p.chamar_externo(3, 'descer')
        self.relogio.agora = 1.5
        self.p.atualizar(mover=False)
        self.assertEqual(self.e.solicitacoes, [6, 7, 3])
        self.assertEqual(pessoa.estado, 'dentro')
        self.chegar()
        self.assertEqual(self.e.andar_atual, 6)
        self.relogio.agora = 3
        self.p.atualizar(mover=False)
        self.chegar()
        self.assertEqual(self.e.andar_atual, 7)
        self.assertEqual(pessoa.estado, 'fora')
        self.p.atualizar()  # Cabine vazia.
        self.chegar()
        self.assertEqual(self.e.andar_atual, 3)

    def test_chamada_imediatamente_apos_fechamento(self):
        self.primeira_parada_interna()
        self.relogio.agora = 1.5
        self.p.atualizar(mover=False)
        self.p.chamar_externo(5, 'descer')
        self.assertEqual(self.e.solicitacoes, [6, 7, 5])
        self.assertFalse(self.e.portas_abertas)

    def test_prazo_antigo_nao_fecha_novo_embarque(self):
        self.embarcar(destinos=(5, 7))
        self.p.chamar_externo(5, 'descer')
        self.p.fechar_portas()
        self.chegar()
        self.p.fechar_portas()  # Suprime o prazo do 5.
        self.chegar()  # 7, último destino da primeira pessoa.
        self.p.atualizar()
        self.chegar()  # Nova externa no 5.
        self.relogio.agora = 100
        self.assertEqual(self.p.atualizar()['evento'], 'portas_abertas')
        self.assertEqual(self.e.passageiros[0].destinos, ())
        self.assertEqual(self.e.passageiros[0].estado, 'dentro')

    def test_fechamento_manual_durante_pausa_nao_retoma_motor(self):
        self.primeira_parada_interna()
        self.p.alternar_pausa()
        self.p.fechar_portas()
        self.relogio.agora = 100
        self.p.atualizar()
        self.assertEqual(self.e.andar_atual, 5)
        self.assertFalse(self.e.portas_abertas)
        self.p.alternar_pausa()
        self.assertEqual(self.p.atualizar()['andar'], 6)
        self.assertTrue(self.e.portas_abertas)

    def test_pulso_de_portas_nunca_move(self):
        self.p.chamar_externo(10, 'descer')
        for _ in range(10):
            self.p.atualizar(mover=False)
        self.assertEqual(self.e.andar_atual, 0)
        self.assertEqual(self.e.consultar_fila()[0]['estado'], 'pendente')

    def test_saida_registra_viagem_incompleta(self):
        self.embarcar()
        self.p.fechar_portas()
        self.p.atualizar()
        with contextlib.redirect_stdout(io.StringIO()) as saida:
            self.p.mostrar_registros()
            self.p.mostrar_fila()
            self.predio.pessoas[0].mostrar_estado()
        self.assertIn('pendentes (5, 6, 7)', saida.getvalue())
        self.assertEqual(self.predio.pessoas[0].estado, 'dentro')
        self.assertEqual(len(self.e.consultar_fila()), 3)


if __name__ == '__main__':
    unittest.main()
