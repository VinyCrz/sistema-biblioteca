"""Exportação de relatórios.

HERANÇA: ExportadorTexto e ExportadorCSV herdam de Exportador.
POLIMORFISMO: a Biblioteca chama exportar() sem saber qual formato é.
DEPENDÊNCIA: o exportador recebe a biblioteca por parâmetro e só a usa ali.
"""

from abc import ABC, abstractmethod


class Exportador(ABC):
    @abstractmethod
    def exportar(self, biblioteca) -> str:
        """Gera o relatório da biblioteca como texto."""

    @abstractmethod
    def extensao(self) -> str:
        """Extensão sugerida para o arquivo."""


class ExportadorTexto(Exportador):
    def exportar(self, biblioteca) -> str:
        linhas = [f"RELATÓRIO - {biblioteca.nome}", "=" * 40, "", "ACERVO"]
        for item in biblioteca.itens:
            situacao = "disponível" if item.disponivel else "emprestado"
            linhas.append(f"  {item.codigo}  {item.descricao()}  [{situacao}]")

        linhas += ["", "MEMBROS"]
        for membro in biblioteca.membros:
            ativos = len(biblioteca.emprestimos_do_membro(membro.matricula))
            linhas.append(
                f"  {membro}  - {ativos}/{membro.limite_emprestimos()} empréstimos"
            )

        linhas += ["", "EMPRÉSTIMOS ATIVOS"]
        ativos = biblioteca.emprestimos_ativos()
        if not ativos:
            linhas.append("  (nenhum)")
        for emp in ativos:
            linhas.append(
                f"  {emp.item.titulo} -> {emp.membro.nome} "
                f"(devolver até {emp.data_prevista:%d/%m/%Y})"
            )

        linhas += ["", f"Total de multas: R$ {biblioteca.total_multas():.2f}"]
        return "\n".join(linhas)

    def extensao(self) -> str:
        return "txt"


class ExportadorCSV(Exportador):
    def exportar(self, biblioteca) -> str:
        linhas = ["codigo;tipo;titulo;ano;disponivel"]
        for item in biblioteca.itens:
            disp = "sim" if item.disponivel else "nao"
            linhas.append(f"{item.codigo};{item.tipo()};{item.titulo};{item.ano};{disp}")
        return "\n".join(linhas)

    def extensao(self) -> str:
        return "csv"
