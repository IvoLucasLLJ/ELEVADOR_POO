"""Regras de domínio e cenários A–H; os dez testes da Aula 12 permanecem intactos."""
import unittest

from Aula_13_Predio.predio import Predio
from Aula_13_Predio.pessoa import Pessoa
from Aula_13_Predio.painel import Painel


class TestDominio(unittest.TestCase):
    def setUp(self):
        self.predio = Predio()
        self.e = self.predio.elevador
        self.painel = Painel(self.predio)

    def chegar(self):
        for _ in range(12):
            evento = self.e.avancar_um_andar()
            if self.e.portas_abertas:
                return evento
        self.fail('Não chegou ao destino em até 12 passos')

    def embarcar(self, andar=0, sentido='subir'):
        self.painel.chamar_externo(andar, sentido)
        self.chegar()
        return self.e.passageiros[-1]

    def estado(self):
        return (self.e.andar_atual, self.e.direcao, self.e.portas_abertas,
                self.e.consultar_fila(), self.e.historico, self.e.eventos,
                tuple((p.identificador, p.estado, p.andar, p.destinos,
                       p.destinos_atendidos) for p in self.predio.pessoas),
                tuple(tuple(p.identificador for p in a.pessoas) for a in self.predio.andares))

    def esvaziar(self):
        for _ in range(250):
            if not self.e.consultar_fila():
                return
            if self.e.portas_abertas:
                for p in self.e.passageiros:
                    if not p.destinos:
                        p.selecionar_destino(0 if p.sentido == 'descer' else 10, self.e)
                self.e.fechar_portas()
            else:
                self.e.avancar_um_andar()
        self.fail('Fila não esvaziou')

    def test_composicao_inicial(self):
        self.assertEqual([a.numero for a in self.predio.andares], list(range(11)))
        self.assertIs(self.e, self.predio.elevador)
        self.assertEqual(self.e.total_andares, 11)
        self.assertEqual(self.e.andar_atual, 0)
        self.assertEqual(self.e.direcao, 'parado')
        self.assertFalse(self.e.portas_abertas)
        self.assertEqual(self.e.consultar_fila(), [])
        self.assertEqual(self.predio.pessoas, ())

    def test_predio_rejeita_configuracoes_diferentes(self):
        for n in (0, 10, 12, True, 11.0, '11', None):
            with self.subTest(n=n), self.assertRaises(ValueError):
                Predio(n)

    def test_validacao_externa_atomica_cenario_g(self):
        for andar in (-1, 11, 1.5, True, False, '3', None):
            with self.subTest(andar=andar):
                antes = self.estado()
                with self.assertRaises(ValueError):
                    self.painel.chamar_externo(andar, 'subir')
                self.assertEqual(self.estado(), antes)

    def test_direcoes_invalidas_atomicas(self):
        for andar, sentido in ((0, 'descer'), (10, 'subir'), (5, ''),
                               (5, 'esquerda'), (5, None), (5, 1)):
            antes = self.estado()
            with self.subTest(andar=andar, sentido=sentido), self.assertRaises(ValueError):
                self.painel.chamar_externo(andar, sentido)
            self.assertEqual(self.estado(), antes)

    def test_normalizacao_e_espera_no_andar(self):
        resultado = self.predio.obter_andar(5).chamar_elevador(' DESCER ')
        pessoa = self.predio.pessoas[0]
        self.assertEqual(resultado['resultado'], 'registrada')
        self.assertEqual(pessoa.estado, 'aguardando')
        self.assertEqual(pessoa.origem, 5)
        self.assertEqual(self.predio.obter_andar(5).aguardando('descer'), (pessoa,))

    def test_propriedades_protegidas(self):
        pessoa = self.embarcar()
        for obj, nome in ((self.e, 'andar_atual'), (self.e, 'portas_abertas'),
                          (self.predio, 'elevador'), (pessoa, 'estado'),
                          (pessoa, 'destinos'), (self.predio.andares[0], 'numero')):
            with self.subTest(nome=nome), self.assertRaises(AttributeError):
                setattr(obj, nome, 99)

    def test_consultas_nao_expoem_fila(self):
        self.painel.chamar_externo(5, 'descer')
        copia = self.e.consultar_fila()
        copia[0]['andar'] = 99
        copia[0]['pessoas'] = ()
        self.e.solicitacoes.clear()
        self.assertEqual(self.e.consultar_fila()[0]['andar'], 5)
        self.assertEqual(self.e.consultar_fila()[0]['pessoas'], (1,))

    def test_estado_fora_inicial_da_pessoa(self):
        pessoa = Pessoa(1, self.predio.obter_andar(0))
        self.assertEqual(pessoa.estado, 'fora')
        self.assertEqual(pessoa.destinos, ())

    def test_cenario_a_chamada_simples(self):
        self.painel.chamar_externo(5, 'descer')
        pessoa = self.predio.pessoas[0]
        for esperado in range(1, 6):
            self.e.avancar_um_andar()
            self.assertEqual(self.e.andar_atual, esperado)
        self.assertEqual(pessoa.estado, 'dentro')
        pessoa.selecionar_destino(0, self.e)
        self.e.fechar_portas()
        self.chegar()
        self.assertIs(self.predio.pessoas[0], pessoa)
        self.assertEqual((pessoa.estado, pessoa.andar), ('fora', 0))
        self.assertIn(pessoa, self.predio.andares[0].pessoas)
        self.assertEqual(pessoa.destinos_atendidos, (0,))
        self.e.fechar_portas()
        self.assertEqual(self.e.consultar_fila(), [])

    def test_cenario_b_fila_externa_completa(self):
        chamadas = [(3, 'descer'), (0, 'subir'), (10, 'descer'), (8, 'descer')]
        for andar, sentido in chamadas:
            self.painel.chamar_externo(andar, sentido)
        self.assertEqual(self.e.solicitacoes, [3, 0, 10, 8])
        self.esvaziar()
        externas = [r['andar'] for r in self.e.historico if r['tipo'] == 'externa']
        self.assertEqual(externas, [3, 0, 10, 8])
        self.assertTrue(all(p.estado == 'fora' for p in self.predio.pessoas))

    def test_cenario_c_chamada_durante_movimento(self):
        self.painel.chamar_externo(7, 'descer')
        self.e.avancar_um_andar()
        self.assertEqual(self.e.andar_atual, 1)
        ativa = self.e.consultar_fila()[0]
        self.painel.chamar_externo(2, 'subir')
        self.assertEqual(self.e.consultar_fila()[0], ativa)
        self.e.avancar_um_andar()
        self.assertEqual(self.e.andar_atual, 2)
        self.assertFalse(self.e.portas_abertas)  # Não ultrapassa a chamada para 7.
        self.assertEqual(self.predio.pessoas[1].estado, 'aguardando')
        self.esvaziar()
        self.assertEqual([r['andar'] for r in self.e.historico][:2], [7, 2])

    def test_cenario_d_multiplos_destinos_mesma_identidade(self):
        pessoa = self.embarcar()
        for destino in (4, 6, 9):
            self.painel.escolher_destino(destino)
        self.assertEqual(len(self.predio.pessoas), 1)
        self.assertEqual(pessoa.destinos, (4, 6, 9))
        self.e.fechar_portas()
        for destino, pendentes in ((4, (6, 9)), (6, (9,)), (9, ())):
            self.chegar()
            self.assertEqual(self.e.andar_atual, destino)
            self.assertEqual(pessoa.destinos, pendentes)
            self.assertEqual(pessoa.estado, 'dentro' if pendentes else 'fora')
            self.assertIs(self.predio.pessoas[0], pessoa)
            self.e.fechar_portas()
        self.assertEqual(pessoa.destinos_atendidos, (4, 6, 9))

    def test_cenario_e_duplicata_pendente_ativa_e_concluida(self):
        self.painel.chamar_externo(0, 'subir')
        antes = self.estado()
        self.assertEqual(self.painel.chamar_externo(0, 'subir')['resultado'], 'duplicada')
        self.assertEqual(self.estado(), antes)
        self.chegar()
        self.assertEqual(self.painel.chamar_externo(0, 'subir')['resultado'], 'duplicada')
        self.assertEqual(len(self.predio.pessoas), 1)
        self.painel.escolher_destino(4)
        self.e.fechar_portas()
        self.assertEqual(self.painel.chamar_externo(0, 'subir')['resultado'], 'registrada')
        self.assertEqual(len(self.predio.pessoas), 2)
        self.esvaziar()

    def test_cenario_f_chamadas_opostas(self):
        self.painel.chamar_externo(5, 'subir')
        self.painel.chamar_externo(5, 'descer')
        subindo, descendo = self.predio.pessoas
        self.chegar()
        self.assertEqual((subindo.estado, descendo.estado), ('dentro', 'aguardando'))
        subindo.selecionar_destino(9, self.e)
        self.e.fechar_portas()
        self.chegar()
        self.assertEqual(self.e.andar_atual, 5)
        self.assertEqual(descendo.estado, 'dentro')
        descendo.selecionar_destino(0, self.e)
        self.e.fechar_portas()
        self.esvaziar()
        self.assertEqual([r.get('sentido') for r in self.e.historico[:2]], ['subir', 'descer'])

    def test_cenario_h_ociosidade_e_nova_chamada(self):
        self.painel.iniciar()
        for _ in range(3):
            self.assertEqual(self.painel.atualizar()['evento'], 'ocioso')
        self.embarcar()
        self.painel.escolher_destino(1)
        self.e.fechar_portas()
        self.chegar()
        self.painel.atualizar()  # Fechamento automático da cabine vazia.
        self.assertFalse(self.e.portas_abertas)
        self.assertEqual(self.painel.atualizar()['evento'], 'ocioso')
        self.painel.chamar_externo(3, 'descer')
        self.painel.atualizar()
        self.assertEqual(self.e.andar_atual, 2)

    def test_portas_abertas_impedem_movimento(self):
        self.embarcar()
        self.painel.escolher_destino(7)
        antes = self.estado()
        for _ in range(5):
            self.assertEqual(self.e.avancar_um_andar()['evento'], 'portas_abertas')
        self.assertEqual(self.estado(), antes)

    def test_fechar_exige_destino_sem_mutacao(self):
        self.embarcar()
        antes = self.estado()
        with self.assertRaises(ValueError):
            self.e.fechar_portas()
        self.assertEqual(self.estado(), antes)

    def test_sem_embarque_interno_e_desembarque_indevidos(self):
        self.painel.chamar_externo(5, 'descer')
        pessoa = self.predio.pessoas[0]
        for operacao in (lambda: pessoa.embarcar(self.e),
                         lambda: pessoa.desembarcar(self.e),
                         lambda: pessoa.selecionar_destino(0, self.e)):
            antes = self.estado()
            with self.assertRaises(ValueError):
                operacao()
            self.assertEqual(self.estado(), antes)

    def test_painel_interno_sem_pessoa(self):
        with self.assertRaises(ValueError):
            self.painel.escolher_destino(3)
        self.assertEqual(self.predio.pessoas, ())

    def test_destinos_invalidos_atomicos(self):
        pessoa = self.embarcar(5, 'descer')
        for andar in (-1, 11, 1.1, True, '3', None, 5, 6):
            antes = self.estado()
            with self.subTest(andar=andar), self.assertRaises(ValueError):
                pessoa.selecionar_destino(andar, self.e)
            self.assertEqual(self.estado(), antes)

    def test_primeiro_destino_respeita_subida(self):
        pessoa = self.embarcar(5, 'subir')
        with self.assertRaises(ValueError):
            pessoa.selecionar_destino(4, self.e)
        pessoa.selecionar_destino(9, self.e)
        pessoa.selecionar_destino(2, self.e)  # Outra etapa da mesma viagem.
        self.assertEqual(pessoa.destinos, (9, 2))

    def test_duplicata_interna_nao_modifica_pessoa(self):
        pessoa = self.embarcar()
        pessoa.selecionar_destino(4, self.e)
        antes = self.estado()
        self.assertEqual(pessoa.selecionar_destino(4, self.e)['resultado'], 'duplicada')
        self.assertEqual(self.estado(), antes)

    def test_destino_compartilhado_preserva_ambas_pessoas(self):
        self.painel.chamar_externo(0, 'subir')
        self.painel.chamar_externo(2, 'subir')
        self.chegar()
        primeira = self.e.passageiros[0]
        primeira.selecionar_destino(8, self.e)
        self.e.fechar_portas()
        self.chegar()
        segunda = self.e.passageiros[-1]
        resultado = segunda.selecionar_destino(8, self.e)
        self.assertEqual(resultado['resultado'], 'vinculada')
        self.assertEqual(len([r for r in self.e.consultar_fila() if r['tipo'] == 'interna']), 1)
        self.e.fechar_portas()
        self.chegar()
        self.assertEqual((primeira.estado, segunda.estado), ('fora', 'fora'))
        self.assertEqual(primeira.destinos_atendidos, (8,))
        self.assertEqual(segunda.destinos_atendidos, (8,))

    def test_fila_global_prevalece_sobre_ordem_individual(self):
        self.painel.chamar_externo(0, 'subir')
        self.painel.chamar_externo(2, 'subir')
        self.chegar()
        self.painel.escolher_destino(6)
        self.e.fechar_portas()
        self.chegar()
        segunda = self.e.passageiros[-1]
        segunda.selecionar_destino(9, self.e)
        segunda.selecionar_destino(6, self.e)
        self.e.fechar_portas()
        self.chegar()
        self.assertEqual(segunda.destinos, (9,))
        self.assertEqual(segunda.estado, 'dentro')
        self.e.fechar_portas()
        self.chegar()
        self.assertEqual(segunda.destinos_atendidos, (6, 9))
        self.assertEqual(segunda.estado, 'fora')

    def test_localizacao_acompanha_cabine(self):
        pessoa = self.embarcar()
        pessoa.selecionar_destino(4, self.e)
        self.e.fechar_portas()
        self.e.avancar_um_andar()
        self.assertEqual(pessoa.andar, 1)
        self.assertEqual(pessoa.origem, 0)
        self.assertNotIn(pessoa, self.predio.andares[0].pessoas)

    def test_andar_atual_respeita_chamada_anterior(self):
        self.painel.chamar_externo(5, 'descer')
        self.painel.chamar_externo(0, 'subir')
        self.e.avancar_um_andar()
        self.assertEqual(self.e.andar_atual, 1)
        self.assertFalse(self.e.portas_abertas)
        self.assertEqual(self.predio.pessoas[1].estado, 'aguardando')

    def test_mesmo_andar_sem_deslocamento(self):
        self.painel.chamar_externo(0, 'subir')
        evento = self.e.avancar_um_andar()
        self.assertEqual(evento['evento'], 'parada')
        self.assertEqual(self.e.andar_atual, 0)
        self.assertTrue(self.e.portas_abertas)
        self.assertEqual(self.e.direcao, 'parado')

    def test_solicitacoes_mantem_tipo_estado_e_ordem(self):
        self.embarcar()
        self.painel.escolher_destino(4)
        primeira, segunda = self.e.consultar_fila()
        self.assertEqual((primeira['tipo'], primeira['estado'], primeira['ordem']),
                         ('externa', 'em_atendimento', 1))
        self.assertEqual((segunda['tipo'], segunda['estado'], segunda['ordem']),
                         ('interna', 'pendente', 2))
        self.e.fechar_portas()
        self.assertEqual(self.e.ultimo_atendimento['estado'], 'concluida')
        copia = self.e.historico
        copia[0]['andar'] = 99
        self.assertEqual(self.e.historico[0]['andar'], 0)

    def test_pausa_preserva_movimento_e_aceita_externas(self):
        self.painel.chamar_externo(7, 'descer')
        self.painel.iniciar()
        self.painel.atualizar()
        self.painel.alternar_pausa()
        self.painel.chamar_externo(3, 'descer')
        for _ in range(3):
            self.painel.atualizar()
        self.assertEqual(self.e.andar_atual, 1)
        self.painel.alternar_pausa()
        self.painel.atualizar()
        self.assertEqual(self.e.andar_atual, 2)

    def test_antes_do_inicio_nao_movimenta(self):
        self.painel.chamar_externo(5, 'descer')
        self.painel.atualizar()
        self.assertEqual(self.e.andar_atual, 0)
        with self.assertRaises(ValueError):
            self.painel.alternar_pausa()

    def test_selecao_pessoa_valida_e_sem_cadastro(self):
        pessoa = self.embarcar()
        for identificador in (999, True, '1'):
            antes = self.estado()
            with self.assertRaises(ValueError):
                self.painel.escolher_destino(4, identificador)
            self.assertEqual(self.estado(), antes)
        self.painel.escolher_destino(4, pessoa.identificador)
        self.assertEqual(pessoa.destinos, (4,))

    def test_pertencimento_unico_em_fluxo_completo(self):
        for andar, sentido in ((3, 'descer'), (0, 'subir'), (10, 'descer'), (8, 'descer')):
            self.painel.chamar_externo(andar, sentido)
        self.esvaziar()
        for pessoa in self.predio.pessoas:
            locais = sum(pessoa in a.pessoas for a in self.predio.andares)
            self.assertEqual(locais + (pessoa in self.e.passageiros), 1)
            self.assertEqual(pessoa.estado, 'fora')
        self.assertTrue(all('quantidade_pessoas' not in r for r in self.e.historico))


if __name__ == '__main__':
    unittest.main()
