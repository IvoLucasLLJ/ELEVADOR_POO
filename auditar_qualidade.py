"""Auditoria local reproduzível, sem pacotes além dos usados pelo aplicativo.

Executa a suíte completa sem instrumentação e mede os testes do domínio com
o trace da biblioteca padrão. Testes de GUI com tempo real ficam fora do trace
para preservar seus tempos; subprocessos e ramos não são contabilizados.
"""
import ast
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import platform
import re
import sys
import sysconfig
import time
import trace
import unittest

ROOT = Path(__file__).resolve().parent
EVIDENCIAS = ROOT / 'evidencias'


def executar_testes(somente_dominio=False):
    if somente_dominio:
        suite = unittest.TestSuite(
            unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=padrao)
            for padrao in ('test_elevador.py', 'test_aula13.py', 'test_qualidade.py'))
    else:
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def main():
    EVIDENCIAS.mkdir(exist_ok=True)
    fontes = sorted((ROOT / 'Aula_13_Predio').glob('*.py')) + [
        ROOT / 'elevador.py', ROOT / 'simulador.py']
    sintaxe = []
    for fonte in fontes + sorted((ROOT / 'tests').glob('*.py')) + [Path(__file__)]:
        codigo = fonte.read_text()
        ast.parse(codigo, filename=str(fonte))
        compile(codigo, str(fonte), 'exec')
        sintaxe.append(str(fonte.relative_to(ROOT)))
    tracer = trace.Trace(count=True, trace=False, ignoredirs=[
        sysconfig.get_path('stdlib'), sysconfig.get_path('purelib')])
    inicio = time.monotonic()
    # Medir antes da descoberta completa inclui as definições/imports reais
    # do domínio, sem colocar os testes com relógio real sob instrumentação.
    from contextlib import redirect_stderr
    with (EVIDENCIAS / 'suite_cobertura_dominio.log').open('w') as log:
        with redirect_stderr(log):
            resultado_cobertura = tracer.runfunc(executar_testes, somente_dominio=True)
    with (EVIDENCIAS / 'suite_completa.log').open('w') as log:
        with redirect_stderr(log):
            resultado = executar_testes()
    cobertura = tracer.results()
    arquivos = {str(p.resolve()) for p in fontes}
    cobertura.counts = {chave: valor for chave, valor in cobertura.counts.items()
                       if str(Path(chave[0]).resolve()) in arquivos}
    resumo = io.StringIO()
    with redirect_stdout(resumo):
        cobertura.write_results(show_missing=True, summary=True,
                                coverdir=str(EVIDENCIAS / 'cobertura'))
    (EVIDENCIAS / 'cobertura_resumo.txt').write_text(resumo.getvalue())
    metricas = {}
    for arquivo in sorted((EVIDENCIAS / 'cobertura').glob('*.cover')):
        executadas = 0
        faltantes = []
        for numero, linha in enumerate(arquivo.read_text().splitlines(), 1):
            if linha.startswith('>>>>>>'):
                faltantes.append(numero)
            elif re.match(r'\s*\d+: ', linha):
                executadas += 1
        total = executadas + len(faltantes)
        metricas[arquivo.stem] = {'linhas_executadas': executadas,
                                  'linhas_executaveis': total,
                                  'percentual': round(100 * executadas / total, 2) if total else None,
                                  'linhas_nao_exercitadas': faltantes}
    total = sum(m['linhas_executaveis'] for m in metricas.values())
    executadas = sum(m['linhas_executadas'] for m in metricas.values())
    dados = {'python': sys.version, 'plataforma': platform.platform(),
             'testes_executados': resultado.testsRun,
             'falhas': len(resultado.failures), 'erros': len(resultado.errors),
             'ignorados': len(resultado.skipped), 'aprovado': resultado.wasSuccessful(),
             'duracao_segundos': round(time.monotonic() - inicio, 3),
             'sintaxe_aprovada': sintaxe,
             'testes_sob_trace': resultado_cobertura.testsRun,
             'cobertura_testes_aprovados': resultado_cobertura.wasSuccessful(),
             'medicao': 'trace: somente suites de domínio; sem GUI, ramos ou subprocessos',
             'modulos_exercitados': metricas,
             'modulos_sem_medicao': [str(p.relative_to(ROOT)) for p in fontes
                                     if not any(str(Path(k[0]).resolve()) == str(p.resolve())
                                                for k in cobertura.counts)],
             'total_linhas': total, 'linhas_executadas': executadas,
             'cobertura_percentual': round(100 * executadas / total, 2) if total else None}
    (EVIDENCIAS / 'auditoria.json').write_text(json.dumps(dados, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in dados.items() if k not in (
        'sintaxe_aprovada', 'modulos_exercitados')}, ensure_ascii=False, indent=2))
    return 0 if resultado.wasSuccessful() and resultado_cobertura.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
