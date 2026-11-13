"""Fronteiras reais: importação isolada, argumentos e processo textual POSIX."""
import ast
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROGRAMA = ROOT / 'elevador_completo.py'


class TestExecucao(unittest.TestCase):
    def executar(self, *args, entrada=None, esperado=0):
        r = subprocess.run([sys.executable, '-B', '-I', '-S', str(PROGRAMA), *args],
                           cwd=ROOT, input=entrada, capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, esperado, r.stdout + r.stderr)
        self.assertNotIn('Traceback', r.stderr)
        return r

    def test_importacao_isolada_silenciosa_sem_iniciar_aplicacao(self):
        codigo = '''import contextlib
import importlib.util
import io
import sys
s = importlib.util.spec_from_file_location("entrega_isolada", sys.argv[1])
m = importlib.util.module_from_spec(s)
saida, erros = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erros):
    s.loader.exec_module(m)
assert saida.getvalue() == "", saida.getvalue()
assert erros.getvalue() == "", erros.getvalue()
assert "textual" not in sys.modules
p = m.Predio()
assert p.total_andares == 11 and p.elevador.andar_atual == 0
assert p.elevador.consultar_fila() == []
print("importação independente e silenciosa")
'''
        # O processo só recebe uma cópia do arquivo de produção, sem arquivos de apoio.
        with tempfile.TemporaryDirectory(prefix='aula15_import_') as pasta:
            copia = Path(pasta) / PROGRAMA.name
            copia.write_bytes(PROGRAMA.read_bytes())
            r = subprocess.run([sys.executable, '-B', '-I', '-S', '-c', codigo, str(copia)],
                               cwd=pasta, capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), 'importação independente e silenciosa')

    def test_sintaxe_compila_e_aceita_gramatica_python_310(self):
        fonte = PROGRAMA.read_text()
        compile(fonte, str(PROGRAMA), 'exec')
        ast.parse(fonte, feature_version=(3, 10))
        # Esta análise não equivale a executar o programa em Python 3.10.

    def test_ajuda_apresenta_argumentos_reais(self):
        r = self.executar('--help')
        self.assertIn('--texto', r.stdout)
        self.assertIn('--tempo-portas', r.stdout)

    def test_visual_sem_textual_informa_dependencia_e_alternativa(self):
        r = self.executar(esperado=1)
        self.assertIn('textual==8.2.8', r.stderr)
        self.assertIn('python elevador_completo.py --texto', r.stderr)

    def test_cli_rejeita_tempos_invalidos(self):
        for valor in ('-1', 'nan', 'inf', 'abc'):
            with self.subTest(valor=valor):
                self.executar('--texto', '--tempo-portas', valor, esperado=2)

    def test_texto_sem_pacotes_processa_varias_linhas_e_eof(self):
        r = self.executar('--texto', entrada='externa 5 descer 2\niniciar\nstatus')
        self.assertIn('registrada', r.stdout)
        self.assertIn('Pessoa 2: origem 5', r.stdout)
        self.assertIn('RELATÓRIO DA SESSÃO', r.stdout)
        self.assertIn('Simulação encerrada', r.stdout)

    def test_texto_rejeita_entradas_e_continua_ate_sair(self):
        r = self.executar('--texto', entrada='externa -1 subir\ninterna 2\npessoa 99\n'
                          'comando_inexistente\nstatus\nsair\n')
        self.assertEqual(r.stdout.count('Entrada rejeitada:'), 4)
        self.assertIn('Fila restante: []', r.stdout)

    @unittest.skipUnless(os.name == 'posix', 'Entrada não bloqueante exige POSIX.')
    def test_viagem_textual_real_com_embarque_e_desembarque(self):
        cmd = [sys.executable, '-B', '-I', '-S', '-u', str(PROGRAMA),
               '--texto', '--tempo-portas', '0']
        p = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
        recebido = bytearray()

        def enviar(linha):
            p.stdin.write((linha + '\n').encode())
            p.stdin.flush()

        def aguardar(trecho):
            prazo = time.monotonic() + 15
            while trecho.encode() not in recebido:
                if time.monotonic() >= prazo:
                    self.fail('Prazo aguardando ' + trecho + '\n' + recebido.decode(errors='replace'))
                prontos, _, _ = select.select([p.stdout], [], [], .1)
                if prontos:
                    dados = os.read(p.stdout.fileno(), 65536)
                    if not dados:
                        self.fail('Processo encerrou antes de ' + trecho + '\n' + recebido.decode(errors='replace'))
                    recebido.extend(dados)

        try:
            aguardar('PAINEL EXTERNO')
            enviar('externa 0 subir')
            enviar('iniciar')
            aguardar('Pessoa 1 embarcou; painel interno disponível.')
            enviar('interna 2')
            enviar('fechar')
            aguardar('Pessoa 1 desembarcou no andar 2; viagem concluída.')
            aguardar('solicitação #2 concluída.')
            enviar('sair')
            p.stdin.close()
            p.stdin = None
            resto, _ = p.communicate(timeout=5)
            recebido.extend(resto)
            saida = recebido.decode()
            self.assertEqual(p.returncode, 0, saida)
            self.assertNotIn('Traceback', saida)
            self.assertIn('Fila restante: []', saida)
            self.assertIn('fora no andar 2', saida)
        finally:
            if p.poll() is None:
                p.kill()
                p.wait()
            if p.stdin is not None:
                p.stdin.close()
            p.stdout.close()


if __name__ == '__main__':
    unittest.main()
