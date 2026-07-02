"""Resolução centralizada de caminhos do projeto.

O mapeamento NÃO é mais salvo em disco (a persistência local foi
removida) — o salvamento agora é feito no Firebase (services/firebase.py).
Aqui ficam apenas os caminhos de leitura: dados das turmas e assets.
"""

from pathlib import Path

# Raiz do projeto (pasta que contém app.py)
RAIZ = Path(__file__).resolve().parent.parent

# Pasta com os dados das turmas: dados/<turno>/<turma>/info.json + fotos
DADOS = RAIZ / "dados"

# Pasta de recursos estáticos
ASSETS = RAIZ / "assets"

# Imagem exibida quando o aluno não tem foto na pasta da turma
AVATAR_PADRAO = ASSETS / "avatar_padrao.png"


def pasta_turno(turno: str) -> Path:
    """Pasta de um turno. Ex.: dados/matutino"""
    return DADOS / turno


def pasta_turma(turno: str, turma: str) -> Path:
    """Pasta de uma turma. Ex.: dados/matutino/3A"""
    return DADOS / turno / turma
