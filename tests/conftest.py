"""Configuração comum dos testes: fixtures e data fixa."""

import os
import sys
from datetime import date

import pytest

# Permite importar o pacote `biblioteca` e o `app` a partir da raiz do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from biblioteca import DVD, Aluno, Biblioteca, Livro, Professor, Revista  # noqa: E402

HOJE = date(2026, 11, 1)  # data fixa para os testes serem previsíveis


@pytest.fixture
def livro():
    return Livro("L1", "Dom Casmurro", 1899, "Machado de Assis")


@pytest.fixture
def revista():
    return Revista("R1", "Superinteressante", 2024, 450)


@pytest.fixture
def dvd():
    return DVD("D1", "Cidade de Deus", 2002, 130)


@pytest.fixture
def aluno():
    return Aluno("Ana Souza", "123.456.789-00", "A001", "Sistemas")


@pytest.fixture
def professor():
    return Professor("Carlos Lima", "98765432100", "P001", "Computação")


@pytest.fixture
def bib(livro, revista, dvd, aluno, professor):
    b = Biblioteca("Biblioteca Teste")
    for item in (livro, revista, dvd):
        b.cadastrar_item(item)
    for membro in (aluno, professor):
        b.cadastrar_membro(membro)
    return b
