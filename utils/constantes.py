"""Constantes globais do sistema.

Tudo que é "número mágico" ou texto fixo do sistema fica aqui,
para você ajustar em um único lugar.
"""

# ---------------------------------------------------------------
# Dimensões fixas da sala
# ---------------------------------------------------------------
# A sala SEMPRE tem NUM_FILAS filas e CADEIRAS_POR_FILA carteiras
# em cada fila. Toda posição sem aluno recebe o card "VAZIO".
NUM_FILAS = 5
CADEIRAS_POR_FILA = 8

# ---------------------------------------------------------------
# Marcador de carteira vazia
# ---------------------------------------------------------------
# Valor interno usado no mapeamento (e salvo no Firebase) para
# indicar uma carteira sem aluno. O card exibe "VAZIO" na tela.
# Não use este texto como nome de aluno.
VAZIO = "__VAZIO__"

# ---------------------------------------------------------------
# Fotos dos alunos
# ---------------------------------------------------------------
# Extensões de imagem aceitas (a busca é case-insensitive).
# A foto deve ter o nome completo do aluno: "MARIA DA SILVA.jpg"
EXTENSOES_IMAGEM = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

# ---------------------------------------------------------------
# Turnos
# ---------------------------------------------------------------
# Ordem de exibição dos turnos na sidebar (nomes das pastas em dados/)
TURNOS = ("matutino", "vespertino")

# Rótulos amigáveis para os turnos
ROTULOS_TURNOS = {
    "matutino": "Matutino",
    "vespertino": "Vespertino",
}

# ---------------------------------------------------------------
# Paleta — Escolas Cívico-Militares do Paraná
# ---------------------------------------------------------------
COR_AZUL_ESCURO = "#0B1F3A"
COR_AZUL_MEDIO = "#1D4E89"
COR_AZUL_CLARO = "#4F86C6"
COR_DOURADO = "#D4A017"
