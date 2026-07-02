# 🏫 Mapa da Sala

Sistema de mapeamento de salas de aula em Streamlit, com visual escuro inspirado
nas Escolas Cívico-Militares do Paraná.

- **Grade fixa 5 × 8**: toda sala tem 5 filas com 8 carteiras. Carteiras sem
  aluno recebem um card **VAZIO**, que participa das trocas como um aluno normal.
- **Alunos sem lugar**: qualquer aluno pode ser tirado do mapa e ficar em uma
  área separada abaixo da sala (a carteira dele vira VAZIO). De lá, pode voltar
  para qualquer carteira.
- **Login com Google** com lista de e-mails autorizados e papéis
  (diretor, pedagoga, professor) + **botão de demonstração** removível.
- **Permissões**: cada professor vê o mapa das suas turmas, mas só o
  **professor conselheiro** da turma, a **pedagoga** e o **diretor** podem
  editar e salvar.
- **Salvamento no Firebase** (Realtime Database, via `requests`) apenas ao
  clicar em **Salvar** — não há mais persistência local nem salvamento
  automático. Enquanto o Firebase não estiver configurado, o botão exibe
  "❌ Não salvo".

---

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Na tela inicial, use **"🎭 Entrar em modo demonstração"** para testar tudo sem
configurar o Google (o modo demo entra como diretor, com acesso total).

---

## Estrutura de pastas

```
app.py                      # ponto de entrada — fluxo geral da página
requirements.txt
.streamlit/
    secrets.toml            # ← credenciais do LOGIN COM GOOGLE (editar!)
config/                     # ← tudo que você precisa editar fica aqui
    credenciais.py          # ← credenciais do FIREBASE (editar!)
    usuarios.py             # ← e-mails autorizados e papéis (editar!)
    equipe.py               # ← conselheiro/pedagoga exibidos por turma (editar!)
components/                 # interface
    styles.py               # todo o CSS (visual)
    sidebar.py              # usuário logado + seleção de turno/turma
    cards.py                # HTML dos cards (aluno, VAZIO, mesa, porta)
    layout_sala.py          # grade da sala, área "sem lugar" e lógica de cliques
services/                   # regras e integrações
    auth.py                 # login Google, botão demo, papéis e permissões
    firebase.py             # salvar/carregar mapeamento via requests
    mapeamento.py           # grade 5×8, VAZIO, trocas, reconciliação
    arquivos.py             # leitura de dados/ (turnos, turmas, info.json)
    imagens.py              # fotos dos alunos (busca por nome + cache)
utils/
    constantes.py           # nº de filas/carteiras, marcador VAZIO, turnos
    paths.py                # caminhos do projeto
assets/
    avatar_padrao.png       # foto padrão de quem não tem imagem
dados/
    matutino/3A/info.json   # turmas de exemplo (substitua pelas reais)
    vespertino/1B/info.json
```

---

## Dados das turmas

Cada turma é uma pasta `dados/<turno>/<turma>/` com um `info.json`:

```json
{
    "MARIA DA SILVA":  { "numero": 1 },
    "JOÃO DOS SANTOS": { "numero": 2 }
}
```

`numero` é o número da chamada (aparece no badge do card).

**Fotos (opcionais)** ficam na mesma pasta, com o nome completo do aluno:
`MARIA DA SILVA.jpg`. A busca ignora acentos e maiúsculas/minúsculas.
Extensões aceitas: `.jpg .jpeg .png .webp .bmp`. Sem foto, usa-se o avatar padrão.

**Dimensões da sala**: se um dia precisar de outra grade, mude `NUM_FILAS` e
`CADEIRAS_POR_FILA` em `utils/constantes.py`.

---

## Papéis e permissões — `config/usuarios.py`

| Papel       | Vê                      | Edita e salva                    |
|-------------|-------------------------|----------------------------------|
| `diretor`   | todas as turmas         | todas as turmas                  |
| `pedagoga`  | todas as turmas         | todas as turmas                  |
| `professor` | só as turmas em `turmas`| só as turmas em `conselheiro_de` |

Exemplo de professor:

```python
"prof@escola.pr.gov.br": {
    "nome": "Prof. Fulano",
    "papel": "professor",
    "turmas": [("matutino", "3A"), ("vespertino", "1B")],  # pode VER
    "conselheiro_de": [("matutino", "3A")],                # pode EDITAR
},
```

Use os mesmos nomes das pastas em `dados/`. Quem loga com um e-mail fora da
lista vê a tela de "acesso negado".

Os **nomes exibidos** de conselheiro e pedagoga no cabeçalho de cada turma
ficam em `config/equipe.py` (é só exibição — as permissões vêm de
`usuarios.py`).

---

## Login com Google — `.streamlit/secrets.toml`

O app usa o login nativo do Streamlit (`st.login`, requer `streamlit>=1.42`
e `Authlib`, já no requirements). Configuração:

1. Acesse <https://console.cloud.google.com> e crie/selecione um projeto.
2. **APIs e serviços → Tela de consentimento OAuth**: configure como
   "Externo" (ou "Interno", se usar Google Workspace da escola), preencha
   nome do app e e-mail de suporte.
3. **APIs e serviços → Credenciais → Criar credenciais → ID do cliente
   OAuth → Aplicativo da Web**.
4. Em **URIs de redirecionamento autorizados**, adicione exatamente:
   - `http://localhost:8501/oauth2callback` (para rodar local)
   - `https://SEU-DOMINIO/oauth2callback` (quando publicar)
5. Copie o **ID do cliente** e a **chave secreta** para
   `.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "string-longa-e-aleatoria-criada-por-voce"
client_id = "xxxxx.apps.googleusercontent.com"
client_secret = "xxxxx"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

Para gerar o `cookie_secret`:
`python -c "import secrets; print(secrets.token_hex(32))"`

Enquanto o `client_id` estiver com o valor de exemplo, o botão
"Entrar com Google" mostra um aviso e o modo demonstração continua funcionando.

### Botão de demonstração (remover em produção)

O botão "🎭 Entrar em modo demonstração" pula o login e entra como um diretor
fictício. Para remover, abra `services/auth.py` e mude **uma linha**:

```python
MOSTRAR_BOTAO_DEMO = False
```

(Os blocos relacionados estão marcados com o comentário `BLOCO DEMO`, caso
queira apagá-los de vez.)

---

## Firebase — `config/credenciais.py`

O botão **💾 Salvar mapeamento** grava no Firebase Realtime Database via API
REST (`requests`), no caminho:

```
<FIREBASE_URL>/mapeamentos/<turno>/<turma>.json
{
    "mapa": { "(1,1)": "NOME DO ALUNO", "(1,2)": "__VAZIO__", ... },
    "sem_lugar": ["NOME A", "NOME B"]
}
```

Configuração:

1. Crie um projeto em <https://console.firebase.google.com>.
2. **Criação → Realtime Database → Criar banco de dados**.
3. Copie a URL (ex.: `https://seu-projeto-default-rtdb.firebaseio.com`) para
   `FIREBASE_URL` em `config/credenciais.py` (sem `/` no final).
4. Token: em **⚙ Configurações do projeto → Contas de serviço → Segredos do
   banco de dados**, copie o segredo para `FIREBASE_AUTH_TOKEN`.
   (Para testes rápidos, você pode deixar `""` e abrir as regras do banco —
   `".read": true, ".write": true` — mas **nunca em produção**.)

Comportamento:

- **Firebase configurado + salvar OK** → "✅ Salvo com sucesso!"
- **Qualquer falha (ou não configurado)** → "❌ Não salvo" com o motivo.
- Ao abrir uma turma, o app tenta **carregar** o mapeamento salvo no Firebase;
  se não existir (ou o Firebase não estiver configurado), gera o layout
  inicial automaticamente (alunos em ordem alfabética, fila por fila, e VAZIO
  nas carteiras que sobram).
- O layout carregado é **reconciliado** com o `info.json`: alunos que saíram
  viram VAZIO; alunos novos entram nas primeiras carteiras vazias (ou na área
  "sem lugar" se a sala lotar).

---

## Como usar o mapa

1. **Trocar dois lugares**: toque no primeiro card (ganha borda dourada) e
   depois no segundo. Vale também para o card **VAZIO** — trocar um aluno com
   um VAZIO simplesmente o move de carteira.
2. **Tirar um aluno do mapa**: toque no card dele e clique em
   **"🪑 Enviar aluno selecionado para «sem lugar»"**. A carteira vira VAZIO e
   o aluno aparece na área "Alunos sem lugar no mapa", abaixo da sala.
3. **Recolocar**: toque no aluno da área "sem lugar" e depois na carteira
   desejada (ou vice-versa). Se a carteira estava ocupada, os dois trocam:
   o ocupante anterior vai para a área "sem lugar".
4. **Salvar**: nada é salvo automaticamente. Clique em
   **💾 Salvar mapeamento** para gravar no Firebase. O aviso vermelho
   "Alterações não salvas" lembra quando há mudanças pendentes.

Usuários sem permissão de edição veem o mapa em **somente leitura**
(cards não clicáveis, sem botão Salvar, com o selo 🔒 no cabeçalho).
