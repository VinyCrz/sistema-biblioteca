"""Testes da barra de menu (Desk App II): todo item do menu precisa funcionar."""

import pytest

tk = pytest.importorskip("tkinter")

from app import ABAS, App, dados_exemplo  # noqa: E402
from dialogos import FormularioDialog, JanelaLista, JanelaTexto  # noqa: E402


@pytest.fixture
def app():
    try:
        janela = App(dados_exemplo())
    except tk.TclError:
        pytest.skip("Sem display disponível para o Tkinter")
    janela.withdraw()
    janela.erros, janela.infos, janela.excecoes = [], [], []
    janela.mostrar_erro = janela.erros.append
    janela.mostrar_info = janela.infos.append
    janela.confirmar = lambda msg: True
    janela.pedir_arquivo = lambda exp: ""
    # Erros dentro de callbacks do Tk não sobem sozinhos: guardamos para o teste
    janela.report_callback_exception = lambda *exc: janela.excecoes.append(exc)
    yield janela
    janela.destroy()


def entradas_do_menu(menu):
    """Lista (rótulo, índice, submenu) de todas as entradas com comando."""
    resultado = []
    for i in range(menu.index("end") + 1):
        tipo = menu.type(i)
        if tipo == "command":
            resultado.append((menu.entrycget(i, "label"), i, menu))
        elif tipo == "cascade":
            sub = menu.nametowidget(menu.entrycget(i, "menu"))
            resultado += entradas_do_menu(sub)
    return resultado


def fechar_janelas(app):
    for filho in app.winfo_children():
        if isinstance(filho, tk.Toplevel):
            filho.destroy()


def test_menu_tem_todos_os_grupos(app):
    barra = app.barra_menu
    nomes = [barra.entrycget(i, "label") for i in range(barra.index("end") + 1)]
    assert nomes == ["Arquivo", "Cadastros", "Movimentação", "Consultas",
                     "Relatórios", "Exibir", "Ajuda"]


def test_menu_da_acesso_a_todos_os_modelos(app):
    rotulos = " ".join(r for r, _, _ in entradas_do_menu(app.barra_menu))
    for modelo in ("Livro", "Revista", "DVD", "Aluno", "Professor", "carteirinha",
                   "Emprestar", "Devolver", "Texto", "CSV"):
        assert modelo in rotulos


def test_todas_as_entradas_do_menu_funcionam(app):
    """Aciona cada comando do menu (menos Sair) e verifica que nenhum quebra."""
    entradas = [e for e in entradas_do_menu(app.barra_menu) if e[0] != "Sair"]
    assert len(entradas) >= 30
    for rotulo, indice, menu in entradas:
        menu.invoke(indice)
        assert not app.excecoes, f"Erro ao acionar '{rotulo}': {app.excecoes}"
        fechar_janelas(app)


def test_cadastrar_cada_tipo_pelo_menu(app):
    for tipo, codigo, extra in (("Livro", "L9", "Autor"), ("Revista", "R9", "3"), ("DVD", "D9", "90")):
        dlg = app.abrir_novo_item(tipo)
        assert isinstance(dlg, FormularioDialog)
        for chave, valor in (("codigo", codigo), ("titulo", "Teste"), ("ano", "2020"), ("extra", extra)):
            dlg.definir(chave, valor)
        assert dlg.confirmar()
        assert app.bib.buscar_item(codigo).tipo() == tipo
    for tipo, mat in (("Aluno", "A9"), ("Professor", "P9")):
        dlg = app.abrir_novo_membro(tipo)
        for chave, valor in (("nome", "Fulano"), ("cpf", "11122233344"), ("matricula", mat), ("extra", "X")):
            dlg.definir(chave, valor)
        assert dlg.confirmar()
        assert app.bib.buscar_membro(mat).tipo() == tipo
    assert app.tree_itens.exists("D9") and app.tree_membros.exists("P9")


def test_formulario_com_erro_continua_aberto(app):
    dlg = app.abrir_novo_item("Livro")
    dlg.definir("codigo", "L1")  # duplicado
    dlg.definir("titulo", "X")
    dlg.definir("ano", "2000")
    assert not dlg.confirmar()
    assert dlg.winfo_exists() and app.erros


def test_editar_item_pelo_menu_usa_selecao_da_tabela(app):
    app.tree_itens.selection_set("R1")
    dlg = app.abrir_editar_item()
    assert dlg.entradas["item"].get() == "R1 - Superinteressante"
    assert dlg.rotulos["extra"].cget("text") == "Edição"
    assert dlg.entradas["extra"].get() == "450"
    dlg.definir("titulo", "Super")
    assert dlg.confirmar()
    assert app.bib.buscar_item("R1").titulo == "Super"
    assert "Super" in app.tree_itens.item("R1", "values")[2]


def test_trocar_item_no_editor_recarrega_campos(app):
    dlg = app.abrir_editar_item()
    dlg.definir("item", "D1 - Cidade de Deus")
    dlg._mudou("item")
    assert dlg.entradas["tipo"].get() == "DVD"
    assert dlg.rotulos["extra"].cget("text") == "Duração (min)"
    assert dlg.entradas["extra"].get() == "130"


def test_editar_membro_pelo_menu(app):
    app.tree_membros.selection_set("P001")
    dlg = app.abrir_editar_membro()
    assert dlg.rotulos["extra"].cget("text") == "Departamento"
    dlg.definir("extra", "Matemática")
    assert dlg.confirmar()
    assert app.bib.buscar_membro("P001").departamento == "Matemática"


def test_remover_pelo_menu(app):
    dlg = app.abrir_remover_item()
    dlg.definir("item", "L2 - Clean Code")
    assert dlg.confirmar()
    assert not app.tree_itens.exists("L2")
    dlg = app.abrir_remover_membro()
    dlg.definir("membro", "P001 - Carlos Lima")
    assert dlg.confirmar()
    assert not app.tree_membros.exists("P001")


def test_remover_cancelado_nao_remove(app):
    app.confirmar = lambda msg: False
    dlg = app.abrir_remover_item()
    assert not dlg.confirmar()
    assert len(app.bib.itens) == 4


def test_emprestar_e_devolver_pelo_menu(app):
    dlg = app.abrir_emprestar()
    dlg.definir("item", "D1 - Cidade de Deus")
    dlg.definir("membro", "A001 - Ana Souza")
    dlg.definir("data", "01/11/2026")
    assert dlg.confirmar()
    # o item emprestado não aparece mais para emprestar, só para devolver
    assert "D1 - Cidade de Deus" not in app.abrir_emprestar().entradas["item"]["values"]
    dlg = app.abrir_devolver()
    assert list(dlg.entradas["item"]["values"]) == ["D1 - Cidade de Deus"]
    dlg.definir("data", "06/11/2026")
    assert dlg.confirmar()
    assert "R$ 4.00" in app.infos[-1]


def test_devolver_sem_emprestimos(app):
    assert app.abrir_devolver() is None
    assert "Não há itens emprestados" in app.erros[-1]


def test_renovar_carteirinha_pelo_menu(app):
    dlg = app.abrir_renovar_carteirinha()
    dlg.definir("membro", "A001 - Ana Souza")
    dlg.definir("data", "01/01/2027")
    assert dlg.confirmar()
    assert app.tree_membros.item("A001", "values")[4] == "01/01/2028"


def test_consultas_abrem_listas(app):
    app.bib.emprestar("D1", "A001")
    assert len(app.consultar_acervo("todos").tree.get_children()) == 4
    assert len(app.consultar_acervo("disponiveis").tree.get_children()) == 3
    assert len(app.consultar_acervo("emprestados").tree.get_children()) == 1
    assert len(app.consultar_membros().tree.get_children()) == 2
    cart = app.consultar_carteirinhas()
    assert cart.tree.item(cart.tree.get_children()[0], "values")[5] == "Válida"
    assert len(app.consultar_emprestimos("ativos").tree.get_children()) == 1
    assert len(app.consultar_emprestimos("atrasados").tree.get_children()) == 0
    assert len(app.consultar_emprestimos("todos").tree.get_children()) == 1


def test_pesquisa_e_historico_pelo_menu(app):
    dlg = app.abrir_pesquisa()
    dlg.definir("texto", "machado")
    assert dlg.confirmar()
    assert isinstance(app.ultima_janela, JanelaLista)
    assert len(app.ultima_janela.tree.get_children()) == 1

    app.bib.emprestar("L1", "A001")
    dlg = app.abrir_historico_membro()
    dlg.definir("membro", "A001 - Ana Souza")
    assert dlg.confirmar()
    assert len(app.ultima_janela.tree.get_children()) == 1


def test_relatorio_pelo_menu_vai_para_aba(app):
    texto = app.relatorio_pelo_menu("CSV")
    assert texto.startswith("codigo;tipo")
    assert app.abas.index("current") == ABAS.index("Relatório")


def test_salvar_relatorio(app, tmp_path):
    destino = tmp_path / "rel.txt"
    app.pedir_arquivo = lambda exp: str(destino)
    assert app.salvar_relatorio()
    assert destino.read_text(encoding="utf-8").startswith("RELATÓRIO")


def test_resumo_e_ajuda(app):
    assert "Itens no acervo" in app.mostrar_resumo().txt.get("1.0", "end")
    menu = app.menus["Ajuda"]
    menu.invoke(0)
    assert isinstance(app.ultima_janela, JanelaTexto)
    assert "REGRAS" in app.ultima_janela.txt.get("1.0", "end")


def test_exibir_troca_de_aba(app):
    for i in range(len(ABAS)):
        app.menus["Exibir"].invoke(i)
        assert app.abas.index("current") == i


def test_arquivo_nova_biblioteca_e_exemplo(app):
    assert app.nova_biblioteca()
    assert app.bib.itens == [] and not app.tree_itens.get_children()
    assert "0 itens" in app.var_status.get()
    assert app.abrir_editar_item() is None  # sem itens: avisa em vez de abrir
    assert app.carregar_exemplo()
    assert len(app.tree_itens.get_children()) == 4


def test_sair_pede_confirmacao(app):
    app.confirmar = lambda msg: False
    assert not app.sair()
    assert app.winfo_exists()


def test_barra_de_status(app):
    assert app.var_status.get().startswith("4 itens (4 disponíveis)")
    app.bib.emprestar("L1", "A001")
    app.atualizar_tudo()
    assert "1 empréstimos ativos" in app.var_status.get()


# ------------------------------------------------------------ Desk App III
@pytest.fixture
def app_banco(tmp_path):
    try:
        janela = App(caminho_banco=str(tmp_path / "app.db"))
    except tk.TclError:
        pytest.skip("Sem display disponível para o Tkinter")
    janela.withdraw()
    janela.erros, janela.infos = [], []
    janela.mostrar_erro = janela.erros.append
    janela.mostrar_info = janela.infos.append
    janela.confirmar = lambda msg: True
    yield janela
    repo = janela.repo
    try:
        janela.destroy()
    except tk.TclError:
        pass  # já foi fechada (teste do Sair)
    else:
        repo.fechar()


def test_app_com_banco_grava_e_reabre(app_banco, tmp_path):
    from app import abrir_banco
    assert len(app_banco.bib.itens) == 4        # primeira vez: dados de exemplo gravados
    assert "banco de dados: app.db" in app_banco.var_status.get()
    dlg = app_banco.abrir_novo_item("Livro")
    for chave, valor in (("codigo", "L9"), ("titulo", "Vidas Secas"), ("ano", "1938"), ("extra", "Graciliano")):
        dlg.definir(chave, valor)
    assert dlg.confirmar()
    reaberta = abrir_banco(str(tmp_path / "app.db"))
    assert reaberta.buscar_item("L9").titulo == "Vidas Secas"
    reaberta.repositorio.fechar()


def test_app_nova_biblioteca_limpa_o_banco(app_banco):
    assert app_banco.nova_biblioteca()
    assert app_banco.repo.vazio()
    assert app_banco.carregar_exemplo()
    assert len(app_banco.bib.itens) == 4 and not app_banco.repo.vazio()


def test_ver_banco_pelo_menu(app_banco, app):
    janela = app_banco.ver_banco()
    assert "TABELA EMPRESTIMOS" in janela.txt.get("1.0", "end")
    assert app.ver_banco() is None and "só em memória" in app.erros[-1]


def test_sair_fecha_o_banco(app_banco):
    repo = app_banco.repo
    assert app_banco.sair()
    import sqlite3
    with pytest.raises(sqlite3.ProgrammingError):
        repo.consultar("SELECT 1")
