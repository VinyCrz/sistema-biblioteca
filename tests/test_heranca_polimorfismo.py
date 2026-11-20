"""Testes de HERANÇA e POLIMORFISMO."""

import pytest

from biblioteca import (
    DVD, Aluno, BibliotecaError, Exportador, ExportadorCSV, ExportadorTexto,
    ItemAcervo, ItemIndisponivelError, Livro, Membro, NaoEncontradoError,
    Pessoa, Professor, Revista,
)

# ---------------------------------------------------------------- herança

def test_itens_herdam_de_item_acervo(livro, revista, dvd):
    for item in (livro, revista, dvd):
        assert isinstance(item, ItemAcervo)
    assert issubclass(Livro, ItemAcervo)
    assert issubclass(Revista, ItemAcervo)
    assert issubclass(DVD, ItemAcervo)


def test_membros_herdam_de_membro_e_pessoa(aluno, professor):
    for membro in (aluno, professor):
        assert isinstance(membro, Membro)
        assert isinstance(membro, Pessoa)
    assert issubclass(Membro, Pessoa)


def test_exportadores_herdam_de_exportador():
    assert issubclass(ExportadorTexto, Exportador)
    assert issubclass(ExportadorCSV, Exportador)


def test_excecoes_herdam_de_biblioteca_error():
    assert issubclass(ItemIndisponivelError, BibliotecaError)
    assert issubclass(NaoEncontradoError, BibliotecaError)


@pytest.mark.parametrize("classe, args", [
    (ItemAcervo, ("X", "Título", 2000)),
    (Pessoa, ("Nome", "12345678900")),
    (Membro, ("Nome", "12345678900", "M1")),
    (Exportador, ()),
])
def test_classes_abstratas_nao_instanciam(classe, args):
    with pytest.raises(TypeError):
        classe(*args)

# ----------------------------------------------------------- polimorfismo

@pytest.mark.parametrize("fixture, prazo, multa, tipo", [
    ("livro", 14, 1.00, "Livro"),
    ("revista", 7, 0.50, "Revista"),
    ("dvd", 3, 2.00, "DVD"),
])
def test_prazo_multa_e_tipo_por_item(request, fixture, prazo, multa, tipo):
    item = request.getfixturevalue(fixture)
    assert item.prazo_dias() == prazo
    assert item.multa_diaria() == multa
    assert item.tipo() == tipo


def test_descricao_sobrescrita(livro, revista, dvd):
    assert livro.descricao() == "[Livro] Dom Casmurro (1899) - Machado de Assis"
    assert revista.descricao() == "[Revista] Superinteressante (2024) - edição 450"
    assert dvd.descricao() == "[DVD] Cidade de Deus (2002) - 130 min"
    assert str(livro) == livro.descricao()


def test_revista_converte_edicao_para_int():
    assert Revista("R9", "Veja", 2020, "12").edicao == 12


def test_limites_e_descontos_dos_membros(aluno, professor):
    assert aluno.limite_emprestimos() == 3
    assert professor.limite_emprestimos() == 10
    assert aluno.desconto_multa() == 0.0
    assert professor.desconto_multa() == 0.5


def test_str_do_membro_usa_tipo(aluno, professor):
    assert str(aluno) == "Aluno: Ana Souza (A001)"
    assert str(professor) == "Professor: Carlos Lima (P001)"


def test_exportadores_polimorficos(bib):
    resultados = {e.extensao(): bib.gerar_relatorio(e)
                  for e in (ExportadorTexto(), ExportadorCSV())}
    assert resultados["txt"].startswith("RELATÓRIO - Biblioteca Teste")
    assert resultados["csv"].startswith("codigo;tipo;titulo;ano;disponivel")

# ------------------------------------------------------------- validações

@pytest.mark.parametrize("codigo, titulo, ano", [
    ("", "Título", 2000),
    ("X1", "   ", 2000),
    ("X1", "Título", -1),
    ("X1", "Título", "abc"),
])
def test_validacoes_do_item(codigo, titulo, ano):
    with pytest.raises(ValueError):
        Livro(codigo, titulo, ano, "Autor")


def test_cpf_guarda_so_digitos(aluno):
    assert aluno.cpf == "12345678900"


@pytest.mark.parametrize("nome, cpf, matricula", [
    ("", "12345678900", "A9"),
    ("Fulano", "123", "A9"),
    ("Fulano", "12345678900", ""),
])
def test_validacoes_da_pessoa(nome, cpf, matricula):
    with pytest.raises(ValueError):
        Aluno(nome, cpf, matricula, "Curso")
