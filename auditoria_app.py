import sys
import smtplib
from email.mime.text import MIMEText
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QRadioButton, QGridLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QButtonGroup
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QDate



def enviar_email(destinatario, assunto, mensagem):
    remetente = ""       
    senha = ""                  

    msg = MIMEText(mensagem, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remetente, senha)
            servidor.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False



class ChecklistTab(QWidget):
    def __init__(self):
        super().__init__()
        self.perguntas = [
            "bla bla bla ble ble ble blublub lbu",
            "bla bla bla ble ble ble blublub lbu",
            "bla bla bla ble ble ble blublub lbu",
            "bla bla bla ble ble ble blublub lbu",
            "bla bla bla ble ble ble blublub lbu"
        ]
        
        self.button_groups = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Checklist de Auditoria de Qualidade")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(titulo)

        grid = QGridLayout()
        self.respostas = []

        for i, pergunta in enumerate(self.perguntas):
            label = QLabel(pergunta)
            rb_sim = QRadioButton("Sim")
            rb_nao = QRadioButton("Não")
            rb_na = QRadioButton("N/A")

         
            grupo = QButtonGroup(self)
            grupo.addButton(rb_sim)
            grupo.addButton(rb_nao)
            grupo.addButton(rb_na)

            self.button_groups.append(grupo)  
            self.respostas.append((grupo, rb_sim, rb_nao, rb_na))

            grid.addWidget(label, i, 0)
            grid.addWidget(rb_sim, i, 1)
            grid.addWidget(rb_nao, i, 2)
            grid.addWidget(rb_na, i, 3)

        layout.addLayout(grid)

        self.btn_calcular = QPushButton("Calcular Aderência")
        self.btn_calcular.clicked.connect(self.calcular)
        self.btn_calcular.setStyleSheet("""
            QPushButton {
                background-color: #F8BBD0;
                border: none;
                padding: 8px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F48FB1;
            }
        """)
        layout.addWidget(self.btn_calcular, alignment=Qt.AlignmentFlag.AlignCenter)

        self.resultado = QLabel("")
        self.resultado.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(self.resultado, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def calcular(self):
        total_validas = 0
        total_sim = 0

        for grupo, rb_sim, rb_nao, rb_na in self.respostas:
            if rb_na.isChecked():
                continue
            if rb_sim.isChecked():
                total_sim += 1
            total_validas += 1

        if total_validas == 0:
            QMessageBox.warning(self, "Aviso", "Nenhuma questão válida para cálculo.")
            return

        aderencia = (total_sim / total_validas) * 100
        self.resultado.setText(f"Aderência: {aderencia:.1f}%")
        self.resultado.setStyleSheet("color: green;" if aderencia >= 80 else "color: red;")




class NCTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Registro e Acompanhamento de Não Conformidades")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(titulo)

      
        self.label_desc = QLabel("Descrição:")
        self.input_desc = QTextEdit()

        self.label_resp = QLabel("Responsável (E-mail):")
        self.input_resp = QLineEdit()

        self.label_grav = QLabel("Gravidade (Grave, Média, Leve):")
        self.input_grav = QLineEdit()

        self.label_prazo = QLabel("Prazo (automático):")
        self.input_prazo = QLineEdit()
        self.input_prazo.setReadOnly(True)

        self.input_grav.textChanged.connect(self.definir_prazo)

        
        self.btn_registrar = QPushButton("Registrar NC")
        self.btn_registrar.clicked.connect(self.registrar_nc)

        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.clicked.connect(self.limpar)

        for btn in [self.btn_registrar, self.btn_limpar]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8BBD0;
                    border: none;
                    padding: 8px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F48FB1;
                }
            """)

       
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Descrição", "Responsável", "Gravidade", "Prazo"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # type: ignore

       
        layout.addWidget(self.label_desc)
        layout.addWidget(self.input_desc)
        layout.addWidget(self.label_resp)
        layout.addWidget(self.input_resp)
        layout.addWidget(self.label_grav)
        layout.addWidget(self.input_grav)
        layout.addWidget(self.label_prazo)
        layout.addWidget(self.input_prazo)

        botoes = QHBoxLayout()
        botoes.addWidget(self.btn_registrar)
        botoes.addWidget(self.btn_limpar)
        layout.addLayout(botoes)

        layout.addWidget(self.tabela)
        self.setLayout(layout)

    def definir_prazo(self):
        gravidade = self.input_grav.text().strip().lower()
        if gravidade == "grave":
            dias = 1
        elif gravidade in ("média", "media"):
            dias = 4
        elif gravidade == "leve":
            dias = 5
        else:
            dias = None

        if dias:
            data = QDate.currentDate().addDays(dias).toString("dd/MM/yyyy")
            self.input_prazo.setText(f"{dias} dias (até {data})")
        else:
            self.input_prazo.clear()

    def registrar_nc(self):
        desc = self.input_desc.toPlainText().strip()
        resp = self.input_resp.text().strip()
        grav = self.input_grav.text().strip()
        prazo = self.input_prazo.text().strip()

        if not all([desc, resp, grav, prazo]):
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha todos os campos corretamente.")
            return

        linha = self.tabela.rowCount()
        self.tabela.insertRow(linha)
        self.tabela.setItem(linha, 0, QTableWidgetItem(desc))
        self.tabela.setItem(linha, 1, QTableWidgetItem(resp))
        self.tabela.setItem(linha, 2, QTableWidgetItem(grav))
        self.tabela.setItem(linha, 3, QTableWidgetItem(prazo))

        assunto = f"Nova Não Conformidade - Gravidade: {grav}"
        mensagem = (
            f"Descrição: {desc}\n"
            f"Gravidade: {grav}\n"
            f"Prazo: {prazo}\n\n"
            f"Atenciosamente,\nSistema de Auditoria"
        )
        enviar_email(resp, assunto, mensagem)
        QMessageBox.information(self, "Sucesso", "NC registrada e e-mail enviado!")
        self.limpar()

    def limpar(self):
        self.input_desc.clear()
        self.input_resp.clear()
        self.input_grav.clear()
        self.input_prazo.clear()



class AuditoriaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Auditoria de Qualidade")
        self.setGeometry(200, 100, 900, 700)
        self.config_tema()
        self.init_ui()

    def config_tema(self):
       
        self.setStyleSheet("""
            QWidget {
                background-color: #FFF5F7;
                color: #222;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
            
            QRadioButton {
                spacing: 6px;
            }

            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 7px;
                border: 2px solid #E91E63; /* rosa escuro */
                background-color: white;
            }

            QRadioButton::indicator:hover {
                border-color: #C2185B; /* rosa mais escuro no hover */
            }

            QRadioButton::indicator:checked {
                background-color: #E91E63; /* bolinha rosa preenchida */
                border: 2px solid #C2185B;
            }

            QTabWidget::pane {
                border: 1px solid #E1BEE7;
                border-radius: 8px;
                background: #FFFFFF;
            }
            QTabBar::tab {
                background: #F8BBD0;
                border: 1px solid #E1BEE7;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #F48FB1;
                font-weight: bold;
            }
            QTextEdit, QLineEdit {
                background: #FFFFFF;
                border: 1px solid #E1BEE7;
                border-radius: 6px;
                padding: 4px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        abas = QTabWidget()
        abas.addTab(ChecklistTab(), "Checklist")
        abas.addTab(NCTab(), "Não Conformidades")
        layout.addWidget(abas)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = AuditoriaApp()
    janela.show()
    sys.exit(app.exec())
