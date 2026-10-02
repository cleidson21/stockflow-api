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

3. Instale as dependências oficiais:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   - Copie o arquivo base: `cp .env.example .env`
   - O arquivo `.env.example` serve apenas como gabarito (não contém dados sensíveis reais). O arquivo `.env` gerado é inserido automaticamente no `.gitignore` para não ser versionado e deve ser preenchido com suas configurações:
   ```ini
   DB_HOST=127.0.0.1
   DB_PORT=5432
   DB_NAME=stockflow
   DB_USER=stockflow_app
   DB_PASSWORD=<senha-local>
   ```

---

## Migrations (Estrutura do Banco)

O esquema do banco de dados é controlado via **Alembic**, garantindo previsibilidade sobre o modelo final de dados. *(O modelo automático `Base.metadata.create_all()` não é utilizado).*

Para aplicar a estrutura no banco de dados previamente configurado:

```bash
alembic upgrade head
```

Para verificar se a base está atualizada:
```bash
alembic current
```

---

## Execução

Inicie o servidor de desenvolvimento com reload ativado (recarrega as mudanças no código automaticamente):

```bash
python -m uvicorn app.main:app --reload
```

Os endpoints básicos ficarão disponíveis nestas URLs:

- **API:** http://127.0.0.1:8000
- **Swagger UI (Testes Interativos):** http://127.0.0.1:8000/docs
- **OpenAPI JSON (Contrato Automático):** http://127.0.0.1:8000/openapi.json

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

---

## Endpoints e Recursos

| Método   | Rota                                      | Função |
| :------- | :---------------------------------------- | :----- |
| **GET**  | `/`                                       | Retorna status básico. |
| **GET**  | `/health`                                 | Confirma integridade operacional do servidor. |
| **GET**  | `/categorias`                             | Lista categorias. |
| **POST** | `/categorias`                             | Cria uma categoria. |
| **GET**  | `/categorias/{categoria_id}`              | Busca categoria específica. |
| **PUT**  | `/categorias/{categoria_id}`              | Edita categoria. |
| **DELETE**| `/categorias/{categoria_id}`             | Exclui categoria (Restrito). |
| **GET**  | `/fornecedores`                           | Lista fornecedores. |
| **POST** | `/fornecedores`                           | Cria um fornecedor. |
| **GET**  | `/fornecedores/{fornecedor_id}`           | Busca fornecedor específico. |
| **PUT**  | `/fornecedores/{fornecedor_id}`           | Edita fornecedor. |
| **DELETE**| `/fornecedores/{fornecedor_id}`          | Exclui fornecedor (Restrito). |
| **GET**  | `/produtos`                               | Lista produtos. |
| **POST** | `/produtos`                               | Cria um produto. |
| **GET**  | `/produtos/{produto_id}`                  | Busca produto específico. |
| **PUT**  | `/produtos/{produto_id}`                  | Edita produto. |
| **DELETE**| `/produtos/{produto_id}`                 | Exclui produto (Restrito). |
| **GET**  | `/produtos/consultas/estoque-minimo`      | Lista todos os produtos cujo estoque <= estoque mínimo. |
| **GET**  | `/movimentacoes`                          | Lista movimentações históricas de entrada e saída. |
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

Para assegurar blindagem contra concorrência e o antipadrão _lost update_, a submissão de movimentações foi desenhada em uma arquitetura transacional rígida:

1. Abertura do bloco contextual (`with db.begin()`).
2. Disparo de instrução de bloqueio no PostgreSQL (`SELECT Produto FOR UPDATE`).
3. Validação matemática do Saldo (Caso `SAIDA`).
4. Atualização lógica do `quantidade_em_estoque` e acoplamento em banco da cópia _histórica_ (`nova_movimentacao`).
5. Fechamento seguro (`COMMIT` único, ou Rollback caso levante `HTTPException`).

Isso defende inteiramente a base de dados em cenários de requisições simultâneas ou overselling que descolariam o relatório da realidade factual do estoque.

---

## Fluxo de Uso Recomendado

O ecossistema demanda uma hierarquia forte na inserção. Para um teste linear, siga:

1. `POST /categorias` (ex. "Eletrônicos")
2. `POST /fornecedores` (ex. CNPJ Válido)
3. `POST /produtos` (ex. Mouse - vinculado às chaves de Categoria e Fornecedor. Nasce com saldo `0`).
4. `POST /movimentacoes` (ENTRADA de 50 mouses).
5. `GET /produtos` (Atestar saldo atualizado para 50).
6. `POST /movimentacoes` (SAIDA de 10 mouses).
7. Repita requisições excedentes na saída e observe as rejeições de Conflito. Nunca force update no saldo via PUT Produto.

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

- **400 Bad Request:** Requisições lógicas incompatíveis, sem tocar o banco (ex: Data Início no futuro com relação a Data Fim).
- **404 Not Found:** Falta de entidade. No endpoint de buscas, uma busca _perfeitamente bem formulada_, cujo fornecedor não possua movimentações, retornará `200` acompanhado de array vazio `[]` e não um `404`. Um filtro com `fornecedor_id` não correspondente a nada vivo devolverá _404 explícito_.
- **409 Conflict:** Violação de estados imutáveis, Unique Violation do DB, Falta de Saldo ou Deletes Protegidos por referências vitais.
- **422 Validation Error:** Falha de validação do contrato de entrada, como tipo, formato, limites ou campos extras não permitidos. Não vaza input malicioso injetado nos "details".
- **500 Internal Server Error:** O contrato é estruturado contendo `{"status": 500, "error": "internal_error", "message": "Erro interno do servidor.", "details": null}`. Os detalhes técnicos ficam apenas no log do servidor.

---

## Estado dos testes

Houve validação funcional durante o desenvolvimento para atestar as regras e as modelagens.
A suíte automatizada permanente ainda será criada na Fase 7.

---

## Documentação Técnica Complementar

- [docs/DOMAIN_MODELING.md](docs/DOMAIN_MODELING.md)
- [docs/DECISIONS.md](docs/DECISIONS.md)
- [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)

*(Lembrete fundamental de Segurança: o arquivo `.env` verdadeiro e credenciais confidenciais nunca devem ser commitados no GitHub)*.