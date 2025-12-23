import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtGui import QIcon, QPixmap
import os
from PyQt6.QtCore import Qt
import pyqtgraph as pg

 # Permite importar __version__ mesmo com execução direta
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src import __version__

# v4.3.0: Menu lateral agora inclui as opções 'Lista de Moedas' e 'Cotações' no submenu 'Consultar Base de Dados'.
# O título da janela principal exibe o número da versão automaticamente lido de src.__init__.__version__.

# v4.3.2: A indentação dos submenus foi reduzida para metade do valor padrão usando setIndentation no QTreeWidget.


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # O título da janela inclui o número da versão do projeto
        self.setWindowTitle(f"CryptoPlay Dashboard v{__version__}")
        self.resize(900, 600)
        self.init_ui()

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Sidebar (menu tree)
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setMaximumWidth(220)
        # Reduz a indentação dos submenus para metade do padrão
        default_indent = self.sidebar.indentation()
        self.sidebar.setIndentation(max(10, default_indent // 2))

        # Top-level menu groups
        icon_dir = os.path.join(os.path.dirname(__file__), "icons")
        groups = [
            ("Início", "inicio.png"),
            ("Atualizar Dados", "atualizar.png"),
            ("Consultar Base de Dados", "database.png"),
            ("Relatórios", "relatorio.png"),
            ("Gráficos", "graficos.png"),
            ("Outras funcionalidades", "others.png")
        ]
        self.group_items = []
        for group_name, icon_file in groups:
            group_item = QTreeWidgetItem([group_name])
            # Submenus específicos para Relatórios, Consultar Base de Dados, Gráficos e Atualizar Dados
            if group_name == "Relatórios":
                atualizar_item = QTreeWidgetItem(["Atualizar relatório"])
                abrir_item = QTreeWidgetItem(["Abrir relatório"])
                group_item.addChild(atualizar_item)
                group_item.addChild(abrir_item)
            elif group_name == "Atualizar Dados":
                # Novas opções para Atualizar Dados v4.3.3
                diaria_item = QTreeWidgetItem(["Atualização Diária"])
                reavaliar_item = QTreeWidgetItem(["Reavaliar Moedas"])
                forcar_item = QTreeWidgetItem(["Forçar Atualização"])
                group_item.addChild(diaria_item)
                group_item.addChild(reavaliar_item)
                group_item.addChild(forcar_item)
            elif group_name == "Consultar Base de Dados":
                # Novas opções adicionadas na v4.3.0
                lista_moedas = QTreeWidgetItem(["Lista de Moedas"])
                cotacoes = QTreeWidgetItem(["Cotações"])
                group_item.addChild(lista_moedas)
                group_item.addChild(cotacoes)
            elif group_name == "Gráficos":
                # Novas opções de gráficos adicionadas na v4.3.1
                graficos_opcoes = [
                    "Candlestick",
                    "Linha",
                    "OHLC (Open-High-Low-Close)",
                    "Volume",
                    "Volatilidade (%)",
                    "Média móvel (SMA/EMA)",
                    "RSI (Relative Strength Index)",
                    "MACD (Moving Average Convergence Divergence)",
                    "Bollinger Bands",
                    "Comparativo entre ativos"
                ]
                for opcao in graficos_opcoes:
                    group_item.addChild(QTreeWidgetItem([opcao]))
            elif group_name != "Início":
                dummy = QTreeWidgetItem(["(exemplo)"])
                group_item.addChild(dummy)
            self.sidebar.addTopLevelItem(group_item)
            self.group_items.append(group_item)

        main_layout.addWidget(self.sidebar)

        # Content area (right)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
        main_layout.addWidget(self.content_area)

        # Placeholder for initial content removido (será controlado pelo menu)

        # Connect sidebar selection
        self.sidebar.currentItemChanged.connect(self.display_content)

        # Selecionar "Início" por defeito
        self.sidebar.setCurrentItem(self.group_items[0])

    def display_content(self, current, previous):
        # Clear current content
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if current is None:
            label = QLabel("Selecione uma opção no menu à esquerda.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
            return

        # Se for grupo (top-level)
        if current.parent() is None:
            group_name = current.text(0)
            # Imagem sugestiva (se existir)
            icon_map = {
                "Início": "inicio.png",
                "Atualizar Dados": "atualizar.png",
                "Relatórios": "relatorio.png",
                "Consultar Base de Dados": "database.png",
                "Gráficos": "graficos.png",
                "Outras funcionalidades": "others.png"
            }
            icon_dir = os.path.join(os.path.dirname(__file__), "icons")
            icon_file = icon_map.get(group_name, None)
            img_path = os.path.join(icon_dir, icon_file) if icon_file else None
            if img_path and os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                from PyQt6.QtWidgets import QSizePolicy
                img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.content_layout.addWidget(img_label)

                # Função para redimensionar a imagem ao espaço disponível
                def resize_pixmap():
                    area_size = self.content_area.size()
                    w = max(100, area_size.width() - 40)
                    h = max(100, area_size.height() - 40)
                    img_label.setPixmap(pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

                # Redimensiona ao abrir
                resize_pixmap()

                # Redimensiona sempre que a área de conteúdo for redimensionada
                old_resize_event = self.content_area.resizeEvent
                def new_resize_event(event):
                    resize_pixmap()
                    if old_resize_event:
                        old_resize_event(event)
                self.content_area.resizeEvent = new_resize_event
            else:
                label = QLabel(f"Imagem sugestiva para: {group_name}")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(label)
        else:
            # Sub-item selecionado
            parent_name = current.parent().text(0)
            sub_name = current.text(0)
            if parent_name == "Relatórios" and sub_name == "Atualizar relatório":
                # Mostra data de atualização do relatório Excel
                # Caminho absoluto a partir do diretório do projeto
                project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                excel_path = os.path.join(project_dir, "reports", "AnaliseCrypto.xlsx")
                import datetime
                if os.path.exists(excel_path):
                    mtime = os.path.getmtime(excel_path)
                    dt = datetime.datetime.fromtimestamp(mtime)
                    label = QLabel(f"Última atualização do relatório: {dt.strftime('%d/%m/%Y %H:%M:%S')}")
                else:
                    label = QLabel("Relatório Excel não encontrado.")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(label)
            elif parent_name == "Relatórios" and sub_name == "Abrir relatório":
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                excel_path = os.path.join(base_dir, "reports", "AnaliseCrypto.xlsx")
                if os.path.exists(excel_path):
                    label = QLabel("Abrindo relatório no Excel...")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.content_layout.addWidget(label)
                    # Não abrir o Excel se estiver em ambiente de teste
                    if not (os.environ.get("PYTEST_RUNNING") or os.environ.get("TESTING")):
                        try:
                            if sys.platform.startswith("win"):
                                os.startfile(excel_path)
                            else:
                                import subprocess
                                subprocess.Popen(["xdg-open", excel_path])
                        except Exception:
                            label.setText("Erro ao abrir o relatório.")
                else:
                    label = QLabel("Relatório Excel não encontrado.")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.content_layout.addWidget(label)
            else:
                label = QLabel(f"Sub-opção '{sub_name}' em '{parent_name}' (dummy)")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(label)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
