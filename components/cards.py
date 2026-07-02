"""Geração do HTML dos cards (aluno, VAZIO, mesa, porta).

Aqui fica apenas o HTML — os estilos estão em components/styles.py
e a lógica de clique em components/layout_sala.py.
"""

import html


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
    return f"""
    <div class="{classes}">
        {badge}
        <div class="card-foto">
            <img src="{foto_uri}" alt="Foto de {nome_seguro}">
        </div>
        <div class="card-nome" title="{nome_seguro}">{nome_seguro}</div>
    </div>
    """


def html_card_vazio(selecionado: bool) -> str:
    """Card de carteira VAZIA — participa das trocas como um aluno normal
    (clicável, pode ser selecionado e trocado de lugar)."""
    classes = "card-aluno card-vazio"
    if selecionado:
        classes += " selecionado"
    return f"""
    <div class="{classes}">
        <div class="vazio-rotulo">VAZIO</div>
    </div>
    """


def html_mesa_professor() -> str:
    """Faixa da mesa do professor, exibida na frente da sala."""
    return """
    <div class="mesa-professor">
        <span class="selo">★</span>MESA DO PROFESSOR
    </div>
    """


def html_porta() -> str:
    """Indicador da porta da sala."""
    return '<div class="porta-sala">🚪 PORTA</div>'
