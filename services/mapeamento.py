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
    carteira.

Posicao = (fila, posicao_na_fila)
    fila: 1..NUM_FILAS  ·  posicao_na_fila: 1..CADEIRAS_POR_FILA
    A posição 1 é a carteira da FRENTE (junto à mesa do professor).
"""
import re

from utils.constantes import CADEIRAS_POR_FILA, NUM_FILAS, VAZIO

Posicao = tuple[int, int]  # (fila, posicao_na_fila)

_PADRAO_POSICAO = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)")


# ------------------------------------------------------------------
# Conversão de chaves (usada ao salvar/carregar JSON do Firebase)
# ------------------------------------------------------------------
def chave_para_posicao(chave: str) -> Posicao | None:
    """'(1,2)' -> (1, 2). Tolera espaços: '( 1 , 2 )'. Retorna None se inválida."""
    m = _PADRAO_POSICAO.fullmatch(chave.strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def posicao_para_chave(pos: Posicao) -> str:
    """(1, 2) -> '(1,2)'"""
    return f"({pos[0]},{pos[1]})"


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
    """True se a posição está dentro da grade 5 × 8."""
    return 1 <= pos[0] <= NUM_FILAS and 1 <= pos[1] <= CADEIRAS_POR_FILA


def gerar_mapeamento_inicial(alunos: dict[str, str]) -> dict[Posicao, str]:
    """Distribui os alunos em ordem alfabética preenchendo fila por fila
    (fila 1 da posição 1 à 8, depois fila 2, ...). Todas as carteiras
    restantes recebem VAZIO — a grade fica sempre completa."""
    nomes = sorted(alunos.keys())
    mapa: dict[Posicao, str] = {pos: VAZIO for pos in todas_as_posicoes()}
    for indice, nome in enumerate(nomes):
        fila = indice // CADEIRAS_POR_FILA + 1
        posicao = indice % CADEIRAS_POR_FILA + 1
        if fila <= NUM_FILAS:
            mapa[(fila, posicao)] = nome
        # Se houver mais alunos que carteiras, os excedentes ficarão
        # "sem lugar" (tratados por reconciliar(), chamada no app).
    return mapa


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
    alunos: dict[str, str],
) -> None:
    """Sincroniza (in place) o mapeamento com a lista oficial de alunos
    do info.json:

    1. Nomes no mapa que não existem mais no info.json viram VAZIO.
    2. Nomes na lista sem_lugar que não existem mais são removidos.
    3. Alunos novos (que não estão nem no mapa nem em sem_lugar) são
       colocados nas primeiras carteiras VAZIAS; se a sala lotar,
       vão para a lista de "sem lugar".
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
    for nome in sorted(nomes_validos - presentes):
        vaga = next((p for p in todas_as_posicoes() if mapa[p] == VAZIO), None)
        if vaga is not None:
            mapa[vaga] = nome
        else:
            sem_lugar.append(nome)


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
