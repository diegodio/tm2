"""Mapa de Sala — sistema de mapeamento de salas de aula.

Execução:
    pip install -r requirements.txt
    streamlit run app.py

FLUXO DA PÁGINA (nesta ordem):
1. Login — Google (st.login) ou botão de demonstração (removível).
2. Autorização — o e-mail precisa estar em config/usuarios.py.
3. Sidebar — usuário logado + seleção de turno/turma (filtrada por
   permissão: professor só vê as turmas dele).
4. Carregamento do mapa — tenta o Firebase; se não houver, gera o
   layout inicial (5 filas × 8 carteiras, VAZIO nas sobras).
5. Sala — grade de cards com trocas (só para quem pode editar:
   professor conselheiro da turma, pedagoga ou diretor).
6. Área "alunos sem lugar" + botão SALVAR (grava no Firebase via
   requests). NADA é salvo automaticamente.
"""
import streamlit as st

from components.layout_sala import (
    render_barra_acoes,
    render_sala,
    render_sem_lugar,
)
from components.sidebar import render_sidebar
from components.styles import aplicar_estilos
from config.equipe import equipe_da_turma
from services import auth, firebase
from services.arquivos import carregar_alunos, carregar_info
from services.mapeamento import (
    completar_grade,
    gerar_mapeamento_inicial,
    reconciliar,
)
from utils.constantes import ROTULOS_TURNOS, VAZIO

# ------------------------------------------------------------------
# Configuração da página + estilos
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Mapa da Sala",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)
aplicar_estilos()

# ------------------------------------------------------------------
# 1–2) Login e autorização
# ------------------------------------------------------------------
usuario = auth.obter_usuario()

if usuario is None:
    auth.render_pagina_login()
    st.stop()

if not usuario["autorizado"]:
    auth.render_nao_autorizado(usuario)
    st.stop()

# ------------------------------------------------------------------
# 3) Sidebar: turno/turma visíveis para este usuário
# ------------------------------------------------------------------
turno, turma = render_sidebar(usuario)
if turno is None or turma is None:
    st.markdown(
        """
        <div class="faixa-titulo">
            <div class="brasao">🏫</div>
            <div class="bloco-titulo">
                <p class="titulo-app">Mapa da <span class="destaque">Sala</span></p>
                <div class="linha-meta">
                    <span class="meta-info">Crie a estrutura em
                    <code>dados/&lt;turno&gt;/&lt;turma&gt;/info.json</code>
                    e cadastre suas turmas em <code>config/usuarios.py</code>.</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

alunos = carregar_alunos(turno, turma)
if not alunos:
    st.error(f"O arquivo `info.json` da turma {turma} está vazio ou inválido.")
    st.stop()

# Índice nome -> número da chamada (para o badge do card)
info = carregar_info(turno, turma)
numero_por_nome = {
    nome: str(dados["numero"])
    for nome, dados in info.items()
    if isinstance(dados, dict) and dados.get("numero") is not None
}

# Este usuário pode editar/salvar esta turma?
# (professor conselheiro da turma, pedagoga ou diretor)
editavel = auth.pode_editar(usuario, turno, turma)

# ------------------------------------------------------------------
# 4) Carrega o estado quando o usuário muda de turno/turma
#    (Firebase primeiro; senão, layout inicial gerado)
# ------------------------------------------------------------------
contexto = (turno, turma)
if st.session_state.get("contexto") != contexto:
    salvo = firebase.carregar_mapeamento(turno, turma)
    if salvo is not None:
        mapa, sem_lugar = salvo
        completar_grade(mapa)  # garante as 40 posições (VAZIO onde faltar)
    else:
        mapa = gerar_mapeamento_inicial(alunos)
        sem_lugar = []
    # Sincroniza com o info.json (alunos novos, alunos que saíram)
    reconciliar(mapa, sem_lugar, alunos)

    st.session_state["contexto"] = contexto
    st.session_state["mapa"] = mapa
    st.session_state["sem_lugar"] = sem_lugar
    st.session_state["selecionado"] = None
    st.session_state["alterado"] = False

mapa = st.session_state["mapa"]
sem_lugar = st.session_state["sem_lugar"]

# Feedback da última ação (troca / sem lugar), definido nos callbacks
ultima_acao = st.session_state.pop("ultima_acao", None)
if ultima_acao:
    st.toast(ultima_acao, icon="✅")

# ------------------------------------------------------------------
# 5) Cabeçalho da turma: turno, conselheiro, pedagoga, permissão
# ------------------------------------------------------------------
rotulo_turno = ROTULOS_TURNOS.get(turno, turno.capitalize())
equipe = equipe_da_turma(turno, turma)

pills_equipe = ""
if equipe.get("conselheiro"):
    pills_equipe += (
        f'<span class="pill-equipe"><span class="funcao">Conselheiro</span> '
        f'{equipe["conselheiro"]}</span>'
    )
if equipe.get("pedagoga"):
    pills_equipe += (
        f'<span class="pill-equipe"><span class="funcao">Pedagoga</span> '
        f'{equipe["pedagoga"]}</span>'
    )

pill_leitura = "" if editavel else '<span class="pill-leitura">🔒 somente leitura</span>'
total_no_mapa = sum(1 for n in mapa.values() if n != VAZIO)
dica = "toque em dois cards para trocar lugares" if editavel else "visualização"

st.markdown(
    f"""
    <div class="faixa-titulo">
        <div class="brasao">🏫</div>
        <div class="bloco-titulo">
            <p class="titulo-app">Turma <span class="destaque">{turma}</span></p>
            <div class="linha-meta">
                <span class="pill-turno">☀ {rotulo_turno}</span>
                {pills_equipe}
                {pill_leitura}
                <span class="meta-info">{total_no_mapa} alunos no mapa · {dica}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Área de status: seleção atual + aviso de alterações não salvas
selecao = st.session_state.get("selecionado")
partes_status = []
if selecao is not None:
    tipo, alvo = selecao
    nome_sel = mapa.get(alvo, "") if tipo == "carteira" else alvo
    rotulo_sel = "carteira vazia" if nome_sel == VAZIO else nome_sel
    partes_status.append(
        f'<div class="chip-status">⇄ Trocando: <strong>{rotulo_sel}</strong>'
        " — escolha o outro card</div>"
    )
if editavel and st.session_state.get("alterado"):
    partes_status.append(
        '<div class="chip-alterado">● Alterações não salvas — use o botão '
        "Salvar no fim da página</div>"
    )
st.markdown(
    f'<div class="area-status">{"".join(partes_status)}</div>',
    unsafe_allow_html=True,
)

# Botão "Enviar para sem lugar" (aparece quando um aluno está selecionado)
render_barra_acoes(editavel)

# ------------------------------------------------------------------
# 6) Sala + área "sem lugar" + botão Salvar (Firebase)
# ------------------------------------------------------------------
render_sala(turno, turma, numero_por_nome, editavel)
render_sem_lugar(turno, turma, numero_por_nome, editavel)

if editavel:
    st.divider()
    if st.button("💾 Salvar mapeamento", key="btn_salvar"):
        ok, motivo = firebase.salvar_mapeamento(turno, turma, mapa, sem_lugar)
        if ok:
            st.session_state["alterado"] = False
            st.success("✅ Salvo com sucesso! O mapeamento foi gravado no Firebase.")
        else:
            st.error(f"❌ Não salvo. {motivo}")
    st.caption(
        "O mapeamento é gravado no Firebase apenas ao clicar em Salvar. "
        "Sem salvar, as alterações são perdidas ao trocar de turma ou sair."
    )
