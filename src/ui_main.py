import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget, QLabel
from PyQt6.QtCore import Qt
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptoPlay Dashboard")
        self.resize(900, 600)
        self.init_ui()

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Sidebar (menu)
        sidebar = QListWidget()
        sidebar.addItems([
            "Atualizar Dados",
            "Abrir Relatório",
            "Consultar Base de Dados",
            "Ver Gráficos"
        ])
        sidebar.setMaximumWidth(180)
        main_layout.addWidget(sidebar)

        # Content area (right)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
        main_layout.addWidget(self.content_area)

        # Placeholder for initial content
        self.placeholder_label = QLabel("Selecione uma opção no menu à esquerda.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.placeholder_label)

        # Connect sidebar selection
        sidebar.currentRowChanged.connect(self.display_content)

    def display_content(self, index):
        # Clear current content
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if index == 0:
            label = QLabel("Função: Atualizar Dados (a implementar)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
        elif index == 1:
            label = QLabel("Função: Abrir Relatório (a implementar)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
        elif index == 2:
            label = QLabel("Função: Consultar Base de Dados (a implementar)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)
        elif index == 3:
            plot_widget = pg.PlotWidget()
            plot_widget.plot([1,2,3,4,5], [10, 20, 15, 30, 25], pen=pg.mkPen(color='b', width=2))
            self.content_layout.addWidget(plot_widget)
        else:
            label = QLabel("Selecione uma opção no menu à esquerda.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(label)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
