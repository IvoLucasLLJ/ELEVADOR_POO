"""Cenários novos da preparação da Aula 15, usando a API pública do simulador."""
import unittest

from elevador_completo import Painel, Predio


class RelogioManual:
    """Relógio de teste injetado pela API de Painel; dispensa esperas reais."""
    def __init__(self):
        self.agora = 0

    def __call__(self):
        return self.agora

    def avancar(self, segundos):
        self.agora += segundos


class TestDominio(unittest.TestCase):
    def setUp(self):
        self.predio = Predio()
        self.relogio = RelogioManual()
        self.painel = Painel(self.predio, tempo_portas=10, relogio=self.relogio)
        self.e = self.predio.elevador

    def chegar(self):
        """Percorre a próxima solicitação em até onze pulsos, sem tocar no estado."""
        self.assertFalse(self.e.portas_abertas)
        for _ in range(11):
            anterior = self.e.andar_atual
            resultado = self.painel.atualizar()
            self.assertLessEqual(abs(self.e.andar_atual - anterior), 1)
            self.assertIn(self.e.andar_atual, range(11))
            if self.e.portas_abertas:
                self.assertEqual(resultado['evento'], 'parada')
                self.assertEqual(self.e.direcao, 'parado')
                return
        self.fail('A solicitação não chegou em onze pulsos.')

    def embarcar(self, andar=0, sentido='subir', quantidade=1):
        self.painel.chamar_externo(andar, sentido, quantidade)
        self.painel.iniciar()
        self.chegar()
        return self.e.passageiros

    def estado(self):
        return (self.e.andar_atual, self.e.direcao, self.e.portas_abertas,
                self.e.consultar_fila(), self.e.historico, self.e.eventos,
                tuple((p.identificador, p.andar, p.estado, p.destinos,
                       p.destinos_atendidos) for p in self.predio.pessoas),
                tuple(a.pessoas for a in self.predio.andares))

    def test_composicao_e_limites_dos_andares(self):
        self.assertEqual(self.predio.total_andares, 11)
        self.assertEqual([a.numero for a in self.predio.andares], list(range(11)))
        self.assertEqual((self.e.andar_atual, self.e.direcao, self.e.portas_abertas),
                         (0, 'parado', False))
        self.assertEqual(self.e.total_andares, 11)
        self.assertEqual(self.e.consultar_fila(), [])
        self.assertEqual(self.e.passageiros, ())
        self.assertEqual(self.predio.pessoas, ())
        for valor in (0, 10):
            self.assertIs(self.predio.obter_andar(valor), self.predio.andares[valor])
        for valor in (-1, 11, True, 1.5, '2', None):
            with self.subTest(andar=valor), self.assertRaises(ValueError):
                self.predio.obter_andar(valor)
        for total in (0, 10, 12, True, 11.0):
            with self.subTest(total=total), self.assertRaises(ValueError):
                Predio(total)

    def test_chamada_externa_rejeitada_sem_mutacao_e_normalizacao(self):
        invalidas = [(-1, 'subir', 1), (11, 'descer', 1), (True, 'subir', 1),
                     (2.0, 'subir', 1), (0, 'descer', 1), (10, 'subir', 1),
                     (3, 'parado', 1), (3, None, 1), (3, 'subir', 0),
                     (3, 'subir', True), (3, 'subir', 1.5)]
        for args in invalidas:
            antes = self.estado()
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.painel.chamar_externo(*args)
            self.assertEqual(self.estado(), antes)
        resposta = self.predio.obter_andar(10).chamar_elevador(' DESCER ', 2)
        self.assertEqual(resposta['resultado'], 'registrada')
        self.assertEqual(resposta['solicitacao']['sentido'], 'descer')
        self.assertEqual(len(self.predio.obter_andar(10).aguardando('descer')), 2)

    def test_fifo_global_inclui_chamada_durante_movimento(self):
        for andar, sentido in ((8, 'descer'), (2, 'subir'), (5, 'descer')):
            self.painel.chamar_externo(andar, sentido)
        self.painel.iniciar()
        self.painel.atualizar()
        self.assertEqual(self.e.andar_atual, 1)
        self.painel.chamar_externo(1, 'subir')
        self.assertEqual(self.e.solicitacoes, [8, 2, 5, 1])
        self.chegar()
        self.assertEqual(self.e.andar_atual, 8)
        self.painel.escolher_destino(0)
        self.painel.fechar_portas()
        self.assertEqual(self.e.solicitacoes, [2, 5, 1, 0])
        self.chegar()
        self.assertEqual(self.e.andar_atual, 2)

    def test_duplicacao_pendente_ativa_e_nova_chamada_apos_conclusao(self):
        primeira = self.painel.chamar_externo(0, 'subir', 2)
        antes = self.estado()
        self.assertEqual(self.painel.chamar_externo(0, 'subir', 6)['resultado'], 'duplicada')
        self.assertEqual(self.estado(), antes)
        self.painel.iniciar()
        self.chegar()
        antes = self.estado()
        self.assertEqual(self.painel.chamar_externo(0, 'subir')['resultado'], 'duplicada')
        self.assertEqual(self.estado(), antes)
        for pessoa in self.e.passageiros:
            self.painel.escolher_destino(2, pessoa.identificador)
        self.painel.fechar_portas()
        nova = self.painel.chamar_externo(0, 'subir')
        self.assertEqual(nova['resultado'], 'registrada')
        self.assertEqual(primeira['solicitacao']['ordem'], 1)
        self.assertEqual(nova['solicitacao']['ordem'], 3)
        self.assertEqual(len(self.predio.pessoas), 3)

    def test_sentidos_opostos_no_mesmo_andar_sao_chamadas_distintas(self):
        self.painel.chamar_externo(5, 'subir')
        self.painel.chamar_externo(5, 'descer')
        fila = self.e.consultar_fila()
        self.assertEqual([r['sentido'] for r in fila], ['subir', 'descer'])
        self.painel.iniciar()
        self.chegar()
        self.assertEqual(self.e.passageiros, (self.predio.pessoas[0],))
        self.assertEqual(self.predio.obter_andar(5).aguardando('descer'),
                         (self.predio.pessoas[1],))

    def test_antes_do_inicio_e_pulso_sem_movimento(self):
        self.painel.chamar_externo(3, 'descer')
        antes = self.estado()
        self.assertEqual(self.painel.atualizar()['evento'], 'aguardando')
        self.assertEqual(self.estado(), antes)
        self.painel.iniciar()
        self.painel.atualizar(mover=False)
        self.assertEqual(self.estado(), antes)
        self.painel.atualizar()
        self.assertEqual(self.e.andar_atual, 1)

    def test_movimento_subida_descida_e_portas_na_chegada(self):
        (pessoa,) = self.embarcar(2, 'descer')
        self.assertEqual((pessoa.andar, pessoa.estado), (2, 'dentro'))
        self.painel.escolher_destino(0)
        self.painel.fechar_portas()
        self.painel.atualizar()
        self.assertEqual((self.e.andar_atual, self.e.direcao), (1, 'descendo'))
        self.assertFalse(self.e.portas_abertas)
        self.painel.atualizar()
        self.assertEqual((self.e.andar_atual, self.e.direcao), (0, 'parado'))
        self.assertTrue(self.e.portas_abertas)
        self.assertEqual((pessoa.estado, pessoa.andar), ('fora', 0))

    def test_portas_abertas_impedem_movimento(self):
        self.embarcar()
        antes = self.estado()
        self.assertEqual(self.e.avancar_um_andar()['evento'], 'portas_abertas')
        self.painel.atualizar()
        self.assertEqual(self.estado(), antes)

    def test_embarque_preserva_identidade_e_localizacao_unica(self):
        self.painel.chamar_externo(0, 'subir', 2)
        pessoas = self.predio.pessoas
        self.assertEqual(self.predio.obter_andar(0).pessoas, pessoas)
        with self.assertRaises(ValueError):
            pessoas[0].embarcar(self.e)
        self.painel.iniciar()
        self.chegar()
        for indice, pessoa in enumerate(pessoas):
            self.assertIs(self.e.passageiros[indice], pessoa)
            self.assertEqual(pessoa.estado, 'dentro')
            self.assertEqual(sum(pessoa in a.pessoas for a in self.predio.andares), 0)
        self.assertEqual(self.predio.obter_andar(0).pessoas, ())

    def test_fechamento_bloqueado_se_uma_pessoa_nao_tem_destino(self):
        p1, p2 = self.embarcar(quantidade=2)
        self.painel.escolher_destino(2, p1.identificador)
        antes = self.estado()
        with self.assertRaisesRegex(ValueError, 'Pessoa 2'):
            self.painel.fechar_portas()
        self.assertEqual(self.estado(), antes)
        self.painel.escolher_destino(3, p2.identificador)
        self.painel.fechar_portas()
        self.assertFalse(self.e.portas_abertas)

    def test_destinos_individuais_selecao_e_desembarque(self):
        p1, p2 = self.embarcar(quantidade=2)
        self.assertIs(self.painel.pessoa_ativa, p2)
        self.assertIs(self.painel.selecionar_pessoa(p1.identificador), p1)
        self.painel.escolher_destino(2)
        self.painel.atualizar(mover=False)
        self.assertIs(self.painel.pessoa_ativa, p1)
        self.painel.escolher_destino(3, p2.identificador)
        self.painel.fechar_portas()
        self.chegar()
        self.assertEqual((p1.estado, p1.andar), ('fora', 2))
        self.assertEqual(self.e.passageiros, (p2,))
        self.assertIs(self.predio.obter_andar(2).pessoas[0], p1)
        self.painel.fechar_portas()
        self.chegar()
        self.assertEqual((p2.estado, p2.andar), ('fora', 3))
        self.assertEqual(self.e.passageiros, ())
        self.painel.atualizar()
        self.assertEqual(self.e.consultar_fila(), [])
        self.assertEqual([r['andar'] for r in self.e.historico], [0, 2, 3])

    def test_destino_compartilhado_e_duplicacao_interna(self):
        p1, p2 = self.embarcar(quantidade=2)
        self.assertEqual(self.painel.escolher_destino(4, p1.identificador)['resultado'], 'registrada')
        antes = self.estado()
        self.assertEqual(self.painel.escolher_destino(4, p1.identificador)['resultado'], 'duplicada')
        self.assertEqual(self.estado(), antes)
        self.assertEqual(self.painel.escolher_destino(4, p2.identificador)['resultado'], 'vinculada')
        internas = [r for r in self.e.consultar_fila() if r['tipo'] == 'interna']
        self.assertEqual(len(internas), 1)
        self.assertEqual(internas[0]['pessoas'], (p1.identificador, p2.identificador))
        self.painel.fechar_portas()
        self.chegar()
        self.assertEqual(self.predio.obter_andar(4).pessoas, (p1, p2))
        self.painel.atualizar()
        self.assertEqual(len(self.e.historico), 2)

    def test_multiplos_destinos_preservam_pessoa_na_parada_intermediaria(self):
        (pessoa,) = self.embarcar()
        self.painel.escolher_destino(2)
        self.painel.escolher_destino(4)
        self.painel.fechar_portas()
        self.chegar()
        self.assertIs(self.e.passageiros[0], pessoa)
        self.assertEqual((pessoa.destinos, pessoa.destinos_atendidos), ((4,), (2,)))
        with self.assertRaises(ValueError):
            pessoa.desembarcar(self.e)
        self.painel.fechar_portas()
        self.chegar()
        self.assertEqual(pessoa.destinos, ())
        self.assertEqual(pessoa.destinos_atendidos, (2, 4))
        self.assertIs(self.predio.obter_andar(4).pessoas[0], pessoa)
        self.assertEqual(sum(pessoa in a.pessoas for a in self.predio.andares), 1)

    def test_destinos_invalidos_e_efeito_de_selecao_documentado(self):
        with self.assertRaises(ValueError):
            self.painel.escolher_destino(2)
        p1, p2 = self.embarcar(3, 'descer', 2)
        for destino in (-1, 11, True, 1.5, 3, 4):
            with self.subTest(destino=destino), self.assertRaises(ValueError):
                self.painel.escolher_destino(destino, p1.identificador)
            self.assertEqual(p1.destinos, ())
        # A escolha da pessoa ocorre antes da validação do destino, como no código.
        self.painel.selecionar_pessoa(p2.identificador)
        with self.assertRaises(ValueError):
            self.painel.escolher_destino(11, p1.identificador)
        self.assertIs(self.painel.pessoa_ativa, p1)
        for identificador in (999, True, '1'):
            with self.subTest(id=identificador), self.assertRaises(ValueError):
                self.painel.selecionar_pessoa(identificador)

    def test_pausa_bloqueia_motor_e_aceita_novas_chamadas(self):
        self.painel.chamar_externo(5, 'descer')
        self.painel.iniciar()
        self.painel.atualizar()
        self.painel.alternar_pausa()
        self.painel.iniciar()
        self.assertTrue(self.painel.pausado)
        antes = self.estado()
        self.painel.atualizar()
        self.assertEqual(self.estado(), antes)
        self.painel.chamar_externo(2, 'subir')
        self.assertEqual(self.e.solicitacoes, [5, 2])
        self.painel.alternar_pausa()
        self.painel.atualizar()
        self.assertEqual(self.e.andar_atual, 2)

    def test_pausa_preserva_tempo_restante_das_portas(self):
        self.embarcar()
        self.painel.escolher_destino(2)
        self.painel.escolher_destino(4)
        self.painel.fechar_portas()
        self.chegar()
        self.relogio.avancar(3)
        self.painel.alternar_pausa()
        self.relogio.avancar(100)
        self.painel.atualizar(mover=False)
        self.assertTrue(self.e.portas_abertas)
        self.painel.alternar_pausa()
        self.relogio.avancar(6)
        self.painel.atualizar(mover=False)
        self.assertTrue(self.e.portas_abertas)
        self.relogio.avancar(1)
        self.assertEqual(self.painel.atualizar(mover=False)['evento'], 'fechamento')
        self.assertEqual(self.e.andar_atual, 2)
        self.assertFalse(self.e.portas_abertas)

    def test_consultas_nao_expoem_colecoes_ou_registros_internos(self):
        (pessoa,) = self.embarcar()
        fila = self.e.consultar_fila()
        fila[0]['andar'] = 10
        fila[0]['pessoas'] = ()
        fila.clear()
        self.e.solicitacoes.clear()
        self.assertEqual(self.e.consultar_fila()[0]['andar'], 0)
        self.assertEqual(self.e.consultar_fila()[0]['pessoas'], (pessoa.identificador,))
        for colecao in (self.predio.andares, self.predio.pessoas, self.e.passageiros,
                        self.e.eventos, pessoa.destinos, self.predio.obter_andar(0).pessoas):
            self.assertIsInstance(colecao, tuple)
        with self.assertRaises(AttributeError):
            pessoa.destinos = (10,)
        with self.assertRaises(AttributeError):
            self.e.andar_atual = 10
        self.painel.escolher_destino(2)
        self.painel.fechar_portas()
        historico = self.e.historico
        historico[0]['andar'] = 9
        self.assertEqual(self.e.historico[0]['andar'], 0)

    def test_conclusao_somente_ao_fechar_e_uma_vez(self):
        self.embarcar()
        self.assertEqual(self.e.historico, ())
        self.assertEqual(self.e.consultar_fila()[0]['estado'], 'em_atendimento')
        self.painel.escolher_destino(2)
        self.painel.fechar_portas()
        self.assertEqual(len(self.e.historico), 1)
        self.assertEqual(self.e.historico[0]['estado'], 'concluida')
        antes = self.estado()
        with self.assertRaises(ValueError):
            self.painel.fechar_portas()
        self.assertEqual(self.estado(), antes)

    def test_configuracao_de_tempo_e_pausa_antes_do_inicio(self):
        with self.assertRaises(ValueError):
            self.painel.alternar_pausa()
        for tempo in (-1, float('nan'), float('inf'), True, '1'):
            with self.subTest(tempo=tempo), self.assertRaises(ValueError):
                Painel(Predio(), tempo_portas=tempo)
        self.assertEqual(Painel(Predio(), tempo_portas=0).tempo_portas, 0)


if __name__ == '__main__':
    unittest.main()
