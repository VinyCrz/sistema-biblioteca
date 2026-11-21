"""Itens do acervo.

HERANÇA: Livro, Revista e DVD herdam de ItemAcervo (classe abstrata).
POLIMORFISMO: cada subclasse responde do seu jeito a prazo_dias(),
multa_diaria(), tipo() e descricao().
"""

from abc import ABC, abstractmethod

from .excecoes import ItemIndisponivelError, OperacaoInvalidaError


def inteiro_positivo(valor, nome):
    """Converte para int (>= 0) com mensagem de erro em português."""
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{nome} deve ser um número inteiro.") from None
    if numero < 0:
        raise ValueError(f"{nome} não pode ser negativo.")
    return numero


class ItemAcervo(ABC):
    """Classe abstrata: representa qualquer item que pode ser emprestado."""

    def __init__(self, codigo, titulo, ano):
        codigo = str(codigo).strip()
        if not codigo:
            raise ValueError("O código do item é obrigatório.")

        # ENCAPSULAMENTO: atributos privados expostos por @property
        self._codigo = codigo
        self._titulo = self._validar_titulo(titulo)
        self._ano = inteiro_positivo(ano, "O ano")
        self._disponivel = True

    @staticmethod
    def _validar_titulo(titulo):
        titulo = str(titulo).strip()
        if not titulo:
            raise ValueError("O título do item é obrigatório.")
        return titulo

    def alterar(self, titulo, ano, extra):
        """Altera os dados do item (o código não muda).

        Valida tudo antes de alterar, para não deixar o objeto pela metade.
        """
        titulo = self._validar_titulo(titulo)
        ano = inteiro_positivo(ano, "O ano")
        extra = self._validar_extra(extra)
        self._titulo, self._ano = titulo, ano
        self._definir_extra(extra)

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

    # POLIMORFISMO: cada tipo tem um campo extra diferente (autor/edição/duração)
    @abstractmethod
    def rotulo_extra(self) -> str:
        """Nome do campo extra do tipo (ex.: 'Autor')."""

    @abstractmethod
    def valor_extra(self):
        """Valor atual do campo extra."""

    @abstractmethod
    def _validar_extra(self, valor):
        """Valida e converte o campo extra."""

    @abstractmethod
    def _definir_extra(self, valor):
        """Grava o campo extra já validado."""

    def descricao(self) -> str:
        return f"[{self.tipo()}] {self._titulo} ({self._ano})"

    def __str__(self):
        return self.descricao()


class Livro(ItemAcervo):
    """HERANÇA: Livro é um ItemAcervo."""

    def __init__(self, codigo, titulo, ano, autor, isbn=""):
        super().__init__(codigo, titulo, ano)
        self.autor = self._validar_extra(autor)
        self.isbn = isbn

    def rotulo_extra(self) -> str:
        return "Autor"

    def valor_extra(self):
        return self.autor

    def _validar_extra(self, valor):
        return str(valor).strip()

    def _definir_extra(self, valor):
        self.autor = valor

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
        self.edicao = self._validar_extra(edicao)

    def rotulo_extra(self) -> str:
        return "Edição"

    def valor_extra(self):
        return self.edicao

    def _validar_extra(self, valor):
        return inteiro_positivo(valor, "A edição")

    def _definir_extra(self, valor):
        self.edicao = valor

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
        self.duracao_min = self._validar_extra(duracao_min)

    def rotulo_extra(self) -> str:
        return "Duração (min)"

    def valor_extra(self):
        return self.duracao_min

    def _validar_extra(self, valor):
        return inteiro_positivo(valor, "A duração")

    def _definir_extra(self, valor):
        self.duracao_min = valor

    def prazo_dias(self) -> int:
        return 3

    def multa_diaria(self) -> float:
        return 2.00

    def tipo(self) -> str:
        return "DVD"

    def descricao(self) -> str:
        return f"{super().descricao()} - {self.duracao_min} min"
