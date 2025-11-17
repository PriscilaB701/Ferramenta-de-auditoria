import sys
import smtplib
from email.mime.text import MIMEText
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QRadioButton, QGridLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QButtonGroup, QComboBox, QScrollArea, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal

# ============================================
#           THREAD PARA ENVIO DE EMAIL
# ============================================
class EmailThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, remetente, senha, destinatario, assunto, mensagem):
        super().__init__()
        self.remetente = remetente
        self.senha = senha
        self.destinatario = destinatario
        self.assunto = assunto
        self.mensagem = mensagem

    def run(self):
        try:
            msg = MIMEText(self.mensagem, "plain", "utf-8")
            msg["Subject"] = self.assunto
            msg["From"] = self.remetente
            msg["To"] = self.destinatario

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
                servidor.login(self.remetente, self.senha)
                servidor.send_message(msg)

            self.finished.emit(True, "E-mail enviado com sucesso!")

        except Exception as e:
            self.finished.emit(False, f"Erro ao enviar e-mail: {e}")

# ============================================
#                CHECKLIST
# ============================================
class ChecklistTab(QWidget):
    def __init__(self):
        super().__init__()
        self.perguntas = [
            "Os critérios de qualidade obrigatórios para a avaliação e seleção de potenciais fornecedores (ex: certificações, histórico de não conformidades, capacidade técnica) estão claramente identificados e documentados?",
            "Os requisitos de qualidade (especificações técnicas e normas aplicáveis) foram comunicados integralmente aos fornecedores nos pedidos de proposta?",
            "As respostas e propostas dos fornecedores foram avaliadas de acordo com os critérios de qualidade e técnicos previamente estabelecidos, e os desvios foram justificados e aprovados?",
            "O orçamento previsto e o custo estimado da aquisição foram analisados, e o impacto potencial nos custos de não-qualidade (falhas, retrabalho) foi considerado?",
            "O cronograma do processo de aquisição está claramente definido, incluindo datas e responsáveis para as verificações e validações de qualidade?",
            "O contrato ou pedido de compra inclui cláusulas específicas sobre os padrões de qualidade, requisitos de inspeção e critérios de aceitação do produto/serviço?",
            "Existe um plano de verificação e validação (V&V) definido para as entregas, que compare o produto ou serviço do fornecedor com os requisitos acordados?",
            "As atividades críticas do fornecedor estão sendo monitoradas e inspecionadas em campo (quando aplicável) conforme o acordo estabelecido (Ex: auditorias programadas)?",
            "O desempenho do fornecedor é documentado, e os dados de qualidade são revisados tecnicamente pela equipe adquirente (ex: Engenharia, Qualidade) em intervalos definidos?",
            "Existem medidas quantitativas (KPIs) para avaliar o desempenho dos fornecedores, e estes indicadores estão alinhados com as metas de qualidade da organização?",
            "O processo de aquisição prevê a rastreabilidade do produto ou serviço adquirido (ex: lotes, números de série, registros de teste)?",
            "O plano de aquisição considerou e mitigou os riscos relacionados à dependência de fornecedor único ou à capacidade do fornecedor de atender a requisitos regulamentares?",
            "Há um plano de contingência ou estratégias de fornecimento alternativas caso o fornecedor falhe criticamente no cumprimento dos requisitos de qualidade?",
            "Os registros e evidências de todo o processo de aquisição (avaliação, seleção, pedidos, inspeções e aceitação) estão arquivados e acessíveis para fins de auditoria?",
            "Existe um procedimento claro para o tratamento de não conformidades identificadas nas entregas do fornecedor, incluindo a comunicação e a implementação de ações corretivas?"
            
        ]

        self.button_groups = []
        self.init_ui()

    def init_ui(self):
        layout_externo = QVBoxLayout()
        layout_externo.setContentsMargins(20, 20, 20, 20)
        layout_externo.setSpacing(15)

        titulo = QLabel("Checklist de Auditoria de Qualidade - Plano de Aquisição")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout_externo.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignCenter)

       
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget_container = QWidget()
        layout_container = QVBoxLayout()
        layout_container.setSpacing(15)

        self.respostas = []

        for i, pergunta in enumerate(self.perguntas):
            h_layout = QHBoxLayout()
            h_layout.setSpacing(15)

            #perguntas
            label = QLabel(f"{i + 1}. {pergunta}")
            label.setWordWrap(True)
            label.setFont(QFont("Segoe UI", 11))
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

            #botoes
            rb_sim = QRadioButton("Sim")
            rb_nao = QRadioButton("Não")
            rb_na = QRadioButton("N/A")
            for rb in [rb_sim, rb_nao, rb_na]:
                rb.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            grupo = QButtonGroup(self)
            grupo.addButton(rb_sim)
            grupo.addButton(rb_nao)
            grupo.addButton(rb_na)

            self.button_groups.append(grupo)
            self.respostas.append((grupo, rb_sim, rb_nao, rb_na))

            h_layout.addWidget(label)
            h_layout.addWidget(rb_sim)
            h_layout.addWidget(rb_nao)
            h_layout.addWidget(rb_na)
            layout_container.addLayout(h_layout)

        widget_container.setLayout(layout_container)
        scroll.setWidget(widget_container)
        layout_externo.addWidget(scroll)

        #btn calcular
        layout_externo.addSpacing(10)
        self.btn_calcular = QPushButton("Calcular Aderência")
        self.btn_calcular.clicked.connect(self.calcular)
        layout_externo.addWidget(self.btn_calcular, alignment=Qt.AlignmentFlag.AlignCenter)

        #resultado 
        self.resultado = QLabel("")
        self.resultado.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout_externo.addWidget(self.resultado, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout_externo)

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

    def get_itens_nao_conformidade(self):
        itens = []
        for i, (grupo, rb_sim, rb_nao, rb_na) in enumerate(self.respostas):
            if rb_nao.isChecked():
                itens.append(f"{i + 1}. {self.perguntas[i]}")
        return itens


# ============================================
#                TELA DE NC
# ============================================
class NCTab(QWidget):
    def __init__(self, checklist: ChecklistTab):
        super().__init__()
        self.checklist = checklist
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Registro e Acompanhamento de Não Conformidades")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(titulo)

        #item do checklist
        self.label_item = QLabel("Item do Checklist relacionado:")
        self.combo_item = QComboBox()
        self.combo_item.addItem("Nenhum item marcado como 'Não' ainda")
        self.combo_item.setEnabled(False)
        layout.addWidget(self.label_item)
        layout.addWidget(self.combo_item)

        self.label_desc = QLabel("Descrição da NC:")
        self.input_desc = QTextEdit()
        layout.addWidget(self.label_desc)
        layout.addWidget(self.input_desc)

        #responsavel
        self.label_resp = QLabel("Responsável (E-mail):")
        self.input_resp = QLineEdit()
        layout.addWidget(self.label_resp)
        layout.addWidget(self.input_resp)

        #gravidade
        self.label_grav = QLabel("Gravidade:")
        self.input_grav = QComboBox()
        self.input_grav.addItems(["Selecione...", "Grave", "Média", "Leve"])
        layout.addWidget(self.label_grav)
        layout.addWidget(self.input_grav)

        #prazo
        self.label_prazo = QLabel("Prazo (automático):")
        self.input_prazo = QLineEdit()
        self.input_prazo.setReadOnly(True)
        layout.addWidget(self.label_prazo)
        layout.addWidget(self.input_prazo)

        self.input_grav.currentTextChanged.connect(self.definir_prazo)

        #btns registrar e limpar
        self.btn_registrar = QPushButton("Registrar NC")
        self.btn_limpar = QPushButton("Limpar")

        self.btn_registrar.clicked.connect(self.registrar_nc)
        self.btn_limpar.clicked.connect(self.limpar_tudo)

        botoes = QHBoxLayout()
        botoes.setSpacing(20)
        botoes.setContentsMargins(0, 15, 0, 15)
        botoes.addWidget(self.btn_registrar)
        botoes.addWidget(self.btn_limpar)
        layout.addLayout(botoes)

        #tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Item Checklist", "Descrição", "Responsável", "Gravidade", "Prazo", "Status"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # type: ignore
        layout.addWidget(self.tabela)

        self.setLayout(layout)

    #att itens marcados como nao no checklist
    def atualizar_itens_nao(self):
        itens_nao = self.checklist.get_itens_nao_conformidade()
        self.combo_item.clear()

        if not itens_nao:
            self.combo_item.addItem("Nenhum item marcado como 'Não' no checklist")
            self.combo_item.setEnabled(False)
        else:
            self.combo_item.addItem("Selecione o item do checklist...")
            for item in itens_nao:
                self.combo_item.addItem(item)
            self.combo_item.setEnabled(True)

    #prazo automatico conforme a gravidade
    def definir_prazo(self):
        gravidade = self.input_grav.currentText()
        if gravidade == "Grave":
            dias = 1
        elif gravidade == "Média":
            dias = 4
        elif gravidade == "Leve":
            dias = 5
        else:
            self.input_prazo.clear()
            return
        data = QDate.currentDate().addDays(dias).toString("dd/MM/yyyy")
        self.input_prazo.setText(f"{dias} dias (até {data})")

   
    def email_finalizado(self, sucesso, mensagem):
        if sucesso:
            QMessageBox.information(self, "E-mail", mensagem)
        else:
            QMessageBox.critical(self, "Erro no e-mail", mensagem)

    #regitro nc
    def registrar_nc(self):
        if not self.combo_item.isEnabled():
            QMessageBox.warning(self, "Sem NC possível",
                                "Nenhum item foi marcado como 'Não' no checklist.")
            return
        idx_item = self.combo_item.currentIndex()
        if idx_item <= 0:
            QMessageBox.warning(self, "Campos obrigatórios",
                                "Selecione o item do checklist relacionado à NC.")
            return

        item_checklist = self.combo_item.currentText()
        desc = self.input_desc.toPlainText().strip()
        resp = self.input_resp.text().strip()
        grav = self.input_grav.currentText()
        prazo = self.input_prazo.text().strip()

        if not all([desc, resp, grav != "Selecione...", prazo]):
            QMessageBox.warning(self, "Campos obrigatórios",
                                "Preencha todos os campos corretamente.")
            return

        #add na tabela
        linha = self.tabela.rowCount()
        self.tabela.insertRow(linha)

        itens = [
            QTableWidgetItem(item_checklist),
            QTableWidgetItem(desc),
            QTableWidgetItem(resp),
            QTableWidgetItem(grav),
            QTableWidgetItem(prazo)
        ]
        for col, item in enumerate(itens):
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(linha, col, item)

      
        status_combo = QComboBox()
        status_combo.addItems(["Pendente", "Em andamento", "Concluída"])
        self.tabela.setCellWidget(linha, 5, status_combo)

        remetente = "" #configuraçao email
        senha = ""
        assunto = f"Nova Não Conformidade - {grav}"
        mensagem = f"Item: {item_checklist}\nDescrição: {desc}\nGravidade: {grav}\nPrazo: {prazo}"

        self.thread = EmailThread(remetente, senha, resp, assunto, mensagem)  # type: ignore
        self.thread.finished.connect(self.email_finalizado)  # type: ignore
        self.thread.start()  # type: ignore

        self.limpar_campos()

    def limpar_campos(self):
        self.input_desc.clear()
        self.input_resp.clear()
        self.input_grav.setCurrentIndex(0)
        self.input_prazo.clear()
        if self.combo_item.isEnabled():
            self.combo_item.setCurrentIndex(0)

    def limpar_tudo(self):
        self.limpar_campos()
        
# ============================================
#              JANELA GRAVIDADES
# ============================================
class GravidadesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo = QLabel("Descrição das Gravidades de NC")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(titulo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)

        descricoes = {
            "Grave": "Impacto crítico na operação ou qualidade do produto/serviço, requer ação imediata (1 dia) para evitar consequências significativas.",
            "Média": "Impacto moderado que pode afetar parcialmente processos ou resultados, requer ação em até 4 dias.",
            "Leve": "Impacto pequeno, geralmente de natureza documental ou processual, requer ação em até 5 dias."
        }

        for nivel, descricao in descricoes.items():
            lbl_nivel = QLabel(f"<b>{nivel}:</b> {descricao}")
            lbl_nivel.setWordWrap(True)
            lbl_nivel.setFont(QFont("Segoe UI", 11))
            lbl_nivel.setAlignment(Qt.AlignmentFlag.AlignCenter) 
            layout.addWidget(lbl_nivel)
            layout.addSpacing(5)

        layout.addStretch()
        self.setLayout(layout)


# ============================================
#              JANELA PRINCIPAL
# ============================================
class AuditoriaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Auditoria de Qualidade")
        self.setMinimumSize(1090, 730)
        self.config_tema()
        self.init_ui()

    def config_tema(self):
        self.setStyleSheet("""
            QWidget {
    background-color: #F5F5F5;
    color: #212121;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 11pt;
}

QPushButton {
    background-color: #E0E0E0;  
    color: #212121;             
    border: 1px solid #BDBDBD;  
    border-radius: 4px;         
    padding: 8px 14px;
    font-weight: bold;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #BDBDBD;  
}

QPushButton:pressed {
    background-color: #9E9E9E;  
}


QRadioButton {
    spacing: 10px;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 1px solid #424242;
    background-color: #FFFFFF;
}

QRadioButton::indicator:checked {
    background-color: #B0BEC5;   
    border: 1px solid #424242;
}


QTabWidget::pane {
    border: 1px solid #BDBDBD;
    border-radius: 8px;
    background: #FFFFFF;
}

QTabBar::tab {
    background: #E0E0E0;
    border: 1px solid #BDBDBD;
    border-radius: 4px;       
    padding: 6px 12px;
    margin: 2px;
}

QTabBar::tab:selected {
    background: #BDBDBD;
    font-weight: bold;
}

QTextEdit, QLineEdit, QComboBox {
    background: #FFFFFF;
    border: 1px solid #BDBDBD;
    border-radius: 6px;
    padding: 4px;
}

        """)

    def init_ui(self):
        layout = QVBoxLayout()
        abas = QTabWidget()

        checklist_tab = ChecklistTab()
        nc_tab = NCTab(checklist_tab)
        gravidades_tab = GravidadesTab()

        abas.addTab(checklist_tab, "Checklist")
        abas.addTab(nc_tab, "Não Conformidades")
        abas.addTab(gravidades_tab, "Gravidades")


        def on_tab_changed(index):
            widget = abas.widget(index)
            if widget is nc_tab:
                nc_tab.atualizar_itens_nao()

        abas.currentChanged.connect(on_tab_changed)
        layout.addWidget(abas)
        self.setLayout(layout)

# ============================================
#               EXECUÇÃO
# ============================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = AuditoriaApp()
    janela.show()
    sys.exit(app.exec())

