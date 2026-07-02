"""Salvamento e carregamento do mapeamento no Firebase Realtime Database.

Usa a API REST do Firebase com a biblioteca `requests` — sem SDK.
As credenciais ficam em config/credenciais.py (edite lá).

ESTRUTURA GRAVADA NO BANCO
--------------------------
<FIREBASE_URL>/<FIREBASE_NO_RAIZ>/<turno>/<turma>.json
{
    "mapa": { "(1,1)": "NOME DO ALUNO", "(1,2)": "__VAZIO__", ... },
    "sem_lugar": ["NOME A", "NOME B"]
}

Enquanto o Firebase não estiver configurado (FIREBASE_URL ainda com o
valor de exemplo), salvar_mapeamento() retorna sempre (False, motivo),
e o app exibe "Não salvo" — exatamente o comportamento pedido.
"""
import requests

from config.credenciais import (
    FIREBASE_AUTH_TOKEN,
    FIREBASE_NO_RAIZ,
    FIREBASE_TIMEOUT,
    FIREBASE_URL,
)
from services.mapeamento import (
    Posicao,
    chave_para_posicao,
    posicao_para_chave,
)


def firebase_configurado() -> bool:
    """True se a URL do Firebase parece ter sido preenchida com um valor real."""
    url = (FIREBASE_URL or "").strip()
    return url.startswith("https://") and "SEU_PROJETO" not in url


def _url(turno: str, turma: str) -> str:
    """Monta a URL REST do nó da turma. O sufixo .json é exigido pela API."""
    base = FIREBASE_URL.rstrip("/")
    return f"{base}/{FIREBASE_NO_RAIZ}/{turno}/{turma}.json"


def _params() -> dict:
    """Parâmetros de query — inclui o token de autenticação se houver."""
    token = (FIREBASE_AUTH_TOKEN or "").strip()
    return {"auth": token} if token else {}


def salvar_mapeamento(
    turno: str,
    turma: str,
    mapa: dict[Posicao, str],
    sem_lugar: list[str],
) -> tuple[bool, str]:
    """Grava o mapeamento da turma no Firebase (PUT substitui o nó inteiro).

    Retorna (True, "") em caso de sucesso, ou (False, motivo) em falha —
    o app usa isso para mostrar "Salvo com sucesso" ou "Não salvo".
    """
    if not firebase_configurado():
        return False, (
            "Firebase não configurado. Edite config/credenciais.py "
            "com a URL e o token reais do seu projeto."
        )

    payload = {
        "mapa": {posicao_para_chave(pos): nome for pos, nome in sorted(mapa.items())},
        "sem_lugar": list(sem_lugar),
    }
    try:
        resposta = requests.put(
            _url(turno, turma),
            json=payload,
            params=_params(),
            timeout=FIREBASE_TIMEOUT,
        )
        resposta.raise_for_status()
        return True, ""
    except requests.RequestException as erro:
        return False, f"Erro ao comunicar com o Firebase: {erro}"


def carregar_mapeamento(
    turno: str, turma: str
) -> tuple[dict[Posicao, str], list[str]] | None:
    """Busca o mapeamento salvo da turma no Firebase.

    Retorna (mapa, sem_lugar) ou None se o Firebase não estiver
    configurado, a turma nunca tiver sido salva, ou houver erro de rede
    — nesses casos o app gera o layout inicial automaticamente.
    """
    if not firebase_configurado():
        return None
    try:
        resposta = requests.get(
            _url(turno, turma), params=_params(), timeout=FIREBASE_TIMEOUT
        )
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError):
        return None

    if not isinstance(dados, dict) or "mapa" not in dados:
        return None

    mapa: dict[Posicao, str] = {}
    for chave, nome in dados.get("mapa", {}).items():
        pos = chave_para_posicao(str(chave))
        if pos is not None and str(nome).strip():
            mapa[pos] = str(nome).strip()

    sem_lugar = [str(n).strip() for n in dados.get("sem_lugar", []) if str(n).strip()]
    return (mapa, sem_lugar) if mapa else None
