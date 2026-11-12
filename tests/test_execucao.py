"""Entrada oficial, alternativa textual e fluxo real com entrada por pipe."""
import contextlib
import io
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time
import unittest

from Aula_13_Predio.interface_texto import executar_comando
from Aula_13_Predio.painel import Painel
from Aula_13_Predio.predio import Predio

ROOT = Path(__file__).resolve().parents[1]


class TestExecucao(unittest.TestCase):
    def test_ajuda_ponto_de_entrada(self):
        r = subprocess.run([sys.executable, '-B', '-m', 'Aula_13_Predio.main', '--help'],
                           cwd=ROOT, capture_output=True, text=True, timeout=5)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('--texto', r.stdout)

    def test_importar_nao_executa_interface_nem_carrega_aula12(self):
        codigo = ("from Aula_13_Predio.main import main; "
                  "from Aula_13_Predio.predio import Predio; "
                  "print(type(Predio().elevador).__module__)")
        r = subprocess.run([sys.executable, '-B', '-S', '-c', codigo], cwd=ROOT,
                           capture_output=True, text=True, timeout=5)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), 'Aula_13_Predio.elevador')

    def test_fallback_sem_site_packages_e_varias_linhas_eof(self):
        r = subprocess.run([sys.executable, '-B', '-S', '-m', 'Aula_13_Predio.main', '--texto'],
                           cwd=ROOT, input='externa 5 descer\niniciar\nstatus\n',
                           capture_output=True, text=True, timeout=5)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('registrada', r.stdout)
        self.assertIn('Simulação encerrada', r.stdout)
        self.assertIn('RELATÓRIO DA SESSÃO', r.stdout)
        self.assertIn('aguardando no andar 5', r.stdout)
        self.assertNotIn('Traceback', r.stderr)

    def test_comandos_invalidos_nao_alteram_dominio(self):
        painel = Painel(Predio())
        for comando in ('externa abc subir', 'externa 11 descer', 'interna 4',
                        'externa 0 descer', 'sair extra', 'status extra', 'qualquer'):
            with contextlib.redirect_stdout(io.StringIO()), self.subTest(comando=comando):
                with self.assertRaises(ValueError):
                    executar_comando(painel, comando)
            self.assertEqual(painel.elevador.consultar_fila(), [])
            self.assertEqual(painel.predio.pessoas, ())

    def test_comandos_completam_viagem(self):
        painel = Painel(Predio())
        with contextlib.redirect_stdout(io.StringIO()):
            executar_comando(painel, 'externa 0 subir')
            executar_comando(painel, 'iniciar')
            painel.atualizar()
            executar_comando(painel, 'interna 4 1')
            executar_comando(painel, 'interna 6 1')
            executar_comando(painel, 'fechar')
            for _ in range(4):
                painel.atualizar()
            executar_comando(painel, 'fechar')
            for _ in range(2):
                painel.atualizar()
            painel.atualizar()
            self.assertFalse(executar_comando(painel, 'sair'))
        self.assertEqual(painel.predio.pessoas[0].destinos_atendidos, (4, 6))
        self.assertEqual(painel.predio.pessoas[0].estado, 'fora')

    def test_loop_real_aceita_comando_durante_movimento(self):
        codigo = ('from Aula_13_Predio.predio import Predio; '
                  'from Aula_13_Predio.painel import Painel; '
                  'from Aula_13_Predio.interface_texto import executar; '
                  'executar(Painel(Predio()), intervalo=0.15)')
        processo = subprocess.Popen([sys.executable, '-B', '-u', '-c', codigo],
                                    cwd=ROOT, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        saida = b''

        def enviar(texto):
            processo.stdin.write(texto.encode())
            processo.stdin.flush()

        def aguardar(trecho):
            nonlocal saida
            limite = time.monotonic() + 6
            alvo = trecho.encode()
            while alvo not in saida and time.monotonic() < limite:
                if select.select([processo.stdout], [], [], 0.2)[0]:
                    bloco = os.read(processo.stdout.fileno(), 16384)
                    if not bloco:
                        break
                    saida += bloco
            self.assertIn(alvo, saida, saida.decode(errors='replace'))

        try:
            enviar('externa 0 subir\niniciar\n')
            aguardar('Portas abertas no andar 0')
            enviar('interna 4\nfechar\n')
            aguardar('Elevador subindo: andar 1.')
            enviar('externa 2 descer\n')
            aguardar('Externa #3: andar 2, descer')
            aguardar('Portas abertas no andar 4')
            # Nova chamada não produziu parada intermediária no andar 2.
            self.assertNotIn(b'Portas abertas no andar 2', saida)
            aguardar('Portas abertas no andar 2')
            enviar('interna 0\nfechar\n')
            aguardar('Pessoa 2 desembarcou no andar 0')
            enviar('sair\n')
            processo.communicate(timeout=5)
            self.assertEqual(processo.returncode, 0)
        finally:
            if processo.poll() is None:
                processo.kill()
            processo.communicate()

    def test_saida_por_interrupcao(self):
        processo = subprocess.Popen(
            [sys.executable, '-B', '-u', '-m', 'Aula_13_Predio.main', '--texto'],
            cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            limite = time.monotonic() + 5
            saida = b''
            while b'Cabine:' not in saida and time.monotonic() < limite:
                if select.select([processo.stdout], [], [], 0.2)[0]:
                    saida += os.read(processo.stdout.fileno(), 8192)
            self.assertIn(b'Cabine:', saida)
            processo.send_signal(signal.SIGINT)
            resto, erros = processo.communicate(timeout=5)
            self.assertEqual(processo.returncode, 0, erros)
            self.assertIn('Simulação encerrada', resto.decode())
            self.assertNotIn(b'Traceback', erros)
        finally:
            if processo.poll() is None:
                processo.kill()
            processo.communicate()


if __name__ == '__main__':
    unittest.main()
