"""Empréstimo de um item para um membro.

ASSOCIAÇÃO: o Emprestimo guarda referências a um Membro e a um ItemAcervo,
que existem independentemente dele.
DEPENDÊNCIA: usa CalculadoraMulta só dentro de devolver().
"""

from datetime import date, timedelta

from .excecoes import OperacaoInvalidaError
from .multa import CalculadoraMulta


class Emprestimo:
    def __init__(self, membro, item, data_emprestimo=None):
        # ASSOCIAÇÃO: o empréstimo aponta para o membro e para o item
        self._membro = membro
        self._item = item
        self._data_emprestimo = data_emprestimo or date.today()
        # POLIMORFISMO: o prazo depende do tipo do item
        self._data_prevista = self._data_emprestimo + timedelta(days=item.prazo_dias())
        self._data_devolucao = None
        self._multa = 0.0
        item.marcar_emprestado()

    @property
    def membro(self):
        return self._membro

    @property
    def item(self):
        return self._item

    @property
    def data_emprestimo(self):
        return self._data_emprestimo

    @property
    def data_prevista(self):
        return self._data_prevista

    @property
    def data_devolucao(self):
        return self._data_devolucao

    @property
    def multa(self):
        return self._multa

    @property
    def ativo(self):
        return self._data_devolucao is None

    def atrasado_em(self, dia) -> bool:
        return self.ativo and dia > self._data_prevista

    def devolver(self, data=None) -> float:
        if not self.ativo:
            raise OperacaoInvalidaError("Este empréstimo já foi devolvido.")
        data = data or date.today()
        if data < self._data_emprestimo:
            raise OperacaoInvalidaError(
                "A data de devolução não pode ser anterior à data do empréstimo."
            )
        # DEPENDÊNCIA: usa a calculadora só aqui, sem guardar como atributo
        self._multa = CalculadoraMulta.calcular(
            self._item, self._membro, self._data_prevista, data
        )
        self._data_devolucao = data
        self._item.marcar_devolvido()
        return self._multa
