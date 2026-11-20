"""Testes das FUNCIONALIDADES do sistema."""

from datetime import date, timedelta

import pytest

from biblioteca import (
    DVD, Aluno, CadastroDuplicadoError, ExportadorCSV, ExportadorTexto,
    ItemIndisponivelError, LimiteEmprestimosError, Livro, NaoEncontradoError,
    OperacaoInvalidaError,
)
from tests.conftest import HOJE

# -------------------------------------------------------------- cadastros

def test_cadastrar_item_e_membro(bib):
    bib.cadastrar_item(Livro("L9", "Memórias Póstumas", 1881, "Machado de Assis"))
    bib.cadastrar_membro(Aluno("Bruno", "11122233344", "A002", "ADS"))
    assert bib.buscar_item("L9").titulo == "Memórias Póstumas"
    assert bib.buscar_membro("A002").nome == "Bruno"
    assert len(bib.itens) == 4 and len(bib.membros) == 3


def test_item_duplicado(bib):
    with pytest.raises(CadastroDuplicadoError):
        bib.cadastrar_item(Livro("L1", "Outro", 2000, "Autor"))


def test_membro_duplicado(bib):
    with pytest.raises(CadastroDuplicadoError):
        bib.cadastrar_membro(Aluno("Outra", "11122233344", "A001", "ADS"))


def test_busca_inexistente(bib):
    with pytest.raises(NaoEncontradoError):
        bib.buscar_item("ZZZ")
    with pytest.raises(NaoEncontradoError):
        bib.buscar_membro("ZZZ")

# --------------------------------------------------------------- remoções

def test_remover_item_e_membro(bib):
    bib.remover_item("R1")
    bib.remover_membro("P001")
    with pytest.raises(NaoEncontradoError):
        bib.buscar_item("R1")
    with pytest.raises(NaoEncontradoError):
        bib.buscar_membro("P001")


def test_nao_remove_item_emprestado(bib):
    bib.emprestar("L1", "A001", HOJE)
    with pytest.raises(OperacaoInvalidaError):
        bib.remover_item("L1")


def test_nao_remove_membro_com_emprestimo(bib):
    bib.emprestar("L1", "A001", HOJE)
    with pytest.raises(OperacaoInvalidaError):
        bib.remover_membro("A001")
    bib.devolver("L1", HOJE)
    bib.remover_membro("A001")  # depois de devolver, pode remover

# --------------------------------------------------------------- pesquisa

def test_pesquisa_sem_diferenciar_maiusculas(bib):
    assert [i.codigo for i in bib.pesquisar("MACHADO")] == ["L1"]
    assert [i.codigo for i in bib.pesquisar("dvd")] == ["D1"]
    assert bib.pesquisar("inexistente") == []


def test_itens_disponiveis(bib):
    bib.emprestar("D1", "A001", HOJE)
    assert {i.codigo for i in bib.itens_disponiveis()} == {"L1", "R1"}

# ------------------------------------------------------------ empréstimos

@pytest.mark.parametrize("codigo, data_prevista", [
    ("L1", date(2026, 11, 15)),
    ("R1", date(2026, 11, 8)),
    ("D1", date(2026, 11, 4)),
])
def test_prazo_por_tipo(bib, codigo, data_prevista):
    assert bib.emprestar(codigo, "A001", HOJE).data_prevista == data_prevista


def test_item_indisponivel(bib):
    bib.emprestar("L1", "A001", HOJE)
    with pytest.raises(ItemIndisponivelError):
        bib.emprestar("L1", "P001", HOJE)


def test_item_marcar_emprestado_duas_vezes(livro):
    livro.marcar_emprestado()
    with pytest.raises(ItemIndisponivelError):
        livro.marcar_emprestado()


def test_item_devolvido_sem_estar_emprestado(livro):
    with pytest.raises(OperacaoInvalidaError):
        livro.marcar_devolvido()


def test_limite_do_aluno_e_professor_ainda_consegue(bib):
    bib.cadastrar_item(DVD("D2", "Tropa de Elite", 2007, 115))
    for codigo in ("L1", "R1", "D1"):
        bib.emprestar(codigo, "A001", HOJE)
    with pytest.raises(LimiteEmprestimosError):
        bib.emprestar("D2", "A001", HOJE)
    bib.emprestar("D2", "P001", HOJE)  # professor tem limite 10
    assert len(bib.emprestimos_do_membro("P001")) == 1


def test_carteirinha_vencida_bloqueia(bib, aluno):
    vencida = aluno.carteirinha.validade + timedelta(days=1)
    with pytest.raises(OperacaoInvalidaError):
        bib.emprestar("L1", "A001", vencida)


def test_data_padrao_e_hoje(bib):
    emp = bib.emprestar("L1", "A001")
    assert emp.data_emprestimo == date.today()

# ------------------------------------------------------------- devoluções

def test_devolucao_sem_multa(bib, livro):
    bib.emprestar("L1", "A001", HOJE)
    assert bib.devolver("L1", HOJE + timedelta(days=14)) == 0.0
    assert livro.disponivel


def test_devolucao_com_multa(bib):
    bib.emprestar("D1", "A001", HOJE)  # prazo 3 dias, R$ 2,00/dia
    assert bib.devolver("D1", date(2026, 11, 6)) == 4.00


def test_devolucao_com_desconto_professor(bib):
    bib.emprestar("D1", "P001", HOJE)
    assert bib.devolver("D1", date(2026, 11, 6)) == 2.00


def test_devolver_duas_vezes_e_item_nao_emprestado(bib):
    emp = bib.emprestar("L1", "A001", HOJE)
    emp.devolver(HOJE)
    with pytest.raises(OperacaoInvalidaError):
        emp.devolver(HOJE)
    with pytest.raises(OperacaoInvalidaError):
        bib.devolver("L1", HOJE)


def test_devolucao_antes_do_emprestimo(bib):
    bib.emprestar("L1", "A001", HOJE)
    with pytest.raises(OperacaoInvalidaError):
        bib.devolver("L1", HOJE - timedelta(days=1))


def test_total_multas(bib):
    bib.emprestar("D1", "A001", HOJE)
    bib.emprestar("R1", "A001", HOJE)
    bib.devolver("D1", date(2026, 11, 6))   # prevista 04/11 -> 2 dias x 2,00 = 4,00
    bib.devolver("R1", date(2026, 11, 10))  # prevista 08/11 -> 2 dias x 0,50 = 1,00
    assert bib.total_multas() == 5.00


def test_atrasados(bib):
    emp_dvd = bib.emprestar("D1", "A001", HOJE)
    bib.emprestar("L1", "A001", HOJE)
    dia = date(2026, 11, 5)
    assert bib.atrasados(dia) == [emp_dvd]
    assert emp_dvd.atrasado_em(dia)
    bib.devolver("D1", dia)
    assert bib.atrasados(dia) == []


def test_emprestimos_ativos_e_do_membro(bib):
    bib.emprestar("L1", "A001", HOJE)
    bib.emprestar("R1", "P001", HOJE)
    assert len(bib.emprestimos_ativos()) == 2
    assert [e.item.codigo for e in bib.emprestimos_do_membro("A001")] == ["L1"]

# -------------------------------------------------------------- relatório

def test_relatorio_texto(bib):
    bib.emprestar("L1", "A001", HOJE)
    texto = bib.gerar_relatorio(ExportadorTexto())
    assert "RELATÓRIO - Biblioteca Teste" in texto
    for secao in ("ACERVO", "MEMBROS", "EMPRÉSTIMOS ATIVOS"):
        assert secao in texto
    assert "Aluno: Ana Souza (A001)  - 1/3 empréstimos" in texto
    assert "Dom Casmurro -> Ana Souza (devolver até 15/11/2026)" in texto
    assert "emprestado" in texto
    assert "Total de multas: R$ 0.00" in texto


def test_relatorio_csv(bib):
    bib.emprestar("L1", "A001", HOJE)
    linhas = bib.gerar_relatorio(ExportadorCSV()).splitlines()
    assert linhas[0] == "codigo;tipo;titulo;ano;disponivel"
    assert "L1;Livro;Dom Casmurro;1899;nao" in linhas
    assert "D1;DVD;Cidade de Deus;2002;sim" in linhas
    assert len(linhas) == 4
