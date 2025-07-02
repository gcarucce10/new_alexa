import sys
import json
import os
import speech_recognition as sr
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget,
    QVBoxLayout, QDialog, QLabel, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QLineEdit


CONFIG_PATH = "config.json"

def carregar_config():
    if not os.path.exists(CONFIG_PATH):
        return {"modo_escuro": False}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def salvar_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


class ConfigWindow(QDialog):
    def __init__(self, config, aplicar_tema_callback):
        super().__init__()
        self.setWindowTitle("Configurações")
        self.setFixedSize(300, 200)
        self.config = config
        self.aplicar_tema_callback = aplicar_tema_callback

        layout = QVBoxLayout()

        label = QLabel("Aqui vão as configurações da assistente...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.checkbox = QCheckBox("Ativar modo escuro")
        self.checkbox.setChecked(config.get("modo_escuro", False))
        layout.addWidget(self.checkbox)

        self.checkbox.stateChanged.connect(self.salvar_config)

        self.setLayout(layout)

    def salvar_config(self):
        self.config["modo_escuro"] = self.checkbox.isChecked()
        salvar_config(self.config)
        self.aplicar_tema_callback(self.config["modo_escuro"])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = carregar_config()
        self.texto_digitado = ""

        self.setWindowTitle("Assistente Virtual")
        self.setFixedSize(400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_voz = QPushButton("Usar Voz")
        self.btn_texto = QPushButton("Usar Texto")
        self.layout.addWidget(self.btn_voz)
        self.layout.addWidget(self.btn_texto)

        self.input_texto = QLineEdit()
        self.input_texto.setPlaceholderText("Digite aqui...")
        self.input_texto.returnPressed.connect(self.salvar_texto_digitado)
        self.input_texto.hide()  # esconde inicialmente
        self.layout.addWidget(self.input_texto)

        self.btn_config = QPushButton("⚙")
        self.btn_config.setFixedSize(30, 30)
        self.btn_config.setParent(self)
        self.btn_config.move(self.width() - 40, 10)
        self.btn_config.clicked.connect(self.abrir_configuracoes)

        self.btn_voz.clicked.connect(self.reconhecer_voz)
        self.btn_texto.clicked.connect(self.mostrar_input_texto)

        central_widget.setLayout(self.layout)

        self.aplicar_tema(self.config.get("modo_escuro", False))

    def aplicar_tema(self, escuro: bool):
        app = QApplication.instance()
        palette = QPalette()
        if escuro:
            palette.setColor(QPalette.ColorRole.Window, QColor("#121212"))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        else:
            palette = app.style().standardPalette()
        app.setPalette(palette)

    def abrir_configuracoes(self):
        self.config_window = ConfigWindow(self.config, self.aplicar_tema)
        self.config_window.exec()

    def reconhecer_voz(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Fale alguma coisa...")
            audio = recognizer.listen(source)

        try:
            texto = recognizer.recognize_google(audio, language="pt-BR")
            print("Você disse:", texto)
        except sr.UnknownValueError:
            print("Não entendi o que você disse.")
        except sr.RequestError as e:
            print(f"Erro ao acessar o serviço de reconhecimento de voz: {e}")

    def mostrar_input_texto(self):
        self.input_texto.show()
        self.input_texto.setFocus()

    def salvar_texto_digitado(self):
        self.texto_digitado = self.input_texto.text()
        print("Texto digitado:", self.texto_digitado)
        self.input_texto.clear()
        self.input_texto.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
