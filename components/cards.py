"""Geração do HTML dos cards (aluno, VAZIO, mesa, porta).

Aqui fica apenas o HTML — os estilos estão em components/styles.py
e a lógica de clique em components/layout_sala.py.

Todo HTML é passado por `compactar()` (utils/html_utils.py) para
evitar que o Markdown do Streamlit exiba o código cru na tela.
"""

import html

from utils.html_utils import compactar


def html_card_aluno(
    nome: str,
    numero: str | None,
    foto_uri: str,
    selecionado: bool,
    classe_extra: str = "",
) -> str:
    """Card de um aluno (foto + badge com nº da chamada + nome).

    `classe_extra` permite variações visuais — usada em "sem-lugar"
    para os alunos fora do mapa.
    """
    classes = "card-aluno"
    if selecionado:
        classes += " selecionado"
    if classe_extra:
        classes += f" {classe_extra}"
    nome_seguro = html.escape(nome)
    badge = (
        f'<span class="card-num-badge">{html.escape(str(numero))}</span>'
        if numero is not None
        else ""
    )
    return compactar(f"""
    <div class="{classes}">
        {badge}
        <div class="card-foto">
            <img src="{foto_uri}" alt="Foto de {nome_seguro}">
        </div>
        <div class="card-nome" title="{nome_seguro}">{nome_seguro}</div>
    </div>
    """)


def html_card_vazio(selecionado: bool) -> str:
    """Card de carteira VAZIA — participa das trocas como um aluno normal
    (clicável, pode ser selecionado e trocado de lugar).

    IMPORTANTE: a estrutura interna é a MESMA do card de aluno
    (área da foto + área do nome), para que o card VAZIO tenha
    exatamente o mesmo tamanho e o mesmo espaçamento na grade.
    """
    classes = "card-aluno card-vazio"
    if selecionado:
        classes += " selecionado"
    return compactar(f"""
    <div class="{classes}">
        <div class="card-foto">
            <div class="card-foto-vazia"><span class="vazio-rotulo">VAZIO</span></div>
        </div>
        <div class="card-nome card-nome-vazio">&nbsp;</div>
    </div>
    """)


def html_mesa_professor() -> str:
    """Faixa da mesa do professor, exibida na frente da sala."""
    return compactar("""
    <div class="mesa-professor">
        <span class="selo">★</span>MESA DO PROFESSOR
    </div>
    """)


def html_porta() -> str:
    """Indicador da porta da sala."""
    return '<div class="porta-sala">🚪 PORTA</div>'
