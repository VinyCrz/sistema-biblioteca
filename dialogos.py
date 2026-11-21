"""Janelas auxiliares usadas pelo menu do sistema.

- FormularioDialog: formulário genérico (cadastro, edição, empréstimo...).
- JanelaLista: tabela somente leitura para as consultas.
- JanelaTexto: texto longo (ajuda, regras de negócio, sobre).
"""

import tkinter as tk
from tkinter import ttk


class _JanelaFilha(tk.Toplevel):
    """Base das janelas: fica na frente da principal e fecha com Esc."""

    def __init__(self, pai, titulo):
        super().__init__(pai)
        self.title(titulo)
        self.transient(pai)
        self.bind("<Escape>", lambda e: self.destroy())


class FormularioDialog(_JanelaFilha):
    """Formulário genérico.

    campos: lista de dicionários com as chaves
        chave   -> nome do campo no dicionário de valores
        rotulo  -> texto do rótulo
        opcoes  -> (opcional) lista para um Combobox somente leitura
        valor   -> (opcional) valor inicial
    ao_confirmar(valores) deve retornar True quando a ação deu certo;
    nesse caso a janela fecha. Se retornar False, a janela continua aberta
    para o usuário corrigir.
    ao_mudar(chave, dialogo) é chamado quando um Combobox muda de valor.
    """

    def __init__(self, pai, titulo, campos, ao_confirmar, texto_botao="Salvar",
                 ao_mudar=None, modal=True):
        super().__init__(pai, titulo)
        self.resizable(False, False)
        self._ao_confirmar = ao_confirmar
        self._ao_mudar = ao_mudar
        self.entradas = {}
        self.rotulos = {}

        corpo = ttk.Frame(self, padding=12)
        corpo.pack(fill="both", expand=True)
        for linha, campo in enumerate(campos):
            chave = campo["chave"]
            lbl = ttk.Label(corpo, text=campo["rotulo"])
            lbl.grid(row=linha, column=0, sticky="w", padx=4, pady=3)
            if "opcoes" in campo:
                ent = ttk.Combobox(corpo, values=list(campo["opcoes"]),
                                   state="readonly", width=38)
                ent.bind("<<ComboboxSelected>>",
                         lambda e, c=chave: self._mudou(c))
            else:
                ent = ttk.Entry(corpo, width=40)
            ent.grid(row=linha, column=1, sticky="we", padx=4, pady=3)
            self.entradas[chave] = ent
            self.rotulos[chave] = lbl
            if campo.get("valor") not in (None, ""):
                self.definir(chave, campo["valor"])

        botoes = ttk.Frame(corpo)
        botoes.grid(row=len(campos), column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(botoes, text=texto_botao, command=self.confirmar).pack(side="left", padx=4)
        ttk.Button(botoes, text="Cancelar", command=self.destroy).pack(side="left")
        self.bind("<Return>", lambda e: self.confirmar())

        primeiro = next(iter(self.entradas.values()), None)
        if primeiro is not None:
            primeiro.focus_set()
        if modal:
            try:
                self.grab_set()  # bloqueia a janela principal enquanto aberto
            except tk.TclError:
                pass  # janela ainda não visível (ex.: nos testes)

    def _mudou(self, chave):
        if self._ao_mudar:
            self._ao_mudar(chave, self)

    def definir(self, chave, valor):
        ent = self.entradas[chave]
        if isinstance(ent, ttk.Combobox):
            ent.set(valor)
        else:
            estado = str(ent.cget("state"))
            ent.config(state="normal")  # campos somente leitura também são preenchidos
            ent.delete(0, "end")
            ent.insert(0, str(valor))
            ent.config(state=estado)

    def valores(self):
        return {chave: ent.get() for chave, ent in self.entradas.items()}

    def confirmar(self):
        if self._ao_confirmar(self.valores()):
            self.destroy()
            return True
        return False


class JanelaLista(_JanelaFilha):
    """Tabela somente leitura usada nas consultas do menu."""

    def __init__(self, pai, titulo, colunas, larguras, linhas, rodape=""):
        super().__init__(pai, titulo)
        self.geometry("900x420")
        corpo = ttk.Frame(self, padding=10)
        corpo.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(corpo, columns=colunas, show="headings")
        for col, larg in zip(colunas, larguras):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=larg, anchor="w")
        barra = ttk.Scrollbar(corpo, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=barra.set)
        self.tree.pack(side="top", fill="both", expand=True)
        barra.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, anchor="ne")

        for linha in linhas:
            self.tree.insert("", "end", values=linha)

        base = ttk.Frame(corpo)
        base.pack(fill="x", pady=(8, 0))
        total = f"{len(linhas)} registro(s)"
        ttk.Label(base, text=f"{total}   {rodape}".strip()).pack(side="left")
        ttk.Button(base, text="Fechar", command=self.destroy).pack(side="right")


class JanelaTexto(_JanelaFilha):
    """Mostra um texto somente leitura (ajuda, regras, sobre)."""

    def __init__(self, pai, titulo, texto):
        super().__init__(pai, titulo)
        self.geometry("620x440")
        corpo = ttk.Frame(self, padding=10)
        corpo.pack(fill="both", expand=True)
        self.txt = tk.Text(corpo, wrap="word", font=("Courier", 10))
        self.txt.insert("1.0", texto)
        self.txt.config(state="disabled")
        self.txt.pack(fill="both", expand=True)
        ttk.Button(corpo, text="Fechar", command=self.destroy).pack(anchor="e", pady=(8, 0))
