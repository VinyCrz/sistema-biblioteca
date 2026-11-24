"""Testes do banco de dados SQLite (Desk App III).

Cada teste grava num arquivo temporário, fecha o banco e abre de novo,
para provar que os dados ficaram salvos de verdade.
"""

from datetime import date, timedelta

import pytest

from biblioteca import (
    DVD, Aluno, Biblioteca, BibliotecaPersistente, CadastroDuplicadoError, Livro,
    Professor, RepositorioSQLite, Revista,
)

from .conftest import HOJE


@pytest.fixture
def caminho(tmp_path):
    return tmp_path / "teste.db"


def abrir(caminho):
    return BibliotecaPersistente("Teste", RepositorioSQLite(caminho))


def reabrir(bib, caminho):
    bib.repositorio.fechar()
    return abrir(caminho)


@pytest.fixture
def bib(caminho):
    b = abrir(caminho)
    b.cadastrar_item(Livro("L1", "Dom Casmurro", 1899, "Machado de Assis", "978-85"))
    b.cadastrar_item(Revista("R1", "Superinteressante", 2024, 450))
    b.cadastrar_item(DVD("D1", "Cidade de Deus", 2002, 130))
    b.cadastrar_membro(Aluno("Ana Souza", "123.456.789-00", "A001", "Sistemas"))
    b.cadastrar_membro(Professor("Carlos Lima", "98765432100", "P001", "Computação"))
    yield b
    b.repositorio.fechar()


def test_heranca_biblioteca_persistente(bib):
    assert isinstance(bib, Biblioteca)  # HERANÇA: continua sendo uma Biblioteca
    assert isinstance(bib.repositorio, RepositorioSQLite)


def test_banco_cria_as_tabelas(caminho):
    repo = RepositorioSQLite(caminho)
    tabelas = {r["name"] for r in repo.consultar("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"itens", "membros", "emprestimos"} <= tabelas
    assert repo.vazio()
    repo.fechar()


def test_cadastros_sobrevivem_ao_fechar(bib, caminho):
    nova = reabrir(bib, caminho)
    assert [i.codigo for i in nova.itens] == ["L1", "R1", "D1"]
    livro, revista, dvd = nova.itens
    assert (type(livro), livro.autor, livro.isbn) == (Livro, "Machado de Assis", "978-85")
    assert (type(revista), revista.edicao) == (Revista, 450)
    assert (type(dvd), dvd.duracao_min) == (DVD, 130)
    ana, carlos = nova.membros
    assert (type(ana), ana.curso, ana.cpf) == (Aluno, "Sistemas", "12345678900")
    assert (type(carlos), carlos.departamento) == (Professor, "Computação")
    assert carlos.desconto_multa() == 0.5  # POLIMORFISMO continua funcionando
    nova.repositorio.fechar()


def test_carteirinha_volta_com_numero_e_validade(bib, caminho):
    numero = bib.buscar_membro("A001").carteirinha.numero
    bib.renovar_carteirinha("A001", date(2027, 1, 1))
    nova = reabrir(bib, caminho)
    cart = nova.buscar_membro("A001").carteirinha
    assert cart.numero == numero
    assert cart.validade == date(2028, 1, 1)
    # um membro novo recebe um número que ainda não existe no banco
    nova.cadastrar_membro(Aluno("Bruno", "11122233344", "A002", "ADS"))
    numeros = [m.carteirinha.numero for m in nova.membros]
    assert len(set(numeros)) == 3
    nova.repositorio.fechar()


def test_edicao_e_gravada(bib, caminho):
    bib.editar_item("R1", "Super", 2025, "451")
    bib.editar_membro("P001", "Carlos L.", "98765432100", "Matemática")
    nova = reabrir(bib, caminho)
    revista = nova.buscar_item("R1")
    assert (revista.titulo, revista.ano, revista.edicao) == ("Super", 2025, 451)
    assert nova.buscar_membro("P001").departamento == "Matemática"
    nova.repositorio.fechar()


def test_emprestimo_e_devolucao_com_multa_sao_gravados(bib, caminho):
    bib.emprestar("D1", "A001", HOJE)
    bib.devolver("D1", HOJE + timedelta(days=5))    # 2 dias de atraso: R$ 4,00
    bib.emprestar("L1", "A001", HOJE)               # continua emprestado
    nova = reabrir(bib, caminho)
    assert nova.total_multas() == 4.0
    assert not nova.buscar_item("L1").disponivel
    assert nova.buscar_item("D1").disponivel
    ativo = nova.emprestimo_ativo_do_item("L1")
    assert ativo.membro is nova.buscar_membro("A001")  # ASSOCIAÇÃO refeita
    assert ativo.data_prevista == HOJE + timedelta(days=14)
    # dá para devolver depois de reabrir, e isso também é gravado
    assert nova.devolver("L1", HOJE + timedelta(days=16)) == 2.0
    outra = reabrir(nova, caminho)
    assert outra.total_multas() == 6.0 and not outra.emprestimos_ativos()
    outra.repositorio.fechar()


def test_regras_continuam_valendo_depois_de_reabrir(bib, caminho):
    for codigo in ("L1", "R1", "D1"):
        bib.emprestar(codigo, "A001", HOJE)
    nova = reabrir(bib, caminho)
    nova.cadastrar_item(Livro("L2", "Clean Code", 2008, "Martin"))
    with pytest.raises(Exception, match="limite de 3"):
        nova.emprestar("L2", "A001", HOJE)
    with pytest.raises(CadastroDuplicadoError):
        nova.cadastrar_item(Livro("L1", "Outro", 2000, "X"))
    nova.repositorio.fechar()


def test_remocao_mantem_historico(bib, caminho):
    bib.emprestar("D1", "P001", HOJE)
    bib.devolver("D1", HOJE + timedelta(days=4))     # 1 dia × R$ 2 × 50% = R$ 1,00
    bib.remover_item("D1")
    bib.remover_membro("P001")
    nova = reabrir(bib, caminho)
    assert "D1" not in [i.codigo for i in nova.itens]
    assert "P001" not in [m.matricula for m in nova.membros]
    assert len(nova.emprestimos) == 1 and nova.total_multas() == 1.0
    linha = nova.repositorio.consultar("SELECT ativo FROM itens WHERE codigo = 'D1'")[0]
    assert linha["ativo"] == 0
    # o código pode ser cadastrado de novo
    nova.cadastrar_item(DVD("D1", "Central do Brasil", 1998, 110))
    outra = reabrir(nova, caminho)
    assert outra.buscar_item("D1").titulo == "Central do Brasil"
    outra.repositorio.fechar()


def test_erro_de_regra_nao_grava_nada(bib, caminho):
    with pytest.raises(ValueError):
        bib.editar_item("R1", "", 2020, "1")
    with pytest.raises(CadastroDuplicadoError):
        bib.cadastrar_membro(Aluno("Outra", "11122233344", "A001", "X"))
    nova = reabrir(bib, caminho)
    assert nova.buscar_item("R1").titulo == "Superinteressante"
    assert nova.buscar_membro("A001").nome == "Ana Souza"
    nova.repositorio.fechar()


def test_limpar_e_descrever(bib, caminho):
    texto = bib.repositorio.descrever()
    assert "TABELA ITENS (3 registros)" in texto and "Dom Casmurro" in texto
    bib.repositorio.limpar()
    assert bib.repositorio.vazio()
    nova = reabrir(bib, caminho)
    assert nova.itens == [] and nova.membros == [] and nova.emprestimos == []
    nova.repositorio.fechar()


def test_chave_estrangeira_ativa(bib):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        bib.repositorio._con.execute(
            "INSERT INTO emprestimos (codigo_item, matricula, data_emprestimo, data_prevista) "
            "VALUES ('XX', 'A001', '2026-01-01', '2026-01-02')")
