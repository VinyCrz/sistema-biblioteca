"""Itens do acervo.

HERANÇA: Livro, Revista e DVD herdam de ItemAcervo (classe abstrata).
POLIMORFISMO: cada subclasse responde do seu jeito a prazo_dias(),
multa_diaria(), tipo() e descricao().
"""

from abc import ABC, abstractmethod

from .excecoes import ItemIndisponivelError, OperacaoInvalidaError


class ItemAcervo(ABC):
    """Classe abstrata: representa qualquer item que pode ser emprestado."""

    def __init__(self, codigo, titulo, ano):
        codigo = str(codigo).strip()
        titulo = str(titulo).strip()
        if not codigo:
            raise ValueError("O código do item é obrigatório.")
        if not titulo:
            raise ValueError("O título do item é obrigatório.")
        try:
            ano = int(ano)
        except (TypeError, ValueError):
            raise ValueError("O ano deve ser um número inteiro.") from None
        if ano < 0:
            raise ValueError("O ano não pode ser negativo.")

        # ENCAPSULAMENTO: atributos privados expostos por @property
        self._codigo = codigo
        self._titulo = titulo
        self._ano = ano
        self._disponivel = True

    @property
    def codigo(self):
        return self._codigo

    @property
    def titulo(self):
        return self._titulo

    @property
    def ano(self):
        return self._ano

    @property
    def disponivel(self):
        return self._disponivel

    def marcar_emprestado(self):
        if not self._disponivel:
            raise ItemIndisponivelError(f"O item '{self._titulo}' já está emprestado.")
        self._disponivel = False

    def marcar_devolvido(self):
        if self._disponivel:
            raise OperacaoInvalidaError(f"O item '{self._titulo}' não está emprestado.")
        self._disponivel = True

    # POLIMORFISMO: métodos abstratos que cada subclasse implementa
    @abstractmethod
    def prazo_dias(self) -> int:
        """Quantos dias o item pode ficar emprestado."""

    @abstractmethod
    def multa_diaria(self) -> float:
        """Valor da multa por dia de atraso."""

    @abstractmethod
    def tipo(self) -> str:
        """Nome do tipo do item (Livro, Revista, DVD)."""

    def descricao(self) -> str:
        return f"[{self.tipo()}] {self._titulo} ({self._ano})"

    def __str__(self):
        return self.descricao()


class Livro(ItemAcervo):
    """HERANÇA: Livro é um ItemAcervo."""

    def __init__(self, codigo, titulo, ano, autor, isbn=""):
        super().__init__(codigo, titulo, ano)
        self.autor = str(autor).strip()
        self.isbn = isbn

    def prazo_dias(self) -> int:
        return 14

    def multa_diaria(self) -> float:
        return 1.00

    def tipo(self) -> str:
        return "Livro"

    def descricao(self) -> str:
        # POLIMORFISMO: sobrescreve e reaproveita a descrição da classe-mãe
        return f"{super().descricao()} - {self.autor}"


class Revista(ItemAcervo):
    """HERANÇA: Revista é um ItemAcervo."""

    def __init__(self, codigo, titulo, ano, edicao):
        super().__init__(codigo, titulo, ano)
        self.edicao = int(edicao)

    def prazo_dias(self) -> int:
        return 7

    def multa_diaria(self) -> float:
        return 0.50

    def tipo(self) -> str:
        return "Revista"

    def descricao(self) -> str:
        return f"{super().descricao()} - edição {self.edicao}"


class DVD(ItemAcervo):
    """HERANÇA: DVD é um ItemAcervo."""

    def __init__(self, codigo, titulo, ano, duracao_min):
        super().__init__(codigo, titulo, ano)
        self.duracao_min = int(duracao_min)

    def prazo_dias(self) -> int:
        return 3

    def multa_diaria(self) -> float:
        return 2.00

    def tipo(self) -> str:
        return "DVD"

    def descricao(self) -> str:
        return f"{super().descricao()} - {self.duracao_min} min"
