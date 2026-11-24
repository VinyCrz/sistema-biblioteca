"""Biblioteca que grava tudo no banco de dados (Desk App III).

HERANÇA: BibliotecaPersistente é uma Biblioteca. As regras de negócio
continuam todas na classe-mãe; aqui cada método chama o da mãe (super())
e, se deu certo, grava a alteração no banco.
ASSOCIAÇÃO: guarda uma referência ao RepositorioSQLite que recebeu.
"""

from .biblioteca import Biblioteca


class BibliotecaPersistente(Biblioteca):
    def __init__(self, nome, repositorio):
        super().__init__(nome)
        self._repo = repositorio
        # ao abrir, recarrega do banco tudo o que foi salvo antes
        itens, membros, emprestimos = repositorio.carregar()
        for item in itens:
            self._itens[item.codigo] = item
        for membro in membros:
            self._membros[membro.matricula] = membro
        self._emprestimos.extend(emprestimos)

    @property
    def repositorio(self):
        return self._repo

    # ---------- itens ----------
    def cadastrar_item(self, item):
        super().cadastrar_item(item)
        self._repo.salvar_item(item)

    def editar_item(self, codigo, titulo, ano, extra):
        item = super().editar_item(codigo, titulo, ano, extra)
        self._repo.salvar_item(item)
        return item

    def remover_item(self, codigo):
        item = super().remover_item(codigo)
        self._repo.remover_item(codigo)
        return item

    # ---------- membros ----------
    def cadastrar_membro(self, membro):
        super().cadastrar_membro(membro)
        self._repo.salvar_membro(membro)

    def editar_membro(self, matricula, nome, cpf, extra):
        membro = super().editar_membro(matricula, nome, cpf, extra)
        self._repo.salvar_membro(membro)
        return membro

    def renovar_carteirinha(self, matricula, emissao=None):
        carteirinha = super().renovar_carteirinha(matricula, emissao)
        self._repo.salvar_membro(carteirinha.titular)
        return carteirinha

    def remover_membro(self, matricula):
        membro = super().remover_membro(matricula)
        self._repo.remover_membro(matricula)
        return membro

    # ---------- empréstimos ----------
    def emprestar(self, codigo, matricula, data=None):
        emprestimo = super().emprestar(codigo, matricula, data)
        self._repo.inserir_emprestimo(emprestimo)
        return emprestimo

    def devolver(self, codigo, data=None):
        emprestimo = self.emprestimo_ativo_do_item(codigo)
        multa = super().devolver(codigo, data)
        self._repo.atualizar_emprestimo(emprestimo)
        return multa
