"""Classe central do sistema.

AGREGAÇÃO: itens e membros são criados fora e apenas adicionados aqui;
se forem removidos, continuam existindo.
COMPOSIÇÃO: os empréstimos são criados dentro de emprestar() e pertencem
à biblioteca.
DEPENDÊNCIA: gerar_relatorio() recebe um Exportador por parâmetro.
"""

from datetime import date

from .emprestimo import Emprestimo
from .excecoes import (
    CadastroDuplicadoError,
    ItemIndisponivelError,
    LimiteEmprestimosError,
    NaoEncontradoError,
    OperacaoInvalidaError,
)


class Biblioteca:
    def __init__(self, nome):
        self.nome = nome
        # AGREGAÇÃO: guarda objetos criados fora da biblioteca
        self._itens = {}
        self._membros = {}
        # COMPOSIÇÃO: empréstimos são criados e mantidos pela biblioteca
        self._emprestimos = []

    # ---------- consultas ----------
    @property
    def itens(self):
        return list(self._itens.values())  # cópia: protege a coleção interna

    @property
    def membros(self):
        return list(self._membros.values())

    @property
    def emprestimos(self):
        return list(self._emprestimos)

    def buscar_item(self, codigo):
        try:
            return self._itens[codigo]
        except KeyError:
            raise NaoEncontradoError(f"Item '{codigo}' não encontrado.") from None

    def buscar_membro(self, matricula):
        try:
            return self._membros[matricula]
        except KeyError:
            raise NaoEncontradoError(f"Membro '{matricula}' não encontrado.") from None

    def pesquisar(self, texto):
        texto = texto.strip().lower()
        return [i for i in self._itens.values() if texto in i.descricao().lower()]

    def itens_disponiveis(self):
        return [i for i in self._itens.values() if i.disponivel]

    def itens_emprestados(self):
        return [i for i in self._itens.values() if not i.disponivel]

    def emprestimos_ativos(self):
        return [e for e in self._emprestimos if e.ativo]

    def emprestimos_do_membro(self, matricula):
        return [e for e in self.emprestimos_ativos() if e.membro.matricula == matricula]

    def historico_do_membro(self, matricula):
        """Todos os empréstimos (ativos e devolvidos) de um membro."""
        self.buscar_membro(matricula)
        return [e for e in self._emprestimos if e.membro.matricula == matricula]

    def atrasados(self, hoje=None):
        hoje = hoje or date.today()
        return [e for e in self._emprestimos if e.atrasado_em(hoje)]

    def total_multas(self):
        return round(sum(e.multa for e in self._emprestimos), 2)

    def resumo(self, hoje=None):
        """Números gerais da biblioteca (usado na barra de status e no menu)."""
        return {
            "itens": len(self._itens),
            "disponiveis": len(self.itens_disponiveis()),
            "membros": len(self._membros),
            "ativos": len(self.emprestimos_ativos()),
            "atrasados": len(self.atrasados(hoje)),
            "emprestimos": len(self._emprestimos),
            "multas": self.total_multas(),
        }

    # ---------- cadastros ----------
    def cadastrar_item(self, item):
        if item.codigo in self._itens:
            raise CadastroDuplicadoError(f"Já existe um item com o código '{item.codigo}'.")
        self._itens[item.codigo] = item

    def cadastrar_membro(self, membro):
        if membro.matricula in self._membros:
            raise CadastroDuplicadoError(
                f"Já existe um membro com a matrícula '{membro.matricula}'."
            )
        self._membros[membro.matricula] = membro

    def editar_item(self, codigo, titulo, ano, extra):
        item = self.buscar_item(codigo)
        item.alterar(titulo, ano, extra)  # POLIMORFISMO: cada tipo valida seu extra
        return item

    def editar_membro(self, matricula, nome, cpf, extra):
        membro = self.buscar_membro(matricula)
        membro.alterar(nome, cpf, extra)
        return membro

    def renovar_carteirinha(self, matricula, emissao=None):
        membro = self.buscar_membro(matricula)
        membro.carteirinha.renovar(emissao)
        return membro.carteirinha

    def remover_item(self, codigo):
        item = self.buscar_item(codigo)
        if not item.disponivel:
            raise OperacaoInvalidaError("Não é possível remover um item emprestado.")
        return self._itens.pop(codigo)  # AGREGAÇÃO: o objeto continua existindo

    def remover_membro(self, matricula):
        self.buscar_membro(matricula)
        if self.emprestimos_do_membro(matricula):
            raise OperacaoInvalidaError(
                "Não é possível remover um membro com empréstimos ativos."
            )
        return self._membros.pop(matricula)

    # ---------- empréstimos ----------
    def emprestar(self, codigo, matricula, data=None):
        data = data or date.today()
        item = self.buscar_item(codigo)
        membro = self.buscar_membro(matricula)
        if not item.disponivel:
            raise ItemIndisponivelError(f"O item '{item.titulo}' já está emprestado.")
        if not membro.carteirinha.valida_em(data):
            raise OperacaoInvalidaError(
                f"A carteirinha {membro.carteirinha.numero} não é válida nesta data."
            )
        # POLIMORFISMO: o limite depende do tipo do membro (Aluno/Professor)
        if len(self.emprestimos_do_membro(matricula)) >= membro.limite_emprestimos():
            raise LimiteEmprestimosError(
                f"{membro.nome} atingiu o limite de {membro.limite_emprestimos()} empréstimos."
            )
        # COMPOSIÇÃO: o empréstimo nasce dentro da biblioteca
        emprestimo = Emprestimo(membro, item, data)
        self._emprestimos.append(emprestimo)
        return emprestimo

    def devolver(self, codigo, data=None) -> float:
        self.buscar_item(codigo)
        for emp in self._emprestimos:
            if emp.ativo and emp.item.codigo == codigo:
                return emp.devolver(data)
        raise OperacaoInvalidaError(f"O item '{codigo}' não está emprestado.")

    # ---------- relatórios ----------
    def gerar_relatorio(self, exportador) -> str:
        # DEPENDÊNCIA + POLIMORFISMO: qualquer Exportador serve
        return exportador.exportar(self)
