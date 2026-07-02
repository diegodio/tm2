"""EQUIPE DE CADA TURMA — edite com os nomes reais.

Estes nomes são apenas para EXIBIÇÃO no cabeçalho da página da turma
(quem é o professor conselheiro e a pedagoga responsável).

As PERMISSÕES de edição não vêm daqui — vêm de config/usuarios.py
(campo "conselheiro_de" de cada professor, e os papéis diretor/pedagoga).

Chave: (turno, turma) — mesmos nomes das pastas em dados/.
"""

EQUIPE_TURMAS = {
    ("matutino", "3A"): {
        "conselheiro": "Prof. Conselheiro do 3A",
        "pedagoga": "Nome da Pedagoga",
    },
    ("vespertino", "1B"): {
        "conselheiro": "Profa. Conselheira do 1B",
        "pedagoga": "Nome da Pedagoga",
    },
}


def equipe_da_turma(turno: str, turma: str) -> dict:
    """Retorna {"conselheiro": ..., "pedagoga": ...} da turma,
    ou dicionário vazio se a turma não estiver cadastrada acima."""
    return EQUIPE_TURMAS.get((turno, turma), {})
