"""USUÁRIOS AUTORIZADOS — edite este arquivo com os e-mails reais.

Somente e-mails listados aqui conseguem usar o sistema após o login
com Google. O e-mail retornado pelo Google é comparado (em minúsculas)
com as chaves deste dicionário.

PAPÉIS DISPONÍVEIS:
  "diretor"   → vê e EDITA todas as turmas.
  "pedagoga"  → vê e EDITA todas as turmas.
  "professor" → vê apenas as turmas listadas em "turmas";
                EDITA apenas as turmas listadas em "conselheiro_de"
                (ou seja, as turmas em que é professor conselheiro).

CAMPOS DE CADA USUÁRIO:
  nome            → nome exibido na sidebar.
  papel           → um dos papéis acima.
  turmas          → (só para professor) lista de (turno, turma) que
                    ele pode VISUALIZAR. Use os mesmos nomes das
                    pastas em dados/. Ex.: ("matutino", "3A").
  conselheiro_de  → (só para professor) lista de (turno, turma) que
                    ele pode EDITAR e SALVAR, por ser conselheiro.
                    Deve ser um subconjunto de "turmas".

Diretor e pedagoga não precisam de "turmas" nem "conselheiro_de".
"""

USUARIOS_AUTORIZADOS = {
    # ----------------------------------------------------------
    # DIREÇÃO — vê e edita tudo
    # ----------------------------------------------------------
    "diretor@escola.pr.gov.br": {
        "nome": "Nome do Diretor",
        "papel": "diretor",
    },

    # ----------------------------------------------------------
    # PEDAGOGA — vê e edita tudo
    # ----------------------------------------------------------
    "pedagoga@escola.pr.gov.br": {
        "nome": "Nome da Pedagoga",
        "papel": "pedagoga",
    },

    # ----------------------------------------------------------
    # PROFESSORES — visualizam suas turmas; editam apenas as
    # turmas em que são professores conselheiros
    # ----------------------------------------------------------
    "professor.conselheiro@escola.pr.gov.br": {
        "nome": "Prof. Conselheiro do 3A",
        "papel": "professor",
        "turmas": [("matutino", "3A"), ("vespertino", "1B")],
        "conselheiro_de": [("matutino", "3A")],
    },
    "professora.exemplo@escola.pr.gov.br": {
        "nome": "Profa. Exemplo",
        "papel": "professor",
        "turmas": [("vespertino", "1B")],
        "conselheiro_de": [],  # não é conselheira → somente leitura
    },
}

# Rótulos amigáveis dos papéis (usados na interface)
ROTULOS_PAPEIS = {
    "diretor": "Diretor(a)",
    "pedagoga": "Pedagoga",
    "professor": "Professor(a)",
}
