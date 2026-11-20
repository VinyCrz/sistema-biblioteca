"""Exceções próprias do sistema de biblioteca.

HERANÇA: todas as exceções específicas herdam de BibliotecaError,
assim a interface consegue capturar qualquer erro de regra de negócio
com um único `except BibliotecaError`.
"""


class BibliotecaError(Exception):
    """Erro base de qualquer regra de negócio da biblioteca."""


class ItemIndisponivelError(BibliotecaError):
    """O item já está emprestado."""


class LimiteEmprestimosError(BibliotecaError):
    """O membro atingiu o limite de empréstimos simultâneos."""


class NaoEncontradoError(BibliotecaError):
    """Item ou membro não cadastrado."""


class CadastroDuplicadoError(BibliotecaError):
    """Já existe um cadastro com o mesmo código ou matrícula."""


class OperacaoInvalidaError(BibliotecaError):
    """Operação que não faz sentido no estado atual (ex.: devolver duas vezes)."""
