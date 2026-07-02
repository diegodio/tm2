"""Leitura de diretórios e arquivos de dados (turnos, turmas, alunos).

Os dados de cada turma ficam em dados/<turno>/<turma>/info.json:

    {
        "NOME COMPLETO DO ALUNO": { "numero": 1, "posicao": "(1,1)" },
        "OUTRO ALUNO":            { "numero": 2, "posicao": "(2,1)" }
    }

- "numero"  → número da chamada, exibido no badge do card.
- "posicao" → carteira desejada, no formato "(cadeira,fila)":
      * cadeira: 1..CADEIRAS_POR_FILA  (1 = frente / junto ao professor,
                                        CADEIRAS_POR_FILA = fundo)
      * fila:    1..NUM_FILAS          (1 = extremo esquerdo,
                                        NUM_FILAS = extremo direito)
  Exemplos: "(1,1)" = primeira cadeira da primeira fila (frente-esquerda);
            "(8,5)" = fundo da última fila (fundo-direita).
  Opcional: quem não tiver "posicao" cai nas primeiras carteiras
  VAZIAS que sobrarem.

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


def _ler_info_bruto(turno: str, turma: str) -> dict:
    """Lê o info.json cru. Retorna {} se o arquivo não existir ou for inválido."""
    arquivo = paths.pasta_turma(turno, turma) / "info.json"
    if not arquivo.is_file():
        return {}
    try:
        with arquivo.open(encoding="utf-8") as f:
            dados = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return dados if isinstance(dados, dict) else {}


def carregar_alunos(turno: str, turma: str) -> dict[str, str | None]:
    """Retorna {nome: posicao_desejada} lida do info.json.

    - A posição vem como string no formato "(fila,posicao_na_fila)"
      (por exemplo, "(1,1)"). Se o aluno não tiver o campo "posicao",
      ou se estiver em branco, o valor é None e o aluno será colocado
      em uma das carteiras VAZIAS restantes pelo `gerar_mapeamento_inicial`.
    - Nomes vazios/inválidos são descartados.
    """
    resultado: dict[str, str | None] = {}
    for nome, dados in _ler_info_bruto(turno, turma).items():
        nome_limpo = str(nome).strip()
        if not nome_limpo:
            continue
        posicao: str | None = None
        if isinstance(dados, dict):
            valor = dados.get("posicao")
            if isinstance(valor, str) and valor.strip():
                posicao = valor.strip()
        resultado[nome_limpo] = posicao
    return resultado


def carregar_info(turno: str, turma: str) -> dict[str, dict]:
    """Carrega info.json completo -> {nome: {"numero": ..., "posicao": ...}}.
    Retorna {} se o arquivo não existir ou for inválido."""
    return _ler_info_bruto(turno, turma)
