"""Mostra no terminal o conteúdo do banco de dados.

Uso:  python3 ver_banco.py               (lê biblioteca.db)
      python3 ver_banco.py outro.db
"""

import os
import sys

from app import BANCO_PADRAO
from biblioteca import RepositorioSQLite

caminho = sys.argv[1] if len(sys.argv) > 1 else BANCO_PADRAO
if not os.path.exists(caminho):
    sys.exit(f"Banco não encontrado: {caminho}. Abra o app uma vez para criá-lo.")
repo = RepositorioSQLite(caminho)
print(repo.descrever())
repo.fechar()
