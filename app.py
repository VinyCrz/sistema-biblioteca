"""Interface gráfica (Tkinter) do Sistema de Biblioteca - Desk App III.

A janela tem uma BARRA DE MENU que dá acesso a todos os modelos
(Livro, Revista, DVD, Aluno, Professor, Carteirinha, Empréstimo e
Exportadores) e a todas as funcionalidades. Desde o Desk App III, todas as
alterações são gravadas num banco de dados SQLite (arquivo biblioteca.db).

Execute com:  python3 app.py               (usa biblioteca.db na pasta do projeto)
         ou:  python3 app.py outro.db      (usa outro arquivo de banco)
"""

import os
import sys
import tkinter as tk
from datetime import date, datetime
from tkinter import filedialog, messagebox, ttk

from biblioteca import (
    DVD, Aluno, Biblioteca, BibliotecaError, BibliotecaPersistente, ExportadorCSV,
    ExportadorTexto, Livro, Professor, RepositorioSQLite, Revista,
)
from dialogos import FormularioDialog, JanelaLista, JanelaTexto

FMT_DATA = "%d/%m/%Y"
NOME_BIBLIOTECA = "Biblioteca Desk App III"
BANCO_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca.db")


def ler_data(texto):
    """Converte 'dd/mm/aaaa' em date. Texto vazio = hoje."""
    texto = (texto or "").strip()
    if not texto:
        return date.today()
    try:
        return datetime.strptime(texto, FMT_DATA).date()
    except ValueError:
        raise BibliotecaError("Data inválida. Use o formato dd/mm/aaaa.") from None


def dados_exemplo(bib=None):
    """Preenche a biblioteca com os dados da demonstração (cria uma em memória se não vier)."""
    bib = bib if bib is not None else Biblioteca(NOME_BIBLIOTECA)
    bib.cadastrar_item(Livro("L1", "Dom Casmurro", 1899, "Machado de Assis"))
    bib.cadastrar_item(Livro("L2", "Clean Code", 2008, "Robert C. Martin"))
    bib.cadastrar_item(Revista("R1", "Superinteressante", 2024, 450))
    bib.cadastrar_item(DVD("D1", "Cidade de Deus", 2002, 130))
    bib.cadastrar_membro(Aluno("Ana Souza", "123.456.789-00", "A001", "Sistemas de Informação"))
    bib.cadastrar_membro(Professor("Carlos Lima", "987.654.321-00", "P001", "Computação"))
    return bib


def abrir_banco(caminho=BANCO_PADRAO):
    """Abre (ou cria) o banco. Na primeira vez, grava os dados de exemplo."""
    repo = RepositorioSQLite(caminho)
    bib = BibliotecaPersistente(NOME_BIBLIOTECA, repo)
    if repo.vazio():
        dados_exemplo(bib)
    return bib


# Campo extra de cada tipo de item: (rótulo, classe)
TIPOS_ITEM = {
    "Livro": ("Autor", Livro),
    "Revista": ("Edição", Revista),
    "DVD": ("Duração (min)", DVD),
}
TIPOS_MEMBRO = {
    "Aluno": ("Curso", Aluno),
    "Professor": ("Departamento", Professor),
}

ABAS = ("Acervo", "Membros", "Empréstimos", "Relatório")

TEXTO_REGRAS = """REGRAS DE NEGÓCIO

Prazos e multas por tipo de item
  Livro .......... 14 dias  | R$ 1,00 por dia de atraso
  Revista ........  7 dias  | R$ 0,50 por dia de atraso
  DVD ............  3 dias  | R$ 2,00 por dia de atraso

Membros
  Aluno .......... até 3 empréstimos ao mesmo tempo
  Professor ...... até 10 empréstimos e 50% de desconto na multa

Multa = dias de atraso x multa diária do item x (1 - desconto do membro)

Carteirinha
  Criada junto com o membro (CART-0001, CART-0002...), vale 365 dias.
  Vencida, não permite novos empréstimos. Pode ser renovada pelo menu
  Cadastros > Membros > Renovar carteirinha.

Bloqueios
  - emprestar item já emprestado ou passar do limite do membro;
  - cadastrar código ou matrícula repetidos;
  - remover item emprestado ou membro com empréstimo ativo;
  - devolver duas vezes ou com data anterior ao empréstimo.
"""

TEXTO_ATALHOS = """ATALHOS DE TECLADO

  Ctrl+L ........ Novo livro
  Ctrl+M ........ Novo membro (aluno)
  Ctrl+E ........ Emprestar item
  Ctrl+D ........ Devolver item
  Ctrl+F ........ Pesquisar no acervo
  Ctrl+R ........ Gerar relatório em texto
  Ctrl+S ........ Salvar relatório em arquivo
  Ctrl+1 a 4 .... Ir para as abas Acervo, Membros, Empréstimos e Relatório
  F1 ............ Regras de negócio
  Ctrl+Q ........ Sair

Nas janelas: Enter confirma e Esc fecha.
"""

TEXTO_SOBRE = """SISTEMA DE BIBLIOTECA

Projeto acadêmico de Programação Orientada a Objetos
Disciplinas: Desk App I, II e III
Autor: Vinicius

Python 3 + Tkinter + SQLite. Desde o Desk App III, cada cadastro,
edição, remoção, empréstimo e devolução é gravado na hora no banco
de dados (arquivo biblioteca.db). Ao abrir o programa de novo,
tudo volta como estava.

Relações demonstradas: Herança, Polimorfismo, Composição,
Agregação, Associação e Dependência.
"""


class App(tk.Tk):
    def __init__(self, biblioteca=None, caminho_banco=BANCO_PADRAO):
        super().__init__()
        self.bib = biblioteca if biblioteca is not None else abrir_banco(caminho_banco)
        self.geometry("1150x640")
        self.ultima_janela = None  # última janela aberta pelo menu (usada nos testes)

        self._criar_menu()
        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=8, pady=(8, 0))
        self._criar_aba_acervo()
        self._criar_aba_membros()
        self._criar_aba_emprestimos()
        self._criar_aba_relatorio()

        self.var_status = tk.StringVar()
        ttk.Label(self, textvariable=self.var_status, relief="sunken",
                  anchor="w", padding=(6, 2)).pack(fill="x", side="bottom")
        self._criar_atalhos()
        self.protocol("WM_DELETE_WINDOW", self.sair)
        self.atualizar_tudo()

    # ================================================================ MENU
    def _criar_menu(self):
        barra = tk.Menu(self, tearoff=False)
        self.menus = {}

        def novo_menu(nome, pai=barra):
            menu = tk.Menu(pai, tearoff=False)
            pai.add_cascade(label=nome, menu=menu)
            self.menus[nome] = menu
            return menu

        # ---- Arquivo
        m = novo_menu("Arquivo")
        m.add_command(label="Nova biblioteca (vazia)", command=self.nova_biblioteca)
        m.add_command(label="Carregar dados de exemplo", command=self.carregar_exemplo)
        m.add_separator()
        m.add_command(label="Ver banco de dados", command=self.ver_banco)
        m.add_separator()
        m.add_command(label="Sair", accelerator="Ctrl+Q", command=self.sair)

        # ---- Cadastros (todos os modelos)
        m = novo_menu("Cadastros")
        acervo = novo_menu("Acervo", m)
        for tipo, atalho in (("Livro", "Ctrl+L"), ("Revista", ""), ("DVD", "")):
            artigo = "Nova" if tipo == "Revista" else "Novo"
            acervo.add_command(label=f"{artigo} {tipo}...", accelerator=atalho,
                               command=lambda t=tipo: self.abrir_novo_item(t))
        acervo.add_separator()
        acervo.add_command(label="Editar item...", command=self.abrir_editar_item)
        acervo.add_command(label="Remover item...", command=self.abrir_remover_item)

        membros = novo_menu("Membros", m)
        membros.add_command(label="Novo Aluno...", accelerator="Ctrl+M",
                            command=lambda: self.abrir_novo_membro("Aluno"))
        membros.add_command(label="Novo Professor...",
                            command=lambda: self.abrir_novo_membro("Professor"))
        membros.add_separator()
        membros.add_command(label="Editar membro...", command=self.abrir_editar_membro)
        membros.add_command(label="Remover membro...", command=self.abrir_remover_membro)
        membros.add_separator()
        membros.add_command(label="Renovar carteirinha...", command=self.abrir_renovar_carteirinha)

        # ---- Movimentação
        m = novo_menu("Movimentação")
        m.add_command(label="Emprestar item...", accelerator="Ctrl+E", command=self.abrir_emprestar)
        m.add_command(label="Devolver item...", accelerator="Ctrl+D", command=self.abrir_devolver)

        # ---- Consultas
        m = novo_menu("Consultas")
        m.add_command(label="Acervo completo", command=lambda: self.consultar_acervo("todos"))
        m.add_command(label="Itens disponíveis", command=lambda: self.consultar_acervo("disponiveis"))
        m.add_command(label="Itens emprestados", command=lambda: self.consultar_acervo("emprestados"))
        m.add_command(label="Pesquisar no acervo...", accelerator="Ctrl+F", command=self.abrir_pesquisa)
        m.add_separator()
        m.add_command(label="Membros", command=self.consultar_membros)
        m.add_command(label="Carteirinhas", command=self.consultar_carteirinhas)
        m.add_separator()
        m.add_command(label="Empréstimos ativos", command=lambda: self.consultar_emprestimos("ativos"))
        m.add_command(label="Empréstimos atrasados", command=lambda: self.consultar_emprestimos("atrasados"))
        m.add_command(label="Histórico de empréstimos", command=lambda: self.consultar_emprestimos("todos"))
        m.add_command(label="Empréstimos de um membro...", command=self.abrir_historico_membro)

        # ---- Relatórios
        m = novo_menu("Relatórios")
        m.add_command(label="Relatório em Texto", accelerator="Ctrl+R",
                      command=lambda: self.relatorio_pelo_menu("Texto"))
        m.add_command(label="Relatório em CSV", command=lambda: self.relatorio_pelo_menu("CSV"))
        m.add_command(label="Salvar relatório...", accelerator="Ctrl+S", command=self.salvar_relatorio)
        m.add_separator()
        m.add_command(label="Resumo geral", command=self.mostrar_resumo)

        # ---- Exibir
        m = novo_menu("Exibir")
        for i, nome in enumerate(ABAS):
            m.add_command(label=nome, accelerator=f"Ctrl+{i + 1}",
                          command=lambda i=i: self.ir_para_aba(i))

        # ---- Ajuda
        m = novo_menu("Ajuda")
        m.add_command(label="Regras de negócio", accelerator="F1",
                      command=lambda: self._texto("Regras de negócio", TEXTO_REGRAS))
        m.add_command(label="Atalhos de teclado",
                      command=lambda: self._texto("Atalhos de teclado", TEXTO_ATALHOS))
        m.add_separator()
        m.add_command(label="Sobre", command=lambda: self._texto("Sobre", TEXTO_SOBRE))

        self.config(menu=barra)
        self.barra_menu = barra

    def _criar_atalhos(self):
        atalhos = {
            "<Control-l>": lambda: self.abrir_novo_item("Livro"),
            "<Control-m>": lambda: self.abrir_novo_membro("Aluno"),
            "<Control-e>": self.abrir_emprestar,
            "<Control-d>": self.abrir_devolver,
            "<Control-f>": self.abrir_pesquisa,
            "<Control-r>": lambda: self.relatorio_pelo_menu("Texto"),
            "<Control-s>": self.salvar_relatorio,
            "<Control-q>": self.sair,
            "<F1>": lambda: self._texto("Regras de negócio", TEXTO_REGRAS),
        }
        for i in range(len(ABAS)):
            atalhos[f"<Control-Key-{i + 1}>"] = lambda i=i: self.ir_para_aba(i)
        for tecla, acao in atalhos.items():
            self.bind(tecla, lambda e, a=acao: (a(), "break")[1])

    # ============================================================ utilidades
    def mostrar_erro(self, msg):
        messagebox.showerror("Erro", msg, parent=self)

    def mostrar_info(self, msg):
        messagebox.showinfo("Sucesso", msg, parent=self)

    def confirmar(self, msg):
        return messagebox.askyesno("Confirmar", msg, parent=self)

    def _executar(self, acao, msg_ok):
        """Executa uma ação tratando os erros de regra de negócio."""
        try:
            resultado = acao()
        except (BibliotecaError, ValueError) as erro:
            self.mostrar_erro(str(erro))
            return False
        texto = msg_ok(resultado) if callable(msg_ok) else msg_ok
        self.mostrar_info(texto)
        self.atualizar_tudo()
        return True

    def _abrir(self, janela):
        self.ultima_janela = janela
        return janela

    def _texto(self, titulo, texto):
        return self._abrir(JanelaTexto(self, titulo, texto))

    def _lista(self, titulo, colunas, larguras, linhas, rodape=""):
        return self._abrir(JanelaLista(self, titulo, colunas, larguras, linhas, rodape))

    def _formulario(self, titulo, campos, ao_confirmar, **opcoes):
        return self._abrir(FormularioDialog(self, titulo, campos, ao_confirmar, **opcoes))

    @staticmethod
    def _tabela(pai, colunas, larguras):
        tree = ttk.Treeview(pai, columns=colunas, show="headings", height=14)
        for col, larg in zip(colunas, larguras):
            tree.heading(col, text=col)
            tree.column(col, width=larg, anchor="w")
        tree.pack(fill="both", expand=True, pady=(8, 0))
        return tree

    @staticmethod
    def _limpar(tree):
        tree.delete(*tree.get_children())

    def _campo(self, pai, linha, rotulo, coluna=0, largura=25):
        lbl = ttk.Label(pai, text=rotulo)
        lbl.grid(row=linha, column=coluna, sticky="w", padx=4, pady=2)
        ent = ttk.Entry(pai, width=largura)
        ent.grid(row=linha, column=coluna + 1, sticky="w", padx=4, pady=2)
        return lbl, ent

    @staticmethod
    def _codigo(texto):
        """'L1 - Dom Casmurro' -> 'L1'."""
        return (texto or "").split(" - ")[0].strip()

    @staticmethod
    def _opcoes_itens(itens):
        return [f"{i.codigo} - {i.titulo}" for i in itens]

    @staticmethod
    def _opcoes_membros(membros):
        return [f"{m.matricula} - {m.nome}" for m in membros]

    @staticmethod
    def _selecionado(tree):
        sel = tree.selection()
        return sel[0] if sel else None

    def _escolhido(self, opcoes, tree):
        """Opção inicial de um combo: o selecionado na tabela ou o primeiro."""
        sel = self._selecionado(tree)
        for op in opcoes:
            if self._codigo(op) == sel:
                return op
        return opcoes[0] if opcoes else ""

    # ---- linhas das tabelas (usadas nas abas e nas consultas)
    @staticmethod
    def _linha_item(item):
        return (item.codigo, item.tipo(), item.descricao(), f"{item.prazo_dias()} dias",
                f"R$ {item.multa_diaria():.2f}",
                "Disponível" if item.disponivel else "Emprestado")

    def _linha_membro(self, m):
        ativos = len(self.bib.emprestimos_do_membro(m.matricula))
        return (m.matricula, m.tipo(), m.nome, m.carteirinha.numero,
                f"{m.carteirinha.validade:%d/%m/%Y}", f"{ativos}/{m.limite_emprestimos()}")

    @staticmethod
    def _linha_emprestimo(e, hoje):
        if not e.ativo:
            situacao = f"Devolvido (R$ {e.multa:.2f})"
        elif e.atrasado_em(hoje):
            situacao = "ATRASADO"
        else:
            situacao = "Ativo"
        devolucao = f"{e.data_devolucao:%d/%m/%Y}" if e.data_devolucao else "-"
        return (e.item.descricao(), str(e.membro), f"{e.data_emprestimo:%d/%m/%Y}",
                f"{e.data_prevista:%d/%m/%Y}", devolucao, situacao)

    COLS_ITEM = (("Código", "Tipo", "Descrição", "Prazo", "Multa/dia", "Situação"),
                 (80, 90, 520, 80, 90, 120))
    COLS_MEMBRO = (("Matrícula", "Tipo", "Nome", "Carteirinha", "Validade", "Empréstimos"),
                   (90, 90, 360, 120, 110, 110))
    COLS_EMPRESTIMO = (("Item", "Membro", "Empréstimo", "Previsto", "Devolução", "Situação"),
                       (300, 260, 110, 110, 110, 150))

    # ============================================================ ARQUIVO
    @property
    def repo(self):
        """Repositório do banco, ou None quando a biblioteca está só em memória."""
        return getattr(self.bib, "repositorio", None)

    def _biblioteca_vazia(self):
        if self.repo is None:
            return Biblioteca(NOME_BIBLIOTECA)
        self.repo.limpar()
        return BibliotecaPersistente(NOME_BIBLIOTECA, self.repo)

    def nova_biblioteca(self):
        if not self.confirmar("Apagar TODOS os dados e começar uma biblioteca vazia?"):
            return False
        self.bib = self._biblioteca_vazia()
        self.atualizar_tudo()
        return True

    def carregar_exemplo(self):
        if not self.confirmar("Apagar os dados atuais e carregar os dados de exemplo?"):
            return False
        self.bib = dados_exemplo(self._biblioteca_vazia())
        self.atualizar_tudo()
        return True

    def ver_banco(self):
        if self.repo is None:
            self.mostrar_erro("Esta biblioteca está só em memória, sem banco de dados.")
            return None
        return self._texto("Banco de dados", self.repo.descrever())

    def sair(self):
        if not self.confirmar("Deseja sair do sistema?"):
            return False
        repo = self.repo
        self.destroy()
        if repo is not None:
            repo.fechar()  # os dados já foram gravados a cada operação
        return True

    # ============================================================ ACERVO (aba)
    def _criar_aba_acervo(self):
        aba = ttk.Frame(self.abas, padding=8)
        self.abas.add(aba, text="Acervo")
        form = ttk.LabelFrame(aba, text="Novo item", padding=8)
        form.pack(fill="x")

        ttk.Label(form, text="Tipo").grid(row=0, column=0, sticky="w", padx=4)
        self.tipo_item = ttk.Combobox(form, values=list(TIPOS_ITEM), state="readonly", width=22)
        self.tipo_item.current(0)
        self.tipo_item.grid(row=0, column=1, sticky="w", padx=4)
        self.tipo_item.bind("<<ComboboxSelected>>", lambda e: self._mudar_tipo_item())

        _, self.ent_codigo = self._campo(form, 1, "Código")
        _, self.ent_titulo = self._campo(form, 2, "Título")
        _, self.ent_ano = self._campo(form, 1, "Ano", coluna=2)
        self.lbl_extra_item, self.ent_extra_item = self._campo(form, 2, "Autor", coluna=2)

        botoes = ttk.Frame(form)
        botoes.grid(row=0, column=4, rowspan=3, padx=16)
        ttk.Button(botoes, text="Cadastrar", command=self.cadastrar_item).pack(fill="x", pady=2)
        ttk.Button(botoes, text="Editar selecionado", command=self.abrir_editar_item).pack(fill="x", pady=2)
        ttk.Button(botoes, text="Remover selecionado", command=self.remover_item).pack(fill="x", pady=2)

        busca = ttk.Frame(aba)
        busca.pack(fill="x", pady=(8, 0))
        ttk.Label(busca, text="Pesquisar:").pack(side="left")
        self.var_pesquisa = tk.StringVar()
        self.var_pesquisa.trace_add("write", lambda *a: self.atualizar_acervo())
        ttk.Entry(busca, textvariable=self.var_pesquisa, width=40).pack(side="left", padx=4)

        self.tree_itens = self._tabela(aba, *self.COLS_ITEM)
        self.tree_itens.bind("<Double-1>", lambda e: self.abrir_editar_item())

    def _mudar_tipo_item(self):
        self.lbl_extra_item.config(text=TIPOS_ITEM[self.tipo_item.get()][0])

    def cadastrar_item(self):
        def acao():
            classe = TIPOS_ITEM[self.tipo_item.get()][1]
            item = classe(self.ent_codigo.get(), self.ent_titulo.get(),
                          self.ent_ano.get(), self.ent_extra_item.get())
            self.bib.cadastrar_item(item)
            for ent in (self.ent_codigo, self.ent_titulo, self.ent_ano, self.ent_extra_item):
                ent.delete(0, "end")
            return item
        return self._executar(acao, lambda item: f"{item.tipo()} cadastrado: {item.titulo}")

    def remover_item(self):
        codigo = self._selecionado(self.tree_itens)
        if not codigo:
            self.mostrar_erro("Selecione um item na tabela.")
            return False
        return self._executar(lambda: self.bib.remover_item(codigo),
                              lambda item: f"Item removido: {item.titulo}")

    def atualizar_acervo(self):
        self._limpar(self.tree_itens)
        texto = self.var_pesquisa.get()
        itens = self.bib.pesquisar(texto) if texto.strip() else self.bib.itens
        for item in itens:
            self.tree_itens.insert("", "end", iid=item.codigo, values=self._linha_item(item))

    # ---- acervo pelo menu
    def abrir_novo_item(self, tipo):
        rotulo, classe = TIPOS_ITEM[tipo]

        def salvar(v):
            def acao():
                item = classe(v["codigo"], v["titulo"], v["ano"], v["extra"])
                self.bib.cadastrar_item(item)
                return item
            return self._executar(acao, lambda item: f"{item.tipo()} cadastrado: {item.titulo}")

        campos = [
            {"chave": "codigo", "rotulo": "Código"},
            {"chave": "titulo", "rotulo": "Título"},
            {"chave": "ano", "rotulo": "Ano"},
            {"chave": "extra", "rotulo": rotulo},
        ]
        return self._formulario(f"Cadastrar {tipo}", campos, salvar, texto_botao="Cadastrar")

    def abrir_editar_item(self):
        opcoes = self._opcoes_itens(self.bib.itens)
        if not opcoes:
            self.mostrar_erro("Não há itens cadastrados.")
            return None

        def carregar(_chave, dlg):
            item = self.bib.buscar_item(self._codigo(dlg.entradas["item"].get()))
            dlg.rotulos["extra"].config(text=item.rotulo_extra())  # POLIMORFISMO
            dlg.definir("tipo", item.tipo())
            dlg.definir("titulo", item.titulo)
            dlg.definir("ano", item.ano)
            dlg.definir("extra", item.valor_extra())

        def salvar(v):
            return self._executar(
                lambda: self.bib.editar_item(self._codigo(v["item"]), v["titulo"], v["ano"], v["extra"]),
                lambda item: f"Item alterado: {item.descricao()}")

        campos = [
            {"chave": "item", "rotulo": "Item", "opcoes": opcoes},
            {"chave": "tipo", "rotulo": "Tipo"},
            {"chave": "titulo", "rotulo": "Título"},
            {"chave": "ano", "rotulo": "Ano"},
            {"chave": "extra", "rotulo": "Extra"},
        ]
        dlg = self._formulario("Editar item", campos, salvar, ao_mudar=carregar)
        dlg.definir("item", self._escolhido(opcoes, self.tree_itens))
        carregar("item", dlg)
        dlg.entradas["tipo"].config(state="readonly")
        return dlg

    def abrir_remover_item(self):
        opcoes = self._opcoes_itens(self.bib.itens)
        if not opcoes:
            self.mostrar_erro("Não há itens cadastrados.")
            return None

        def remover(v):
            if not self.confirmar(f"Remover o item {v['item']}?"):
                return False
            return self._executar(lambda: self.bib.remover_item(self._codigo(v["item"])),
                                  lambda item: f"Item removido: {item.titulo}")

        campos = [{"chave": "item", "rotulo": "Item", "opcoes": opcoes,
                   "valor": self._escolhido(opcoes, self.tree_itens)}]
        return self._formulario("Remover item", campos, remover, texto_botao="Remover")

    # ============================================================ MEMBROS (aba)
    def _criar_aba_membros(self):
        aba = ttk.Frame(self.abas, padding=8)
        self.abas.add(aba, text="Membros")
        form = ttk.LabelFrame(aba, text="Novo membro", padding=8)
        form.pack(fill="x")

        ttk.Label(form, text="Tipo").grid(row=0, column=0, sticky="w", padx=4)
        self.tipo_membro = ttk.Combobox(form, values=list(TIPOS_MEMBRO), state="readonly", width=22)
        self.tipo_membro.current(0)
        self.tipo_membro.grid(row=0, column=1, sticky="w", padx=4)
        self.tipo_membro.bind("<<ComboboxSelected>>", lambda e: self._mudar_tipo_membro())

        _, self.ent_nome = self._campo(form, 1, "Nome")
        _, self.ent_cpf = self._campo(form, 2, "CPF")
        _, self.ent_matricula = self._campo(form, 1, "Matrícula", coluna=2)
        self.lbl_extra_membro, self.ent_extra_membro = self._campo(form, 2, "Curso", coluna=2)

        botoes = ttk.Frame(form)
        botoes.grid(row=0, column=4, rowspan=3, padx=16)
        ttk.Button(botoes, text="Cadastrar", command=self.cadastrar_membro).pack(fill="x", pady=2)
        ttk.Button(botoes, text="Editar selecionado", command=self.abrir_editar_membro).pack(fill="x", pady=2)
        ttk.Button(botoes, text="Remover selecionado", command=self.remover_membro).pack(fill="x", pady=2)

        self.tree_membros = self._tabela(aba, *self.COLS_MEMBRO)
        self.tree_membros.bind("<Double-1>", lambda e: self.abrir_editar_membro())

    def _mudar_tipo_membro(self):
        self.lbl_extra_membro.config(text=TIPOS_MEMBRO[self.tipo_membro.get()][0])

    def cadastrar_membro(self):
        def acao():
            classe = TIPOS_MEMBRO[self.tipo_membro.get()][1]
            membro = classe(self.ent_nome.get(), self.ent_cpf.get(),
                            self.ent_matricula.get(), self.ent_extra_membro.get())
            self.bib.cadastrar_membro(membro)
            for ent in (self.ent_nome, self.ent_cpf, self.ent_matricula, self.ent_extra_membro):
                ent.delete(0, "end")
            return membro
        return self._executar(acao, lambda m: f"{m.tipo()} cadastrado: {m.nome} ({m.carteirinha.numero})")

    def remover_membro(self):
        matricula = self._selecionado(self.tree_membros)
        if not matricula:
            self.mostrar_erro("Selecione um membro na tabela.")
            return False
        return self._executar(lambda: self.bib.remover_membro(matricula),
                              lambda m: f"Membro removido: {m.nome}")

    def atualizar_membros(self):
        self._limpar(self.tree_membros)
        for m in self.bib.membros:
            self.tree_membros.insert("", "end", iid=m.matricula, values=self._linha_membro(m))

    # ---- membros pelo menu
    def abrir_novo_membro(self, tipo):
        rotulo, classe = TIPOS_MEMBRO[tipo]

        def salvar(v):
            def acao():
                membro = classe(v["nome"], v["cpf"], v["matricula"], v["extra"])
                self.bib.cadastrar_membro(membro)
                return membro
            return self._executar(
                acao, lambda m: f"{m.tipo()} cadastrado: {m.nome} ({m.carteirinha.numero})")

        campos = [
            {"chave": "nome", "rotulo": "Nome"},
            {"chave": "cpf", "rotulo": "CPF"},
            {"chave": "matricula", "rotulo": "Matrícula"},
            {"chave": "extra", "rotulo": rotulo},
        ]
        return self._formulario(f"Cadastrar {tipo}", campos, salvar, texto_botao="Cadastrar")

    def abrir_editar_membro(self):
        opcoes = self._opcoes_membros(self.bib.membros)
        if not opcoes:
            self.mostrar_erro("Não há membros cadastrados.")
            return None

        def carregar(_chave, dlg):
            m = self.bib.buscar_membro(self._codigo(dlg.entradas["membro"].get()))
            dlg.rotulos["extra"].config(text=m.rotulo_extra())  # POLIMORFISMO
            dlg.definir("tipo", m.tipo())
            dlg.definir("nome", m.nome)
            dlg.definir("cpf", m.cpf)
            dlg.definir("extra", m.valor_extra())

        def salvar(v):
            return self._executar(
                lambda: self.bib.editar_membro(self._codigo(v["membro"]), v["nome"], v["cpf"], v["extra"]),
                lambda m: f"Membro alterado: {m}")

        campos = [
            {"chave": "membro", "rotulo": "Membro", "opcoes": opcoes},
            {"chave": "tipo", "rotulo": "Tipo"},
            {"chave": "nome", "rotulo": "Nome"},
            {"chave": "cpf", "rotulo": "CPF"},
            {"chave": "extra", "rotulo": "Extra"},
        ]
        dlg = self._formulario("Editar membro", campos, salvar, ao_mudar=carregar)
        dlg.definir("membro", self._escolhido(opcoes, self.tree_membros))
        carregar("membro", dlg)
        dlg.entradas["tipo"].config(state="readonly")
        return dlg

    def abrir_remover_membro(self):
        opcoes = self._opcoes_membros(self.bib.membros)
        if not opcoes:
            self.mostrar_erro("Não há membros cadastrados.")
            return None

        def remover(v):
            if not self.confirmar(f"Remover o membro {v['membro']}?"):
                return False
            return self._executar(lambda: self.bib.remover_membro(self._codigo(v["membro"])),
                                  lambda m: f"Membro removido: {m.nome}")

        campos = [{"chave": "membro", "rotulo": "Membro", "opcoes": opcoes,
                   "valor": self._escolhido(opcoes, self.tree_membros)}]
        return self._formulario("Remover membro", campos, remover, texto_botao="Remover")

    def abrir_renovar_carteirinha(self):
        opcoes = self._opcoes_membros(self.bib.membros)
        if not opcoes:
            self.mostrar_erro("Não há membros cadastrados.")
            return None

        def renovar(v):
            return self._executar(
                lambda: self.bib.renovar_carteirinha(self._codigo(v["membro"]), ler_data(v["data"])),
                lambda c: f"Carteirinha {c.numero} renovada. Válida até {c.validade:%d/%m/%Y}.")

        campos = [
            {"chave": "membro", "rotulo": "Membro", "opcoes": opcoes,
             "valor": self._escolhido(opcoes, self.tree_membros)},
            {"chave": "data", "rotulo": "Nova emissão (vazio = hoje)"},
        ]
        return self._formulario("Renovar carteirinha", campos, renovar, texto_botao="Renovar")

    # ======================================================== EMPRÉSTIMOS (aba)
    def _criar_aba_emprestimos(self):
        aba = ttk.Frame(self.abas, padding=8)
        self.abas.add(aba, text="Empréstimos")
        form = ttk.LabelFrame(aba, text="Empréstimo / devolução", padding=8)
        form.pack(fill="x")

        ttk.Label(form, text="Item").grid(row=0, column=0, sticky="w", padx=4)
        self.cb_item = ttk.Combobox(form, state="readonly", width=40)
        self.cb_item.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        ttk.Label(form, text="Membro").grid(row=1, column=0, sticky="w", padx=4)
        self.cb_membro = ttk.Combobox(form, state="readonly", width=40)
        self.cb_membro.grid(row=1, column=1, sticky="w", padx=4, pady=2)
        _, self.ent_data = self._campo(form, 2, "Data (dd/mm/aaaa)")
        ttk.Label(form, text="vazio = hoje").grid(row=2, column=2, sticky="w")

        botoes = ttk.Frame(form)
        botoes.grid(row=0, column=3, rowspan=3, padx=16)
        ttk.Button(botoes, text="Emprestar", command=self.emprestar).pack(fill="x", pady=2)
        ttk.Button(botoes, text="Devolver item", command=self.devolver).pack(fill="x", pady=2)

        self.var_atrasados = tk.BooleanVar(value=False)
        ttk.Checkbutton(aba, text="Mostrar só atrasados", variable=self.var_atrasados,
                        command=self.atualizar_emprestimos).pack(anchor="w", pady=(8, 0))

        self.tree_emprestimos = self._tabela(aba, *self.COLS_EMPRESTIMO)

    @staticmethod
    def _codigo_do_combo(combo):
        """'L1 - Dom Casmurro' -> 'L1'."""
        return App._codigo(combo.get())

    def _msg_emprestimo(self, e):
        return (f"'{e.item.titulo}' emprestado para {e.membro.nome}. "
                f"Devolver até {e.data_prevista:%d/%m/%Y}.")

    @staticmethod
    def _msg_devolucao(multa):
        return (f"Devolução registrada. Multa: R$ {multa:.2f}" if multa
                else "Devolução registrada. Sem multa.")

    def emprestar(self):
        def acao():
            data = ler_data(self.ent_data.get())
            return self.bib.emprestar(self._codigo_do_combo(self.cb_item),
                                      self._codigo_do_combo(self.cb_membro), data)
        return self._executar(acao, self._msg_emprestimo)

    def devolver(self):
        def acao():
            data = ler_data(self.ent_data.get())
            return self.bib.devolver(self._codigo_do_combo(self.cb_item), data)
        return self._executar(acao, self._msg_devolucao)

    def atualizar_emprestimos(self):
        self.cb_item["values"] = self._opcoes_itens(self.bib.itens)
        self.cb_membro["values"] = self._opcoes_membros(self.bib.membros)
        self._limpar(self.tree_emprestimos)
        hoje = date.today()
        lista = self.bib.atrasados(hoje) if self.var_atrasados.get() else self.bib.emprestimos
        for e in lista:
            self.tree_emprestimos.insert("", "end", values=self._linha_emprestimo(e, hoje))

    # ---- movimentação pelo menu
    def abrir_emprestar(self):
        itens = self._opcoes_itens(self.bib.itens_disponiveis())
        membros = self._opcoes_membros(self.bib.membros)
        if not itens or not membros:
            self.mostrar_erro("É preciso ter ao menos um item disponível e um membro cadastrado.")
            return None

        def emprestar(v):
            return self._executar(
                lambda: self.bib.emprestar(self._codigo(v["item"]), self._codigo(v["membro"]),
                                           ler_data(v["data"])),
                self._msg_emprestimo)

        campos = [
            {"chave": "item", "rotulo": "Item disponível", "opcoes": itens,
             "valor": self._escolhido(itens, self.tree_itens)},
            {"chave": "membro", "rotulo": "Membro", "opcoes": membros,
             "valor": self._escolhido(membros, self.tree_membros)},
            {"chave": "data", "rotulo": "Data (vazio = hoje)"},
        ]
        return self._formulario("Emprestar item", campos, emprestar, texto_botao="Emprestar")

    def abrir_devolver(self):
        itens = self._opcoes_itens(self.bib.itens_emprestados())
        if not itens:
            self.mostrar_erro("Não há itens emprestados no momento.")
            return None

        def devolver(v):
            return self._executar(
                lambda: self.bib.devolver(self._codigo(v["item"]), ler_data(v["data"])),
                self._msg_devolucao)

        campos = [
            {"chave": "item", "rotulo": "Item emprestado", "opcoes": itens,
             "valor": self._escolhido(itens, self.tree_itens)},
            {"chave": "data", "rotulo": "Data (vazio = hoje)"},
        ]
        return self._formulario("Devolver item", campos, devolver, texto_botao="Devolver")

    # ============================================================ CONSULTAS
    def consultar_acervo(self, filtro="todos"):
        fontes = {
            "todos": ("Acervo completo", self.bib.itens),
            "disponiveis": ("Itens disponíveis", self.bib.itens_disponiveis()),
            "emprestados": ("Itens emprestados", self.bib.itens_emprestados()),
        }
        titulo, itens = fontes[filtro]
        return self._lista(titulo, *self.COLS_ITEM, [self._linha_item(i) for i in itens])

    def abrir_pesquisa(self):
        def pesquisar(v):
            itens = self.bib.pesquisar(v["texto"])
            self._lista(f"Pesquisa: {v['texto']}", *self.COLS_ITEM,
                        [self._linha_item(i) for i in itens])
            return True

        campos = [{"chave": "texto", "rotulo": "Título, autor ou tipo"}]
        return self._formulario("Pesquisar no acervo", campos, pesquisar, texto_botao="Pesquisar")

    def consultar_membros(self):
        return self._lista("Membros", *self.COLS_MEMBRO,
                           [self._linha_membro(m) for m in self.bib.membros])

    def consultar_carteirinhas(self):
        hoje = date.today()
        linhas = [(m.carteirinha.numero, m.nome, m.tipo(),
                   f"{m.carteirinha.emissao:%d/%m/%Y}", f"{m.carteirinha.validade:%d/%m/%Y}",
                   "Válida" if m.carteirinha.valida_em(hoje) else "VENCIDA")
                  for m in self.bib.membros]
        return self._lista("Carteirinhas",
                           ("Número", "Titular", "Tipo", "Emissão", "Validade", "Situação"),
                           (110, 300, 100, 110, 110, 100), linhas)

    def consultar_emprestimos(self, modo="todos"):
        hoje = date.today()
        fontes = {
            "ativos": ("Empréstimos ativos", self.bib.emprestimos_ativos()),
            "atrasados": ("Empréstimos atrasados", self.bib.atrasados(hoje)),
            "todos": ("Histórico de empréstimos", self.bib.emprestimos),
        }
        titulo, lista = fontes[modo]
        return self._lista(titulo, *self.COLS_EMPRESTIMO,
                           [self._linha_emprestimo(e, hoje) for e in lista])

    def abrir_historico_membro(self):
        opcoes = self._opcoes_membros(self.bib.membros)
        if not opcoes:
            self.mostrar_erro("Não há membros cadastrados.")
            return None

        def consultar(v):
            try:
                lista = self.bib.historico_do_membro(self._codigo(v["membro"]))
            except BibliotecaError as erro:
                self.mostrar_erro(str(erro))
                return False
            hoje = date.today()
            multas = sum(e.multa for e in lista)
            self._lista(f"Empréstimos de {v['membro']}", *self.COLS_EMPRESTIMO,
                        [self._linha_emprestimo(e, hoje) for e in lista],
                        rodape=f"| Multas pagas: R$ {multas:.2f}")
            return True

        campos = [{"chave": "membro", "rotulo": "Membro", "opcoes": opcoes,
                   "valor": self._escolhido(opcoes, self.tree_membros)}]
        return self._formulario("Empréstimos de um membro", campos, consultar,
                                texto_botao="Consultar")

    # ============================================================ RELATÓRIO
    def _criar_aba_relatorio(self):
        aba = ttk.Frame(self.abas, padding=8)
        self.abas.add(aba, text="Relatório")
        topo = ttk.Frame(aba)
        topo.pack(fill="x")
        self.var_formato = tk.StringVar(value="Texto")
        for nome in ("Texto", "CSV"):
            ttk.Radiobutton(topo, text=nome, value=nome, variable=self.var_formato).pack(side="left", padx=4)
        ttk.Button(topo, text="Gerar", command=self.gerar_relatorio).pack(side="left", padx=8)
        ttk.Button(topo, text="Salvar em arquivo", command=self.salvar_relatorio).pack(side="left")
        self.txt_relatorio = tk.Text(aba, font=("Courier", 10))
        self.txt_relatorio.pack(fill="both", expand=True, pady=(8, 0))

    def _exportador(self):
        # POLIMORFISMO: qualquer Exportador funciona no mesmo lugar
        return ExportadorCSV() if self.var_formato.get() == "CSV" else ExportadorTexto()

    def gerar_relatorio(self):
        texto = self.bib.gerar_relatorio(self._exportador())
        self.txt_relatorio.delete("1.0", "end")
        self.txt_relatorio.insert("1.0", texto)
        return texto

    def relatorio_pelo_menu(self, formato):
        self.var_formato.set(formato)
        self.ir_para_aba(ABAS.index("Relatório"))
        return self.gerar_relatorio()

    def pedir_arquivo(self, exportador):
        return filedialog.asksaveasfilename(
            parent=self, defaultextension=f".{exportador.extensao()}",
            initialfile=f"relatorio.{exportador.extensao()}",
        )

    def salvar_relatorio(self):
        exportador = self._exportador()
        caminho = self.pedir_arquivo(exportador)
        if not caminho:
            return False
        with open(caminho, "w", encoding="utf-8") as arq:
            arq.write(self.bib.gerar_relatorio(exportador))
        self.mostrar_info(f"Relatório salvo em {caminho}")
        return True

    def mostrar_resumo(self):
        r = self.bib.resumo()
        texto = (
            f"RESUMO GERAL - {self.bib.nome}\n\n"
            f"Itens no acervo ........ {r['itens']}\n"
            f"  disponíveis .......... {r['disponiveis']}\n"
            f"  emprestados .......... {r['itens'] - r['disponiveis']}\n"
            f"Membros ................ {r['membros']}\n"
            f"Empréstimos registrados  {r['emprestimos']}\n"
            f"  ativos ............... {r['ativos']}\n"
            f"  atrasados ............ {r['atrasados']}\n"
            f"Total de multas ........ R$ {r['multas']:.2f}\n"
        )
        return self._texto("Resumo geral", texto)

    # ================================================================ GERAL
    def ir_para_aba(self, indice):
        self.abas.select(indice)

    def atualizar_status(self):
        r = self.bib.resumo()
        self.var_status.set(
            f"{r['itens']} itens ({r['disponiveis']} disponíveis)  |  {r['membros']} membros  |  "
            f"{r['ativos']} empréstimos ativos  |  {r['atrasados']} atrasados  |  "
            f"multas: R$ {r['multas']:.2f}  |  {self._origem_dados()}"
        )

    def _origem_dados(self):
        if self.repo is None:
            return "dados em memória"
        return f"banco de dados: {os.path.basename(self.repo.caminho)}"

    def atualizar_tudo(self):
        self.title(f"Sistema de Biblioteca - {self.bib.nome}")
        self.atualizar_acervo()
        self.atualizar_membros()
        self.atualizar_emprestimos()
        self.atualizar_status()


if __name__ == "__main__":
    App(caminho_banco=sys.argv[1] if len(sys.argv) > 1 else BANCO_PADRAO).mainloop()
