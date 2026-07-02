"""Sidebar: identificação do usuário logado, sair, e seleção de
turno/turma — mostrando APENAS as turmas que o usuário pode ver
(diretor e pedagoga veem todas; professor vê só as dele)."""
import streamlit as st

from utils.constantes import NOME_COLEGIO
from utils.html_utils import compactar

from services import auth
from utils.constantes import ROTULOS_TURNOS


def render_sidebar(usuario: dict) -> tuple[str | None, str | None]:
    """Desenha a sidebar e retorna (turno, turma) selecionados,
    ou (None, None) se não houver turma disponível para o usuário."""
    with st.sidebar:
        # ---------- Cabeçalho ----------
        st.markdown(
            compactar(f"""
            <div style="padding:.2rem 0 .8rem;">
                <div style="font-family:'Sora',sans-serif;font-weight:800;
                            font-size:1.05rem;color:#EDF2F9;">
                    🏫 Mapa da Sala
                </div>
                <div style="color:#9FB3CE;font-size:.78rem;margin-top:.15rem;">
                    {NOME_COLEGIO}
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        # ---------- Usuário logado ----------
        selo_demo = (
            '<span class="pill-demo">demonstração</span>'
            if usuario.get("demo")
            else ""
        )
        st.markdown(
            compactar(f"""
            <div class="cartao-usuario">
                <div class="usuario-nome">{usuario['nome']}</div>
                <div class="usuario-email">{usuario['email']}</div>
                <div class="usuario-pills">
                    <span class="pill-papel">{auth.rotulo_papel(usuario)}</span>
                    {selo_demo}
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        if st.button("Sair", key="btn_sair", use_container_width=True):
            auth.sair()
            st.rerun()

        st.divider()

        # ---------- Turno / turma (filtrados por permissão) ----------
        visiveis = auth.turmas_visiveis(usuario)
        if not visiveis:
            st.warning(
                "Nenhuma turma disponível para o seu usuário. "
                "Verifique as pastas em `dados/` e o cadastro em "
                "`config/usuarios.py`."
            )
            return None, None

        turnos = sorted(
            {t for t, _ in visiveis},
            key=lambda t: list(ROTULOS_TURNOS).index(t) if t in ROTULOS_TURNOS else 99,
        )
        turno = st.selectbox(
            "Turno",
            options=turnos,
            format_func=lambda t: ROTULOS_TURNOS.get(t, t.capitalize()),
            key="sel_turno",
        )

        turmas = sorted(tu for (tn, tu) in visiveis if tn == turno)
        if not turmas:
            st.warning("Nenhuma turma neste turno para o seu usuário.")
            return turno, None
        turma = st.selectbox("Turma", options=turmas, key="sel_turma")

        st.divider()
        if auth.pode_editar(usuario, turno, turma):
            st.caption(
                "Toque em dois cards para trocá-los de lugar "
                "(o card VAZIO também troca). Depois use **Salvar** "
                "para gravar no Firebase — nada é salvo automaticamente."
            )
        else:
            st.caption(
                "🔒 Somente leitura: apenas o professor conselheiro da "
                "turma, a pedagoga e o diretor podem editar o mapeamento."
            )
    return turno, turma
