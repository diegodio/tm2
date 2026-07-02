"""Leitura de diretórios e arquivos de dados (turnos, turmas, alunos).

Os dados de cada turma ficam em dados/<turno>/<turma>/info.json:

    {
        "NOME COMPLETO DO ALUNO": { "numero": 1 },
        "OUTRO ALUNO":            { "numero": 2 }
    }

"numero" é o número da chamada, exibido no badge do card.
As fotos (opcionais) ficam na mesma pasta, com o nome do aluno:
"NOME COMPLETO DO ALUNO.jpg".
"""
import json

from utils import paths
from utils.constantes import TURNOS


def listar_turnos() -> list[str]:
    """Retorna os turnos que de fato existem em disco, na ordem definida
    em utils/constantes.py (TURNOS)."""
    return [turno for turno in TURNOS if paths.pasta_turno(turno).is_dir()]


def listar_turmas(turno: str) -> list[str]:
    """Lista as turmas (subpastas com info.json) de um turno, em ordem
    alfabética."""
    pasta = paths.pasta_turno(turno)
    if not pasta.is_dir():
        return []
    turmas = [
        p.name
        for p in pasta.iterdir()
        if p.is_dir() and (p / "info.json").is_file()
    ]
    return sorted(turmas)


def carregar_alunos(turno: str, turma: str) -> dict[str, str]:
    """Carrega info.json e retorna {nome: nome} (apenas os nomes válidos).
    Retorna {} se o arquivo não existir ou for inválido."""
    arquivo = paths.pasta_turma(turno, turma) / "info.json"
    if not arquivo.is_file():
        return {}
    try:
        with arquivo.open(encoding="utf-8") as f:
            dados = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return {str(k).strip(): str(k).strip() for k in dados if str(k).strip()}


def carregar_info(turno: str, turma: str) -> dict[str, dict]:
    """Carrega info.json completo -> {nome: {"numero": ...}}.
    Retorna {} se o arquivo não existir ou for inválido."""
    arquivo = paths.pasta_turma(turno, turma) / "info.json"
    if not arquivo.is_file():
        return {}
    try:
        with arquivo.open(encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
