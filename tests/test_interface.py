"""Testes da interface Tkinter (pulados se não houver display)."""

import pytest

tk = pytest.importorskip("tkinter")

from app import App, dados_exemplo, ler_data  # noqa: E402
from biblioteca import BibliotecaError  # noqa: E402


@pytest.fixture
def app():
    try:
        janela = App(dados_exemplo())
    except tk.TclError:
        pytest.skip("Sem display disponível para o Tkinter")
    janela.withdraw()
    janela.erros, janela.infos = [], []
    janela.mostrar_erro = janela.erros.append
    janela.mostrar_info = janela.infos.append
    yield janela
    janela.destroy()


def preencher(entry, texto):
    entry.delete(0, "end")
    entry.insert(0, texto)


def cadastrar_item(app, tipo, codigo, titulo, ano, extra):
    app.tipo_item.set(tipo)
    app._mudar_tipo_item()
    preencher(app.ent_codigo, codigo)
    preencher(app.ent_titulo, titulo)
    preencher(app.ent_ano, ano)
    preencher(app.ent_extra_item, extra)
    return app.cadastrar_item()


@pytest.mark.parametrize("tipo, codigo, extra, rotulo", [
    ("Livro", "L9", "José de Alencar", "Autor"),
    ("Revista", "R9", "12", "Edição"),
    ("DVD", "D9", "120", "Duração (min)"),
])
def test_cadastrar_cada_tipo_pela_tela(app, tipo, codigo, extra, rotulo):
    assert cadastrar_item(app, tipo, codigo, "Teste", "2020", extra)
    assert app.lbl_extra_item.cget("text") == rotulo
    assert app.bib.buscar_item(codigo).tipo() == tipo
    assert app.tree_itens.exists(codigo)
    assert app.infos and not app.erros


def test_cadastro_invalido_mostra_erro(app):
    assert not cadastrar_item(app, "Livro", "", "Sem código", "2020", "Autor")
    assert not cadastrar_item(app, "Livro", "L1", "Duplicado", "2020", "Autor")
    assert len(app.erros) == 2 and not app.infos


def test_pesquisa_filtra_tabela(app):
    app.var_pesquisa.set("machado")
    assert app.tree_itens.get_children() == ("L1",)
    app.var_pesquisa.set("")
    assert len(app.tree_itens.get_children()) == 4


def test_cadastrar_e_remover_membro(app):
    app.tipo_membro.set("Professor")
    app._mudar_tipo_membro()
    assert app.lbl_extra_membro.cget("text") == "Departamento"
    preencher(app.ent_nome, "Maria Silva")
    preencher(app.ent_cpf, "111.222.333-44")
    preencher(app.ent_matricula, "P002")
    preencher(app.ent_extra_membro, "Matemática")
    assert app.cadastrar_membro()
    valores = app.tree_membros.item("P002", "values")
    assert valores[1] == "Professor" and valores[5] == "0/10"

    app.tree_membros.selection_set("P002")
    assert app.remover_membro()
    assert not app.tree_membros.exists("P002")


def test_remover_sem_selecao(app):
    assert not app.remover_item()
    assert not app.remover_membro()
    assert len(app.erros) == 2


def test_remover_item_selecionado(app):
    app.tree_itens.selection_set("L2")
    assert app.remover_item()
    assert not app.tree_itens.exists("L2")


def emprestar(app, item, membro, data):
    app.cb_item.set(item)
    app.cb_membro.set(membro)
    preencher(app.ent_data, data)
    return app.emprestar()


def test_emprestimo_e_devolucao_com_multa(app):
    assert "D1 - Cidade de Deus" in app.cb_item["values"]
    assert emprestar(app, "D1 - Cidade de Deus", "A001 - Ana Souza", "01/11/2026")
    assert app.tree_itens.item("D1", "values")[5] == "Emprestado"
    assert app.tree_membros.item("A001", "values")[5] == "1/3"

    preencher(app.ent_data, "06/11/2026")
    assert app.devolver()
    assert "R$ 4.00" in app.infos[-1]
    linha = app.tree_emprestimos.get_children()[0]
    assert app.tree_emprestimos.item(linha, "values")[5] == "Devolvido (R$ 4.00)"


def test_item_indisponivel_pela_tela(app):
    assert emprestar(app, "D1 - Cidade de Deus", "A001 - Ana Souza", "01/11/2026")
    assert not emprestar(app, "D1 - Cidade de Deus", "P001 - Carlos Lima", "01/11/2026")
    assert "já está emprestado" in app.erros[-1]


def test_filtro_de_atrasados(app):
    emprestar(app, "D1 - Cidade de Deus", "A001 - Ana Souza", "01/11/2026")  # atrasado
    emprestar(app, "L1 - Dom Casmurro", "A001 - Ana Souza", "")               # hoje: em dia
    assert len(app.tree_emprestimos.get_children()) == 2
    app.var_atrasados.set(True)
    app.atualizar_emprestimos()
    linhas = app.tree_emprestimos.get_children()
    assert len(linhas) == 1
    assert app.tree_emprestimos.item(linhas[0], "values")[5] == "ATRASADO"


def test_data_invalida(app):
    assert not emprestar(app, "L1 - Dom Casmurro", "A001 - Ana Souza", "31/02/2026")
    assert app.erros[-1] == "Data inválida. Use o formato dd/mm/aaaa."
    with pytest.raises(BibliotecaError):
        ler_data("2026-11-01")


def test_relatorio_texto_e_csv(app):
    app.var_formato.set("Texto")
    texto = app.gerar_relatorio()
    assert texto.startswith("RELATÓRIO - ")
    assert "ACERVO" in app.txt_relatorio.get("1.0", "end")
    app.var_formato.set("CSV")
    csv = app.gerar_relatorio()
    assert csv.splitlines()[0] == "codigo;tipo;titulo;ano;disponivel"
    assert app.txt_relatorio.get("1.0", "end").startswith("codigo;tipo")
