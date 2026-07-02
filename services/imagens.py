"""Localização e preparo das fotos dos alunos.

A foto de um aluno é procurada na pasta da turma pelo NOME COMPLETO
(comparação sem acentos e sem diferenciar maiúsculas/minúsculas).
Ex.: dados/matutino/3A/MARIA DA SILVA.jpg

Sem foto, o card usa assets/avatar_padrao.png.
As imagens são recortadas em quadrado, redimensionadas e embutidas
na página como data URI (com cache do Streamlit).
"""
import base64
import unicodedata
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

from utils import paths
from utils.constantes import EXTENSOES_IMAGEM

# Tamanho final (px) das fotos nos cards
_TAMANHO_FOTO = (192, 192)


def normalizar_nome(nome: str) -> str:
    """Normaliza para comparação: maiúsculas, sem acentos, sem apóstrofos."""
    nome = nome.upper().strip()
    nome = unicodedata.normalize("NFD", nome)
    nome = "".join(c for c in nome if unicodedata.category(c) != "Mn")
    nome = nome.replace("'", " ").replace("’", " ")
    nome = " ".join(nome.split())
    return nome


def localizar_imagem(pasta_turma: Path, nome_aluno: str) -> Path | None:
    """Procura {NOME COMPLETO}.{ext} na pasta da turma, comparando por
    nome normalizado, de forma case-insensitive."""
    if not pasta_turma.is_dir():
        return None

    nome_norm = normalizar_nome(nome_aluno)
    for arquivo in pasta_turma.iterdir():
        if not arquivo.is_file():
            continue
        if (
            normalizar_nome(arquivo.stem) == nome_norm
            and arquivo.suffix.lower() in EXTENSOES_IMAGEM
        ):
            return arquivo
    return None


@st.cache_data(show_spinner=False)
def _carregar_data_uri(caminho: str, mtime: float) -> str:
    """Abre a imagem, recorta em quadrado, redimensiona e devolve um data URI.
    `mtime` participa da chave de cache para invalidar quando a foto mudar."""
    with Image.open(caminho) as img:
        img = ImageOps.exif_transpose(img)
        img = ImageOps.fit(img.convert("RGB"), _TAMANHO_FOTO, Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=82)
    dados = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{dados}"


def foto_data_uri(pasta_turma: Path, nome_aluno: str | None) -> str:
    """Retorna o data URI da foto do aluno, ou do avatar padrão.
    Se nem o avatar existir, devolve um pixel transparente (nunca quebra)."""
    caminho = None
    if nome_aluno is not None:
        caminho = localizar_imagem(pasta_turma, nome_aluno)
    if caminho is None:
        caminho = paths.AVATAR_PADRAO
    if not caminho.is_file():
        return (
            "data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
            "AAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
    return _carregar_data_uri(str(caminho), caminho.stat().st_mtime)
