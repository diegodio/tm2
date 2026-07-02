"""Utilidades para HTML embutido no Streamlit.

PROBLEMA que este módulo resolve: o `st.markdown` interpreta o texto
como Markdown ANTES de aceitar o HTML. Em Markdown, linhas indentadas
com 4+ espaços (como as de um f-string triplo indentado no código)
podem ser tratadas como *bloco de código* — e aí o HTML aparece cru
na tela (ex.: `<span class="meta-info">...</span>` visível).

SOLUÇÃO: `compactar()` remove a indentação e junta tudo em uma única
linha antes de enviar ao `st.markdown`.
"""


def compactar(html: str) -> str:
    """Remove indentação/linhas em branco e devolve o HTML em uma linha.

    Deve envolver TODO HTML passado a `st.markdown(..., unsafe_allow_html=True)`.
    """
    return " ".join(
        linha.strip() for linha in html.strip().splitlines() if linha.strip()
    )
