
import os
import sys
# Force offscreen Qt platform during CI, explicit request, or unit test runs
# This avoids warnings like: QApplication::regClass: Registering window class
# 'Qt6101ThemeChangeObserverWindow' failed. (Class already exists.)
if (
    "QT_QPA_PLATFORM" not in os.environ
    and (
        os.environ.get("CI") == "true"
        or os.environ.get("FORCE_QT_OFFSCREEN") == "1"
        or "unittest" in sys.modules
        or os.environ.get("PYTEST_RUNNING") == "1"
    )
):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Prefer project-local fonts directory to avoid Qt warnings when PyQt cannot find system fonts
if "QT_QPA_FONTDIR" not in os.environ:
    proj_fonts = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts"))
    if os.path.isdir(proj_fonts):
        os.environ["QT_QPA_FONTDIR"] = proj_fonts


from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

 # Permite importar __version__ mesmo com execução direta
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src import __version__

# v4.3.0: Menu lateral agora inclui as opções 'Lista de Moedas' e 'Cotações' no submenu 'Consultar Base de Dados'.
# O título da janela principal exibe o número da versão automaticamente lido de src.__init__.__version__.

# v4.3.2: A indentação dos submenus foi reduzida para metade do valor padrão usando setIndentation no QTreeWidget.



class MainWindow(QMainWindow):
    def closeEvent(self, event):
        # Garante que qualquer QThread criado é terminado corretamente
        if hasattr(self, 'thread') and self.thread is not None:
            try:
                if self.thread.isRunning():
                    self.thread.quit()
                    self.thread.wait()
            except Exception:
                pass
        super().closeEvent(event)

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
        groups = [
            ("Início", "inicio.png"),
            ("Atualizar Dados", "atualizar.png"),
            ("Consultar Base de Dados", "database.png"),
            ("Gráficos", "graficos.png"),
            ("Relatórios", "relatorio.png"),
            ("Ferramentas", "tools.png"),
            ("Outras funcionalidades", "others.png")
        ]
        self.group_items = []
        for group_name, icon_file in groups:
            group_item = QTreeWidgetItem([group_name])
            # Submenus específicos para Relatórios, Consultar Base de Dados, Gráficos, Atualizar Dados e Ferramentas
            if group_name == "Relatórios":
                atualizar_item = QTreeWidgetItem(["Atualizar relatório"])
                abrir_item = QTreeWidgetItem(["Abrir relatório"])
                group_item.addChild(atualizar_item)
                group_item.addChild(abrir_item)
            elif group_name == "Atualizar Dados":
                diaria_item = QTreeWidgetItem(["Atualização Diária"])
                reavaliar_item = QTreeWidgetItem(["Reavaliar Moedas"])
                forcar_item = QTreeWidgetItem(["Forçar Atualização"])
                group_item.addChild(diaria_item)
                group_item.addChild(reavaliar_item)
                group_item.addChild(forcar_item)
            elif group_name == "Consultar Base de Dados":
                lista_moedas = QTreeWidgetItem(["Lista de Moedas"])
                cotacoes = QTreeWidgetItem(["Cotações"])
                group_item.addChild(lista_moedas)
                group_item.addChild(cotacoes)
            elif group_name == "Gráficos":
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
            elif group_name == "Ferramentas":
                configuracoes_item = QTreeWidgetItem(["Configurações"])
                ajuda_item = QTreeWidgetItem(["Ajuda"])
                group_item.addChild(configuracoes_item)
                group_item.addChild(ajuda_item)
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
        # Expand top-level group when clicked
        self.sidebar.itemClicked.connect(self.on_item_clicked)

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
                "Ferramentas": "tools.png",
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
            elif parent_name == "Ferramentas" and sub_name == "Ajuda":
                # Mostra a documentação do projeto (README.md)
                readme_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "README.md"))
                if os.path.exists(readme_path):
                    with open(readme_path, "r", encoding="utf-8") as f:
                        doc_text = f.read()
                    from PyQt6.QtWidgets import QTextEdit
                    doc_widget = QTextEdit()
                    doc_widget.setReadOnly(True)
                    doc_widget.setPlainText(doc_text)
                    self.content_layout.addWidget(doc_widget)
                else:
                    label = QLabel("README.md não encontrado.")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.content_layout.addWidget(label)
            elif parent_name == "Atualizar Dados" and sub_name == "Atualização Diária":
                # Executa main.py diretamente e mostra o output na área de trabalho usando QThread
                from PyQt6.QtWidgets import QTextEdit
                from PyQt6.QtCore import QThread, pyqtSignal, QObject
                import subprocess
                output_widget = QTextEdit()
                output_widget.setReadOnly(True)
                output_widget.setPlainText("A atualizar cotações... Aguarde.\n")
                self.content_layout.addWidget(output_widget)

                class Worker(QObject):
                    output = pyqtSignal(str)
                    finished = pyqtSignal()

                    def run(self):
                        try:
                            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                            python_exe = sys.executable
                            process = subprocess.Popen(
                                [python_exe, script_path, "--all-from-db", "--auto-range"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
                                text=True,
                                encoding="utf-8",
                                errors="replace"
                            )
                            for line in process.stdout:
                                self.output.emit(line.rstrip())
                            process.wait()
                            self.output.emit("\nAtualização concluída.")
                        except Exception as e:
                            self.output.emit(f"Erro ao executar main.py: {e}")
                        self.finished.emit()

                self.thread = QThread()
                self.worker = Worker()
                self.worker.moveToThread(self.thread)
                self.thread.started.connect(self.worker.run)
                self.worker.output.connect(output_widget.append)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                self.thread.start()
            elif parent_name == "Ferramentas" and sub_name == "Configurações":
                label = QLabel("Configurações do projeto (em breve)")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(label)
            elif parent_name == "Consultar Base de Dados" and sub_name == "Lista de Moedas":
                # Exibe a tabela crypto_info
                from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
                import traceback
                try:
                    from src.database import CryptoDatabase
                    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "crypto_prices.db"))
                    db = CryptoDatabase(db_path)
                    rows = db.get_all_crypto_info()
                    if not rows:
                        label = QLabel("Nenhuma moeda encontrada na base de dados.")
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.content_layout.addWidget(label)
                        return
                    headers = list(rows[0].keys())
                    table = QTableWidget(len(rows), len(headers))
                    table.setHorizontalHeaderLabels(headers)
                    for i, row in enumerate(rows):
                        for j, key in enumerate(headers):
                            value = row[key]
                            table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
                    table.resizeColumnsToContents()
                    self.content_layout.addWidget(table)
                except Exception as e:
                    label = QLabel("Erro ao carregar moedas:\n" + str(e) + "\n" + traceback.format_exc())
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.content_layout.addWidget(label)
            elif parent_name == "Consultar Base de Dados" and sub_name == "Cotações":
                # Exibe a tabela price_quotes (todas as cotações)
                from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
                import traceback
                try:
                    from src.database import CryptoDatabase
                    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "crypto_prices.db"))
                    db = CryptoDatabase(db_path)
                    # Buscar todas as cotações de todas as moedas
                    # Obter todos os símbolos
                    symbols = db.get_all_symbols()
                    all_quotes = []
                    for symbol in symbols:
                        quotes = db.get_quotes(symbol)
                        all_quotes.extend(quotes)
                    if not all_quotes:
                        label = QLabel("Nenhuma cotação encontrada na base de dados.")
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.content_layout.addWidget(label)
                        return
                    headers = list(all_quotes[0].keys())
                    table = QTableWidget(len(all_quotes), len(headers))
                    table.setHorizontalHeaderLabels(headers)
                    for i, row in enumerate(all_quotes):
                        for j, key in enumerate(headers):
                            value = row[key]
                            table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
                    table.resizeColumnsToContents()
                    self.content_layout.addWidget(table)
                except Exception as e:
                    label = QLabel("Erro ao carregar cotações:\n" + str(e) + "\n" + traceback.format_exc())
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.content_layout.addWidget(label)
            else:
                label = QLabel(f"Sub-opção '{sub_name}' em '{parent_name}' (dummy)")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(label)
    def on_item_clicked(self, item, column):
        # When a top-level (main) option is clicked, expand its subtree
        try:
            if item is not None and item.parent() is None:
                item.setExpanded(True)
        except Exception:
            pass

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
