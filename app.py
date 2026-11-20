"""Interface gráfica (Tkinter) do Sistema de Biblioteca.

Execute com:  python3 app.py
"""

import tkinter as tk
from datetime import date, datetime
from tkinter import filedialog, messagebox, ttk

from biblioteca import (
    DVD, Aluno, Biblioteca, BibliotecaError, ExportadorCSV, ExportadorTexto,
    Livro, Professor, Revista,
)

FMT_DATA = "%d/%m/%Y"


def ler_data(texto):
    """Converte 'dd/mm/aaaa' em date. Texto vazio = hoje."""
    texto = (texto or "").strip()
    if not texto:
        return date.today()
    try:
        return datetime.strptime(texto, FMT_DATA).date()
    except ValueError:
        raise BibliotecaError("Data inválida. Use o formato dd/mm/aaaa.") from None


def dados_exemplo():
    """Biblioteca já preenchida para a demonstração."""
    bib = Biblioteca("Biblioteca Desk App I")
    bib.cadastrar_item(Livro("L1", "Dom Casmurro", 1899, "Machado de Assis"))
    bib.cadastrar_item(Livro("L2", "Clean Code", 2008, "Robert C. Martin"))
    bib.cadastrar_item(Revista("R1", "Superinteressante", 2024, 450))
    bib.cadastrar_item(DVD("D1", "Cidade de Deus", 2002, 130))
    bib.cadastrar_membro(Aluno("Ana Souza", "123.456.789-00", "A001", "Sistemas de Informação"))
    bib.cadastrar_membro(Professor("Carlos Lima", "987.654.321-00", "P001", "Computação"))
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


class App(tk.Tk):
    def __init__(self, biblioteca=None):
        super().__init__()
        self.bib = biblioteca if biblioteca is not None else dados_exemplo()
        self.title(f"Sistema de Biblioteca - {self.bib.nome}")
        self.geometry("1150x600")

        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=8, pady=8)
        self._criar_aba_acervo()
        self._criar_aba_membros()
        self._criar_aba_emprestimos()
        self._criar_aba_relatorio()
        self.atualizar_tudo()

    # ------------------------------------------------------------ utilidades
    def mostrar_erro(self, msg):
        messagebox.showerror("Erro", msg, parent=self)

    def mostrar_info(self, msg):
        messagebox.showinfo("Sucesso", msg, parent=self)

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

    # ----------------------------------------------------------------- acervo
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
        ttk.Button(botoes, text="Remover selecionado", command=self.remover_item).pack(fill="x", pady=2)

        busca = ttk.Frame(aba)
        busca.pack(fill="x", pady=(8, 0))
        ttk.Label(busca, text="Pesquisar:").pack(side="left")
        self.var_pesquisa = tk.StringVar()
        self.var_pesquisa.trace_add("write", lambda *a: self.atualizar_acervo())
        ttk.Entry(busca, textvariable=self.var_pesquisa, width=40).pack(side="left", padx=4)

        self.tree_itens = self._tabela(
            aba, ("Código", "Tipo", "Descrição", "Prazo", "Multa/dia", "Situação"),
            (80, 90, 520, 80, 90, 120),
        )

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
        sel = self.tree_itens.selection()
        if not sel:
            self.mostrar_erro("Selecione um item na tabela.")
            return False
        codigo = self.tree_itens.item(sel[0], "values")[0]
        return self._executar(lambda: self.bib.remover_item(codigo),
                              lambda item: f"Item removido: {item.titulo}")

    def atualizar_acervo(self):
        self._limpar(self.tree_itens)
        texto = self.var_pesquisa.get()
        itens = self.bib.pesquisar(texto) if texto.strip() else self.bib.itens
        for item in itens:
            self.tree_itens.insert("", "end", iid=item.codigo, values=(
                item.codigo, item.tipo(), item.descricao(), f"{item.prazo_dias()} dias",
                f"R$ {item.multa_diaria():.2f}",
                "Disponível" if item.disponivel else "Emprestado",
            ))

    # ---------------------------------------------------------------- membros
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
        ttk.Button(botoes, text="Remover selecionado", command=self.remover_membro).pack(fill="x", pady=2)

        self.tree_membros = self._tabela(
            aba, ("Matrícula", "Tipo", "Nome", "Carteirinha", "Validade", "Empréstimos"),
            (90, 90, 360, 120, 110, 110),
        )

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
        sel = self.tree_membros.selection()
        if not sel:
            self.mostrar_erro("Selecione um membro na tabela.")
            return False
        matricula = self.tree_membros.item(sel[0], "values")[0]
        return self._executar(lambda: self.bib.remover_membro(matricula),
                              lambda m: f"Membro removido: {m.nome}")

    def atualizar_membros(self):
        self._limpar(self.tree_membros)
        for m in self.bib.membros:
            ativos = len(self.bib.emprestimos_do_membro(m.matricula))
            self.tree_membros.insert("", "end", iid=m.matricula, values=(
                m.matricula, m.tipo(), m.nome, m.carteirinha.numero,
                f"{m.carteirinha.validade:%d/%m/%Y}", f"{ativos}/{m.limite_emprestimos()}",
            ))

    # ------------------------------------------------------------ empréstimos
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

        self.tree_emprestimos = self._tabela(
            aba, ("Item", "Membro", "Empréstimo", "Previsto", "Devolução", "Situação"),
            (300, 260, 110, 110, 110, 150),
        )

    @staticmethod
    def _codigo_do_combo(combo):
        """'L1 - Dom Casmurro' -> 'L1'."""
        return combo.get().split(" - ")[0].strip()

    def emprestar(self):
        def acao():
            data = ler_data(self.ent_data.get())
            return self.bib.emprestar(self._codigo_do_combo(self.cb_item),
                                      self._codigo_do_combo(self.cb_membro), data)
        return self._executar(acao, lambda e: (
            f"'{e.item.titulo}' emprestado para {e.membro.nome}. "
            f"Devolver até {e.data_prevista:%d/%m/%Y}."))

    def devolver(self):
        def acao():
            data = ler_data(self.ent_data.get())
            return self.bib.devolver(self._codigo_do_combo(self.cb_item), data)
        return self._executar(acao, lambda multa: (
            f"Devolução registrada. Multa: R$ {multa:.2f}" if multa
            else "Devolução registrada. Sem multa."))

    def atualizar_emprestimos(self):
        self.cb_item["values"] = [f"{i.codigo} - {i.titulo}" for i in self.bib.itens]
        self.cb_membro["values"] = [f"{m.matricula} - {m.nome}" for m in self.bib.membros]
        self._limpar(self.tree_emprestimos)
        hoje = date.today()
        lista = self.bib.atrasados(hoje) if self.var_atrasados.get() else self.bib.emprestimos
        for e in lista:
            if not e.ativo:
                situacao = f"Devolvido (R$ {e.multa:.2f})"
            elif e.atrasado_em(hoje):
                situacao = "ATRASADO"
            else:
                situacao = "Ativo"
            devolucao = f"{e.data_devolucao:%d/%m/%Y}" if e.data_devolucao else "-"
            self.tree_emprestimos.insert("", "end", values=(
                e.item.descricao(), str(e.membro), f"{e.data_emprestimo:%d/%m/%Y}",
                f"{e.data_prevista:%d/%m/%Y}", devolucao, situacao,
            ))

    # -------------------------------------------------------------- relatório
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

    def salvar_relatorio(self):
        exportador = self._exportador()
        caminho = filedialog.asksaveasfilename(
            parent=self, defaultextension=f".{exportador.extensao()}",
            initialfile=f"relatorio.{exportador.extensao()}",
        )
        if not caminho:
            return False
        with open(caminho, "w", encoding="utf-8") as arq:
            arq.write(self.bib.gerar_relatorio(exportador))
        self.mostrar_info(f"Relatório salvo em {caminho}")
        return True

    # ------------------------------------------------------------------ geral
    def atualizar_tudo(self):
        self.atualizar_acervo()
        self.atualizar_membros()
        self.atualizar_emprestimos()


if __name__ == "__main__":
    App().mainloop()
