"""Testes das RELAÇÕES entre classes (uma seção por relação)."""

from datetime import date, timedelta
from unittest.mock import patch

from biblioteca import (
    Aluno, Biblioteca, CalculadoraMulta, Carteirinha, Emprestimo, Exportador,
)
from tests.conftest import HOJE

# ============================================================ COMPOSIÇÃO

def test_composicao_carteirinha_criada_pelo_membro(aluno):
    assert isinstance(aluno.carteirinha, Carteirinha)
    assert aluno.carteirinha.titular is aluno
    assert aluno.carteirinha.numero.startswith("CART-")


def test_composicao_carteirinha_exclusiva(aluno, professor):
    assert aluno.carteirinha is not professor.carteirinha
    assert aluno.carteirinha.numero != professor.carteirinha.numero


def test_composicao_carteirinha_vale_um_ano(aluno):
    cart = aluno.carteirinha
    assert cart.validade == cart.emissao + timedelta(days=365)
    assert cart.valida_em(cart.validade)
    assert not cart.valida_em(cart.validade + timedelta(days=1))


def test_composicao_biblioteca_cria_e_possui_emprestimos(bib):
    emp = bib.emprestar("L1", "A001", HOJE)
    assert isinstance(emp, Emprestimo)
    assert emp in bib.emprestimos


def test_composicao_lista_exposta_e_copia(bib):
    bib.emprestar("L1", "A001", HOJE)
    copia = bib.emprestimos
    copia.clear()
    assert len(bib.emprestimos) == 1
    bib.itens.clear()
    assert len(bib.itens) == 3

# ============================================================= AGREGAÇÃO

def test_agregacao_item_removido_continua_existindo(bib, livro):
    removido = bib.remover_item("L1")
    assert removido is livro
    assert livro.titulo == "Dom Casmurro"  # o objeto continua vivo


def test_agregacao_item_pode_ir_para_outra_biblioteca(bib, livro):
    bib.remover_item("L1")
    outra = Biblioteca("Filial")
    outra.cadastrar_item(livro)
    assert outra.buscar_item("L1") is livro


def test_agregacao_mesmo_membro_em_duas_bibliotecas(bib, aluno):
    outra = Biblioteca("Filial")
    outra.cadastrar_membro(aluno)
    assert bib.buscar_membro("A001") is outra.buscar_membro("A001")

# ============================================================ ASSOCIAÇÃO

def test_associacao_emprestimo_aponta_para_membro_e_item(aluno, livro):
    emp = Emprestimo(aluno, livro, HOJE)
    assert emp.membro is aluno
    assert emp.item is livro
    assert not livro.disponivel  # o item foi afetado pela associação


def test_associacao_objetos_existem_sem_o_emprestimo(aluno, livro):
    emp = Emprestimo(aluno, livro, HOJE)
    emp.devolver(HOJE)
    del emp
    assert aluno.nome == "Ana Souza"
    assert livro.disponivel

# ============================================================ DEPENDÊNCIA

def test_dependencia_emprestimo_usa_calculadora(aluno, dvd):
    emp = Emprestimo(aluno, dvd, HOJE)
    with patch.object(CalculadoraMulta, "calcular", return_value=99.0) as falso:
        multa = emp.devolver(HOJE + timedelta(days=10))
    assert multa == 99.0
    falso.assert_called_once_with(dvd, aluno, emp.data_prevista, HOJE + timedelta(days=10))


def test_dependencia_calculadora_nao_e_atributo(aluno, dvd):
    emp = Emprestimo(aluno, dvd, HOJE)
    assert not any(isinstance(v, CalculadoraMulta) for v in vars(emp).values())


def test_dependencia_biblioteca_recebe_exportador(bib):
    class ExportadorFalso(Exportador):
        def __init__(self):
            self.recebido = None

        def exportar(self, biblioteca):
            self.recebido = biblioteca
            return "ok"

        def extensao(self):
            return "fake"

    falso = ExportadorFalso()
    assert bib.gerar_relatorio(falso) == "ok"
    assert falso.recebido is bib


def test_dependencia_valores_da_calculadora(livro, aluno, professor):
    prevista = date(2026, 11, 10)
    assert CalculadoraMulta.dias_atraso(prevista, date(2026, 11, 13)) == 3
    assert CalculadoraMulta.dias_atraso(prevista, date(2026, 11, 5)) == 0
    assert CalculadoraMulta.calcular(livro, aluno, prevista, date(2026, 11, 13)) == 3.00
    assert CalculadoraMulta.calcular(livro, professor, prevista, date(2026, 11, 13)) == 1.50
