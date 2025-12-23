import unittest
import importlib.util
import sys

class TestUIMain(unittest.TestCase):
    def test_menu_options_present(self):
        """Testa se as opções 'Lista de Moedas' e 'Cotações' estão presentes no submenu 'Consultar Base de Dados'."""
        import importlib.util
        spec = importlib.util.find_spec("src.ui_main")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        from PyQt6.QtWidgets import QApplication, QTreeWidget
        app = QApplication.instance() or QApplication(sys.argv)
        window = module.MainWindow()
        sidebar = window.findChild(QTreeWidget)
        self.assertIsNotNone(sidebar)
        found_lista = found_cotacoes = False
        for i in range(sidebar.topLevelItemCount()):
            item = sidebar.topLevelItem(i)
            if item.text(0) == "Consultar Base de Dados":
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.text(0) == "Lista de Moedas":
                        found_lista = True
                    if child.text(0) == "Cotações":
                        found_cotacoes = True
        window.close()
        self.assertTrue(found_lista, "Opção 'Lista de Moedas' não encontrada no menu.")
        self.assertTrue(found_cotacoes, "Opção 'Cotações' não encontrada no menu.")

    def test_window_title_version(self):
        """Testa se o título da janela inclui o número da versão."""
        import importlib.util
        spec = importlib.util.find_spec("src.ui_main")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        from PyQt6.QtWidgets import QApplication
        from src import __version__
        app = QApplication.instance() or QApplication(sys.argv)
        window = module.MainWindow()
        self.assertIn(__version__, window.windowTitle())
        window.close()
    def test_ui_main_import(self):
        """Testa se o módulo src.ui_main pode ser importado sem erros."""
        spec = importlib.util.find_spec("src.ui_main")
        self.assertIsNotNone(spec, "src.ui_main não encontrado")
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            self.fail(f"Erro ao importar src.ui_main: {e}")

    def test_mainwindow_init(self):
        """Testa se a MainWindow pode ser instanciada sem erros."""
        spec = importlib.util.find_spec("src.ui_main")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # QApplication só pode ser criada uma vez por processo
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        window = module.MainWindow()
        self.assertIsNotNone(window)
        self.assertTrue(window.isVisible() or not window.isVisible())  # Só para garantir que instancia
        window.close()

    def test_menu_navigation(self):
        """Testa navegação básica do menu lateral."""
        spec = importlib.util.find_spec("src.ui_main")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        from PyQt6.QtWidgets import QApplication, QTreeWidget
        app = QApplication.instance() or QApplication(sys.argv)
        window = module.MainWindow()
        sidebar = window.findChild(QTreeWidget)
        self.assertIsNotNone(sidebar)
        # Seleciona cada item do menu e verifica se não lança erro
        for i in range(sidebar.topLevelItemCount()):
            item = sidebar.topLevelItem(i)
            sidebar.setCurrentItem(item)
            # Se tiver filhos, testa seleção dos filhos também
            for j in range(item.childCount()):
                child = item.child(j)
                sidebar.setCurrentItem(child)
        window.close()

if __name__ == "__main__":
    unittest.main()
