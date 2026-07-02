"""CREDENCIAIS DO FIREBASE — edite este arquivo com os valores reais.

┌──────────────────────────────────────────────────────────────────┐
│  ONDE FICA CADA CREDENCIAL DO SISTEMA                            │
│                                                                  │
│  • Firebase (salvar/carregar mapeamento) ......... este arquivo │
│  • Login com Google (OAuth) ....... .streamlit/secrets.toml     │
│  • E-mails autorizados e papéis ....... config/usuarios.py      │
│  • Conselheiro/pedagoga de cada turma .. config/equipe.py       │
└──────────────────────────────────────────────────────────────────┘

COMO CONFIGURAR O FIREBASE (Realtime Database):
1. Acesse https://console.firebase.google.com e crie um projeto.
2. No menu "Criação" > "Realtime Database", clique em "Criar banco de dados".
3. Copie a URL do banco (algo como https://seu-projeto-default-rtdb.firebaseio.com)
   e cole em FIREBASE_URL abaixo (SEM barra no final).
4. Token de acesso (FIREBASE_AUTH_TOKEN):
   - Opção simples (segredo legado): no console, engrenagem > Configurações
     do projeto > Contas de serviço > Segredos do banco de dados > copie o segredo.
   - Se preferir deixar o banco aberto durante testes (regras
     ".read": true / ".write": true), pode deixar o token como "".
     ⚠ NUNCA deixe o banco aberto em produção.

Enquanto FIREBASE_URL continuar com o valor de exemplo abaixo, o botão
"Salvar" sempre exibirá "Não salvo" (comportamento esperado até você
configurar as credenciais reais).
"""

# URL do Realtime Database — TROQUE pelo valor real, sem "/" no final.
FIREBASE_URL = "https://SEU_PROJETO-default-rtdb.firebaseio.com"

# Token/segredo de autenticação do banco. Deixe "" se as regras do banco
# permitirem leitura/escrita sem autenticação (apenas para testes!).
FIREBASE_AUTH_TOKEN = ""

# Nó (pasta) dentro do banco onde os mapeamentos são gravados.
# Os dados ficam em: <FIREBASE_URL>/<FIREBASE_NO_RAIZ>/<turno>/<turma>.json
FIREBASE_NO_RAIZ = "mapeamentos"

# Tempo máximo (segundos) de espera pelas requisições ao Firebase.
FIREBASE_TIMEOUT = 10
