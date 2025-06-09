import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QLabel, QLineEdit, QStackedWidget, QHBoxLayout)

# Tela 1: Uma página simples com um rótulo
class Pagina1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Esta é a Página 1.\nClique no botão acima para trocar de tela."))
        self.setLayout(layout)

# Tela 2: Contém a caixa de texto e a lógica para interagir com ela
class Pagina2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Widget de caixa de texto
        self.caixa_texto = QLineEdit(self)
        self.caixa_texto.setPlaceholderText("Digite seu nome aqui...") # Texto de ajuda
        
        # Botão para enviar o texto
        self.botao_enviar = QPushButton("Enviar", self)
        
        # Rótulo para mostrar o resultado
        self.label_resultado = QLabel("O resultado aparecerá aqui.", self)
        
        # Conecta o clique do botão à função
        self.botao_enviar.clicked.connect(self.processar_texto)
        
        layout.addWidget(QLabel("Esta é a Página 2."))
        layout.addWidget(self.caixa_texto)
        layout.addWidget(self.botao_enviar)
        layout.addWidget(self.label_resultado)
        
        self.setLayout(layout)

    def processar_texto(self):
        # 1. Pega o texto da caixa de texto
        texto_digitado = self.caixa_texto.text()
        
        # Verifica se o texto não está vazio
        if texto_digitado:
            # 2. Altera o texto do rótulo de resultado
            self.label_resultado.setText(f"Olá, {texto_digitado}!")
            # 3. Limpa a caixa de texto para a próxima entrada
            self.caixa_texto.clear()
        else:
            self.label_resultado.setText("Por favor, digite algo na caixa de texto.")


# Janela Principal que gerencia as telas
class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicação Qt Interativa")
        self.setGeometry(100, 100, 350, 200)

        # Layout principal da janela
        layout_principal = QVBoxLayout()

        # 1. Criando o QStackedWidget para gerenciar as telas
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(Pagina1()) # Índice 0
        self.stacked_widget.addWidget(Pagina2()) # Índice 1
        
        # 2. Criando os botões de navegação
        layout_botoes = QHBoxLayout()
        botao_pag1 = QPushButton("Página 1")
        botao_pag2 = QPushButton("Página 2")
        layout_botoes.addWidget(botao_pag1)
        layout_botoes.addWidget(botao_pag2)
        
        # 3. Conectando os botões para alterar a tela visível
        botao_pag1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        botao_pag2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        # Adicionando os widgets ao layout principal
        layout_principal.addLayout(layout_botoes)
        layout_principal.addWidget(self.stacked_widget)
        
        self.setLayout(layout_principal)

# Ponto de entrada da aplicação
if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())