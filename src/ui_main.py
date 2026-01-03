
"""Main UI window and sidebar for CryptoPlay application.

Configures offscreen Qt for CI/tests and provides the main application
window class `MainWindow` used by the UI tests and the desktop app.
"""

import os
import sys

# UI constants — centralised to avoid repeated string literals
INICIO = "Início"
ATUALIZAR_DADOS = "Atualizar Dados"
CONSULTAR_DB = "Consultar Base de Dados"
GRAFICOS = "Gráficos"
RELATORIOS = "Relatórios"
FERRAMENTAS = "Ferramentas"
BINANCE = "Binance"
OUTRAS = "Outras funcionalidades"

# Relatórios submenu
ATUALIZAR_REL = "Atualizar relatório"
ABRIR_REL = "Abrir relatório"

# Consultar DB submenu
LISTA_MOEDAS = "Lista de Moedas"
COTACOES = "Cotações"

# Binance submenu
CONSULTAR_TRANSACOES = "Consultar Transações"
IMPORTAR_TRANSACOES = "Importar Transações"

REPORT_FILENAME = "AnaliseCrypto.xlsx"

ICON_MAP = {
    INICIO: "inicio.png",
    ATUALIZAR_DADOS: "atualizar.png",
    CONSULTAR_DB: "database.png",
    GRAFICOS: "graficos.png",
    RELATORIOS: "relatorio.png",
    FERRAMENTAS: "tools.png",
    BINANCE: "binance.png",
    OUTRAS: "others.png",
}

# Additional submenu labels
ATUALIZACAO_DIARIA = "Atualização Diária"
REAVALIAR_MOEDAS = "Reavaliar Moedas"
FORCAR_ATUALIZACAO = "Forçar Atualização"
CONFIGURACOES = "Configurações"
AJUDA = "Ajuda"
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


 # Permite importar __version__ mesmo com execução direta
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Import project version after third-party imports to satisfy import-order checks
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
            (INICIO, ICON_MAP[INICIO]),
            (ATUALIZAR_DADOS, ICON_MAP[ATUALIZAR_DADOS]),
            (CONSULTAR_DB, ICON_MAP[CONSULTAR_DB]),
            (GRAFICOS, ICON_MAP[GRAFICOS]),
            (RELATORIOS, ICON_MAP[RELATORIOS]),
            (BINANCE, ICON_MAP[BINANCE]),
            (FERRAMENTAS, ICON_MAP[FERRAMENTAS]),
            (OUTRAS, ICON_MAP[OUTRAS]),
        ]
        self.group_items = []
        for group_name, _icon_file in groups:
            group_item = QTreeWidgetItem([group_name])
            # Submenus específicos para Relatórios, Consultar Base de Dados, Gráficos, Atualizar Dados e Ferramentas
            if group_name == RELATORIOS:
                atualizar_item = QTreeWidgetItem([ATUALIZAR_REL])
                abrir_item = QTreeWidgetItem([ABRIR_REL])
                group_item.addChild(atualizar_item)
                group_item.addChild(abrir_item)
            elif group_name == ATUALIZAR_DADOS:
                diaria_item = QTreeWidgetItem([ATUALIZACAO_DIARIA])
                reavaliar_item = QTreeWidgetItem([REAVALIAR_MOEDAS])
                forcar_item = QTreeWidgetItem([FORCAR_ATUALIZACAO])
                group_item.addChild(diaria_item)
                group_item.addChild(reavaliar_item)
                group_item.addChild(forcar_item)
            elif group_name == CONSULTAR_DB:
                lista_moedas = QTreeWidgetItem([LISTA_MOEDAS])
                cotacoes = QTreeWidgetItem([COTACOES])
                group_item.addChild(lista_moedas)
                group_item.addChild(cotacoes)
            elif group_name == BINANCE:
                consultar_item = QTreeWidgetItem([CONSULTAR_TRANSACOES])
                importar_item = QTreeWidgetItem([IMPORTAR_TRANSACOES])
                group_item.addChild(consultar_item)
                group_item.addChild(importar_item)
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
            elif group_name == FERRAMENTAS:
                configuracoes_item = QTreeWidgetItem(["Configurações"])
                ajuda_item = QTreeWidgetItem(["Ajuda"])
                group_item.addChild(configuracoes_item)
                group_item.addChild(ajuda_item)
            elif group_name != INICIO:
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

    def _clear_content(self):
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def _show_group_image(self, group_name: str):
        icon_dir = os.path.join(os.path.dirname(__file__), "icons")
        icon_file = ICON_MAP.get(group_name)
        img_path = os.path.join(icon_dir, icon_file) if icon_file else None
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            from PyQt6.QtWidgets import QSizePolicy
            img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.content_layout.addWidget(img_label)

            def resize_pixmap():
                area_size = self.content_area.size()
                w = max(100, area_size.width() - 40)
                h = max(100, area_size.height() - 40)
                img_label.setPixmap(
                    pixmap.scaled(
                        w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                    )
                )

            resize_pixmap()

            old_resize_event = getattr(self.content_area, "resizeEvent", None)

            def new_resize_event(event):
                resize_pixmap()
                if old_resize_event:
                    old_resize_event(event)

            self.content_area.resizeEvent = new_resize_event
        else:
            label = QLabel(f"Imagem sugestiva para: {group_name}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)

    def _show_report_update(self):
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        excel_path = os.path.join(project_dir, "reports", REPORT_FILENAME)
        import datetime

        if os.path.exists(excel_path):
            mtime = os.path.getmtime(excel_path)
            dt = datetime.datetime.fromtimestamp(mtime)
            label = QLabel(f"Última atualização do relatório: {dt.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            label = QLabel("Relatório Excel não encontrado.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(label)

    def _open_report(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        excel_path = os.path.join(base_dir, "reports", REPORT_FILENAME)
        if os.path.exists(excel_path):
            # In test or CI environments do not actually open external programs
            is_test_env = (
                os.environ.get("PYTEST_RUNNING")
                or os.environ.get("TESTING")
                or os.environ.get("CI") == "true"
                or "unittest" in sys.modules
            )
            if is_test_env:
                label = QLabel("(Simulação) Abrindo relatório no Excel (testes) ...")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(label)
                return

            label = QLabel("Abrindo relatório no Excel...")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
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

    def _show_readme(self):
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

    def _show_binance_transactions(self):
        """Exibe as transações Binance da base de dados."""
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
        import traceback
        try:
            from src.database import CryptoDatabase

            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "crypto_prices.db"))
            db = CryptoDatabase(db_path)
            
            # Buscar todas as transações da tabela binance_transactions
            cursor = db.conn.cursor()
            cursor.execute("SELECT * FROM binance_transactions ORDER BY binance_timestamp DESC")
            transactions = cursor.fetchall()
            
            if not transactions:
                label = QLabel("Nenhuma transação Binance encontrada na base de dados.")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(label)
                return
            
            # Obter nomes das colunas
            column_names = [desc[0] for desc in cursor.description]
            
            # Criar tabela
            table = QTableWidget(len(transactions), len(column_names))
            table.setHorizontalHeaderLabels(column_names)
            
            for i, transaction in enumerate(transactions):
                for j, value in enumerate(transaction):
                    table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
            
            table.resizeColumnsToContents()
            self.content_layout.addWidget(table)
            
            db.close()
        except Exception as e:
            label = QLabel("Erro ao carregar transações Binance:\n" + str(e) + "\n" + traceback.format_exc())
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)

    def _import_binance_transactions(self):
        """Interface para importar transações Binance."""
        from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QComboBox, QHBoxLayout
        from datetime import datetime, timezone
        
        layout = QVBoxLayout()
        
        info_label = QLabel("Importe transações Binance de um ficheiro CSV")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Opção para duplicados
        dup_layout = QHBoxLayout()
        dup_label = QLabel("Se encontrar duplicados:")
        dup_combo = QComboBox()
        dup_combo.addItem("Ignorar", "skip")
        dup_combo.addItem("Substituir", "replace")
        dup_layout.addWidget(dup_label)
        dup_layout.addWidget(dup_combo)
        dup_layout.addStretch()
        layout.addLayout(dup_layout)
        
        # Botão para selecionar ficheiro
        def select_file():
            # Pasta por defeito é external\in
            default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "external", "in"))
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Selecione ficheiro CSV de transações Binance",
                default_dir,
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                on_duplicate = dup_combo.currentData()
                output_widget.setPlainText(f"Ficheiro selecionado: {file_path}\n")
                output_widget.setPlainText(output_widget.toPlainText() + f"Modo: {'substituir duplicados' if on_duplicate == 'replace' else 'ignorar duplicados'}\n")
                output_widget.setPlainText(output_widget.toPlainText() + "Processando ficheiro...\n")
                
                try:
                    from src.database import CryptoDatabase
                    from src.api_binance import get_price_at_second
                    
                    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "crypto_prices.db"))
                    db = CryptoDatabase(db_path)
                    
                    # Importar transações
                    with open(file_path, 'r', encoding='utf-8') as f:
                        import csv

                        def pick(row_dict, *names):
                            for name in names:
                                if name in row_dict and row_dict[name] != "":
                                    return row_dict.get(name, "")
                            return ""

                        def parse_float_scientific(value_str):
                            """Parse float from string, handling scientific notation (e.g., '2E-8', '1.5E-7')."""
                            if not value_str or not value_str.strip():
                                return 0.0
                            try:
                                return float(value_str.strip())
                            except ValueError:
                                return 0.0

                        def format_decimal(value):
                            """Format float as decimal string without scientific notation (e.g., 2e-08 → '0.00000002')."""
                            if value == 0:
                                return "0"
                            # Use format with enough precision and no exponent
                            formatted = f"{value:.20f}".rstrip("0").rstrip(".")
                            return formatted

                        reader = csv.DictReader(f)
                        count = 0
                        skipped = 0
                        price_cache = {}

                        def fetch_price_eur(coin_symbol, dt_utc):
                            key = (coin_symbol, dt_utc.replace(microsecond=0))
                            if key in price_cache:
                                return price_cache[key]

                            if coin_symbol == 'EUR':
                                result = (1.0, int(dt_utc.timestamp() * 1000))
                                price_cache[key] = result
                                return result

                            # Try direct EUR pair first
                            symbol_pair = f"{coin_symbol}EUR"
                            try:
                                price_eur, ts_open = get_price_at_second(symbol_pair, dt_utc)
                                if price_eur is not None:
                                    result = (price_eur, ts_open)
                                    price_cache[key] = result
                                    return result
                            except Exception as e:  # noqa: BLE001
                                output_widget.setPlainText(output_widget.toPlainText() + f"Erro API {symbol_pair}: {e}\n")

                            # Fallback 1: coin/USDT * USDT/EUR
                            try:
                                price_coin_usdt, ts_coin = get_price_at_second(f"{coin_symbol}USDT", dt_utc)
                                price_eur_usdt, ts_usdt = get_price_at_second("EURUSDT", dt_utc)
                                if (
                                    price_coin_usdt is not None
                                    and price_eur_usdt is not None
                                    and price_eur_usdt != 0
                                ):
                                    price_usdt_eur = 1 / price_eur_usdt
                                    ts = ts_coin if ts_coin is not None else ts_usdt
                                    result = (price_coin_usdt * price_usdt_eur, ts)
                                    price_cache[key] = result
                                    return result
                            except Exception as e:  # noqa: BLE001
                                output_widget.setPlainText(output_widget.toPlainText() + f"Erro API fallback1 {coin_symbol}: {e}\n")

                            # Fallback 2: coin/USDC * USDC/EUR
                            try:
                                price_coin_usdc, ts_coin = get_price_at_second(f"{coin_symbol}USDC", dt_utc)
                                price_eur_usdc, ts_usdc = get_price_at_second("EURUSDC", dt_utc)
                                if (
                                    price_coin_usdc is not None
                                    and price_eur_usdc is not None
                                    and price_eur_usdc != 0
                                ):
                                    price_usdc_eur = 1 / price_eur_usdc
                                    ts = ts_coin if ts_coin is not None else ts_usdc
                                    result = (price_coin_usdc * price_usdc_eur, ts)
                                    price_cache[key] = result
                                    return result
                            except Exception as e:  # noqa: BLE001
                                output_widget.setPlainText(output_widget.toPlainText() + f"Erro API fallback2 {coin_symbol}: {e}\n")

                            return None, None

                        for row in reader:
                            # Skip header row if present (shouldn't happen with DictReader, but be safe)
                            if row.get("User ID") == "User ID" or row.get("User_ID") == "User_ID":
                                continue

                            try:
                                user_id = pick(row, 'User ID', 'User_ID').strip()
                                utc_time_str = pick(row, 'UTC Time', 'UTC_Time').strip()
                                account = pick(row, 'Account').strip()
                                operation = pick(row, 'Operation').strip()
                                coin = pick(row, 'Coin').strip().upper()
                                remark = pick(row, 'Remark').strip()
                                change_val = parse_float_scientific(pick(row, 'Change'))

                                if not utc_time_str:
                                    output_widget.setPlainText(output_widget.toPlainText() + "UTC Time vazio – linha ignorada\n")
                                    skipped += 1
                                    continue
                                
                                # Parse UTC time
                                try:
                                    dt = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
                                    if dt.tzinfo is None:
                                        dt = dt.replace(tzinfo=timezone.utc)
                                    dt_utc = dt.astimezone(timezone.utc)
                                except Exception:
                                    output_widget.setPlainText(output_widget.toPlainText() + f"UTC Time inválido: {utc_time_str}\n")
                                    skipped += 1
                                    continue
                                
                                price_eur, ts_open = fetch_price_eur(coin, dt_utc)
                                binance_ts = ts_open if ts_open is not None else int(dt_utc.timestamp() * 1000)
                                value_eur = price_eur * change_val if price_eur is not None else None
                                change_str = format_decimal(change_val)  # Convert to decimal string without scientific notation

                                cursor = db.conn.cursor()
                                # Check duplicate: user_id+utc_time+account+operation+coin+change+remark
                                cursor.execute(
                                    """SELECT rowid FROM binance_transactions
                                           WHERE user_id = ? AND utc_time = ? AND account = ? AND operation = ?
                                                 AND coin = ? AND change = ? AND remark = ?""",
                                    (user_id, utc_time_str, account, operation, coin, change_str, remark)
                                )
                                dup_row = cursor.fetchone()
                                
                                if dup_row:
                                    if on_duplicate == 'replace':
                                        cursor.execute('DELETE FROM binance_transactions WHERE rowid = ?', (dup_row[0],))
                                        # Will be re-inserted below
                                    else:
                                        skipped += 1
                                        continue
                                
                                cursor.execute("""
                                    INSERT INTO binance_transactions 
                                    (user_id, utc_time, account, operation, coin, change, remark, 
                                     price_eur, value_eur, binance_timestamp, source)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    user_id,
                                    utc_time_str,
                                    account,
                                    operation,
                                    coin,
                                    change_str,
                                    remark,
                                    price_eur,
                                    value_eur,
                                    binance_ts,
                                    'BinanceCSV'
                                ))
                                count += 1
                            except Exception as e:
                                output_widget.setPlainText(output_widget.toPlainText() + f"Erro na linha: {e}\n")
                                skipped += 1
                        
                        db.conn.commit()
                        db.close()
                        
                        msg = f"\n✓ {count} transações importadas com sucesso!"
                        if skipped > 0:
                            msg += f" ({skipped} ignoradas)"
                        output_widget.setPlainText(output_widget.toPlainText() + msg)
                except Exception as e:
                    output_widget.setPlainText(output_widget.toPlainText() + f"Erro ao importar: {str(e)}")
        
        select_button = QPushButton("Selecionar Ficheiro CSV")
        select_button.clicked.connect(select_file)
        layout.addWidget(select_button)
        
        output_widget = QTextEdit()
        output_widget.setReadOnly(True)
        output_widget.setPlainText("Selecione um ficheiro CSV para importar transações Binance")
        layout.addWidget(output_widget)
        
        container = QWidget()
        container.setLayout(layout)
        self.content_layout.addWidget(container)

    def _run_daily_update(self):
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
                        errors="replace",
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

    def _show_db_list(self):
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
            headers = list(rows[0])
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

    def display_content(self, current, previous):
        self._clear_content()

        if current is None:
            label = QLabel("Selecione uma opção no menu à esquerda.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
            return

        # Top-level group
        if current.parent() is None:
            group_name = current.text(0)
            self._show_group_image(group_name)
            return

        parent_name = current.parent().text(0)
        sub_name = current.text(0)

        if parent_name == RELATORIOS and sub_name == ATUALIZAR_REL:
            self._show_report_update()
        elif parent_name == RELATORIOS and sub_name == ABRIR_REL:
            self._open_report()
        elif parent_name == FERRAMENTAS and sub_name == AJUDA:
            self._show_readme()
        elif parent_name == ATUALIZAR_DADOS and sub_name == ATUALIZACAO_DIARIA:
            self._run_daily_update()
        elif parent_name == FERRAMENTAS and sub_name == CONFIGURACOES:
            label = QLabel("Configurações do projeto (em breve)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
        elif parent_name == "Consultar Base de Dados" and sub_name == "Lista de Moedas":
            self._show_db_list()
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
                headers = list(all_quotes[0])
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
        elif parent_name == BINANCE and sub_name == CONSULTAR_TRANSACOES:
            self._show_binance_transactions()
        elif parent_name == BINANCE and sub_name == IMPORTAR_TRANSACOES:
            self._import_binance_transactions()
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
