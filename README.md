# StockFlow API

API REST para gerenciamento de produtos, fornecedores, categorias e movimentações de estoque.

Projeto desenvolvido como desafio técnico da trilha Back-End do Prosel 2026.2 da EcompJr.

---

## Tecnologias Utilizadas

A aplicação faz uso exclusivamente das seguintes ferramentas, sem abstrações ou bibliotecas extras desnecessárias:

- **Linguagem:** Python 3.12
- **Framework Web:** FastAPI
- **Banco de Dados:** PostgreSQL
- **ORM:** SQLAlchemy 2.x
- **Driver de Banco:** Psycopg 3
- **Migrations:** Alembic
- **Validação e Configurações:** Pydantic e pydantic-settings
- **Servidor ASGI:** Uvicorn
- **Hashing:** pwdlib[argon2] (hash e verificação de senha)
- **Autenticação:** PyJWT (criação e validação de access tokens JWT)

---

## Pré-requisitos

Para rodar o projeto localmente, é necessário ter instalado:

- **Python 3.12+**
- **PostgreSQL 14+**
- **Git**

---

## Configuração do Banco de Dados PostgreSQL

Antes de iniciar a API, você deve possuir um banco de dados PostgreSQL funcional.
O comando `CREATE ROLE` e `CREATE DATABASE` devem ser executados durante o provisionamento por uma conta PostgreSQL que possua privilégios suficientes. A role `stockflow_app` é a usada normalmente pela aplicação e ela não precisa ser superuser. Conecte-se ao `psql` (ou ferramenta visual de sua preferência) e execute:

```sql
CREATE ROLE stockflow_app WITH LOGIN PASSWORD '<senha-local>';
CREATE DATABASE stockflow OWNER stockflow_app;
```

*(Substitua `<senha-local>` por uma senha segura apenas para seu ambiente de desenvolvimento).*

---

## Instalação e Configuração de Ambiente

Siga esta ordem exata para preparar o ambiente:

1. Clone o repositório:
   ```bash
   git clone https://github.com/cleidson21/stockflow-api.git
   cd stockflow-api
   ```

2. Crie e ative um ambiente virtual isolado:
   - **Linux/macOS:**
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   - Copie o arquivo base: `cp .env.example .env`
   - Preencha os dados do `.env`. Ele não deve ser versionado.
   ```ini
   DB_HOST=127.0.0.1
   DB_PORT=5432
   DB_NAME=stockflow
   DB_USER=stockflow_app
   DB_PASSWORD=<senha-local>

   JWT_SECRET_KEY=CHANGE_ME_WITH_A_RANDOM_SECRET
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
   *Nota sobre o JWT:* `JWT_SECRET_KEY` é obrigatório, requer um comprimento mínimo, deve ser um segredo forte e nunca versionado (você pode gerar um valor com `openssl rand -hex 32` localmente). `JWT_ALGORITHM` usa HS256. `ACCESS_TOKEN_EXPIRE_MINUTES` define a duração do access token (60 minutos por padrão).

5. Aplique as migrações estruturais do banco de dados (Alembic):
   ```bash
   alembic upgrade head
   ```

6. Crie o primeiro usuário administrativo (necessário para usar as rotas protegidas):
   ```bash
   python -m app.cli.create_user --username admin --role ADMIN
   ```
   *(A senha será solicitada interativamente no terminal por segurança. Ela é armazenada somente como hash Argon2 e o username deve ser único. Você também pode criar um FUNCIONARIO informando `--role FUNCIONARIO`).*

7. Inicie o servidor:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

---

## Autenticação, Segurança JWT e RBAC

A aplicação possui um controle rigoroso de acesso e perfis.

### Rotas Públicas vs Protegidas
- **Públicas (sem token):** `GET /`, `GET /health`, `POST /auth/login`, `/docs`, `/openapi.json`.
- **Protegidas:** Todas as demais rotas de negócio exigem envio de um Bearer JWT no header `Authorization`.

### Login e Swagger UI
Para obter acesso, chame a rota de login:
**POST /auth/login**
```json
{
  "username": "admin",
  "password": "..."
}
```
Resposta conceitual:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```
No **Swagger UI** (`/docs`), após gerar o token de acesso via `/auth/login`, copie o `access_token`, clique no botão **Authorize** no topo da tela e cole-o (o prefixo Bearer é embutido automaticamente pelo OpenAPI/FastAPI, forneça apenas o token).

### Arquitetura JWT e Revogação
- O JWT é **assinado**, não criptografado, e o header/payload usam representação Base64URL.
- HS256 usa HMAC-SHA256.
- O payload contém somente: `sub` (identificador do usuário) e `exp`. A senha, o password_hash e a sua _role_ atual NÃO entram no JWT.
- A _role_ é consultada **em tempo real** no banco. Se um ADMIN for alterado para FUNCIONARIO, o mesmo token já emitido obedece instantaneamente ao novo nível de acesso. Se um usuário for removido, o token devolve imediatamente `401`.

### Matriz de Autorização por Perfis (RBAC)
Existem dois perfis principais no estoque corporativo:

| Permissão | ADMIN | FUNCIONARIO |
| :--- | :--- | :--- |
| Criar/Editar/Excluir Categorias, Fornecedores e Produtos | ✅ Permitido | ❌ Proibido |
| Consultar Categorias, Fornecedores e Produtos | ✅ Permitido | ✅ Permitido |
| Listar Produtos com Estoque Mínimo | ✅ Permitido | ✅ Permitido |
| Consultar Movimentações | ✅ Permitido | ✅ Permitido |
| Criar Movimentações (Entrada/Saída) | ✅ Permitido | ✅ Permitido |

---

## Arquitetura do Projeto

A arquitetura atual consolida um modelo claro e pragmático (sem padrões como Repository, Service ou DAO genéricos que não foram demandados pelas complexidades atuais):

- `alembic/` - Configurações e versões de migrações do banco.
- `docs/` - Documentação oficial e registros de decisões (`DECISIONS.md`, `DOMAIN_MODELING.md`, `PROJECT_PLAN.md`).
- `app/`
  - `database.py` - Controle da engine e gerenciamento atômico das sessions.
  - `exceptions.py` - Interceptadores e formatação segura dos Handlers Globais (500, 422, HTTPExceptions).
  - `config.py` - Gerenciamento de variáveis via *pydantic-settings*.
  - `main.py` - Registro de roteadores e instanciamento global do FastAPI.
  - `models/` - Declaração puramente persistente (SQLAlchemy).
  - `schemas/` - Validação rígida e modelos de entrada/saída HTTP (Pydantic).
  - `routers/` - Endpoints, dependências e processamento de regras de negócios controladas.
  - `security/` - Configuração e regras unificadas de senhas, JWT e auth.
  - `cli/` - Comandos e scripts administrativos.

---

## Endpoints e Recursos

| Método   | Rota                                      | Função |
| :------- | :---------------------------------------- | :----- |
| **GET**  | `/`                                       | Retorna status básico. |
| **GET**  | `/health`                                 | Confirma integridade operacional do servidor. |
| **POST** | `/auth/login`                             | Efetua autenticação e devolve JWT. |
| **GET**  | `/categorias`                             | Lista categorias. |
| **POST** | `/categorias`                             | Cria uma categoria (ADMIN). |
| **GET**  | `/categorias/{categoria_id}`              | Busca categoria específica. |
| **PUT**  | `/categorias/{categoria_id}`              | Edita categoria (ADMIN). |
| **DELETE**| `/categorias/{categoria_id}`             | Exclui categoria (ADMIN). |
| **GET**  | `/fornecedores`                           | Lista fornecedores. |
| **POST** | `/fornecedores`                           | Cria um fornecedor (ADMIN). |
| **GET**  | `/fornecedores/{fornecedor_id}`           | Busca fornecedor específico. |
| **PUT**  | `/fornecedores/{fornecedor_id}`           | Edita fornecedor (ADMIN). |
| **DELETE**| `/fornecedores/{fornecedor_id}`          | Exclui fornecedor (ADMIN). |
| **GET**  | `/produtos`                               | Lista produtos. |
| **POST** | `/produtos`                               | Cria um produto (ADMIN). |
| **GET**  | `/produtos/{produto_id}`                  | Busca produto específico. |
| **PUT**  | `/produtos/{produto_id}`                  | Edita produto (ADMIN). |
| **DELETE**| `/produtos/{produto_id}`                 | Exclui produto (ADMIN). |
| **GET**  | `/produtos/consultas/estoque-minimo`      | Lista produtos com estoque em limite crítico. |
| **GET**  | `/movimentacoes`                          | Lista movimentações históricas. |
| **POST** | `/movimentacoes`                          | Efetua movimentação transacional e atualiza o estoque. |
| **GET**  | `/movimentacoes/{movimentacao_id}`        | Busca uma movimentação pelo ID. |

### Consultas Avançadas em Movimentações

O endpoint `GET /movimentacoes` possui três Query Parameters Opcionais cumulativos:
- `data_inicio` e `data_fim`: Filtram movimentações pertencentes a um período cronológico.
- `fornecedor_id`: Filtra apenas as movimentações em que o fornecedor histórico era o dono do produto na época da inserção.

---

## Regras de Negócio Implementadas

1. **Campos com restrição de unicidade:** `Categoria.nome`, `Fornecedor.cnpj`, `Fornecedor.email` e `Produto.sku` possuem _constraints UNIQUE_ no banco de dados. Esses valores podem ser atualizados via PUT, desde que continuem únicos. A entidade imutável pela API é `MovimentacaoEstoque`.
2. **Ciclo de Vida do Estoque:** Todo Produto nasce com estoque `0`. A chave `quantidade_em_estoque` nunca pode ser manipulada nos fluxos `POST`/`PUT` de Produto. O saldo só é alterado por Movimentações validas.
3. **Movimentações Auditáveis:** Toda movimentação (tipo `ENTRADA` ou `SAIDA`) tem seu contrato congelado, não existindo rotas de `PUT`/`PATCH`/`DELETE` de movimentação. Além disso, uma transação deve ter obrigatoriamente `quantidade > 0`.
4. **Saldo e Integridade:** Operações de `SAIDA` estão rigidamente limitadas a `quantidade_em_estoque`. Estoque negativo não é admitido na base de dados.
5. **Delete Restrito:** Nenhuma exclusão no banco faz cascata livre (`ON DELETE RESTRICT`). Não é possível apagar uma categoria ligada a produtos, nem produtos que possuam lastros de movimentação.
6. **Fornecedor Histórico:** Em `MovimentacaoEstoque.fornecedor_id` guardamos a cópia histórica do fornecedor cadastral atual do Produto no momento em que a movimentação foi criada.
7. **Estoque Mínimo:** Trata-se da notificação analítica visual sempre que `quantidade_em_estoque <= estoque_minimo`.

---

## Transação e Concorrência

Para assegurar blindagem contra concorrência e o antipadrão _lost update_, a submissão de movimentações foi desenhada em uma arquitetura transacional rígida.
A estrutura invoca explicitamente o bloqueio através de um `SELECT ... FOR UPDATE` na linha do Produto. Requisições concorrentes sobre o mesmo Produto operam de forma isolada: uma requisição obtém o lock e processa; a segunda transação aguarda a liberação do row lock; depois do commit da primeira, ela adquire o lock, lê o saldo atualizado e recebe 409 pela regra de estoque insuficiente.

O processo funciona da seguinte forma:
1. Disparo de instrução de bloqueio no PostgreSQL (`SELECT Produto FOR UPDATE`).
2. Validação matemática do Saldo (Caso `SAIDA`).
3. Atualização lógica do `quantidade_em_estoque` e instanciamento da cópia _histórica_ (`nova_movimentacao`).
4. Fechamento seguro unificado (`COMMIT` salvando movimentação e saldo na mesma transação, ou `ROLLBACK` blindado nas exceções).

Isso garante que o saldo nunca se descole do histórico.

---

## Tratamento e Modelo de Erros

A API possui um empacotamento restritivo de exceções e bloqueia vazamento de Stack Traces para front-ends:

```json
{
  "status": 409,
  "error": "conflict",
  "message": "Já existe um produto com este SKU.",
  "details": null
}
```

- **400 Bad Request:** Requisições lógicas incompatíveis, sem tocar o banco.
- **401 Unauthorized:** Token ausente, inválido, expirado ou usuário-alvo removido. Acompanha o header `WWW-Authenticate: Bearer`.
- **403 Forbidden:** O cliente é plenamente autenticado, mas a restrição de _role_ impede o acesso. Não emite header `WWW-Authenticate`.
- **404 Not Found:** Falta de entidade (em buscas singulares ou via relacionamentos explícitos). Listagens que resultam vazias respondem `200 []`.
- **409 Conflict:** Violação de estados imutáveis, restrições de unicidade, falta de saldo ou exclusões atreladas a FK.
- **422 Validation Error:** Falha de validação do contrato de entrada. Não vaza input malicioso nos details.
- **500 Internal Server Error:** Oculta falhas técnicas para quem consome a API. Os logs técnicos permanecem seguros no console do uvicorn.

---

## Estado dos testes

A aplicação possui uma suíte automatizada permanente com **94 testes** cobrindo inteiramente: CRUD, unicidade, movimentações estritas, consultas, limites e concorrência local, além de validações estendidas sobre a mecânica de JWT e RBAC. A suíte atua obrigatoriamente sobre um banco de dados real PostgreSQL exclusivo (`stockflow_test`) e se protege contra mutações externas.

---

## Integração Contínua (CI) com GitHub Actions

Configuramos via `.github/workflows/tests.yml` um pipeline robusto ativado em `push` e `pull_request` direcionados à _main_. O Workflow automatiza: PostgreSQL 16 descartável de fundo, aplicação de Migrations Alembic do zero e o disparo de toda a suíte `pytest`. Um fluxo falho gera workflow vermelho na aba _Actions_ do repositório (O bloqueio nativo de merges em vermelho depende apenas de configurações restritas de _Branch Protection_ aplicadas individualmente pelos administradores no repositório remoto).

---

## Documentação Técnica Complementar

- [docs/DOMAIN_MODELING.md](docs/DOMAIN_MODELING.md)
- [docs/DECISIONS.md](docs/DECISIONS.md)
- [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)

*(Lembrete fundamental de Segurança: o arquivo `.env` verdadeiro e credenciais confidenciais nunca devem ser commitados no GitHub)*.