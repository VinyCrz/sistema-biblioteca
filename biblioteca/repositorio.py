"""Banco de dados SQLite do sistema (Desk App III).

O RepositorioSQLite é a única classe que conhece SQL. Ele transforma os
objetos do sistema em linhas de tabela e as linhas de volta em objetos.

Tabelas:
- itens: Livro, Revista e DVD na mesma tabela (coluna "tipo"); cada tipo
  usa sua coluna extra (autor, edicao ou duracao_min).
- membros: Aluno e Professor na mesma tabela, com os dados da carteirinha.
- emprestimos: liga um item a um membro (chaves estrangeiras).

Itens e membros removidos não são apagados de verdade: ficam com ativo = 0,
para que o histórico de empréstimos e as multas continuem no banco.
A disponibilidade do item não é gravada: ela vem dos empréstimos em aberto.
"""

import sqlite3
from datetime import date

from .emprestimo import Emprestimo
from .itens import DVD, Livro, Revista
from .pessoas import Aluno, Carteirinha, Professor

ESQUEMA = """
CREATE TABLE IF NOT EXISTS itens (
    codigo       TEXT PRIMARY KEY,
    tipo         TEXT NOT NULL CHECK (tipo IN ('Livro', 'Revista', 'DVD')),
    titulo       TEXT NOT NULL,
    ano          INTEGER NOT NULL,
    autor        TEXT,
    isbn         TEXT,
    edicao       INTEGER,
    duracao_min  INTEGER,
    ativo        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS membros (
    matricula    TEXT PRIMARY KEY,
    tipo         TEXT NOT NULL CHECK (tipo IN ('Aluno', 'Professor')),
    nome         TEXT NOT NULL,
    cpf          TEXT NOT NULL,
    curso        TEXT,
    departamento TEXT,
    carteirinha  TEXT NOT NULL UNIQUE,
    emissao      TEXT NOT NULL,
    validade     TEXT NOT NULL,
    ativo        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS emprestimos (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_item      TEXT NOT NULL REFERENCES itens (codigo),
    matricula        TEXT NOT NULL REFERENCES membros (matricula),
    data_emprestimo  TEXT NOT NULL,
    data_prevista    TEXT NOT NULL,
    data_devolucao   TEXT,
    multa            REAL NOT NULL DEFAULT 0
);
"""


def _data(texto):
    return date.fromisoformat(texto) if texto else None


class RepositorioSQLite:
    def __init__(self, caminho="biblioteca.db"):
        self.caminho = str(caminho)
        self._con = sqlite3.connect(self.caminho)
        self._con.row_factory = sqlite3.Row
        self._con.execute("PRAGMA foreign_keys = ON")
        with self._con:
            self._con.executescript(ESQUEMA)

    def fechar(self):
        self._con.close()

    def consultar(self, sql, parametros=()):
        """Executa um SELECT e devolve as linhas (usado também no ver_banco.py)."""
        return self._con.execute(sql, parametros).fetchall()

    def descrever(self):
        """Texto com o conteúdo de cada tabela (menu e script ver_banco.py)."""
        partes = [f"BANCO DE DADOS: {self.caminho}"]
        for tabela in ("itens", "membros", "emprestimos"):
            linhas = self.consultar(f"SELECT * FROM {tabela}")
            colunas = [c[1] for c in self.consultar(f"PRAGMA table_info({tabela})")]
            partes += ["", f"TABELA {tabela.upper()} ({len(linhas)} registros)",
                       " | ".join(colunas)]
            partes += [" | ".join("" if v is None else str(v) for v in tuple(r)) for r in linhas]
        return "\n".join(partes)

    def vazio(self):
        return not self.consultar("SELECT 1 FROM itens UNION ALL SELECT 1 FROM membros LIMIT 1")

    def limpar(self):
        """Apaga todos os dados (menu Arquivo > Nova biblioteca)."""
        with self._con:
            self._con.execute("DELETE FROM emprestimos")
            self._con.execute("DELETE FROM itens")
            self._con.execute("DELETE FROM membros")

    # ------------------------------------------------------------------ itens
    def salvar_item(self, item):
        """INSERT do item novo ou UPDATE do item existente (upsert)."""
        extras = {"autor": None, "isbn": None, "edicao": None, "duracao_min": None}
        if isinstance(item, Livro):
            extras.update(autor=item.autor, isbn=item.isbn)
        elif isinstance(item, Revista):
            extras["edicao"] = item.edicao
        elif isinstance(item, DVD):
            extras["duracao_min"] = item.duracao_min
        with self._con:
            self._con.execute(
                """INSERT INTO itens (codigo, tipo, titulo, ano, autor, isbn, edicao, duracao_min, ativo)
                   VALUES (:codigo, :tipo, :titulo, :ano, :autor, :isbn, :edicao, :duracao_min, 1)
                   ON CONFLICT (codigo) DO UPDATE SET
                       tipo = excluded.tipo, titulo = excluded.titulo, ano = excluded.ano,
                       autor = excluded.autor, isbn = excluded.isbn, edicao = excluded.edicao,
                       duracao_min = excluded.duracao_min, ativo = 1""",
                {"codigo": item.codigo, "tipo": item.tipo(), "titulo": item.titulo,
                 "ano": item.ano, **extras},
            )

    def remover_item(self, codigo):
        with self._con:
            self._con.execute("UPDATE itens SET ativo = 0 WHERE codigo = ?", (codigo,))

    @staticmethod
    def _item_da_linha(r):
        if r["tipo"] == "Livro":
            return Livro(r["codigo"], r["titulo"], r["ano"], r["autor"], r["isbn"] or "")
        if r["tipo"] == "Revista":
            return Revista(r["codigo"], r["titulo"], r["ano"], r["edicao"])
        return DVD(r["codigo"], r["titulo"], r["ano"], r["duracao_min"])

    # ---------------------------------------------------------------- membros
    def salvar_membro(self, membro):
        cart = membro.carteirinha
        with self._con:
            self._con.execute(
                """INSERT INTO membros (matricula, tipo, nome, cpf, curso, departamento,
                                        carteirinha, emissao, validade, ativo)
                   VALUES (:matricula, :tipo, :nome, :cpf, :curso, :departamento,
                           :carteirinha, :emissao, :validade, 1)
                   ON CONFLICT (matricula) DO UPDATE SET
                       tipo = excluded.tipo, nome = excluded.nome, cpf = excluded.cpf,
                       curso = excluded.curso, departamento = excluded.departamento,
                       carteirinha = excluded.carteirinha, emissao = excluded.emissao,
                       validade = excluded.validade, ativo = 1""",
                {"matricula": membro.matricula, "tipo": membro.tipo(), "nome": membro.nome,
                 "cpf": membro.cpf,
                 "curso": membro.curso if isinstance(membro, Aluno) else None,
                 "departamento": membro.departamento if isinstance(membro, Professor) else None,
                 "carteirinha": cart.numero, "emissao": cart.emissao.isoformat(),
                 "validade": cart.validade.isoformat()},
            )

    def remover_membro(self, matricula):
        with self._con:
            self._con.execute("UPDATE membros SET ativo = 0 WHERE matricula = ?", (matricula,))

    @staticmethod
    def _membro_da_linha(r):
        if r["tipo"] == "Aluno":
            membro = Aluno(r["nome"], r["cpf"], r["matricula"], r["curso"] or "")
        else:
            membro = Professor(r["nome"], r["cpf"], r["matricula"], r["departamento"] or "")
        # a carteirinha volta com o número e as datas gravados
        cart = membro.carteirinha
        cart.numero = r["carteirinha"]
        cart.emissao, cart.validade = _data(r["emissao"]), _data(r["validade"])
        return membro

    # ------------------------------------------------------------ empréstimos
    def inserir_emprestimo(self, emp):
        with self._con:
            cursor = self._con.execute(
                """INSERT INTO emprestimos (codigo_item, matricula, data_emprestimo, data_prevista,
                                            data_devolucao, multa)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (emp.item.codigo, emp.membro.matricula, emp.data_emprestimo.isoformat(),
                 emp.data_prevista.isoformat(),
                 emp.data_devolucao.isoformat() if emp.data_devolucao else None, emp.multa),
            )
        emp.id = cursor.lastrowid

    def atualizar_emprestimo(self, emp):
        """Grava a devolução (data e multa)."""
        with self._con:
            self._con.execute(
                "UPDATE emprestimos SET data_devolucao = ?, multa = ? WHERE id = ?",
                (emp.data_devolucao.isoformat() if emp.data_devolucao else None, emp.multa, emp.id),
            )

    # ---------------------------------------------------------------- leitura
    def carregar(self):
        """Lê o banco e devolve (itens ativos, membros ativos, empréstimos)."""
        itens = {r["codigo"]: (self._item_da_linha(r), r["ativo"])
                 for r in self.consultar("SELECT * FROM itens ORDER BY rowid")}
        membros = {r["matricula"]: (self._membro_da_linha(r), r["ativo"])
                   for r in self.consultar("SELECT * FROM membros ORDER BY rowid")}

        # a numeração das carteirinhas novas continua depois da maior já gravada
        numeros = [int(m.carteirinha.numero.split("-")[1]) for m, _ in membros.values()]
        if numeros:
            Carteirinha._proximo_numero = max(Carteirinha._proximo_numero, max(numeros) + 1)

        emprestimos = [
            Emprestimo.restaurar(
                r["id"], membros[r["matricula"]][0], itens[r["codigo_item"]][0],
                _data(r["data_emprestimo"]), _data(r["data_prevista"]),
                _data(r["data_devolucao"]), r["multa"],
            )
            for r in self.consultar("SELECT * FROM emprestimos ORDER BY id")
        ]
        return ([i for i, ativo in itens.values() if ativo],
                [m for m, ativo in membros.values() if ativo],
                emprestimos)
