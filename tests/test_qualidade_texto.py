"""Processo POSIX real: comandos não bloqueiam portas e movimento."""
import os
from pathlib import Path
import select
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestQualidadeTexto(unittest.TestCase):
    def test_viagem_1_5_6_7_sem_fechamentos_intermediarios(self):
        codigo = ('from Aula_13_Predio.predio import Predio; '
                  'from Aula_13_Predio.painel import Painel; '
                  'from Aula_13_Predio.interface_texto import executar; '
                  'p=Painel(Predio()); executar(p, intervalo=0.1); p.mostrar_registros()')
        processo = subprocess.Popen([sys.executable, '-B', '-u', '-S', '-c', codigo],
                                    cwd=ROOT, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        saida = b''

        def enviar(texto):
            processo.stdin.write(texto.encode())
            processo.stdin.flush()

        def aguardar(texto):
            nonlocal saida
            alvo = texto.encode()
            limite = time.monotonic() + 8
            while alvo not in saida and time.monotonic() < limite:
                if select.select([processo.stdout], [], [], 0.1)[0]:
                    bloco = os.read(processo.stdout.fileno(), 32768)
                    if not bloco:
                        break
                    saida += bloco
            self.assertIn(alvo, saida, saida.decode(errors='replace'))

        try:
            enviar('externa 1 subir\niniciar\n')
            aguardar('Pessoa 1 embarcou')
            # Não deve sair do embarque sem seleção nem fechamento manual.
            enviar('interna 5\ninterna 6\ninterna 7\nfechar\n')
            aguardar('Portas abertas no andar 5')
            aguardar('Portas fechadas; solicitação #2 concluída.')
            aguardar('Portas abertas no andar 6')
            aguardar('Portas fechadas; solicitação #3 concluída.')
            aguardar('Pessoa 1 desembarcou no andar 7')
            aguardar('Portas fechadas; solicitação #4 concluída.')
            enviar('status\n')
            aguardar('Fila FIFO: []')
            enviar('externa 7 descer\n')
            aguardar('Pessoa 2 embarcou')
            enviar('sair\n')
            resto, erros = processo.communicate(timeout=5)
            saida += resto
            self.assertEqual(processo.returncode, 0, erros)
            self.assertNotIn(b'Traceback', erros)
            self.assertIn(b'destinos atendidos (5, 6, 7)', saida)
            texto = saida.decode()
            self.assertLess(texto.index('Portas abertas no andar 5'),
                            texto.index('Portas abertas no andar 6'))
            (ROOT / 'evidencias').mkdir(exist_ok=True)
            (ROOT / 'evidencias' / 'viagem_alternativa_texto.log').write_text(texto)
        finally:
            if processo.poll() is None:
                processo.kill()
            processo.communicate()

    def test_configuracao_cli_invalida_sem_traceback(self):
        for valor in ('-1', 'nan', 'inf', 'abc'):
            r = subprocess.run([sys.executable, '-B', '-m', 'Aula_13_Predio.main',
                                '--texto', '--tempo-portas', valor], cwd=ROOT,
                               capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertNotIn('Traceback', r.stderr)

    def test_eof_sem_quebra_de_linha_e_entrada_invalida(self):
        r = subprocess.run([sys.executable, '-B', '-S', '-m', 'Aula_13_Predio.main',
                            '--texto', '--tempo-portas', '0.2'], cwd=ROOT,
                           input='externa -1 subir\nexterna 11 descer\nexterna x subir\nstatus',
                           capture_output=True, text=True, timeout=5)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count('Entrada rejeitada:'), 3)
        self.assertIn('Simulação encerrada', r.stdout)
        self.assertIn('Fila restante: []', r.stdout)
