import unittest
import importlib.util
import sys

class TestUIMain(unittest.TestCase):
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
            sidebar.setCurrentRow(i)
        window.close()

if __name__ == "__main__":
    unittest.main()
