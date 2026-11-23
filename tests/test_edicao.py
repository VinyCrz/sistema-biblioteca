"""Testes das funcionalidades adicionadas no Desk App II (modelos)."""

from datetime import date, timedelta

import pytest

from biblioteca import NaoEncontradoError

from .conftest import HOJE


@pytest.mark.parametrize("codigo, extra, rotulo, esperado", [
    ("L1", "Machado", "Autor", "Machado"),
    ("R1", "451", "Edição", 451),
    ("D1", "135", "Duração (min)", 135),
])
def test_editar_cada_tipo_de_item(bib, codigo, extra, rotulo, esperado):
    item = bib.editar_item(codigo, "Novo título", "2000", extra)
    assert item.titulo == "Novo título" and item.ano == 2000
    assert item.rotulo_extra() == rotulo  # POLIMORFISMO
    assert item.valor_extra() == esperado
    assert item.codigo == codigo  # o código não muda


def test_editar_item_invalido_nao_altera_nada(bib):
    with pytest.raises(ValueError, match="edição"):
        bib.editar_item("R1", "Outro", 2020, "abc")
    revista = bib.buscar_item("R1")
    assert revista.titulo == "Superinteressante" and revista.edicao == 450
    with pytest.raises(ValueError, match="título"):
        bib.editar_item("L1", "  ", 2020, "x")
    with pytest.raises(ValueError, match="ano"):
        bib.editar_item("L1", "X", "-1", "x")
    with pytest.raises(NaoEncontradoError):
        bib.editar_item("XX", "X", 2000, "x")


def test_mensagens_de_inteiro_em_portugues():
    from biblioteca import DVD, Revista
    with pytest.raises(ValueError, match="A edição deve ser um número inteiro"):
        Revista("R9", "T", 2000, "x")
    with pytest.raises(ValueError, match="A duração não pode ser negativo"):
        DVD("D9", "T", 2000, -5)


@pytest.mark.parametrize("matricula, rotulo", [("A001", "Curso"), ("P001", "Departamento")])
def test_editar_membro(bib, matricula, rotulo):
    numero = bib.buscar_membro(matricula).carteirinha.numero
    m = bib.editar_membro(matricula, "Nome Novo", "111.222.333-44", "Extra")
    assert m.nome == "Nome Novo" and m.cpf == "11122233344"
    assert m.rotulo_extra() == rotulo and m.valor_extra() == "Extra"
    assert m.carteirinha.numero == numero  # COMPOSIÇÃO: continua a mesma carteirinha


def test_editar_membro_invalido(bib):
    with pytest.raises(ValueError, match="CPF"):
        bib.editar_membro("A001", "Ana", "123", "x")
    assert bib.buscar_membro("A001").cpf == "12345678900"
    with pytest.raises(ValueError, match="nome"):
        bib.editar_membro("A001", "", "12345678900", "x")


def test_renovar_carteirinha_libera_emprestimo(bib):
    membro = bib.buscar_membro("A001")
    membro.carteirinha.renovar(HOJE - timedelta(days=400))  # vencida
    assert not membro.carteirinha.valida_em(HOJE)
    carteirinha = bib.renovar_carteirinha("A001", HOJE)
    assert carteirinha.validade == HOJE + timedelta(days=365)
    assert bib.emprestar("L1", "A001", HOJE)


def test_renovar_sem_data_usa_hoje(bib):
    c = bib.renovar_carteirinha("P001")
    assert c.emissao == date.today()


def test_itens_emprestados_e_historico(bib):
    bib.emprestar("L1", "A001", HOJE)
    bib.emprestar("D1", "A001", HOJE)
    bib.devolver("D1", HOJE + timedelta(days=5))
    assert [i.codigo for i in bib.itens_emprestados()] == ["L1"]
    historico = bib.historico_do_membro("A001")
    assert len(historico) == 2 and len(bib.emprestimos_do_membro("A001")) == 1
    assert bib.historico_do_membro("P001") == []
    with pytest.raises(NaoEncontradoError):
        bib.historico_do_membro("X")


def test_resumo(bib):
    bib.emprestar("D1", "A001", HOJE)
    r = bib.resumo(HOJE + timedelta(days=10))
    assert r == {"itens": 3, "disponiveis": 2, "membros": 2, "ativos": 1,
                 "atrasados": 1, "emprestimos": 1, "multas": 0.0}
