# StockFlow API

API REST para gerenciamento de produtos, fornecedores, categorias e movimentações de estoque.

Projeto acadêmico desenvolvido como desafio técnico da trilha Back-End do Prosel 2026.2 da EcompJr.

---

## Tecnologias Utilizadas

Principais tecnologias utilizadas (dependências declaradas em [requirements.txt](requirements.txt)):

- **Linguagem:** Python 3.12
- **Framework Web:** FastAPI
- **Banco de Dados:** PostgreSQL
- **ORM:** SQLAlchemy 2.x
- **Driver de Banco:** Psycopg 3
- **Migrations:** Alembic
- **Validação e Configurações:** Pydantic e pydantic-settings
- **Servidor ASGI:** Uvicorn
- **Hashing:** pwdlib[argon2] (criação de hashes Argon2id e verificação de senhas)
- **Autenticação:** PyJWT (criação e validação de access tokens JWT)

---

## Pré-requisitos

Para rodar o projeto localmente, é necessário ter instalado:

- **Python 3.12**, versão base do projeto e do CI.
- **PostgreSQL 16**, versão utilizada pelo CI e referência para reproduzir o ambiente.
- **Git**

---

## Configuração do Banco de Dados PostgreSQL

Antes de iniciar a API, você deve possuir um banco de dados PostgreSQL funcional.
Os comandos `CREATE ROLE` e `CREATE DATABASE` devem ser executados durante o provisionamento por uma conta PostgreSQL que possua privilégios suficientes. A role `stockflow_app` é a usada normalmente pela aplicação e ela não precisa ser superuser. Conecte-se ao `psql` (ou ferramenta visual de sua preferência) e execute:

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
     python3.12 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     py -3.12 -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

3. Instale as dependências:
   ```bash
   python -m pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   - Copie o arquivo base: `cp .env.example .env` (Linux/macOS) ou `Copy-Item .env.example .env` (PowerShell).
   - Preencha os dados do `.env`. Ele não deve ser versionado.
   ```ini
   DB_HOST=127.0.0.1
   DB_PORT=5432
   DB_NAME=stockflow
   DB_USER=stockflow_app
   DB_PASSWORD=<senha-local>

   JWT_SECRET_KEY=<substitua-por-um-segredo-aleatorio-de-pelo-menos-32-caracteres>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
   *Nota sobre o JWT:* `JWT_SECRET_KEY` é obrigatório e exige pelo menos 32 caracteres. Substitua o marcador por um segredo aleatório, nunca versionado; para gerá-lo localmente, use `python -c "import secrets; print(secrets.token_hex(32))"`. `JWT_ALGORITHM` tem HS256 como padrão. `ACCESS_TOKEN_EXPIRE_MINUTES` define a duração do access token (60 minutos por padrão).

5. Aplique as migrações estruturais do banco de dados (Alembic):
   ```bash
   python -m alembic upgrade head
   ```

6. Crie o primeiro usuário administrativo (necessário para usar as rotas protegidas):
   ```bash
   python -m app.cli.create_user --username admin --role ADMIN
   ```
   A CLI solicita a senha e sua confirmação sem exibi-las, rejeita senha vazia e armazena um hash Argon2id. O username deve ser único. Para criar um funcionário, informe `--role FUNCIONARIO`. Não há cadastro público nem criação automática de usuários no startup.

7. Inicie o servidor:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   Com a configuração padrão, a API atende em `http://127.0.0.1:8000`. Acesse o Swagger UI em `http://127.0.0.1:8000/docs` e o documento OpenAPI em `http://127.0.0.1:8000/openapi.json`. O modo `--reload` é destinado ao desenvolvimento.

---

## Autenticação, Segurança JWT e RBAC

A aplicação autentica usuários por JWT e verifica permissões pelos papéis ADMIN e FUNCIONARIO armazenados no banco.

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

### JWT e identidade do usuário

- O JWT é **assinado**, não criptografado, e o header/payload usam representação Base64URL.
- HS256 usa HMAC-SHA256.
- O emissor inclui somente `sub` (username) e `exp` (expiração calculada em UTC). Senha, hash e papel não entram no payload.
- O decoder exige os dois claims, valida a assinatura e a expiração e rejeita `sub` que não seja uma string não vazia. Aceita apenas o algoritmo definido na configuração; tokens expirados ou sem assinatura são rejeitados.
- A cada requisição protegida, o usuário é consultado pelo username e suas permissões são verificadas pelo papel atual no banco. Uma alteração de ADMIN para FUNCIONARIO passa a valer nas requisições seguintes, inclusive com tokens já emitidos.
- Um usuário removido resulta em `401` enquanto seu username permanecer ausente. Se esse username for recriado administrativamente, um token anterior ainda válido poderá identificar a nova conta. Não há endpoint de exclusão de usuários, refresh token ou blacklist nesta versão.

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

A aplicação organiza acesso ao banco, schemas, rotas e segurança nos seguintes módulos:

- `alembic/` - Configurações e versões de migrações do banco.
- `docs/` - Documentação oficial e registros de decisões (`DECISIONS.md`, `DOMAIN_MODELING.md`, `PROJECT_PLAN.md`).
- `app/`
  - `database.py` - Criação da engine e das sessões; a dependência fecha a sessão, e os routers controlam commits e rollbacks.
  - `exceptions.py` - Handlers globais para padronizar respostas HTTP, erros de validação e falhas inesperadas.
  - `config.py` - Gerenciamento de variáveis via *pydantic-settings*.
  - `main.py` - Instância FastAPI, registro de routers e handlers e configuração mínima do logging de `app`.
  - `models/` - Declaração puramente persistente (SQLAlchemy).
  - `schemas/` - Validações e modelos de entrada/saída HTTP (Pydantic).
  - `routers/` - Endpoints, dependências e processamento de regras de negócios controladas.
  - `security/` - Configuração e regras unificadas de senhas, JWT e auth.
  - `cli/` - Comandos e scripts administrativos.

---

## Endpoints e Recursos

| Método   | Rota                                      | Função |
| :------- | :---------------------------------------- | :----- |
| **GET**  | `/`                                       | Retorna status básico. |
| **GET**  | `/health`                                 | Confirma resposta HTTP da aplicação, sem consultar o banco. |
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

As consultas, atualizações e o login retornam `200`; a criação de categorias, fornecedores, produtos e movimentações retorna `201`; exclusões bem-sucedidas retornam `204`, sem corpo. Os schemas de entrada e saída estão disponíveis no Swagger UI. As operações de movimentações também documentam os papéis autorizados, regras de estoque, filtros, respostas de erro e exemplos representativos no OpenAPI.

### Consultas Avançadas em Movimentações

O endpoint `GET /movimentacoes` aceita três parâmetros opcionais e combináveis:

- `data_inicio` e `data_fim`: limites inclusivos do período, em formato ISO 8601 com fuso explícito, como `2026-10-01T00:00:00Z`. Intervalo invertido retorna `400`; formato inválido ou ausência de fuso retorna `422`.
- `fornecedor_id`: filtra pela referência histórica do fornecedor associado ao produto quando a movimentação foi criada. Fornecedor inexistente retorna `404`.

Uma consulta válida sem resultados retorna `200` com uma lista vazia.

---

## Regras de Negócio Implementadas

1. **Campos com restrição de unicidade:** `Categoria.nome`, `Fornecedor.cnpj`, `Fornecedor.email` e `Produto.sku` possuem _constraints UNIQUE_ no banco de dados. Esses valores podem ser atualizados via PUT, desde que continuem únicos. A entidade imutável pela API é `MovimentacaoEstoque`.
2. **Ciclo de Vida do Estoque:** Todo Produto nasce com estoque `0`. A chave `quantidade_em_estoque` nunca pode ser manipulada nos fluxos `POST`/`PUT` de Produto. O saldo só é alterado por movimentações válidas.
3. **Movimentações Auditáveis:** Toda movimentação (tipo `ENTRADA` ou `SAIDA`) tem seu contrato congelado, não existindo rotas de `PUT`/`PATCH`/`DELETE` de movimentação. Além disso, uma transação deve ter obrigatoriamente `quantidade > 0`.
4. **Saldo e Integridade:** Operações de `SAIDA` não podem superar o saldo disponível. A API verifica essa regra na transação, e uma constraint `CHECK` impede saldo negativo no banco.
5. **Exclusão Restrita:** As chaves estrangeiras do domínio usam `ON DELETE RESTRICT`. Não é possível excluir categoria com produtos, produto com movimentações ou fornecedor com produtos ou movimentações associados.
6. **Fornecedor Histórico:** Em `MovimentacaoEstoque.fornecedor_id` guardamos a cópia histórica do fornecedor cadastral atual do Produto no momento em que a movimentação foi criada.
7. **Estoque Mínimo:** A consulta retorna os produtos em que `quantidade_em_estoque <= estoque_minimo`; não há envio de notificações nem interface visual de alertas.

---

## Transação e Concorrência

A criação de movimentações utiliza `SELECT ... FOR UPDATE` na linha do produto para coordenar atualizações concorrentes do saldo. Movimentações sobre o mesmo produto aguardam a liberação desse bloqueio e avaliam o saldo atualizado. Uma saída subsequente recebe `409` somente se não houver saldo suficiente; caso contrário, pode ser concluída.

O processo funciona da seguinte forma:

1. Disparo de instrução de bloqueio no PostgreSQL (`SELECT Produto FOR UPDATE`).
2. Validação matemática do Saldo (Caso `SAIDA`).
3. Atualização lógica do `quantidade_em_estoque` e instanciamento da cópia _histórica_ (`nova_movimentacao`).
4. `COMMIT` da movimentação e do saldo na mesma transação, ou `ROLLBACK` em caso de falha antes da confirmação.

O teste de concorrência cobre duas saídas simultâneas de 8 unidades sobre saldo 10: uma retorna `201`, outra `409`, e o saldo final é 2. Esse cenário não comprova ausência de deadlocks ou de limites de recursos sob qualquer carga, nem protege contra alterações diretas no banco fora do fluxo da API.

---

## Tratamento e Modelo de Erros

Os handlers padronizam as respostas de erro. Exemplo de conflito de SKU:

```json
{
  "status": 409,
  "error": "conflict",
  "message": "Já existe um produto com este SKU.",
  "details": null
}
```

- **400 Bad Request:** Intervalo de consulta com `data_inicio` posterior a `data_fim`.
- **401 Unauthorized:** Credenciais de login inválidas, token ausente, inválido ou expirado, ou usuário do token inexistente. Acompanha `WWW-Authenticate: Bearer` e a mensagem genérica `Credenciais inválidas.`.
- **403 Forbidden:** O cliente é plenamente autenticado, mas a restrição de _role_ impede o acesso. Não emite header `WWW-Authenticate`.
- **404 Not Found:** Falta de entidade (em buscas singulares ou via relacionamentos explícitos). Listagens que resultam vazias respondem `200 []`.
- **405 Method Not Allowed:** Método não oferecido pela rota, como `PUT`, `PATCH` ou `DELETE` em `/movimentacoes/{movimentacao_id}`.
- **409 Conflict:** Duplicidade em campos únicos, saldo insuficiente ou conflitos de integridade referencial tratados pelos routers.
- **422 Validation Error:** Falha de validação da entrada. `details` contém apenas `loc`, `msg` e `type`; os campos `input` e `ctx` são omitidos.
- **500 Internal Server Error:** Exceções inesperadas retornam `error="internal_error"`, mensagem `Erro interno do servidor.` e `details=null`, sem traceback no corpo. Isso inclui um hash armazenado não reconhecido pelo pwdlib no login; essa falha interna não é convertida em `401`.

### Logging da aplicação

Movimentações de `ENTRADA` e `SAIDA` confirmadas produzem um evento `INFO` com `event_type="stock_movement_completed"`, emitido somente depois de `commit` e `refresh` bem-sucedidos. Uma `SAIDA` rejeitada por estoque insuficiente produz um evento `WARNING` com `event_type="stock_exit_rejected_insufficient_stock"` antes da resposta HTTP `409`. Esses eventos incluem apenas os identificadores, o tipo e as quantidades pertinentes à operação, sem credenciais.

Exceções inesperadas continuam registradas pelo handler global de `app.exceptions` em nível `ERROR`, com mensagem e traceback. O contexto inclui `event_type`, `http_method`, `route` (padrão da rota) e `exception_type`.

Os metadados operacionais são passados pelo argumento `extra` do logging e tornam-se atributos do `LogRecord`; os dados essenciais também aparecem na mensagem textual. O formato padrão da aplicação permanece textual e não constitui serialização JSON.

Esses registros de logging são observacionais e não substituem o histórico de movimentações persistido no PostgreSQL, que permanece como o registro auditável do domínio.

Quando o logger `app` não encontra handlers próprios ou em ancestrais alcançáveis por propagação, `app/main.py` adiciona um `StreamHandler` com o formato:

```text
%(asctime)s | %(levelname)s | %(name)s | %(message)s
```

O formato apresenta timestamp, nível, nome do logger e mensagem. Se houver configuração externa de handlers, ela é aproveitada, e a saída efetiva pode ser diferente. O formatter não serializa automaticamente todos os atributos adicionais do registro.

O handler da aplicação não acrescenta automaticamente corpos de requisição, `Authorization`, senhas, tokens ou query strings ao contexto. Entretanto, o texto e o traceback de exceções podem conter informações internas; os logs não possuem sanitização universal. Os loggers de acesso e erro do Uvicorn têm configuração própria: não recebem automaticamente esse formatter e podem emitir registros ou tracebacks adicionais. O access log não foi alterado e pode incluir query strings.

---

## Testes automatizados

A suíte possui **105 testes**. A execução do GitHub Actions para o commit `c450970` foi aprovada com o resultado `105 passed, 12 warnings in 7.82s`. Há cenários de CRUD, unicidade, movimentações, consultas avançadas, concorrência, erros HTTP, autenticação, RBAC, JWT e verificação de senhas Argon2. Os quatro cenários mais recentes verificam o logging de `ENTRADA` concluída, `SAIDA` concluída, `SAIDA` rejeitada por estoque insuficiente e falha controlada no commit. Isso não representa uma medição de cobertura de 100% do código.

Os testes de login verificam o contrato completo de `401` para credenciais inválidas e o `500` genérico para hash não reconhecido, sem token ou detalhes internos na resposta. Os testes JWT incluem claims obrigatórios, `sub` vazio, expiração, assinatura incorreta e algoritmos não permitidos.

### Preparação do banco de testes

Use exclusivamente um banco descartável chamado `stockflow_test`. A fixture de segurança consulta `current_database()` e interrompe a suíte se o nome for diferente. As fixtures **apagam os dados das tabelas de domínio e de usuários antes e depois de cada teste**; nunca aponte esses testes para uma instância com dados reais, mesmo que tenha o mesmo nome.

Com uma conta PostgreSQL com privilégios de criação, provisione o banco separado:

```sql
CREATE DATABASE stockflow_test OWNER stockflow_app;
```

Na raiz do repositório, com o ambiente virtual ativado, aplique as migrations nesse banco e execute a suíte. Os demais parâmetros `DB_HOST`, `DB_PORT`, `DB_USER` e `DB_PASSWORD` devem apontar para o ambiente de testes; se forem os mesmos do desenvolvimento local, podem vir do `.env` já configurado. A chave JWT abaixo é fictícia e exclusiva de testes.

**Linux/macOS (Bash):**

```bash
(
  export DB_NAME=stockflow_test
  export JWT_SECRET_KEY=stockflow_test_secret_only_for_automated_tests_123456
  python -m alembic upgrade head
  python -m pytest -q -ra
)
```

**Windows (PowerShell, em um terminal separado com o ambiente virtual ativado):**

```powershell
$env:DB_NAME = "stockflow_test"
$env:JWT_SECRET_KEY = "stockflow_test_secret_only_for_automated_tests_123456"
python -m alembic upgrade head
python -m pytest -q -ra
```

Para executar somente autenticação, substitua o comando pytest do bloco por `python -m pytest tests/test_auth.py -q -ra`. Para conferir a quantidade sem executar os testes nem as fixtures de banco, use `python -m pytest --collect-only -q`, mantendo a configuração de testes.

O subshell Bash limita as variáveis ao bloco. No PowerShell, feche o terminal de testes ao terminar para não iniciar a API com essa configuração.

---

## Integração Contínua (CI) com GitHub Actions

O workflow [.github/workflows/tests.yml](.github/workflows/tests.yml) é acionado por `push` e `pull_request` direcionados à `main`. Ele configura Python 3.12 e um serviço PostgreSQL 16 descartável, instala as dependências, aplica `alembic upgrade head`, consulta `alembic current` e executa `pytest -q`. Falhas nessas etapas fazem o job falhar. Impedir merges com verificações reprovadas depende das regras configuradas no repositório remoto.

---

## Referência do Desafio Técnico

Este projeto acadêmico independente está vinculado ao desafio da trilha Back-End do Prosel 2026.2 da Ecomp Jr. O [enunciado de referência](docs/referencias/prosel-2026.2/desafio-tecnico-backend-prosel-2026.2.md) foi obtido de um colega; sua versão não foi confirmada e pode não ser a mais recente. A cópia registra o prazo original de **16/10/2026**; o prazo posteriormente comunicado ao desenvolvedor foi **24/10/2026**.

---

## Documentação Técnica Complementar

- [docs/DOMAIN_MODELING.md](docs/DOMAIN_MODELING.md)
- [docs/DECISIONS.md](docs/DECISIONS.md)
- [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)

Não versione o arquivo `.env` nem credenciais reais.
