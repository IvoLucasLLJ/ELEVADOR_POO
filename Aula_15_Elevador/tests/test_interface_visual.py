"""Verificações opcionais headless; não são inspeção de tela física ou toque."""
import importlib.util
import unittest

from elevador_completo import InterfaceElevador, Painel, Predio

TEXTUAL_INSTALADO = importlib.util.find_spec('textual') is not None


@unittest.skipUnless(TEXTUAL_INSTALADO, 'Textual indisponível neste processo (ausente ou site-packages desabilitado).')
class TestInterfaceVisual(unittest.IsolatedAsyncioTestCase):
    async def test_montagem_controles_e_atalhos_em_duas_dimensoes(self):
        from textual.widgets import Button, Select

        for tamanho in ((120, 35), (44, 32)):
            with self.subTest(tamanho=tamanho):
                painel = Painel(Predio())
                app = InterfaceElevador(painel, intervalo=60)
                async with app.run_test(size=tamanho) as pilot:
                    await pilot.pause()
                    self.assertTrue(app.query_one('#pessoa', Select).disabled)
                    self.assertTrue(app.query_one('#int-2', Button).disabled)
                    self.assertTrue(app.query_one('#descer', Button).disabled)
                    externo = app.query_one('#externo').region
                    interno = app.query_one('#interno').region
                    if tamanho[0] >= 85:
                        self.assertGreater(interno.x, externo.x)
                    else:
                        self.assertGreater(interno.y, externo.y)
                    await pilot.press('i')
                    self.assertTrue(painel.iniciado)
                    await pilot.press('space')
                    self.assertTrue(painel.pausado)
                    await pilot.press('space')
                    self.assertFalse(painel.pausado)
                    await pilot.press('q')
                self.assertFalse(app.is_running)


if __name__ == '__main__':
    unittest.main()
