"""Cálculo de multas.

DEPENDÊNCIA: o Emprestimo USA a CalculadoraMulta apenas dentro do método
devolver(), sem guardá-la como atributo.
"""


class CalculadoraMulta:
    """Regras de cálculo de multa (só métodos estáticos)."""

    @staticmethod
    def dias_atraso(prevista, devolucao) -> int:
        return max(0, (devolucao - prevista).days)

    @staticmethod
    def calcular(item, membro, prevista, devolucao) -> float:
        dias = CalculadoraMulta.dias_atraso(prevista, devolucao)
        # POLIMORFISMO: multa_diaria() e desconto_multa() variam por tipo
        valor = dias * item.multa_diaria() * (1 - membro.desconto_multa())
        return round(valor, 2)
