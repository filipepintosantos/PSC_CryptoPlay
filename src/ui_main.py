
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
TRANSACOES_BINANCE = "Transações Binance"

# Binance submenu
IMPORTAR_TRANSACOES = "Importar Transações"
ANALISAR_TRANSACOES = "Analisar Transações"
FIFO_WALLET = "FIFO Wallet"
RESUMO_FISCAL = "Resumo Fiscal"

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
                transacoes_binance = QTreeWidgetItem([TRANSACOES_BINANCE])
                group_item.addChild(lista_moedas)
                group_item.addChild(cotacoes)
                group_item.addChild(transacoes_binance)
            elif group_name == BINANCE:
                importar_item = QTreeWidgetItem([IMPORTAR_TRANSACOES])
                analisar_item = QTreeWidgetItem([ANALISAR_TRANSACOES])
                fifo_wallet_item = QTreeWidgetItem([FIFO_WALLET])
                resumo_fiscal_item = QTreeWidgetItem([RESUMO_FISCAL])
                group_item.addChild(importar_item)
                group_item.addChild(analisar_item)
                group_item.addChild(fifo_wallet_item)
                group_item.addChild(resumo_fiscal_item)
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

                        def timestamp_ms_to_iso(ts_ms):
                            """Convert millisecond timestamp to ISO 8601 format string."""
                            if not ts_ms:
                                return ""
                            try:
                                dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
                                return dt.isoformat()
                            except (ValueError, OSError):
                                return ""

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

                                cursor = db.conn.cursor()
                                # Check duplicate: user_id+utc_time+account+operation+coin+change+remark
                                cursor.execute(
                                    """SELECT rowid FROM binance_transactions
                                           WHERE user_id = ? AND utc_time = ? AND account = ? AND operation = ?
                                                 AND coin = ? AND change = ? AND remark = ?""",
                                    (user_id, utc_time_str, account, operation, coin, change_val, remark)
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
                                    change_val,
                                    remark,
                                    price_eur,
                                    value_eur,
                                    timestamp_ms_to_iso(binance_ts),
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

    def _analyze_binance_transactions(self):
        """Analisa as transações Binance com filtros."""
        from PyQt6.QtWidgets import (QLabel, QTableWidget, QTableWidgetItem, QPushButton, 
                                      QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, 
                                      QDateEdit, QScrollArea, QWidget)
        from PyQt6.QtCore import QDate
        import traceback
        
        try:
            from src.database import CryptoDatabase

            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "crypto_prices.db"))
            db = CryptoDatabase(db_path)
            cursor = db.conn.cursor()
            
            # Buscar valores únicos para filtros
            cursor.execute("SELECT DISTINCT coin FROM binance_transactions WHERE coin IS NOT NULL ORDER BY coin")
            all_coins = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT operation FROM binance_transactions WHERE operation IS NOT NULL ORDER BY operation")
            all_operations = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT MIN(utc_time), MAX(utc_time) FROM binance_transactions")
            min_date, max_date = cursor.fetchone()
            
            # Container principal
            main_container = QWidget()
            main_layout = QVBoxLayout(main_container)
            
            # Título
            title = QLabel("Análise de Transações Binance com Filtros")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(title)
            
            # ScrollArea para filtros (máximo 40% da altura)
            filters_scroll = QScrollArea()
            filters_scroll.setWidgetResizable(True)
            filters_scroll.setMaximumHeight(300)  # Limita altura dos filtros
            filters_container = QWidget()
            filters_main_layout = QVBoxLayout(filters_container)
            
            # Painel de filtros horizontal
            filters_layout = QHBoxLayout()
            
            # Helper para criar grupo de filtros com botões
            def create_filter_group(title, items, max_height=200):
                group = QGroupBox(title)
                group_layout = QVBoxLayout()
                
                # Botões marcar/desmarcar todos
                btn_layout = QHBoxLayout()
                btn_all = QPushButton("Todos")
                btn_none = QPushButton("Nenhum")
                btn_all.setMaximumWidth(80)
                btn_none.setMaximumWidth(80)
                btn_layout.addWidget(btn_all)
                btn_layout.addWidget(btn_none)
                btn_layout.addStretch()
                group_layout.addLayout(btn_layout)
                
                # ScrollArea para checkboxes
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setMaximumHeight(max_height)
                scroll_widget = QWidget()
                scroll_layout = QVBoxLayout(scroll_widget)
                
                checks = {}
                for item in items:
                    cb = QCheckBox(item)
                    cb.setChecked(True)
                    checks[item] = cb
                    scroll_layout.addWidget(cb)
                
                scroll_layout.addStretch()
                scroll.setWidget(scroll_widget)
                group_layout.addWidget(scroll)
                
                # Conectar botões
                btn_all.clicked.connect(lambda: [cb.setChecked(True) for cb in checks.values()])
                btn_none.clicked.connect(lambda: [cb.setChecked(False) for cb in checks.values()])
                
                group.setLayout(group_layout)
                return group, checks
            
            # Criar grupos de filtros
            coin_group, coin_checks = create_filter_group("Moedas", all_coins)
            filters_layout.addWidget(coin_group)
            
            op_group, op_checks = create_filter_group("Operações", all_operations)
            # Adicionar checkbox "Agrupar sem Operação" ao grupo de operações
            hide_operation_cb = QCheckBox("Agrupar sem Operação")
            op_group.layout().addWidget(hide_operation_cb)
            filters_layout.addWidget(op_group)
            
            # Filtro Datas
            date_group = QGroupBox("Intervalo de Datas")
            date_layout = QVBoxLayout()
            date_from_label = QLabel("De:")
            date_from = QDateEdit()
            date_from.setCalendarPopup(True)
            if min_date:
                date_from.setDate(QDate.fromString(min_date[:10], "yyyy-MM-dd"))
            date_to_label = QLabel("Até:")
            date_to = QDateEdit()
            date_to.setCalendarPopup(True)
            if max_date:
                date_to.setDate(QDate.fromString(max_date[:10], "yyyy-MM-dd"))
            date_layout.addWidget(date_from_label)
            date_layout.addWidget(date_from)
            date_layout.addWidget(date_to_label)
            date_layout.addWidget(date_to)
            
            # Filtro Positivos/Negativos
            date_layout.addWidget(QLabel(""))  # Espaçador
            sign_label = QLabel("Valores Change:")
            date_layout.addWidget(sign_label)
            sign_all = QCheckBox("Todos")
            sign_all.setChecked(True)
            sign_positive = QCheckBox("Apenas Positivos")
            sign_negative = QCheckBox("Apenas Negativos")
            date_layout.addWidget(sign_all)
            date_layout.addWidget(sign_positive)
            date_layout.addWidget(sign_negative)
            
            # Conectar checkboxes de sinal
            def on_sign_all_changed(state):
                if state:
                    sign_positive.setChecked(False)
                    sign_negative.setChecked(False)
            
            def on_sign_specific_changed():
                if sign_positive.isChecked() or sign_negative.isChecked():
                    sign_all.setChecked(False)
            
            sign_all.stateChanged.connect(on_sign_all_changed)
            sign_positive.stateChanged.connect(on_sign_specific_changed)
            sign_negative.stateChanged.connect(on_sign_specific_changed)
            
            date_group.setLayout(date_layout)
            filters_layout.addWidget(date_group)
            
            filters_main_layout.addLayout(filters_layout)
            filters_scroll.setWidget(filters_container)
            main_layout.addWidget(filters_scroll)
            
            # Botão Aplicar Filtros
            apply_btn = QPushButton("Aplicar Filtros")
            main_layout.addWidget(apply_btn)
            
            # Label para resultados
            results_label = QLabel("")
            results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(results_label)
            
            # Tabela para resultados
            results_table = QTableWidget()
            main_layout.addWidget(results_table)
            
            def apply_filters():
                try:
                    # Construir query com filtros
                    selected_coins = [coin for coin, cb in coin_checks.items() if cb.isChecked()]
                    selected_ops = [op for op, cb in op_checks.items() if cb.isChecked()]
                    date_from_str = date_from.date().toString("yyyy-MM-dd")
                    date_to_str = date_to.date().toString("yyyy-MM-dd")
                    hide_operation = hide_operation_cb.isChecked()
                    
                    where_clauses = []
                    params = []
                    
                    if selected_coins:
                        placeholders = ','.join(['?' for _ in selected_coins])
                        where_clauses.append(f"coin IN ({placeholders})")
                        params.extend(selected_coins)
                    
                    if selected_ops and not hide_operation:
                        placeholders = ','.join(['?' for _ in selected_ops])
                        where_clauses.append(f"operation IN ({placeholders})")
                        params.extend(selected_ops)
                    
                    where_clauses.append("utc_time >= ?")
                    params.append(date_from_str)
                    where_clauses.append("utc_time <= ?")
                    params.append(date_to_str + "T23:59:59")
                    
                    # Filtro por sinal (positivo/negativo)
                    if sign_positive.isChecked() and not sign_negative.isChecked():
                        where_clauses.append("change > 0")
                    elif sign_negative.isChecked() and not sign_positive.isChecked():
                        where_clauses.append("change < 0")
                    
                    where_sql = " AND ".join(where_clauses)
                    
                    # Query com agrupamento (com ou sem operação)
                    if hide_operation:
                        group_by = "coin, account"
                        select_cols = "coin, NULL as operation, account"
                        order_by = "coin, account"
                    else:
                        group_by = "coin, operation, account"
                        select_cols = "coin, operation, account"
                        order_by = "coin, operation, account"
                    
                    query = f"""
                        SELECT {select_cols},
                               COUNT(*) as num_rows,
                               SUM(change) as total_change,
                               SUM(value_eur) as total_value_eur
                        FROM binance_transactions
                        WHERE {where_sql}
                        GROUP BY {group_by}
                        ORDER BY {order_by}
                    """
                    
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    
                    if not results:
                        results_label.setText("Nenhuma transação encontrada com os filtros selecionados.")
                        results_table.setRowCount(0)
                        return
                    
                    # Calcular totais gerais
                    total_rows = sum(r[3] for r in results)
                    total_change_all = sum(r[4] for r in results if r[4] is not None)
                    total_value_all = sum(r[5] for r in results if r[5] is not None)
                    
                    results_label.setText(
                        f"Total: {total_rows} transações | "
                        f"Change Total: {total_change_all:.8f} | "
                        f"Valor EUR Total: {total_value_all:.2f} €"
                    )
                    
                    # Preencher tabela
                    if hide_operation:
                        headers = ["Moeda", "Conta", "Nº Linhas", "Total Change", "Total Value EUR"]
                        col_indices = {"coin": 0, "account": 1, "num_rows": 2, "change": 3, "value": 4}
                    else:
                        headers = ["Moeda", "Operação", "Conta", "Nº Linhas", "Total Change", "Total Value EUR"]
                        col_indices = {"coin": 0, "operation": 1, "account": 2, "num_rows": 3, "change": 4, "value": 5}
                    
                    results_table.setRowCount(len(results))
                    results_table.setColumnCount(len(headers))
                    results_table.setHorizontalHeaderLabels(headers)
                    
                    for i, (coin, operation, account, num_rows, total_change, total_value) in enumerate(results):
                        col = 0
                        results_table.setItem(i, col, QTableWidgetItem(str(coin) if coin else ""))
                        col += 1
                        
                        if not hide_operation:
                            results_table.setItem(i, col, QTableWidgetItem(str(operation) if operation else ""))
                            col += 1
                        
                        results_table.setItem(i, col, QTableWidgetItem(str(account) if account else ""))
                        col += 1
                        results_table.setItem(i, col, QTableWidgetItem(str(num_rows)))
                        col += 1
                        results_table.setItem(i, col, QTableWidgetItem(f"{total_change:.8f}" if total_change else "0"))
                        col += 1
                        
                        # Alinhar valor EUR à direita
                        value_item = QTableWidgetItem(f"{total_value:.2f}" if total_value else "0")
                        value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        results_table.setItem(i, col, value_item)
                    
                    results_table.resizeColumnsToContents()
                    
                except Exception as e:
                    results_label.setText(f"Erro ao aplicar filtros: {e}")
                    import traceback
                    traceback.print_exc()
            
            apply_btn.clicked.connect(apply_filters)
            
            # Aplicar filtros inicialmente
            apply_filters()
            
            self.content_layout.addWidget(main_container)
            
            # Não fechar o DB aqui - será usado pelos filtros
            # Guardar referência para fechar depois se necessário
            if not hasattr(self, '_binance_db'):
                self._binance_db = db
            
        except Exception as e:
            label = QLabel("Erro ao analisar transações:\n" + str(e) + "\n" + traceback.format_exc())
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
        elif parent_name == CONSULTAR_DB and sub_name == TRANSACOES_BINANCE:
            self._show_binance_transactions()
        elif parent_name == BINANCE and sub_name == IMPORTAR_TRANSACOES:
            self._import_binance_transactions()
        elif parent_name == BINANCE and sub_name == ANALISAR_TRANSACOES:
            self._analyze_binance_transactions()
        elif parent_name == BINANCE and sub_name == FIFO_WALLET:
            self._show_fifo_wallet()
        elif parent_name == BINANCE and sub_name == RESUMO_FISCAL:
            self._show_resumo_fiscal()
        else:
            label = QLabel(f"Sub-opção '{sub_name}' em '{parent_name}' (dummy)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
    def _show_fifo_wallet(self):
        """Exibe a carteira FIFO (binance_wallet) com filtros para moeda e amount_remaining."""
        from PyQt6.QtWidgets import (
            QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit,
            QPushButton, QLabel, QWidget, QComboBox
        )
        import traceback
        
        try:
            from src.database import CryptoDatabase
            
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "crypto_prices.db"))
            db = CryptoDatabase(db_path)
            
            # Container principal
            main_widget = QWidget()
            main_layout = QVBoxLayout()
            main_widget.setLayout(main_layout)
            
            # --- Área de filtros no topo ---
            filter_widget = QWidget()
            filter_layout = QHBoxLayout()
            filter_widget.setLayout(filter_layout)
            
            # Filtro: Moeda
            filter_layout.addWidget(QLabel("Moeda:"))
            crypto_combo = QComboBox()
            crypto_combo.addItem("Todas")
            
            # Obter lista de moedas distintas
            cursor = db.conn.cursor()
            cursor.execute("SELECT DISTINCT crypto_id FROM binance_wallet ORDER BY crypto_id")
            cryptos = cursor.fetchall()
            for crypto in cryptos:
                crypto_combo.addItem(crypto[0])
            
            filter_layout.addWidget(crypto_combo)
            
            # Filtro: Amount remaining
            filter_layout.addWidget(QLabel("Amount remaining:"))
            remaining_combo = QComboBox()
            remaining_combo.addItem("Todos")
            remaining_combo.addItem("> 0 (Com saldo)")
            remaining_combo.addItem("= 0 (Esgotado)")
            filter_layout.addWidget(remaining_combo)
            
            # Botão aplicar filtros
            apply_button = QPushButton("Aplicar Filtros")
            filter_layout.addWidget(apply_button)
            
            # Botão reconstruir wallet
            rebuild_button = QPushButton("Reconstruir Wallet")
            rebuild_button.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
            filter_layout.addWidget(rebuild_button)
            
            filter_layout.addStretch()
            main_layout.addWidget(filter_widget)
            
            # --- Tabela de resultados ---
            table = QTableWidget()
            main_layout.addWidget(table)
            
            # Label de resumo (criar antes para estar sempre visível)
            summary_label = QLabel()
            main_layout.addWidget(summary_label)
            
            # Manter referência ao cursor para uso no callback
            wallet_cursor = db.conn.cursor()
            
            # Função para carregar dados na tabela
            def load_wallet_data():
                try:
                    # Construir query com filtros
                    query = "SELECT id, crypto_id, utc_time, amount_total, price_eur, amount_remaining FROM binance_wallet WHERE 1=1"
                    params = []
                    
                    # Filtro moeda
                    selected_crypto = crypto_combo.currentText()
                    if selected_crypto != "Todas":
                        query += " AND crypto_id = ?"
                        params.append(selected_crypto)
                    
                    # Filtro amount_remaining
                    selected_remaining = remaining_combo.currentText()
                    if selected_remaining == "> 0 (Com saldo)":
                        query += " AND amount_remaining > 0"
                    elif selected_remaining == "= 0 (Esgotado)":
                        query += " AND amount_remaining = 0"
                    
                    query += " ORDER BY crypto_id, utc_time"
                    
                    wallet_cursor.execute(query, params)
                    rows = wallet_cursor.fetchall()
                    
                    # Atualizar tabela
                    column_names = ["ID", "Moeda", "Data/Hora", "Total", "Preço EUR", "Restante"]
                    table.setColumnCount(len(column_names))
                    table.setRowCount(len(rows))
                    table.setHorizontalHeaderLabels(column_names)
                    
                    for i, row in enumerate(rows):
                        for j, value in enumerate(row):
                            # Formatar valores numéricos
                            if j in [3, 4, 5]:  # amount_total, price_eur, amount_remaining
                                if value is not None:
                                    item = QTableWidgetItem(f"{float(value):.8f}")
                                else:
                                    item = QTableWidgetItem("")
                            else:
                                item = QTableWidgetItem(str(value) if value is not None else "")
                            table.setItem(i, j, item)
                    
                    table.resizeColumnsToContents()
                    
                    # Mostrar resumo
                    if rows:
                        # Calcular resumo por moeda
                        wallet_cursor.execute(
                            "SELECT crypto_id, SUM(amount_remaining), COUNT(*) FROM binance_wallet WHERE amount_remaining > 0 GROUP BY crypto_id ORDER BY crypto_id"
                        )
                        summary = wallet_cursor.fetchall()
                        summary_text = "Resumo (saldos > 0): " + ", ".join(
                            [f"{row[0]}: {float(row[1]):.8f} ({row[2]} lotes)" for row in summary]
                        )
                    else:
                        summary_text = "Nenhum lote encontrado com os filtros aplicados."
                    
                    # Atualizar label de resumo
                    summary_label.setText(summary_text)
                    
                except Exception as e:
                    table.setRowCount(0)
                    summary_label.setText(f"Erro ao carregar dados: {str(e)}")
            
            # Função para reconstruir wallet
            def rebuild_wallet():
                try:
                    from PyQt6.QtWidgets import QMessageBox
                    # Confirmar ação
                    reply = QMessageBox.question(
                        main_widget, 
                        'Reconstruir Wallet',
                        'Reconstruir a carteira FIFO a partir de todas as transações?\n\nIsto irá:\n- Limpar todos os lotes atuais\n- Recalcular os lotes com base nas transações\n- Aplicar as regras do config.ini',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        summary_label.setText("Reconstruindo wallet...")
                        # Reconstruir
                        lots_created = db.rebuild_binance_wallet()
                        
                        # Recarregar lista de moedas
                        crypto_combo.clear()
                        crypto_combo.addItem("Todas")
                        wallet_cursor.execute("SELECT DISTINCT crypto_id FROM binance_wallet ORDER BY crypto_id")
                        cryptos = wallet_cursor.fetchall()
                        for crypto in cryptos:
                            crypto_combo.addItem(crypto[0])
                        
                        # Recarregar dados
                        load_wallet_data()
                        
                        # Mostrar sucesso
                        QMessageBox.information(
                            main_widget,
                            'Sucesso',
                            f'Wallet reconstruído com sucesso!\n\nLotes criados: {lots_created}'
                        )
                except Exception as e:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        main_widget,
                        'Erro',
                        f'Erro ao reconstruir wallet:\n{str(e)}'
                    )
                    summary_label.setText(f"Erro ao reconstruir: {str(e)}")
            
            # Conectar botão aos filtros
            apply_button.clicked.connect(load_wallet_data)
            rebuild_button.clicked.connect(rebuild_wallet)
            
            # Carregar dados iniciais
            load_wallet_data()
            
            self.content_layout.addWidget(main_widget)
            # Não fechar db aqui, pois os filtros precisam dele
            # A conexão será fechada quando a janela for fechada ou outro menu for selecionado
            
        except Exception as e:
            label = QLabel("Erro ao carregar FIFO Wallet:\n" + str(e) + "\n" + traceback.format_exc())
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
    
    def _show_resumo_fiscal(self):
        """Exibe o resumo fiscal (binance_fiscal) com filtros por tipo, data, moeda e modos de visualização."""
        from PyQt6.QtWidgets import (
            QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit,
            QPushButton, QLabel, QWidget, QComboBox, QDateEdit, QRadioButton, QButtonGroup
        )
        from PyQt6.QtCore import QDate
        import traceback
        
        try:
            from src.database import CryptoDatabase
            
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "crypto_prices.db"))
            db = CryptoDatabase(db_path)
            
            # Container principal
            main_widget = QWidget()
            main_layout = QVBoxLayout()
            main_widget.setLayout(main_layout)
            
            # --- Título ---
            title_label = QLabel("Resumo Fiscal - Binance")
            title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(title_label)
            
            # --- Área de filtros no topo ---
            filter_widget = QWidget()
            filter_layout = QVBoxLayout()
            filter_widget.setLayout(filter_layout)
            
            # Linha 1: Tipo e Moeda
            filter_line1 = QHBoxLayout()
            
            filter_line1.addWidget(QLabel("Tipo:"))
            type_combo = QComboBox()
            type_combo.addItem("Todos", None)
            type_combo.addItem("Income (I)", "I")
            type_combo.addItem("Sales (V)", "V")
            filter_line1.addWidget(type_combo)
            
            filter_line1.addWidget(QLabel("Moeda:"))
            crypto_combo = QComboBox()
            crypto_combo.addItem("Todas", None)
            
            # Obter lista de moedas distintas
            cursor = db.conn.cursor()
            cursor.execute("SELECT DISTINCT crypto_id FROM binance_fiscal ORDER BY crypto_id")
            cryptos = cursor.fetchall()
            for crypto in cryptos:
                crypto_combo.addItem(crypto[0])
            
            filter_line1.addWidget(crypto_combo)
            filter_line1.addStretch()
            filter_layout.addLayout(filter_line1)
            
            # Linha 2: Intervalo de datas
            filter_line2 = QHBoxLayout()
            filter_line2.addWidget(QLabel("Data de:"))
            date_from = QDateEdit()
            date_from.setCalendarPopup(True)
            date_from.setDate(QDate.currentDate().addYears(-1))  # Default: 1 ano atrás
            filter_line2.addWidget(date_from)
            
            filter_line2.addWidget(QLabel("até:"))
            date_to = QDateEdit()
            date_to.setCalendarPopup(True)
            date_to.setDate(QDate.currentDate())
            filter_line2.addWidget(date_to)
            filter_line2.addStretch()
            filter_layout.addLayout(filter_line2)
            
            # Linha 3: Modo de visualização
            filter_line3 = QHBoxLayout()
            filter_line3.addWidget(QLabel("Visualização:"))
            
            view_group = QButtonGroup()
            view_detail = QRadioButton("Linha a linha")
            view_by_crypto = QRadioButton("Agrupado por moeda")
            view_by_type = QRadioButton("Agrupado por tipo")
            view_detail.setChecked(True)
            
            view_group.addButton(view_detail)
            view_group.addButton(view_by_crypto)
            view_group.addButton(view_by_type)
            
            filter_line3.addWidget(view_detail)
            filter_line3.addWidget(view_by_crypto)
            filter_line3.addWidget(view_by_type)
            filter_line3.addStretch()
            filter_layout.addLayout(filter_line3)
            
            # Botão aplicar filtros
            filter_line4 = QHBoxLayout()
            apply_button = QPushButton("Aplicar Filtros")
            apply_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
            filter_line4.addWidget(apply_button)
            filter_line4.addStretch()
            filter_layout.addLayout(filter_line4)
            
            main_layout.addWidget(filter_widget)
            
            # --- Tabela de resultados ---
            table = QTableWidget()
            main_layout.addWidget(table)
            
            # Label de resumo
            summary_label = QLabel()
            summary_label.setStyleSheet("font-weight: bold; padding: 5px;")
            main_layout.addWidget(summary_label)
            
            # Função para carregar dados
            def load_fiscal_data():
                try:
                    cursor = db.conn.cursor()
                    
                    # Construir query com base nos filtros
                    query = "SELECT * FROM binance_fiscal WHERE 1=1"
                    params = []
                    
                    # Filtro por tipo
                    selected_type = type_combo.currentData()
                    if selected_type:
                        query += " AND type = ?"
                        params.append(selected_type)
                    
                    # Filtro por moeda
                    selected_crypto = crypto_combo.currentData()
                    if selected_crypto:
                        query += " AND crypto_id = ?"
                        params.append(selected_crypto)
                    
                    # Filtro por data
                    date_from_str = date_from.date().toString("yyyy-MM-dd")
                    date_to_str = date_to.date().toString("yyyy-MM-dd")
                    query += " AND DATE(trn_date_utc) >= ? AND DATE(trn_date_utc) <= ?"
                    params.append(date_from_str)
                    params.append(date_to_str)
                    
                    # Determinar modo de visualização
                    if view_detail.isChecked():
                        # Linha a linha
                        query += " ORDER BY trn_date_utc DESC"
                        cursor.execute(query, params)
                        rows = cursor.fetchall()
                        
                        if not rows:
                            table.setRowCount(0)
                            table.setColumnCount(0)
                            summary_label.setText("Nenhum registo encontrado com os filtros aplicados.")
                            return
                        
                        column_names = [desc[0] for desc in cursor.description]
                        table.setRowCount(len(rows))
                        table.setColumnCount(len(column_names))
                        table.setHorizontalHeaderLabels(column_names)
                        
                        total_gain = 0.0
                        total_tax = 0.0
                        
                        for i, row in enumerate(rows):
                            for j, value in enumerate(row):
                                table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
                            # Somar gain e tax
                            gain_idx = column_names.index('gain_eur')
                            tax_idx = column_names.index('tax_eur')
                            total_gain += row[gain_idx] if row[gain_idx] else 0.0
                            total_tax += row[tax_idx] if row[tax_idx] else 0.0
                        
                        table.resizeColumnsToContents()
                        summary_label.setText(
                            f"Total de registos: {len(rows)} | "
                            f"Ganho total: {total_gain:.2f} EUR | "
                            f"Imposto total: {total_tax:.2f} EUR"
                        )
                    
                    elif view_by_crypto.isChecked():
                        # Agrupado por moeda
                        group_query = """
                            SELECT 
                                crypto_id,
                                COUNT(*) as num_transacoes,
                                SUM(buy_eur) as total_buy,
                                SUM(sell_eur) as total_sell,
                                SUM(gain_eur) as total_gain,
                                SUM(tax_eur) as total_tax
                            FROM binance_fiscal
                            WHERE 1=1
                        """
                        
                        if selected_type:
                            group_query += " AND type = ?"
                        if selected_crypto:
                            group_query += " AND crypto_id = ?"
                        
                        group_query += " AND DATE(trn_date_utc) >= ? AND DATE(trn_date_utc) <= ?"
                        group_query += " GROUP BY crypto_id ORDER BY total_gain DESC"
                        
                        cursor.execute(group_query, params)
                        rows = cursor.fetchall()
                        
                        if not rows:
                            table.setRowCount(0)
                            table.setColumnCount(0)
                            summary_label.setText("Nenhum registo encontrado com os filtros aplicados.")
                            return
                        
                        column_names = ["Moeda", "Nº Transações", "Total Buy (EUR)", "Total Sell (EUR)", "Total Gain (EUR)", "Total Tax (EUR)"]
                        table.setRowCount(len(rows))
                        table.setColumnCount(len(column_names))
                        table.setHorizontalHeaderLabels(column_names)
                        
                        total_gain = 0.0
                        total_tax = 0.0
                        
                        for i, row in enumerate(rows):
                            for j, value in enumerate(row):
                                # Formatar valores numéricos
                                if j > 0 and value is not None:
                                    if j == 1:  # Nº transações
                                        table.setItem(i, j, QTableWidgetItem(str(value)))
                                    else:  # Valores monetários
                                        table.setItem(i, j, QTableWidgetItem(f"{value:.2f}"))
                                else:
                                    table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
                            
                            total_gain += row[4] if row[4] else 0.0
                            total_tax += row[5] if row[5] else 0.0
                        
                        table.resizeColumnsToContents()
                        summary_label.setText(
                            f"Total de moedas: {len(rows)} | "
                            f"Ganho total: {total_gain:.2f} EUR | "
                            f"Imposto total: {total_tax:.2f} EUR"
                        )
                    
                    elif view_by_type.isChecked():
                        # Agrupado por tipo
                        group_query = """
                            SELECT 
                                type,
                                COUNT(*) as num_transacoes,
                                SUM(buy_eur) as total_buy,
                                SUM(sell_eur) as total_sell,
                                SUM(gain_eur) as total_gain,
                                SUM(tax_eur) as total_tax
                            FROM binance_fiscal
                            WHERE 1=1
                        """
                        
                        if selected_type:
                            group_query += " AND type = ?"
                        if selected_crypto:
                            group_query += " AND crypto_id = ?"
                        
                        group_query += " AND DATE(trn_date_utc) >= ? AND DATE(trn_date_utc) <= ?"
                        group_query += " GROUP BY type ORDER BY type"
                        
                        cursor.execute(group_query, params)
                        rows = cursor.fetchall()
                        
                        if not rows:
                            table.setRowCount(0)
                            table.setColumnCount(0)
                            summary_label.setText("Nenhum registo encontrado com os filtros aplicados.")
                            return
                        
                        column_names = ["Tipo", "Nº Transações", "Total Buy (EUR)", "Total Sell (EUR)", "Total Gain (EUR)", "Total Tax (EUR)"]
                        table.setRowCount(len(rows))
                        table.setColumnCount(len(column_names))
                        table.setHorizontalHeaderLabels(column_names)
                        
                        total_gain = 0.0
                        total_tax = 0.0
                        
                        for i, row in enumerate(rows):
                            # Formatar tipo
                            tipo = row[0]
                            tipo_desc = "Income (I)" if tipo == "I" else "Sales (V)"
                            table.setItem(i, 0, QTableWidgetItem(tipo_desc))
                            
                            for j in range(1, len(row)):
                                value = row[j]
                                if value is not None:
                                    if j == 1:  # Nº transações
                                        table.setItem(i, j, QTableWidgetItem(str(value)))
                                    else:  # Valores monetários
                                        table.setItem(i, j, QTableWidgetItem(f"{value:.2f}"))
                                else:
                                    table.setItem(i, j, QTableWidgetItem(""))
                            
                            total_gain += row[4] if row[4] else 0.0
                            total_tax += row[5] if row[5] else 0.0
                        
                        table.resizeColumnsToContents()
                        summary_label.setText(
                            f"Total de tipos: {len(rows)} | "
                            f"Ganho total: {total_gain:.2f} EUR | "
                            f"Imposto total: {total_tax:.2f} EUR"
                        )
                        
                except Exception as e:
                    summary_label.setText(f"Erro ao carregar dados: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
            
            # Conectar botão aos filtros
            apply_button.clicked.connect(load_fiscal_data)
            
            # Carregar dados iniciais
            load_fiscal_data()
            
            self.content_layout.addWidget(main_widget)
            
        except Exception as e:
            label = QLabel("Erro ao carregar Resumo Fiscal:\n" + str(e) + "\n" + traceback.format_exc())
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
