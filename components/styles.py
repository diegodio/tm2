"""CSS customizado — identidade visual escura com destaques dourados.

GUIA RÁPIDO DAS SEÇÕES (procure pelos títulos nos comentários):
  • Fundo geral / sidebar
  • Cabeçalho da página (faixa-titulo, pills de equipe)
  • Cards de aluno, card VAZIO e área "sem lugar"
  • Botões invisíveis de seleção (prefixo de key "sel_")
  • Botões nomeados (salvar, sem lugar, login, demo, sair)
  • Tela de login
  • Mesa do professor / porta / animações / responsividade

IMPORTANTE — botões invisíveis de seleção:
O Streamlit adiciona a classe CSS "st-key-<key>" ao contêiner de cada
elemento com key. Todos os botões de seleção de card usam keys com o
prefixo "sel_" (sel_c_... para carteiras, sel_s_... para sem lugar);
o CSS abaixo estica SOMENTE esses botões, invisíveis, por cima do card.
Os demais botões (salvar, demo, etc.) permanecem botões normais.
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --azul-escuro: #0B1F3A;
    --azul-medio: #1D4E89;
    --azul-claro: #4F86C6;
    --dourado: #D4A017;
    --superficie: #122A4E;
    --superficie-alta: #16335C;
    --texto: #EDF2F9;
    --texto-suave: #9FB3CE;
    --raio: 14px;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
}

/* ---------- Fundo geral ---------- */
.stApp {
    background:
        radial-gradient(1100px 500px at 85% -10%, rgba(79,134,198,.16), transparent 60%),
        radial-gradient(900px 420px at -10% 110%, rgba(29,78,137,.25), transparent 55%),
        var(--azul-escuro);
}
header[data-testid="stHeader"] { background: transparent; }

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2.5rem;
    max-width: 1180px;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2444 0%, #0B1F3A 100%);
    border-right: 1px solid rgba(79,134,198,.18);
}
section[data-testid="stSidebar"] * { color: var(--texto); }
section[data-testid="stSidebar"] label {
    color: var(--texto-suave) !important;
    font-size: .78rem !important;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
}
div[data-baseweb="select"] > div {
    background: var(--superficie) !important;
    border: 1px solid rgba(79,134,198,.35) !important;
    border-radius: 10px !important;
    color: var(--texto) !important;
}
div[data-baseweb="popover"] li { background: var(--superficie); }

/* Cartão do usuário logado (sidebar) */
.cartao-usuario {
    background: var(--superficie);
    border: 1px solid rgba(79,134,198,.3);
    border-radius: 12px;
    padding: .75rem .85rem;
    margin-bottom: .6rem;
}
.usuario-nome { font-weight: 700; font-size: .92rem; }
.usuario-email { color: var(--texto-suave); font-size: .74rem; margin-top: .1rem; word-break: break-all; }
.usuario-pills { display: flex; gap: .35rem; flex-wrap: wrap; margin-top: .45rem; }
.pill-papel, .pill-demo {
    display: inline-flex; align-items: center;
    border-radius: 999px; padding: .16rem .6rem;
    font-size: .66rem; font-weight: 700;
    letter-spacing: .08em; text-transform: uppercase;
}
.pill-papel { background: rgba(212,160,23,.14); border: 1px solid rgba(212,160,23,.6); color: var(--dourado); }
.pill-demo  { background: rgba(79,134,198,.16); border: 1px solid rgba(79,134,198,.6); color: var(--azul-claro); }

/* ---------- Cabeçalho da página ---------- */
.faixa-titulo {
    display: flex; align-items: center; gap: 1.1rem;
    padding: 1.1rem 1.3rem; margin-bottom: 1.2rem;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(29,78,137,.55) 0%, rgba(11,31,58,.35) 70%);
    border: 1px solid rgba(79,134,198,.35);
    border-bottom: 2px solid rgba(212,160,23,.65);
    box-shadow: 0 14px 34px rgba(0,0,0,.35);
}
.faixa-titulo .brasao {
    width: 62px; height: 62px; flex-shrink: 0;
    border-radius: 16px; display: grid; place-items: center;
    font-size: 1.9rem;
    background: linear-gradient(150deg, var(--azul-medio), var(--azul-escuro));
    border: 1px solid rgba(212,160,23,.6);
    box-shadow: 0 8px 20px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.1);
}
.titulo-app {
    font-family: 'Sora', sans-serif; font-weight: 800;
    font-size: clamp(1.7rem, 4.2vw, 2.4rem);
    color: var(--texto); line-height: 1.1; margin: 0;
    letter-spacing: -.01em;
}
.titulo-app .destaque { color: var(--dourado); text-shadow: 0 0 26px rgba(212,160,23,.35); }

.linha-meta {
    display: flex; align-items: center; flex-wrap: wrap;
    gap: .6rem; margin-top: .45rem;
}
.pill-turno, .pill-equipe, .pill-leitura {
    display: inline-flex; align-items: center; gap: .35rem;
    border-radius: 999px; padding: .26rem .85rem;
    font-size: .78rem; font-weight: 700; letter-spacing: .06em;
}
.pill-turno {
    background: rgba(212,160,23,.14);
    border: 1px solid rgba(212,160,23,.6);
    color: var(--dourado);
    text-transform: uppercase; letter-spacing: .1em;
}
/* Pills do professor conselheiro e da pedagoga da turma */
.pill-equipe {
    background: rgba(79,134,198,.14);
    border: 1px solid rgba(79,134,198,.55);
    color: #BCD3EE;
    font-weight: 600; letter-spacing: 0;
}
.pill-equipe .funcao {
    color: var(--texto-suave);
    font-size: .64rem; font-weight: 700;
    letter-spacing: .08em; text-transform: uppercase;
}
/* Aviso de somente leitura */
.pill-leitura {
    background: rgba(159,179,206,.1);
    border: 1px dashed rgba(159,179,206,.5);
    color: var(--texto-suave);
    letter-spacing: 0; font-weight: 600;
}
.meta-info { color: var(--texto-suave); font-size: .85rem; }

/* Área reservada para o aviso de troca — a página não "pula" */
.area-status {
    min-height: 2.6rem;
    display: flex; align-items: center; gap: .6rem; flex-wrap: wrap;
    margin-bottom: .6rem;
}
.chip-status, .chip-alterado {
    display: inline-flex; align-items: center; gap: .4rem;
    border-radius: 999px; padding: .3rem .8rem;
    font-size: .78rem; font-weight: 600;
}
.chip-status {
    background: rgba(212,160,23,.12);
    border: 1px solid rgba(212,160,23,.5);
    color: var(--dourado);
}
/* Alerta de alterações ainda não salvas no Firebase */
.chip-alterado {
    background: rgba(198,88,79,.12);
    border: 1px solid rgba(198,110,79,.55);
    color: #E8A48B;
}

/* ---------- Cards de aluno ---------- */
.card-aluno {
    position: relative;
    background: linear-gradient(165deg, var(--superficie-alta) 0%, var(--superficie) 100%);
    border: 1px solid rgba(79,134,198,.28);
    border-radius: var(--raio);
    padding: .45rem .45rem .55rem;
    text-align: center;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.card-aluno:hover {
    transform: translateY(-3px);
    border-color: var(--azul-claro);
    box-shadow: 0 12px 26px rgba(0,0,0,.38);
}
.card-aluno.selecionado {
    border: 2px solid var(--dourado);
    box-shadow: 0 0 0 4px rgba(212,160,23,.22), 0 14px 30px rgba(0,0,0,.5);
    transform: translateY(-3px);
}

.card-foto img {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 10px;
    object-fit: cover;
    border: 1px solid rgba(79,134,198,.45);
    box-shadow: 0 4px 12px rgba(0,0,0,.35);
    display: block;
}
.card-aluno.selecionado .card-foto img { border-color: var(--dourado); }

.card-num-badge {
    position: absolute;
    top: .8rem; left: .8rem; z-index: 5;
    width: 32px; height: 32px;
    display: grid; place-items: center;
    background: rgba(11,31,58,.82);
    backdrop-filter: blur(3px);
    color: var(--dourado);
    font-size: .76rem; font-weight: 700;
    border-radius: 50%;
    border: 1px solid rgba(212,160,23,.55);
    box-shadow: 0 4px 10px rgba(0,0,0,.4);
    line-height: 1;
}

.card-nome {
    color: var(--texto);
    font-weight: 600;
    font-size: .82rem;
    line-height: 1.2;
    margin-top: .45rem;
    min-height: calc(2 * 1.2em);     /* reserva 2 linhas p/ alinhar a grade */
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

/* ---------- Card VAZIO (participa das trocas) ---------- */
.card-aluno.card-vazio {
    background: rgba(18,42,78,.35);
    border: 1.5px dashed rgba(159,179,206,.4);
    display: grid; place-items: center;
    aspect-ratio: 1 / 1.34;           /* ~altura de um card com foto + nome */
    padding: 0;
}
.card-aluno.card-vazio:hover { border-color: var(--azul-claro); }
.card-aluno.card-vazio.selecionado {
    border: 2px solid var(--dourado);
    background: rgba(212,160,23,.08);
}
.vazio-rotulo {
    color: rgba(159,179,206,.65);
    font-size: .72rem; font-weight: 700;
    letter-spacing: .18em;
}
.card-aluno.card-vazio.selecionado .vazio-rotulo { color: var(--dourado); }

/* ---------- Área "alunos sem lugar" ---------- */
.secao-sem-lugar-titulo {
    display: flex; align-items: center; gap: .55rem;
    margin: 1.6rem 0 .7rem;
    padding-top: 1.1rem;
    border-top: 1px dashed rgba(159,179,206,.3);
    font-family: 'Sora', sans-serif;
    font-weight: 700; font-size: 1rem;
    color: var(--texto);
}
.contador-sem-lugar {
    display: inline-grid; place-items: center;
    min-width: 24px; height: 24px; padding: 0 .4rem;
    border-radius: 999px;
    background: rgba(212,160,23,.16);
    border: 1px solid rgba(212,160,23,.55);
    color: var(--dourado);
    font-size: .72rem; font-weight: 700;
}
/* Diferencia visualmente os cards fora do mapa */
.card-aluno.card-sem-lugar {
    border-style: dashed;
    border-color: rgba(212,160,23,.4);
}

/* ---------- Botões invisíveis de seleção (keys "sel_...") ----------
   Somente os botões cujo key começa com "sel_" viram uma camada
   invisível esticada sobre o card. Os demais botões são normais. */
div[data-testid="stColumn"] { position: relative; }

div[data-testid="stColumn"] div[class*="st-key-sel_"] {
    position: absolute;
    inset: 0;
    width: 100% !important;
    z-index: 10;
    margin: 0;
}
div[class*="st-key-sel_"] div.stButton,
div[class*="st-key-sel_"] div.stButton > button {
    width: 100%;
    height: 100%;
}
div[class*="st-key-sel_"] div.stButton > button {
    min-height: 0;
    padding: 0;
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    box-shadow: none !important;
    cursor: pointer;
    border-radius: var(--raio);
}
div[class*="st-key-sel_"] div.stButton > button:focus-visible {
    outline: 2px solid var(--dourado);
    outline-offset: 2px;
}
/* Hover do card mesmo com o botão por cima */
div[data-testid="stColumn"] div[data-testid="stVerticalBlock"]:has(div[class*="st-key-sel_"] button:hover) .card-aluno {
    transform: translateY(-3px);
    border-color: var(--azul-claro);
    box-shadow: 0 12px 26px rgba(0,0,0,.38);
}
div[data-testid="stColumn"] div[data-testid="stVerticalBlock"]:has(div[class*="st-key-sel_"] button:hover) .card-aluno.selecionado {
    border-color: var(--dourado);
    box-shadow: 0 0 0 4px rgba(212,160,23,.22), 0 14px 30px rgba(0,0,0,.5);
}

/* ---------- Botões nomeados ---------- */
/* Salvar (dourado, destaque) */
.st-key-btn_salvar button {
    background: linear-gradient(150deg, var(--dourado), #B8890F) !important;
    color: #14233D !important;
    border: none !important;
    font-weight: 700 !important;
    letter-spacing: .04em;
    border-radius: 10px !important;
    box-shadow: 0 8px 20px rgba(212,160,23,.25);
}
.st-key-btn_salvar button:hover { filter: brightness(1.08); }

/* Enviar para sem lugar / sair / login: contorno discreto */
.st-key-btn_semlugar button,
.st-key-btn_sair button,
.st-key-btn_sair_negado button,
.st-key-btn_google button,
.st-key-btn_demo button {
    background: var(--superficie) !important;
    color: var(--texto) !important;
    border: 1px solid rgba(79,134,198,.45) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
.st-key-btn_google button { border-color: rgba(212,160,23,.6) !important; }
.st-key-btn_semlugar button:hover,
.st-key-btn_sair button:hover,
.st-key-btn_google button:hover,
.st-key-btn_demo button:hover { border-color: var(--dourado) !important; }

/* ---------- Tela de login ---------- */
.cartao-login {
    max-width: 560px;
    margin: 3.5rem auto 1.4rem;
    padding: 2rem 2.2rem;
    text-align: center;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(29,78,137,.5) 0%, rgba(11,31,58,.35) 70%);
    border: 1px solid rgba(79,134,198,.35);
    border-bottom: 2px solid rgba(212,160,23,.65);
    box-shadow: 0 14px 34px rgba(0,0,0,.35);
}
.brasao-login {
    width: 72px; height: 72px; margin: 0 auto 1rem;
    border-radius: 18px; display: grid; place-items: center;
    font-size: 2.2rem;
    background: linear-gradient(150deg, var(--azul-medio), var(--azul-escuro));
    border: 1px solid rgba(212,160,23,.6);
    box-shadow: 0 8px 20px rgba(0,0,0,.4);
}
.subtitulo-login {
    color: var(--dourado);
    font-size: .78rem; font-weight: 700;
    letter-spacing: .16em; text-transform: uppercase;
    margin: .4rem 0 1rem;
}
.texto-login { color: var(--texto-suave); font-size: .9rem; line-height: 1.55; }

/* ---------- Mesa do professor e porta ---------- */
.mesa-professor {
    margin: 1.6rem auto .9rem;
    max-width: 460px;
    background: linear-gradient(150deg, var(--azul-medio), #173E6E);
    border: 1px solid rgba(212,160,23,.6);
    border-radius: var(--raio);
    color: var(--texto);
    text-align: center;
    padding: .95rem 1rem;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    letter-spacing: .14em;
    font-size: .86rem;
    box-shadow: 0 10px 26px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.08);
}
.mesa-professor .selo { color: var(--dourado); margin-right: .45rem; }

.porta-sala {
    margin: 0 auto;
    width: max-content;
    color: var(--texto-suave);
    border: 1px solid rgba(159,179,206,.3);
    border-radius: 999px;
    padding: .42rem 1.2rem;
    font-size: .8rem;
    font-weight: 600;
    letter-spacing: .12em;
    background: rgba(18,42,78,.6);
}

/* ---------- Animações ---------- */
@keyframes surgir {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.card-aluno, .mesa-professor, .porta-sala, .faixa-titulo, .cartao-login {
    animation: surgir .35s ease both;
}
@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
}

/* ---------- Responsividade ---------- */
@media (max-width: 1024px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
}
/* Celular: mantém a grade da sala, com cards compactos */
@media (max-width: 640px) {
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: .35rem !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
    }
    .faixa-titulo { padding: .8rem .9rem; gap: .7rem; }
    .faixa-titulo .brasao { width: 46px; height: 46px; font-size: 1.4rem; border-radius: 12px; }
    .linha-meta { margin-top: .3rem; gap: .4rem; }
    .pill-turno, .pill-equipe, .pill-leitura { font-size: .62rem; padding: .2rem .6rem; }
    .meta-info { font-size: .7rem; }

    .card-aluno { padding: .3rem .3rem .4rem; border-radius: 11px; }
    .card-foto img { border-radius: 8px; }
    .card-nome { font-size: .62rem; margin-top: .3rem; }
    .card-num-badge { top: .5rem; left: .5rem; width: 20px; height: 20px; font-size: .56rem; }
    .vazio-rotulo { font-size: .56rem; letter-spacing: .12em; }
    .mesa-professor { font-size: .72rem; padding: .75rem .6rem; letter-spacing: .1em; }
    .cartao-login { margin-top: 1.5rem; padding: 1.4rem 1.1rem; }
}

/* Setas de recolher/expandir a sidebar sempre visíveis */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] button {
    color: #D4A017 !important;
}
</style>
"""


def aplicar_estilos() -> None:
    """Injeta o CSS na página. Chame uma vez, no início do app."""
    st.markdown(_CSS, unsafe_allow_html=True)
