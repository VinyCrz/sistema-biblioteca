"""Pessoas do sistema.

HERANÇA: Pessoa -> Membro -> Aluno / Professor.
POLIMORFISMO: limite_emprestimos() e desconto_multa() mudam conforme o tipo.
COMPOSIÇÃO: todo Membro cria a sua própria Carteirinha no construtor.
"""

from abc import ABC, abstractmethod
from datetime import date, timedelta


class Pessoa(ABC):
    """Classe abstrata com os dados comuns a qualquer pessoa."""

    def __init__(self, nome, cpf):
        nome = str(nome).strip()
        if not nome:
            raise ValueError("O nome é obrigatório.")
        digitos = "".join(c for c in str(cpf) if c.isdigit())
        if len(digitos) != 11:
            raise ValueError("O CPF deve ter 11 dígitos.")
        self._nome = nome
        self._cpf = digitos  # guarda só os números

    @property
    def nome(self):
        return self._nome

    @property
    def cpf(self):
        return self._cpf

    @abstractmethod
    def tipo(self) -> str:
        """Nome do tipo da pessoa."""


class Carteirinha:
    """Documento do membro. Só existe junto com um Membro (composição)."""

    _proximo_numero = 1  # contador compartilhado para numeração sequencial

    def __init__(self, titular, emissao=None):
        self.numero = f"CART-{Carteirinha._proximo_numero:04d}"
        Carteirinha._proximo_numero += 1
        self.titular = titular
        self.emissao = emissao or date.today()
        self.validade = self.emissao + timedelta(days=365)

    def valida_em(self, dia) -> bool:
        # Só verifica o vencimento (permite registrar empréstimos retroativos)
        return dia <= self.validade

    def __str__(self):
        return self.numero


class Membro(Pessoa, ABC):
    """Pessoa que pode pegar itens emprestados."""

    def __init__(self, nome, cpf, matricula):
        super().__init__(nome, cpf)
        matricula = str(matricula).strip()
        if not matricula:
            raise ValueError("A matrícula é obrigatória.")
        self._matricula = matricula
        # COMPOSIÇÃO: a carteirinha nasce junto com o membro
        self._carteirinha = Carteirinha(self)

    @property
    def matricula(self):
        return self._matricula

    @property
    def carteirinha(self):
        return self._carteirinha

    # POLIMORFISMO: cada tipo de membro define seu limite
    @abstractmethod
    def limite_emprestimos(self) -> int:
        """Quantos itens o membro pode ter ao mesmo tempo."""

    def desconto_multa(self) -> float:
        """Percentual de desconto na multa (0.0 a 1.0). Padrão: sem desconto."""
        return 0.0

    def __str__(self):
        return f"{self.tipo()}: {self._nome} ({self._matricula})"


class Aluno(Membro):
    """HERANÇA: Aluno é um Membro."""

    def __init__(self, nome, cpf, matricula, curso):
        super().__init__(nome, cpf, matricula)
        self.curso = curso

    def tipo(self) -> str:
        return "Aluno"

    def limite_emprestimos(self) -> int:
        return 3


class Professor(Membro):
    """HERANÇA: Professor é um Membro, com limite maior e desconto na multa."""

    def __init__(self, nome, cpf, matricula, departamento):
        super().__init__(nome, cpf, matricula)
        self.departamento = departamento

    def tipo(self) -> str:
        return "Professor"

    def limite_emprestimos(self) -> int:
        return 10

    def desconto_multa(self) -> float:
        # POLIMORFISMO: professor paga só metade da multa
        return 0.5
