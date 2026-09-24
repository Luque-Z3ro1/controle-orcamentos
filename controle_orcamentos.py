"""
Controle de Orçamentos e Tarefas 

"""

import sys
import sqlite3
from datetime import date

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QMessageBox, QHeaderView, QFrame, QTextEdit, QAbstractItemView,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QCompleter

DB_PATH = "orcamentos.db"

VENDEDORES = ["Exemplo"]
STATUS_OPCOES = ["A fazer", "Em andamento", "Concluído", "Enviado ao cliente"]

# Paleta futurista/minimalista - fundo escuro com acento ciano
COR_FUNDO = "#0f1420"
COR_PAINEL = "#161d2e"
COR_PAINEL_ALT = "#1c2438"
COR_BORDA = "#2a3450"
COR_TEXTO = "#e6ebf5"
COR_TEXTO_SUAVE = "#8792a8"
COR_ACENTO = "#3fd0c9"
COR_ACENTO_HOVER = "#5be0d9"
COR_PERIGO = "#ff6b6b"

STATUS_CORES = {
    "A fazer": "#3a3350",
    "Em andamento": "#4a3f1a",
    "Concluído": "#1a4a35",
    "Enviado ao cliente": "#1a3550",
}
STATUS_TEXTO_CORES = {
    "A fazer": "#c9b8ff",
    "Em andamento": "#f0d060",
    "Concluído": "#5be0a0",
    "Enviado ao cliente": "#6ab8f0",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {COR_FUNDO};
    color: {COR_TEXTO};
    font-family: 'Segoe UI';
    font-size: 13px;
}}

QFrame#cartaoForm {{
    background-color: {COR_PAINEL};
    border-radius: 14px;
    border: 1px solid {COR_BORDA};
}}

QLabel#tituloSecao {{
    font-size: 15px;
    font-weight: 600;
    color: {COR_TEXTO};
    padding-bottom: 4px;
}}

QLabel#rotulo {{
    color: {COR_TEXTO_SUAVE};
    font-size: 12px;
    font-weight: 500;
}}

QLineEdit, QComboBox, QDateEdit, QTextEdit {{
    background-color: {COR_PAINEL_ALT};
    border: 1px solid {COR_BORDA};
    border-radius: 8px;
    padding: 7px 10px;
    color: {COR_TEXTO};
    selection-background-color: {COR_ACENTO};
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border: 1px solid {COR_ACENTO};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {COR_PAINEL_ALT};
    color: {COR_TEXTO};
    selection-background-color: {COR_ACENTO};
    selection-color: #0f1420;
    border: 1px solid {COR_BORDA};
    outline: none;
}}

QDateEdit::drop-down {{
    border: none;
    width: 24px;
}}

QPushButton#botaoPrimario {{
    background-color: {COR_ACENTO};
    color: #0b1220;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
}}
QPushButton#botaoPrimario:hover {{
    background-color: {COR_ACENTO_HOVER};
}}

QPushButton#botaoSecundario {{
    background-color: transparent;
    color: {COR_TEXTO_SUAVE};
    border: 1px solid {COR_BORDA};
    border-radius: 8px;
    padding: 9px 18px;
}}
QPushButton#botaoSecundario:hover {{
    border: 1px solid {COR_ACENTO};
    color: {COR_TEXTO};
}}

QPushButton#botaoPerigo {{
    background-color: transparent;
    color: {COR_PERIGO};
    border: 1px solid #4a2a2a;
    border-radius: 8px;
    padding: 9px 18px;
}}
QPushButton#botaoPerigo:hover {{
    background-color: rgba(255,107,107,0.12);
}}

QTableWidget {{
    background-color: {COR_PAINEL};
    border: 1px solid {COR_BORDA};
    border-radius: 14px;
    gridline-color: {COR_BORDA};
    selection-background-color: rgba(63,208,201,0.18);
    selection-color: {COR_TEXTO};
}}

QHeaderView::section {{
    background-color: {COR_PAINEL};
    color: {COR_TEXTO_SUAVE};
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid {COR_BORDA};
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}}

QTableWidget::item {{
    padding: 6px;
    border-bottom: 1px solid {COR_BORDA};
}}

QScrollBar:vertical {{
    background: {COR_FUNDO};
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {COR_BORDA};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COR_ACENTO};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""


class BancoDados:
    def __init__(self, caminho=DB_PATH):
        self.conn = sqlite3.connect(caminho)
        self.criar_tabela()
        self.migrar_se_necessario()

    def criar_tabela(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS orcamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                vendedor TEXT NOT NULL,
                pfn TEXT NOT NULL,
                cliente TEXT,
                obra TEXT,
                descricao TEXT,
                status TEXT NOT NULL DEFAULT 'A fazer',
                observacoes TEXT
            )
        """)
        self.conn.commit()

    def migrar_se_necessario(self):
        """Migra bancos antigos que tinham a coluna única 'cliente_obra'."""
        colunas = [c[1] for c in self.conn.execute("PRAGMA table_info(orcamentos)").fetchall()]
        if "cliente_obra" in colunas and "cliente" not in colunas:
            self.conn.execute("ALTER TABLE orcamentos ADD COLUMN cliente TEXT")
            self.conn.execute("ALTER TABLE orcamentos ADD COLUMN obra TEXT")
            self.conn.execute("UPDATE orcamentos SET cliente = cliente_obra")
            self.conn.commit()

    def inserir(self, dados):
        self.conn.execute("""
            INSERT INTO orcamentos (data, vendedor, pfn, cliente, obra, descricao, status, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, dados)
        self.conn.commit()

    def atualizar(self, id_registro, dados):
        self.conn.execute("""
            UPDATE orcamentos
            SET data=?, vendedor=?, pfn=?, cliente=?, obra=?, descricao=?, status=?, observacoes=?
            WHERE id=?
        """, dados + (id_registro,))
        self.conn.commit()

    def excluir(self, id_registro):
        self.conn.execute("DELETE FROM orcamentos WHERE id=?", (id_registro,))
        self.conn.commit()

    def listar(self, filtro_vendedor=None, filtro_status=None):
        query = "SELECT id, data, vendedor, pfn, cliente, obra, descricao, status, observacoes FROM orcamentos WHERE 1=1"
        params = []
        if filtro_vendedor and filtro_vendedor != "Todos":
            query += " AND vendedor=?"
            params.append(filtro_vendedor)
        if filtro_status and filtro_status != "Todos":
            query += " AND status=?"
            params.append(filtro_status)
        query += " ORDER BY date(data) DESC, id DESC"
        return self.conn.execute(query, params).fetchall()

    def listar_clientes_distintos(self):
        linhas = self.conn.execute(
            "SELECT DISTINCT cliente FROM orcamentos WHERE cliente IS NOT NULL AND cliente != '' ORDER BY cliente COLLATE NOCASE"
        ).fetchall()
        return [linha[0] for linha in linhas]


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Orçamentos · Novemp")
        self.resize(1200, 700)

        self.db = BancoDados()
        self.id_em_edicao = None

        self._montar_interface()
        self._atualizar_tabela()

    # ---------------------------------------------------------------- UI
    def _montar_interface(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setContentsMargins(24, 24, 24, 24)
        layout_principal.setSpacing(18)

        cabecalho = QLabel("Controle de Orçamentos")
        cabecalho.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {COR_TEXTO};")
        subtitulo = QLabel("Tarefas e orçamentos em andamento · Novemp")
        subtitulo.setStyleSheet(f"color: {COR_TEXTO_SUAVE}; font-size: 12px;")

        cabecalho_layout = QVBoxLayout()
        cabecalho_layout.setSpacing(2)
        cabecalho_layout.addWidget(cabecalho)
        cabecalho_layout.addWidget(subtitulo)

        # --- Cartão do formulário ---
        cartao = QFrame()
        cartao.setObjectName("cartaoForm")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(30)
        sombra.setColor(QColor(0, 0, 0, 120))
        sombra.setOffset(0, 6)
        cartao.setGraphicsEffect(sombra)

        form_wrap = QVBoxLayout(cartao)
        form_wrap.setContentsMargins(22, 20, 22, 20)
        form_wrap.setSpacing(14)

        titulo_form = QLabel("Novo orçamento / tarefa")
        titulo_form.setObjectName("tituloSecao")
        form_wrap.addWidget(titulo_form)

        linha1 = QHBoxLayout()
        linha1.setSpacing(14)
        self.campo_data = QDateEdit(calendarPopup=True)
        self.campo_data.setDate(QDate.currentDate())
        self.campo_data.setDisplayFormat("dd/MM/yyyy")
        self.campo_vendedor = QComboBox()
        self.campo_vendedor.addItems(VENDEDORES)
        self.campo_pfn = QLineEdit()
        self.campo_pfn.setPlaceholderText("Ex: 4521")
        self.campo_status = QComboBox()
        self.campo_status.addItems(STATUS_OPCOES)

        linha1.addLayout(self._campo_com_rotulo("Data", self.campo_data))
        linha1.addLayout(self._campo_com_rotulo("Vendedor", self.campo_vendedor))
        linha1.addLayout(self._campo_com_rotulo("Nº PFN", self.campo_pfn))
        linha1.addLayout(self._campo_com_rotulo("Status", self.campo_status))
        form_wrap.addLayout(linha1)

        linha2 = QHBoxLayout()
        linha2.setSpacing(14)
        self.campo_cliente = QComboBox()
        self.campo_cliente.setEditable(True)
        self.campo_cliente.setInsertPolicy(QComboBox.NoInsert)
        self.campo_cliente.lineEdit().setPlaceholderText("Digite ou escolha um cliente")
        self._popular_clientes()
        self.campo_obra = QLineEdit()
        self.campo_obra.setPlaceholderText("Nome / local da obra")
        self.campo_descricao = QLineEdit()
        self.campo_descricao.setPlaceholderText("Descrição resumida")

        linha2.addLayout(self._campo_com_rotulo("Cliente", self.campo_cliente))
        linha2.addLayout(self._campo_com_rotulo("Obra", self.campo_obra))
        linha2.addLayout(self._campo_com_rotulo("Descrição", self.campo_descricao))
        form_wrap.addLayout(linha2)

        self.campo_obs = QTextEdit()
        self.campo_obs.setPlaceholderText("Observações (opcional)")
        self.campo_obs.setFixedHeight(56)
        form_wrap.addLayout(self._campo_com_rotulo("Observações", self.campo_obs))

        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(10)
        self.botao_salvar = QPushButton("Adicionar")
        self.botao_salvar.setObjectName("botaoPrimario")
        self.botao_salvar.clicked.connect(self._salvar_registro)
        self.botao_cancelar = QPushButton("Cancelar edição")
        self.botao_cancelar.setObjectName("botaoSecundario")
        self.botao_cancelar.clicked.connect(self._cancelar_edicao)
        self.botao_cancelar.setEnabled(False)
        botoes_layout.addWidget(self.botao_salvar)
        botoes_layout.addWidget(self.botao_cancelar)
        botoes_layout.addStretch()
        form_wrap.addLayout(botoes_layout)

        # --- Filtros ---
        filtro_layout = QHBoxLayout()
        filtro_layout.setSpacing(10)
        rotulo_filtro = QLabel("Filtrar:")
        rotulo_filtro.setObjectName("rotulo")
        self.filtro_vendedor = QComboBox()
        self.filtro_vendedor.addItems(["Todos"] + VENDEDORES)
        self.filtro_vendedor.currentTextChanged.connect(self._atualizar_tabela)
        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos"] + STATUS_OPCOES)
        self.filtro_status.currentTextChanged.connect(self._atualizar_tabela)
        filtro_layout.addWidget(rotulo_filtro)
        filtro_layout.addWidget(self.filtro_vendedor)
        filtro_layout.addWidget(self.filtro_status)
        filtro_layout.addStretch()

        # --- Tabela ---
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels(
            ["Data", "Vendedor", "PFN", "Cliente", "Obra", "Descrição", "Status", "Obs."]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(False)
        self.tabela.itemDoubleClicked.connect(self._carregar_para_edicao)

        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(10)
        botao_editar = QPushButton("Editar selecionado  ·  duplo clique também funciona")
        botao_editar.setObjectName("botaoSecundario")
        botao_editar.clicked.connect(self._carregar_para_edicao)
        botao_excluir = QPushButton("Excluir selecionado")
        botao_excluir.setObjectName("botaoPerigo")
        botao_excluir.clicked.connect(self._excluir_registro)
        acoes_layout.addWidget(botao_editar)
        acoes_layout.addWidget(botao_excluir)
        acoes_layout.addStretch()

        layout_principal.addLayout(cabecalho_layout)
        layout_principal.addWidget(cartao)
        layout_principal.addLayout(filtro_layout)
        layout_principal.addWidget(self.tabela)
        layout_principal.addLayout(acoes_layout)

    def _popular_clientes(self):
        """Preenche o combo de clientes com os nomes já usados antes, mantendo o texto digitado."""
        texto_atual = self.campo_cliente.currentText() if self.campo_cliente.count() or self.campo_cliente.currentText() else ""
        self.campo_cliente.blockSignals(True)
        self.campo_cliente.clear()
        clientes = self.db.listar_clientes_distintos()
        self.campo_cliente.addItems(clientes)
        self.campo_cliente.setCurrentText(texto_atual)
        self.campo_cliente.blockSignals(False)

        completer = QCompleter(clientes, self.campo_cliente)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.campo_cliente.setCompleter(completer)

    def _campo_com_rotulo(self, texto, widget):
        layout = QVBoxLayout()
        layout.setSpacing(4)
        rotulo = QLabel(texto)
        rotulo.setObjectName("rotulo")
        layout.addWidget(rotulo)
        layout.addWidget(widget)
        return layout

    # ------------------------------------------------------------ ações
    def _coletar_dados_formulario(self):
        pfn = self.campo_pfn.text().strip()
        if not pfn:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o número da PFN.")
            return None
        return (
            self.campo_data.date().toString("yyyy-MM-dd"),
            self.campo_vendedor.currentText(),
            pfn,
            self.campo_cliente.currentText().strip(),
            self.campo_obra.text().strip(),
            self.campo_descricao.text().strip(),
            self.campo_status.currentText(),
            self.campo_obs.toPlainText().strip(),
        )

    def _salvar_registro(self):
        dados = self._coletar_dados_formulario()
        if dados is None:
            return
        if self.id_em_edicao is None:
            self.db.inserir(dados)
        else:
            self.db.atualizar(self.id_em_edicao, dados)
            self._cancelar_edicao()
        self._limpar_formulario()
        self._popular_clientes()
        self._atualizar_tabela()

    def _limpar_formulario(self):
        self.campo_data.setDate(QDate.currentDate())
        self.campo_vendedor.setCurrentIndex(0)
        self.campo_pfn.clear()
        self.campo_cliente.setCurrentText("")
        self.campo_obra.clear()
        self.campo_descricao.clear()
        self.campo_status.setCurrentIndex(0)
        self.campo_obs.clear()

    def _carregar_para_edicao(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.information(self, "Selecione um registro", "Clique em uma linha da tabela primeiro.")
            return
        id_registro = self.tabela.item(linha, 0).data(Qt.UserRole)
        registro = next((r for r in self.db.listar() if r[0] == id_registro), None)
        if not registro:
            return
        _, data_str, vendedor, pfn, cliente, obra, descricao, status, obs = registro

        self.campo_data.setDate(QDate.fromString(data_str, "yyyy-MM-dd"))
        self.campo_vendedor.setCurrentText(vendedor)
        self.campo_pfn.setText(pfn)
        self.campo_cliente.setCurrentText(cliente or "")
        self.campo_obra.setText(obra or "")
        self.campo_descricao.setText(descricao or "")
        self.campo_status.setCurrentText(status)
        self.campo_obs.setPlainText(obs or "")

        self.id_em_edicao = id_registro
        self.botao_salvar.setText("Salvar edição")
        self.botao_cancelar.setEnabled(True)

    def _cancelar_edicao(self):
        self.id_em_edicao = None
        self.botao_salvar.setText("Adicionar")
        self.botao_cancelar.setEnabled(False)
        self._limpar_formulario()

    def _excluir_registro(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.information(self, "Selecione um registro", "Clique em uma linha da tabela primeiro.")
            return
        id_registro = self.tabela.item(linha, 0).data(Qt.UserRole)
        resposta = QMessageBox.question(
            self, "Confirmar exclusão", "Deseja realmente excluir este registro?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            self.db.excluir(id_registro)
            self._atualizar_tabela()

    def _atualizar_tabela(self):
        registros = self.db.listar(
            filtro_vendedor=self.filtro_vendedor.currentText(),
            filtro_status=self.filtro_status.currentText()
        )
        self.tabela.setRowCount(0)
        self.tabela.setRowHeight(0, 40)
        for linha_idx, (id_reg, data_str, vendedor, pfn, cliente, obra, descricao, status, obs) in enumerate(registros):
            self.tabela.insertRow(linha_idx)
            self.tabela.setRowHeight(linha_idx, 42)
            data_formatada = QDate.fromString(data_str, "yyyy-MM-dd").toString("dd/MM/yyyy")
            valores = [data_formatada, vendedor, pfn, cliente or "", obra or "", descricao or "", status, obs or ""]
            for col_idx, valor in enumerate(valores):
                item = QTableWidgetItem(valor)
                if col_idx == 0:
                    item.setData(Qt.UserRole, id_reg)
                if col_idx == 6:
                    item.setForeground(QColor(STATUS_TEXTO_CORES.get(status, COR_TEXTO)))
                    fonte = QFont()
                    fonte.setBold(True)
                    item.setFont(fonte)
                self.tabela.setItem(linha_idx, col_idx, item)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
