from tools import *
import sys
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
    QComboBox, QDateTimeEdit, QDoubleSpinBox, QStackedWidget
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtGui import QIcon, QPixmap

# Constantes 
CALC_METHODS = ["linear", "linear_double", "sin", "cos", "square", "sqrt", "log"]
STEPS = ["segundo", "minuto", "hora", "dia"]
STEP_MAP = {
    "segundo": "second", 
    "minuto": "minute", 
    "hora": "hour", 
    "dia": "day"
}

# ----------------------------
# Helpers
# ----------------------------
def back_button(stack):
    btn = QPushButton("← Voltar ao Menu")
    btn.clicked.connect(lambda: stack.setCurrentIndex(0))
    return btn

def default_output_path(prefix: str):
    Path("./output/results").mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(Path(f"./output/results/{prefix}_{ts}.xml").absolute())

def iso(dt_edit: QDateTimeEdit):
    return dt_edit.dateTime().toString(Qt.ISODate)

def create_file_selection(label_text, line_edit, button_text, callback):
    """Cria um layout horizontal com Label, Input e Botão para clareza."""
    layout = QVBoxLayout()
    layout.addWidget(QLabel(f"<b>{label_text}</b>"))
    h_layout = QHBoxLayout()
    h_layout.addWidget(line_edit)
    btn = QPushButton(button_text)
    btn.clicked.connect(callback)
    h_layout.addWidget(btn)
    layout.addLayout(h_layout)
    return layout

class LandingPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30) # Adiciona um respiro nas bordas
        layout.setSpacing(15)

        # 1. Título
        title = QLabel("<h2>Ferramenta de Trends XML</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 2. Ícone Central
        self.logo = QLabel()
        pixmap = QPixmap("./icons/xml-icon.png")
        
        # Redimensiona a imagem para ser um destaque (ex: 150x150)
        if not pixmap.isNull():
            self.logo.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo.setText("[Ícone não encontrado]")
            
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)

        # 3. Espaçador (Empurra os botões para baixo)
        layout.addStretch()

        # 4. Botões de Ação
        actions = [
            ("Gerar Novo Trend XML", 1),
            ("Converter Excel → XML", 2),
            ("Modificar Trend Existente", 3),
            ("Deletar Intervalo de Dados", 4),
        ]

        for text, idx in actions:
            btn = QPushButton(text)
            btn.setMinimumHeight(45) # Botões mais altos para facilitar o clique
            btn.setCursor(Qt.PointingHandCursor) # Cursor de "mãozinha"
            btn.clicked.connect(lambda _, i=idx: stack.setCurrentIndex(i))
            layout.addWidget(btn)

        self.setLayout(layout)

class GenerateXMLPage(QWidget):
    def __init__(self, stack):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(back_button(stack))
        layout.addWidget(QLabel("<h3>Gerar Novo Trend XML</h3>"))

        self.start_dt = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_dt = QDateTimeEdit(QDateTime.currentDateTime().addDays(1))

        self.start_dt.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.end_dt.setDisplayFormat("dd/MM/yyyy HH:mm:ss")

        self.step = QComboBox(); self.step.addItems(STEPS)
        self.calc = QComboBox(); self.calc.addItems(CALC_METHODS)
        self.output_path = QLineEdit(default_output_path("gerado"))

        layout.addWidget(QLabel("Início:"))
        layout.addWidget(self.start_dt)
        layout.addWidget(QLabel("Fim:"))
        layout.addWidget(self.end_dt)
        layout.addWidget(QLabel("Frequência (Passo):"))
        layout.addWidget(self.step)
        layout.addWidget(QLabel("Cálculo:"))
        layout.addWidget(self.calc)
        
        layout.addLayout(create_file_selection("Salvar Resultado Em:", self.output_path, "Alterar Destino", self.browse))

        run = QPushButton("Gerar Arquivo")
        run.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        run.clicked.connect(self.run)
        layout.addWidget(run)
        self.setLayout(layout)

    def browse(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar XML", self.output_path.text(), "XML Files (*.xml)")
        if path: self.output_path.setText(path)

    def run(self):
        generate_xml(
            start_date=iso(self.start_dt),
            end_date=iso(self.end_dt),
            step=STEP_MAP[self.step.currentText()],
            calc=self.calc.currentText(),
            file_path=self.output_path.text(),
        )
        QMessageBox.information(self, "Sucesso", "XML gerado com sucesso!")

class ConversionWorker(QThread):
    finished = pyqtSignal(str)  # Sinal para quando terminar
    error = pyqtSignal(str)     # Sinal para caso de erro

    def __init__(self, input_path, output_path):
        super().__init__()

        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        try:
            # Chama sua função do backend
            convert_to_xml(self.input_path, self.output_path)
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))

class ConvertExcelPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(back_button(stack))
        layout.addWidget(QLabel("<h3>Converter Excel para XML</h3>"))

        # Guia de Formatação
        guide_box = QWidget()
        guide_box.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;")
        guide_layout = QVBoxLayout(guide_box)
        guide_label = QLabel(
            "<b>Instruções de Formatação:</b><br>"
            "• Colunas: <b>timestamp</b> e <b>value</b> (exatamente esses nomes).<br>"
            "• Datas: Formato padrão de data/hora do Excel. (Ex: 02/10/2026 10:34:06 PM) <br>"
            "• Valores: Apenas números (pontos para decimais)."
        )
        guide_label.setWordWrap(True)
        guide_layout.addWidget(guide_label)
        layout.addWidget(guide_box)

        # Seleção de Arquivo
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Selecione o arquivo .xlsx...")
        layout.addLayout(create_file_selection("Origem:", self.input_path, "Procurar", self.browse_in))

        # Barra de Progresso (Invisível por padrão)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Estilo "Indeterminado/Loading"
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 2px solid #ddd; border-radius: 5px; text-align: center; }
            QProgressBar::chunk { background-color: #3498db; }
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Botão de Ação
        self.btn_run = QPushButton("Iniciar Conversão")
        self.btn_run.setMinimumHeight(45)
        self.btn_run.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.btn_run.clicked.connect(self.start_conversion)
        
        layout.addWidget(self.btn_run)
        layout.addStretch()
        self.setLayout(layout)

    def browse_in(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Excel", "", "Excel Files (*.xlsx *.xls)")
        if path: self.input_path.setText(path)

    def start_conversion(self):
        if not self.input_path.text():
            return QMessageBox.warning(self, "Erro", "Selecione um arquivo!")

        # 1. Preparar Interface
        self.btn_run.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Processando planilha pesada... aguarde.")
        dest = default_output_path("excel_import")

        # 2. Configurar Thread
        self.worker = ConversionWorker(self.input_path.text(), dest)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        
        # 3. Iniciar
        self.worker.start()

    def on_finished(self, dest):
        self.btn_run.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        QMessageBox.information(self, "Sucesso", f"Conversão concluída!\nSalvo em: {dest}")

    def on_error(self, message):
        self.btn_run.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        QMessageBox.critical(self, "Erro na Conversão", f"Ocorreu um erro:\n{message}")

class ModifyTrendPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(back_button(stack))
        layout.addWidget(QLabel("<h3>Modificar Trend Existente</h3>"))

        self.input_path = QLineEdit()
        self.range_start = QDateTimeEdit(QDateTime.currentDateTime())
        self.range_end = QDateTimeEdit(QDateTime.currentDateTime())

        self.range_start.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.range_end.setDisplayFormat("dd/MM/yyyy HH:mm:ss")

        self.mode = QComboBox(); self.mode.addItems(["valor_constante"] + CALC_METHODS)
        self.constant = QDoubleSpinBox(); self.constant.setRange(-999999, 999999)
        self.output_path = QLineEdit(default_output_path("modificado"))

        layout.addLayout(create_file_selection("Arquivo XML Original:", self.input_path, "Procurar XML", self.browse_in))
        layout.addWidget(QLabel("Início do Intervalo:"))
        layout.addWidget(self.range_start)
        layout.addWidget(QLabel("Fim do Intervalo:"))
        layout.addWidget(self.range_end)
        layout.addWidget(QLabel("Tipo de Modificação:"))
        layout.addWidget(self.mode)
        layout.addWidget(QLabel("Valor Constante (se aplicável):"))
        layout.addWidget(self.constant)
        layout.addLayout(create_file_selection("Salvar Novo Arquivo Como:", self.output_path, "Alterar Destino", self.browse_out))

        run = QPushButton("Aplicar e Salvar")
        run.clicked.connect(self.run)
        layout.addWidget(run)
        self.setLayout(layout)

    def browse_in(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar XML de Origem", "", "XML Files (*.xml)")
        if path: self.input_path.setText(path)

    def browse_out(self):
        path, _ = QFileDialog.getSaveFileName(self, "Destino do XML Modificado", self.output_path.text(), "XML Files (*.xml)")
        if path: self.output_path.setText(path)

    def run(self):
        if not self.input_path.text(): return QMessageBox.warning(self, "Erro", "Selecione o arquivo de entrada!")
        
        modify_existing_trend(
            input_file=self.input_path.text(),
            range_start=iso(self.range_start),
            range_end=iso(self.range_end),
            step="minute",
            constant_value=self.constant.value() if self.mode.currentText() == "valor_constante" else None,
            calc=None if self.mode.currentText() == "valor_constante" else self.mode.currentText(),
            output_file=self.output_path.text(),
        )
        QMessageBox.information(self, "Sucesso", "Arquivo modificado com sucesso!")

class DeleteTrendPage(QWidget):
    def __init__(self, stack):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(back_button(stack))
        layout.addWidget(QLabel("<h3>Remover Intervalo de Dados</h3>"))

        self.input_path = QLineEdit()
        self.range_start = QDateTimeEdit(QDateTime.currentDateTime())
        self.range_end = QDateTimeEdit(QDateTime.currentDateTime())

        self.range_start.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.range_end.setDisplayFormat("dd/MM/yyyy HH:mm:ss")        

        self.output_path = QLineEdit(default_output_path("deletado"))

        layout.addLayout(create_file_selection("Arquivo XML Original:", self.input_path, "Procurar XML", self.browse_in))
        layout.addWidget(QLabel("Início da Deleção:"))
        layout.addWidget(self.range_start)
        layout.addWidget(QLabel("Fim da Deleção:"))
        layout.addWidget(self.range_end)
        layout.addLayout(create_file_selection("Salvar Resultado Em:", self.output_path, "Alterar Destino", self.browse_out))

        run = QPushButton("Remover Dados")
        run.setStyleSheet("background-color: #e74c3c; color: white;")
        run.clicked.connect(self.run)
        layout.addWidget(run)
        self.setLayout(layout)

    def browse_in(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar XML de Origem", "", "XML Files (*.xml)")
        if path: self.input_path.setText(path)

    def browse_out(self):
        path, _ = QFileDialog.getSaveFileName(self, "Destino do XML", self.output_path.text(), "XML Files (*.xml)")
        if path: self.output_path.setText(path)

    def run(self):
        delete_existing_trend(
            input_file=self.input_path.text(),
            range_start=iso(self.range_start),
            range_end=iso(self.range_end),
            output_file=self.output_path.text(),
        )
        QMessageBox.information(self, "Sucesso", "Intervalo removido com sucesso!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ferramenta de Trends XML - v2.0")
        
        # Define o ícone da barra de título
        self.setWindowIcon(QIcon("./icons/xml-icon.png"))
        
        self.resize(520, 600)

        stack = QStackedWidget()
        stack.addWidget(LandingPage(stack))
        stack.addWidget(GenerateXMLPage(stack))
        stack.addWidget(ConvertExcelPage(stack))
        stack.addWidget(ModifyTrendPage(stack))
        stack.addWidget(DeleteTrendPage(stack))

        self.setCentralWidget(stack)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())