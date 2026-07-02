"""Regras do mapeamento da sala.

MODELO DE DADOS
---------------
mapa: dict[Posicao, str]
    A grade da sala. SEMPRE contém todas as NUM_FILAS × CADEIRAS_POR_FILA
    posições (5 × 8 = 40). O valor é o nome do aluno, ou o marcador
    VAZIO para carteira sem aluno. O card VAZIO participa das trocas
    normalmente, como se fosse um aluno.

sem_lugar: list[str]
    Alunos que estão FORA do mapa (sem carteira). Ficam em uma área
    separada abaixo da sala e podem ser colocados de volta em qualquer
    carteira. Na exportação/leitura do info.json, correspondem à
    posição especial "(0,0)" — ver POSICAO_SEM_LUGAR abaixo.

Posicao = (fila, posicao_na_fila)
    fila: 1..NUM_FILAS  ·  posicao_na_fila: 1..CADEIRAS_POR_FILA
    A posição 1 é a carteira da FRENTE (junto à mesa do professor).

ENTRADA `alunos`
----------------
`alunos` é o retorno de `services.arquivos.carregar_alunos()`:
`dict[nome_do_aluno, posicao_desejada | None]`, onde a posição vem no
formato externo "(cadeira,fila)" ou é None quando o info.json não
informa a carteira do aluno. `chave_para_posicao` cuida da conversão
para o formato interno Posicao = (fila, cadeira).

POSIÇÃO ESPECIAL "(0,0)" — aluno sem lugar
-------------------------------------------
Um aluno cujo info.json declara "posicao": "(0,0)" começa a sessão
diretamente na área "sem lugar" (fora da grade), em vez de em uma
carteira. É a mesma convenção usada ao EXPORTAR o mapeamento atual
(botão "Baixar mapeamento"): quem está em `sem_lugar` sai no arquivo
com "posicao": "(0,0)".
"""
import re

from utils.constantes import CADEIRAS_POR_FILA, NUM_FILAS, VAZIO

Posicao = tuple[int, int]  # (fila, posicao_na_fila)

_PADRAO_POSICAO = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)")

# Marcador de "aluno sem lugar" no formato de posição (interno e
# externo coincidem, já que 0 invertido continua 0).
POSICAO_SEM_LUGAR: Posicao = (0, 0)


# ------------------------------------------------------------------
# Conversão de chaves
# ------------------------------------------------------------------
# CONVENÇÃO EXTERNA (info.json e Firebase): "(cadeira,fila)"
#   Ex.: "(1,1)" = cadeira 1 (da esquerda) da fila 1 (da frente).
#        "(8,1)" = cadeira 8 (do fundo) da fila 1 (esquerda).
#        "(5,5)" = cadeira 5 da fila 5 (direita).
#        "(0,0)" = aluno SEM LUGAR (fora da grade).
# CONVENÇÃO INTERNA: Posicao = (fila, cadeira) — fila 1..NUM_FILAS
#   e cadeira 1..CADEIRAS_POR_FILA. É o formato usado no render e nas
#   operações do mapa.
# Por isso as duas funções abaixo INVERTEM a ordem — para manter a
# convenção externa consistente onde quer que o usuário a veja.
def chave_para_posicao(chave: str | None) -> Posicao | None:
    """'(cadeira,fila)' -> (fila, cadeira). Tolera espaços: '( 1 , 2 )'.
    '(0,0)' -> (0, 0) (aluno sem lugar — ver POSICAO_SEM_LUGAR).
    Retorna None para entrada None, vazia ou fora do formato."""
    if not chave:
        return None
    m = _PADRAO_POSICAO.fullmatch(str(chave).strip())
    if not m:
        return None
    cadeira, fila = int(m.group(1)), int(m.group(2))
    return fila, cadeira


def posicao_para_chave(pos: Posicao) -> str:
    """(fila, cadeira) -> '(cadeira,fila)' — inversa de chave_para_posicao.
    (0, 0) -> '(0,0)' (aluno sem lugar)."""
    fila, cadeira = pos
    return f"({cadeira},{fila})"


def eh_posicao_sem_lugar(pos: Posicao | None) -> bool:
    """True se `pos` é o marcador de "aluno sem lugar" (0, 0)."""
    return pos == POSICAO_SEM_LUGAR


# ------------------------------------------------------------------
# Grade
# ------------------------------------------------------------------
def todas_as_posicoes() -> list[Posicao]:
    """Todas as posições da grade fixa, em ordem: fila 1 da frente
    para o fundo, depois fila 2, e assim por diante."""
    return [
        (fila, posicao)
        for fila in range(1, NUM_FILAS + 1)
        for posicao in range(1, CADEIRAS_POR_FILA + 1)
    ]


def posicao_valida(pos: Posicao) -> bool:
    """True se a posição está dentro da grade 5 × 8 (não conta a
    posição especial (0,0), que fica FORA da grade por definição)."""
    return 1 <= pos[0] <= NUM_FILAS and 1 <= pos[1] <= CADEIRAS_POR_FILA


def _primeira_vaga(mapa: dict[Posicao, str]) -> Posicao | None:
    """Primeira carteira VAZIA da grade, na ordem de `todas_as_posicoes()`.
    Retorna None se a sala estiver cheia."""
    return next((p for p in todas_as_posicoes() if mapa[p] == VAZIO), None)


def gerar_estado_inicial(
    alunos: dict[str, str | None],
) -> tuple[dict[Posicao, str], list[str]]:
    """Cria o estado inicial (mapa + sem_lugar) a partir do info.json,
    respeitando as posições declaradas.

    Regras (nesta ordem):
    1. Aluno com posicao "(0,0)" vai direto para `sem_lugar` (nunca
       ocupa uma carteira).
    2. Aluno com posicao válida ("(cadeira,fila)" dentro da grade e
       ainda livre) é colocado exatamente onde pediu.
    3. Se dois alunos declararem a MESMA posição, o primeiro fica com
       ela; o(s) outro(s) caem na regra 4.
    4. Alunos sem posição (ausente, inválida ou já ocupada) são
       distribuídos, em ordem alfabética, nas carteiras VAZIAS
       restantes (fila 1 cadeira 1..8, fila 2 cadeira 1..8, ...).
    5. Se não houver mais carteiras vazias, o aluno vai para
       `sem_lugar` também.
    """
    mapa: dict[Posicao, str] = {pos: VAZIO for pos in todas_as_posicoes()}
    sem_lugar: list[str] = []
    sem_posicao: list[str] = []

    for nome, posicao_str in alunos.items():
        pos = chave_para_posicao(posicao_str)
        if eh_posicao_sem_lugar(pos):
            sem_lugar.append(nome)
        elif pos and posicao_valida(pos) and mapa[pos] == VAZIO:
            mapa[pos] = nome
        else:
            sem_posicao.append(nome)

    for nome in sorted(sem_posicao):
        vaga = _primeira_vaga(mapa)
        if vaga is not None:
            mapa[vaga] = nome
        else:
            sem_lugar.append(nome)

    return mapa, sem_lugar


def completar_grade(mapa: dict[Posicao, str]) -> None:
    """Garante (in place) que o mapa tenha exatamente as 40 posições:
    preenche as que faltam com VAZIO e descarta posições fora da grade.
    Útil ao carregar dados antigos ou editados à mão no Firebase."""
    for pos in list(mapa):
        if not posicao_valida(pos):
            del mapa[pos]
    for pos in todas_as_posicoes():
        mapa.setdefault(pos, VAZIO)


def reconciliar(
    mapa: dict[Posicao, str],
    sem_lugar: list[str],
    alunos: dict[str, str | None],
) -> None:
    """Sincroniza (in place) o mapeamento com a lista oficial de alunos
    do info.json:

    1. Nomes no mapa que não existem mais no info.json viram VAZIO.
    2. Nomes na lista sem_lugar que não existem mais são removidos.
    3. Alunos novos (que não estão nem no mapa nem em sem_lugar):
       a) quem declarou "(0,0)" vai direto para sem_lugar;
       b) quem declarou uma posição válida e livre entra nela;
       c) os demais (sem posição, inválida ou ocupada) entram na
          primeira carteira VAZIA disponível; se a sala lotar, vão
          para sem_lugar.
    """
    nomes_validos = set(alunos)

    # 1) remove do mapa quem saiu da turma
    for pos, nome in mapa.items():
        if nome != VAZIO and nome not in nomes_validos:
            mapa[pos] = VAZIO

    # 2) limpa a lista de sem lugar
    sem_lugar[:] = [n for n in sem_lugar if n in nomes_validos]

    # 3) encaixa alunos novos
    presentes = {n for n in mapa.values() if n != VAZIO} | set(sem_lugar)
    novos = sorted(nomes_validos - presentes)

    com_posicao: list[tuple[str, Posicao]] = []
    sem_posicao_declarada: list[str] = []
    for nome in novos:
        pos = chave_para_posicao(alunos.get(nome))
        if eh_posicao_sem_lugar(pos):
            sem_lugar.append(nome)  # 3a
        elif pos and posicao_valida(pos):
            com_posicao.append((nome, pos))
        else:
            sem_posicao_declarada.append(nome)

    # 3b) posições declaradas (se a vaga ainda estiver livre)
    for nome, pos in com_posicao:
        if mapa.get(pos) == VAZIO:
            mapa[pos] = nome
        else:
            sem_posicao_declarada.append(nome)

    # 3c) sem posição (ou com posição já ocupada): primeira vaga VAZIA
    for nome in sem_posicao_declarada:
        vaga = _primeira_vaga(mapa)
        if vaga is not None:
            mapa[vaga] = nome
        else:
            sem_lugar.append(nome)


# ------------------------------------------------------------------
# Exportação (botão "Baixar mapeamento")
# ------------------------------------------------------------------
def exportar_para_info_json(
    mapa: dict[Posicao, str],
    sem_lugar: list[str],
    info_original: dict[str, dict],
) -> dict[str, dict]:
    """Gera um dict pronto para virar um novo info.json, refletindo o
    mapeamento ATUAL da tela (após as trocas feitas na sessão).

    Cada aluno mantém todos os campos que já tinha em `info_original`
    (por exemplo "numero") e apenas o campo "posicao" é atualizado:
    - carteira ocupada  -> "(cadeira,fila)" correspondente;
    - fora do mapa (sem_lugar) -> "(0,0)".

    `info_original` é o retorno de `services.arquivos.carregar_info()`.
    """
    dados: dict[str, dict] = {}

    for pos, nome in mapa.items():
        if nome == VAZIO:
            continue
        entrada = dict(info_original.get(nome, {}))
        entrada["posicao"] = posicao_para_chave(pos)
        dados[nome] = entrada

    for nome in sem_lugar:
        entrada = dict(info_original.get(nome, {}))
        entrada["posicao"] = posicao_para_chave(POSICAO_SEM_LUGAR)
        dados[nome] = entrada

    return dados


# ------------------------------------------------------------------
# Operações de edição (usadas pelos cliques nos cards)
# ------------------------------------------------------------------
def trocar_alunos(mapa: dict[Posicao, str], pos_a: Posicao, pos_b: Posicao) -> None:
    """Troca os ocupantes de duas carteiras (in place).
    Funciona igualmente com cards VAZIO."""
    mapa[pos_a], mapa[pos_b] = mapa[pos_b], mapa[pos_a]


def colocar_sem_lugar(
    mapa: dict[Posicao, str], sem_lugar: list[str], pos: Posicao
) -> str | None:
    """Tira o aluno da carteira `pos` e o coloca na lista de sem lugar.
    A carteira vira VAZIO. Retorna o nome movido (ou None se já era VAZIO)."""
    nome = mapa.get(pos, VAZIO)
    if nome == VAZIO:
        return None
    mapa[pos] = VAZIO
    sem_lugar.append(nome)
    return nome


def colocar_no_mapa(
    mapa: dict[Posicao, str], sem_lugar: list[str], nome: str, pos: Posicao
) -> str | None:
    """Coloca um aluno da lista de sem lugar na carteira `pos`.
    Se a carteira estava ocupada, o ocupante anterior vai para a lista
    de sem lugar (é uma troca). Retorna o nome do ocupante deslocado,
    ou None se a carteira estava VAZIA."""
    ocupante = mapa.get(pos, VAZIO)
    if nome in sem_lugar:
        sem_lugar.remove(nome)
    mapa[pos] = nome
    if ocupante != VAZIO:
        sem_lugar.append(ocupante)
        return ocupante
    return None
