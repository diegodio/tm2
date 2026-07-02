"""Autenticação e permissões.

LOGIN COM GOOGLE
----------------
Usa o login nativo do Streamlit (st.login / st.user), que implementa
OAuth 2.0 / OpenID Connect. As credenciais do Google ficam em
.streamlit/secrets.toml — veja o passo a passo no README.

Após o login, o e-mail do Google é comparado com a lista de
config/usuarios.py. Quem não estiver na lista vê uma tela de
"acesso não autorizado".

PAPÉIS E PERMISSÕES (resumo)
----------------------------
diretor / pedagoga  → veem e EDITAM todas as turmas.
professor           → vê apenas suas "turmas";
                      edita apenas as de "conselheiro_de".
"""
import streamlit as st

from config.usuarios import ROTULOS_PAPEIS, USUARIOS_AUTORIZADOS
from services import arquivos

# =====================================================================
# ⚠ BOTÃO DE DEMONSTRAÇÃO — REMOVER EM PRODUÇÃO ⚠
#
# O botão "Entrar em modo demonstração" pula o login com Google e entra
# como um diretor fictício (acesso total), para você demonstrar o site.
#
# COMO REMOVER: mude MOSTRAR_BOTAO_DEMO para False (1 linha).
# Se quiser apagar de vez, remova também USUARIO_DEMO abaixo e o bloco
# marcado com "BLOCO DEMO" em render_pagina_login().
# =====================================================================
MOSTRAR_BOTAO_DEMO = True

USUARIO_DEMO = {
    "email": "demo@exemplo.com",
    "nome": "Visitante (demonstração)",
    "papel": "diretor",  # acesso total para a demonstração
}
# ================== FIM DO BLOCO DE DEMONSTRAÇÃO =====================


def _google_login_configurado() -> bool:
    """True se a seção [auth] existe em .streamlit/secrets.toml
    e não está com os valores de exemplo."""
    try:
        auth = st.secrets.get("auth", None)
        if not auth:
            return False
        client_id = str(auth.get("client_id", ""))
        return bool(client_id) and "SEU_CLIENT_ID" not in client_id
    except Exception:
        return False


def _email_google() -> tuple[str, str] | None:
    """Retorna (email, nome) do usuário logado via Google, ou None."""
    try:
        usuario = getattr(st, "user", None)
        if usuario is not None and getattr(usuario, "is_logged_in", False):
            email = str(getattr(usuario, "email", "")).strip().lower()
            nome = str(getattr(usuario, "name", "") or email)
            if email:
                return email, nome
    except Exception:
        pass
    return None


def obter_usuario() -> dict | None:
    """Retorna o usuário da sessão atual, ou None se ninguém logou.

    Formato retornado:
    {
        "email": str,
        "nome": str,             # nome exibido
        "papel": str,            # "diretor" | "pedagoga" | "professor"
        "autorizado": bool,      # e-mail está na lista?
        "turmas": [...],         # só para professor
        "conselheiro_de": [...], # só para professor
        "demo": bool,            # True se entrou pelo botão de demonstração
    }
    """
    # ---- BLOCO DEMO (remover em produção) ----
    if MOSTRAR_BOTAO_DEMO and st.session_state.get("login_demo"):
        return {**USUARIO_DEMO, "autorizado": True, "demo": True}
    # ------------------------------------------

    dados_google = _email_google()
    if dados_google is None:
        return None

    email, nome_google = dados_google
    cadastro = USUARIOS_AUTORIZADOS.get(email)
    if cadastro is None:
        # Logou no Google, mas o e-mail não está na lista de autorizados
        return {
            "email": email,
            "nome": nome_google,
            "papel": "",
            "autorizado": False,
            "demo": False,
        }

    return {
        "email": email,
        "nome": cadastro.get("nome", nome_google),
        "papel": cadastro.get("papel", "professor"),
        "turmas": [tuple(t) for t in cadastro.get("turmas", [])],
        "conselheiro_de": [tuple(t) for t in cadastro.get("conselheiro_de", [])],
        "autorizado": True,
        "demo": False,
    }


def sair() -> None:
    """Encerra a sessão (Google ou demonstração)."""
    st.session_state.pop("login_demo", None)  # BLOCO DEMO
    try:
        usuario = getattr(st, "user", None)
        if usuario is not None and getattr(usuario, "is_logged_in", False):
            st.logout()
    except Exception:
        pass


# ------------------------------------------------------------------
# Permissões
# ------------------------------------------------------------------
def turmas_visiveis(usuario: dict) -> list[tuple[str, str]]:
    """Lista de (turno, turma) que o usuário pode VER.
    Diretor e pedagoga: todas as turmas existentes em dados/.
    Professor: apenas as turmas cadastradas para ele (e que existem)."""
    existentes = [
        (turno, turma)
        for turno in arquivos.listar_turnos()
        for turma in arquivos.listar_turmas(turno)
    ]
    if usuario.get("papel") in ("diretor", "pedagoga"):
        return existentes
    permitidas = set(usuario.get("turmas", []))
    return [t for t in existentes if t in permitidas]


def pode_editar(usuario: dict, turno: str, turma: str) -> bool:
    """True se o usuário pode editar E salvar o mapeamento desta turma:
    diretor, pedagoga, ou professor conselheiro da turma."""
    if usuario.get("papel") in ("diretor", "pedagoga"):
        return True
    return (turno, turma) in set(usuario.get("conselheiro_de", []))


def rotulo_papel(usuario: dict) -> str:
    """Rótulo amigável do papel para exibição."""
    return ROTULOS_PAPEIS.get(usuario.get("papel", ""), usuario.get("papel", ""))


# ------------------------------------------------------------------
# Telas de login
# ------------------------------------------------------------------
def render_pagina_login() -> None:
    """Tela inicial: botão de login com Google + botão de demonstração."""
    st.markdown(
        """
        <div class="cartao-login">
            <div class="brasao brasao-login">🏫</div>
            <p class="titulo-app">Mapa da <span class="destaque">Sala</span></p>
            <p class="subtitulo-login">Escolas Cívico-Militares · Paraná</p>
            <p class="texto-login">
                Acesso restrito a servidores autorizados.<br>
                Entre com sua conta Google institucional.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    esquerda, direita = st.columns(2)

    with esquerda:
        if st.button(
            "🔐 Entrar com Google",
            key="btn_google",
            use_container_width=True,
        ):
            if _google_login_configurado():
                st.login()  # redireciona para o Google (secrets.toml [auth])
            else:
                st.warning(
                    "Login com Google ainda não configurado. "
                    "Preencha `.streamlit/secrets.toml` — veja o README. "
                    "Enquanto isso, use o modo demonstração."
                )

    # ---------------- BLOCO DEMO (remover em produção) ----------------
    with direita:
        if MOSTRAR_BOTAO_DEMO and st.button(
            "🎭 Entrar em modo demonstração",
            key="btn_demo",
            use_container_width=True,
        ):
            st.session_state["login_demo"] = True
            st.rerun()
    # ---------------- FIM DO BLOCO DEMO -------------------------------


def render_nao_autorizado(usuario: dict) -> None:
    """Tela para quem logou no Google mas não está na lista de autorizados."""
    st.markdown(
        f"""
        <div class="cartao-login">
            <div class="brasao brasao-login">🚫</div>
            <p class="titulo-app">Acesso <span class="destaque">negado</span></p>
            <p class="texto-login">
                O e-mail <strong>{usuario['email']}</strong> não está na lista
                de usuários autorizados.<br>
                Peça à direção para incluir seu e-mail em
                <code>config/usuarios.py</code>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Sair", key="btn_sair_negado"):
        sair()
        st.rerun()
