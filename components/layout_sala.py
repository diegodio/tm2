"""Renderização da sala e da área de "alunos sem lugar", com a lógica
de cliques (trocas).

ORIENTAÇÃO DA SALA
------------------
Cada fila é uma COLUNA de carteiras na tela. A posição 1 é a carteira
da FRENTE (junto à mesa do professor, desenhada abaixo da grade); por
isso a primeira linha da tela corresponde às últimas carteiras (fundo
da sala).

COMO FUNCIONA A SELEÇÃO
-----------------------
st.session_state["selecionado"] guarda o que está selecionado:
    ("carteira", (fila, posicao))  → uma carteira da grade
    ("sem_lugar", "NOME")          → um aluno da área sem lugar
    None                           → nada selecionado

Sequências de clique possíveis:
  carteira A  →  carteira B   : troca A ⇄ B (vale também para VAZIO)
  carteira A  →  carteira A   : desmarca
  sem_lugar X →  carteira B   : X ocupa B; se B tinha aluno, ele vai
                                para a área "sem lugar" (troca)
  carteira A  →  sem_lugar X  : idem (ordem inversa)
  carteira A  →  botão "Enviar p/ sem lugar": A vira VAZIO e o aluno
                                vai para a área "sem lugar"

Toda alteração marca st.session_state["alterado"] = True — o botão
"Salvar" (Firebase) é quem persiste. NADA é salvo automaticamente.

MODO SOMENTE LEITURA
--------------------
Se `editavel=False` (usuário sem permissão), os cards são desenhados
SEM os botões invisíveis — nada é clicável.
"""
import streamlit as st

from components.cards import (
    html_card_aluno,
    html_card_vazio,
    html_mesa_professor,
    html_porta,
)
from services.imagens import foto_data_uri
from services.mapeamento import (
    Posicao,
    colocar_no_mapa,
    colocar_sem_lugar,
    trocar_alunos,
)
from utils import paths
from utils.constantes import CADEIRAS_POR_FILA, NUM_FILAS, VAZIO
from utils.html_utils import compactar


def _rotulo(nome: str) -> str:
    """Nome exibível nas mensagens (traduz o marcador interno VAZIO)."""
    return "carteira vazia" if nome == VAZIO else nome


# ------------------------------------------------------------------
# Callbacks de clique (executam ANTES do rerun do Streamlit)
# ------------------------------------------------------------------
def _clicar_carteira(pos: Posicao) -> None:
    """Clique em uma carteira da grade (aluno ou VAZIO)."""
    mapa = st.session_state["mapa"]
    sem_lugar = st.session_state["sem_lugar"]
    selecao = st.session_state.get("selecionado")

    if selecao is None:
        # Nada selecionado → seleciona esta carteira
        st.session_state["selecionado"] = ("carteira", pos)
        return

    tipo, alvo = selecao

    if selecao == ("carteira", pos):
        # Clicou de novo na mesma carteira → desmarca
        st.session_state["selecionado"] = None
        return

    if tipo == "carteira":
        # Duas carteiras → troca (funciona com VAZIO dos dois lados)
        trocar_alunos(mapa, alvo, pos)
        st.session_state["ultima_acao"] = (
            f"{_rotulo(mapa[pos])} ⇄ {_rotulo(mapa[alvo])}"
        )
    else:
        # Aluno "sem lugar" selecionado → coloca nesta carteira;
        # o ocupante anterior (se houver) vai para "sem lugar"
        nome = alvo
        deslocado = colocar_no_mapa(mapa, sem_lugar, nome, pos)
        if deslocado:
            st.session_state["ultima_acao"] = f"{nome} ⇄ {deslocado} (sem lugar)"
        else:
            st.session_state["ultima_acao"] = f"{nome} colocado(a) no mapa"

    st.session_state["selecionado"] = None
    st.session_state["alterado"] = True


def _clicar_sem_lugar(nome: str) -> None:
    """Clique em um aluno da área "sem lugar"."""
    mapa = st.session_state["mapa"]
    sem_lugar = st.session_state["sem_lugar"]
    selecao = st.session_state.get("selecionado")

    if selecao == ("sem_lugar", nome):
        st.session_state["selecionado"] = None
        return

    if selecao is not None and selecao[0] == "carteira":
        # Carteira selecionada + clique em aluno sem lugar → o aluno
        # ocupa a carteira; o ocupante anterior (se houver) sai do mapa
        pos = selecao[1]
        deslocado = colocar_no_mapa(mapa, sem_lugar, nome, pos)
        if deslocado:
            st.session_state["ultima_acao"] = f"{nome} ⇄ {deslocado} (sem lugar)"
        else:
            st.session_state["ultima_acao"] = f"{nome} colocado(a) no mapa"
        st.session_state["selecionado"] = None
        st.session_state["alterado"] = True
        return

    # Nada (ou outro sem-lugar) selecionado → seleciona este aluno
    st.session_state["selecionado"] = ("sem_lugar", nome)


def _enviar_para_sem_lugar() -> None:
    """Botão "Enviar para sem lugar": tira o aluno da carteira
    selecionada (a carteira vira VAZIO)."""
    selecao = st.session_state.get("selecionado")
    if not selecao or selecao[0] != "carteira":
        return
    nome = colocar_sem_lugar(
        st.session_state["mapa"], st.session_state["sem_lugar"], selecao[1]
    )
    if nome:
        st.session_state["ultima_acao"] = f"{nome} enviado(a) para «sem lugar»"
        st.session_state["alterado"] = True
    st.session_state["selecionado"] = None


# ------------------------------------------------------------------
# Renderização
# ------------------------------------------------------------------
def render_barra_acoes(editavel: bool) -> bool:
    """Barra acima da sala: botão "Enviar para sem lugar".

    O botão fica SEMPRE visível quando o usuário pode editar — apenas
    desabilitado enquanto nenhum ALUNO de carteira estiver selecionado.
    Assim a barra ocupa sempre a mesma altura e a sala abaixo não se
    desloca quando um card é selecionado.

    Obs.: o botão "Salvar" fica no app.py, junto da chamada ao Firebase.
    """
    if not editavel:
        return False
    selecao = st.session_state.get("selecionado")
    mapa = st.session_state["mapa"]
    tem_aluno_selecionado = bool(
        selecao and selecao[0] == "carteira" and mapa.get(selecao[1], VAZIO) != VAZIO
    )
    st.button(
        "🪑 Enviar aluno selecionado para «sem lugar»",
        key="btn_semlugar",
        on_click=_enviar_para_sem_lugar,
        disabled=not tem_aluno_selecionado,
        help=None if tem_aluno_selecionado else "Selecione um aluno no mapa primeiro.",
    )
    return True


def render_sala(
    turno: str, turma: str, numero_por_nome: dict[str, str], editavel: bool
) -> None:
    """Desenha a grade fixa 5 × 8 (colunas = filas). Cada carteira exibe
    o aluno ou o card VAZIO. Se `editavel`, um botão invisível cobre
    cada card para capturar o clique."""
    mapa = st.session_state["mapa"]
    selecao = st.session_state.get("selecionado")
    pasta = paths.pasta_turma(turno, turma)

    # Do fundo da sala (topo da tela) até a frente (mesa do professor)
    for posicao_na_fila in range(CADEIRAS_POR_FILA, 0, -1):
        colunas = st.columns(NUM_FILAS, gap="small")
        for indice_fila in range(NUM_FILAS):
            fila = indice_fila + 1
            pos = (fila, posicao_na_fila)
            nome = mapa.get(pos, VAZIO)
            esta_selecionado = selecao == ("carteira", pos)

            with colunas[indice_fila]:
                if nome == VAZIO:
                    st.markdown(
                        html_card_vazio(esta_selecionado), unsafe_allow_html=True
                    )
                else:
                    numero = numero_por_nome.get(nome)
                    foto = foto_data_uri(pasta, nome)
                    st.markdown(
                        html_card_aluno(nome, numero, foto, esta_selecionado),
                        unsafe_allow_html=True,
                    )
                if editavel:
                    # Botão invisível esticado sobre o card (ver styles.py;
                    # o prefixo de key "sel_" ativa esse comportamento)
                    st.button(
                        "⇄",
                        key=f"sel_c_{fila}_{posicao_na_fila}",
                        on_click=_clicar_carteira,
                        args=(pos,),
                    )

    st.markdown(html_mesa_professor(), unsafe_allow_html=True)
    st.markdown(html_porta(), unsafe_allow_html=True)


def render_sem_lugar(
    turno: str, turma: str, numero_por_nome: dict[str, str], editavel: bool
) -> None:
    """Área separada, abaixo da sala, com os alunos SEM lugar no mapa.
    Os cards funcionam como os da grade: clique para selecionar e
    depois clique em uma carteira (ou vice-versa)."""
    sem_lugar: list[str] = st.session_state["sem_lugar"]
    if not sem_lugar:
        return

    selecao = st.session_state.get("selecionado")
    pasta = paths.pasta_turma(turno, turma)

    st.markdown(
        compactar(f"""
        <div class="secao-sem-lugar-titulo">
            🪑 Alunos sem lugar no mapa
            <span class="contador-sem-lugar">{len(sem_lugar)}</span>
        </div>
        """),
        unsafe_allow_html=True,
    )

    # Desenha em linhas com a mesma largura da grade (NUM_FILAS colunas)
    for inicio in range(0, len(sem_lugar), NUM_FILAS):
        grupo = sem_lugar[inicio : inicio + NUM_FILAS]
        colunas = st.columns(NUM_FILAS, gap="small")
        for indice, nome in enumerate(grupo):
            esta_selecionado = selecao == ("sem_lugar", nome)
            with colunas[indice]:
                st.markdown(
                    html_card_aluno(
                        nome,
                        numero_por_nome.get(nome),
                        foto_data_uri(pasta, nome),
                        esta_selecionado,
                        classe_extra="card-sem-lugar",
                    ),
                    unsafe_allow_html=True,
                )
                if editavel:
                    st.button(
                        "⇄",
                        key=f"sel_s_{inicio + indice}",
                        on_click=_clicar_sem_lugar,
                        args=(nome,),
                    )
