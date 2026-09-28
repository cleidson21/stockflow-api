# StockFlow API — Decision Log

## 1. Objetivo

Este documento registra decisões técnicas e arquiteturais relevantes do StockFlow API.

O objetivo não é documentar cada linha de código, mas preservar o contexto das escolhas que poderão precisar ser explicadas durante a defesa técnica.

Cada decisão importante deve registrar:

- contexto;
- opções consideradas;
- decisão;
- justificativa;
- consequências.

---

## 2. Estados

Uma decisão pode estar em um dos seguintes estados:

- PROPOSED — ainda em discussão;
- ACCEPTED — decisão aprovada;
- SUPERSEDED — substituída por decisão posterior.

---

## DEC-001 — Nome do projeto

Status: ACCEPTED

### Contexto

O desafio descreve uma API de gerenciamento de estoque envolvendo produtos, fornecedores, categorias e movimentações.

### Decisão

O projeto será chamado StockFlow API e o repositório será stockflow-api.

### Justificativa

O nome representa de forma curta o domínio de estoque e movimentações sem limitar o projeto a uma única entidade.

### Consequências

Documentação e referências ao projeto devem utilizar StockFlow API.

---

## DEC-002 — Fluxo de desenvolvimento assistido por IA

Status: ACCEPTED

### Contexto

Ferramentas de IA serão utilizadas durante o desenvolvimento, mas o projeto exige defesa técnica e compreensão das decisões implementadas.

### Decisão

O fluxo adotado será:

ChatGPT no navegador:
planejamento, explicações, análise de requisitos e decisões arquiteturais.

Antigravity + Codex:
inspeção do repositório, edição de arquivos, execução de tarefas delimitadas e suporte à implementação.

Git/GitHub:
controle de versão, rastreabilidade e histórico real do desenvolvimento.

### Justificativa

A separação reduz o risco de desenvolvimento automático sem compreensão e mantém decisões importantes explícitas.

### Consequências

O Codex não deve tomar silenciosamente decisões importantes de arquitetura ou regra de negócio.

---

## DEC-003 — Controle manual do Git

Status: ACCEPTED

### Contexto

O histórico de commits faz parte da avaliação do desafio.

### Decisão

Agentes de IA não executarão commit, push, rebase, reset ou alterações de histórico sem autorização explícita.

Antes de commits relevantes, o desenvolvedor deve revisar status e diff.

### Justificativa

O desenvolvedor deve manter controle sobre exatamente quais alterações entram no histórico.

### Consequências

O processo pode ser um pouco mais lento, mas aumenta rastreabilidade e compreensão.

---

## DEC-004 — Tecnologias base

Status: ACCEPTED

### Contexto

O desafio exige FastAPI e PostgreSQL e recomenda SQLAlchemy e Alembic.

### Decisão

Serão utilizados:

- Python;
- FastAPI;
- PostgreSQL;
- SQLAlchemy;
- Alembic.

### Justificativa

FastAPI e PostgreSQL são requisitos obrigatórios.

SQLAlchemy fornece uma camada estruturada para acesso ao banco e Alembic permite versionar a evolução do schema.

### Consequências

Os conceitos de ORM, sessão, transação e migrations deverão ser compreendidos durante o desenvolvimento.

---

## DEC-005 — Gerenciamento de dependências

Status: ACCEPTED

### Contexto

Precisamos definir como as dependências Python serão declaradas e reproduzidas em outras máquinas.

### Opções consideradas

1. requirements.txt
2. pyproject.toml

### Decisão

Utilizar requirements.txt como mecanismo principal de declaração das dependências Python do StockFlow API.

### Justificativa

- simplicidade;
- adequação ao tamanho e objetivo da aplicação;
- facilidade de compreensão;
- reprodução do ambiente através de pip;
- ausência de necessidade atual de empacotamento Python;
- evitar configuração adicional sem benefício concreto para os requisitos do desafio.

### Consequências

- as dependências diretas do projeto serão registradas em requirements.txt;
- a instalação poderá ser reproduzida com `pip install -r requirements.txt`;
- deverá existir cuidado para manter o arquivo sincronizado com as dependências realmente utilizadas;
- dependências diretas e transitivas devem ser distinguidas conceitualmente;
- pyproject.toml poderá ser reconsiderado no futuro somente se surgir uma necessidade concreta.

---

## DEC-006 — Versão base do Python

Status: ACCEPTED

### Contexto

O ambiente inicial Linux disponibilizava Python 3.12.3.
Uma segunda máquina Windows disponibilizava inicialmente Python 3.14, e Python 3.12.10 foi posteriormente instalado para manter a mesma série minor entre os ambientes.

### Opções consideradas

1. utilizar a versão Python disponível em cada máquina;
2. padronizar o projeto na série Python 3.12.

### Decisão

O StockFlow API adotará Python 3.12 como versão base.

Patches diferentes dentro da série 3.12 podem ser utilizados entre ambientes quando compatíveis com as dependências do projeto.

### Justificativa

- a série 3.12 já foi validada no ambiente inicial;
- reduz divergência entre máquinas;
- evita trocar de runtime sem necessidade;
- mantém o requisito suficientemente específico sem exigir um patch exato.

### Consequências

- novos ambientes devem preferencialmente possuir Python 3.12;
- o `.venv` deve ser recriado em cada máquina;
- ambientes virtuais não são compartilhados ou versionados;
- alterações futuras da versão minor do Python devem ser decisões explícitas.

---

## DEC-007 — Estrutura inicial da aplicação

Status: ACCEPTED

### Contexto

Era necessário definir uma estrutura mínima para iniciar FastAPI sem introduzir camadas arquiteturais prematuras.

### Opções consideradas

1. manter main.py diretamente na raiz;
2. utilizar um pacote `app` com `app/main.py`;
3. criar desde o início uma estrutura completa com routers, services, repositories, models e schemas.

### Decisão

A aplicação inicia com:

```
app/
├── __init__.py
└── main.py
```

`app/main.py` contém inicialmente:

- a instância FastAPI;
- GET /;
- GET /health.

Novas estruturas serão introduzidas somente quando as responsabilidades reais surgirem.

### Justificativa

- separa código da aplicação dos arquivos de configuração da raiz;
- cria um namespace Python claro;
- permite iniciar via `app.main:app`;
- evita arquitetura excessiva antes da existência do domínio e do banco;
- mantém a aplicação fácil de compreender na defesa técnica.

### Consequências

- `app` é o pacote principal da aplicação;
- `app.main` é atualmente o módulo de entrada;
- routers, models, schemas, services e demais módulos só serão adicionados mediante necessidade concreta;
- a estrutura poderá evoluir conforme a modelagem da Fase 2.

---

# Decisões pendentes

As decisões abaixo não devem ser tomadas silenciosamente durante implementação.

---

## PEND-001 — Gerenciamento de dependências

Status: SUPERSEDED por DEC-005

Questão original:

Utilizar requirements.txt ou pyproject.toml?

A decisão seria tomada na Fase 1 antes de registrar as primeiras dependências.

Resolução: ver DEC-005.

---

## PEND-002 — Estrutura inicial da aplicação

Status: SUPERSEDED por DEC-007

Questão original:

Qual estrutura de módulos oferece clareza suficiente para o tamanho deste desafio sem introduzir arquitetura excessiva?

A decisão seria tomada antes da criação do primeiro código FastAPI.

Resolução: ver DEC-007.

---

## DEC-008 — Cardinalidade Categoria–Produto

Status: ACCEPTED

### Contexto

Produto é a entidade central do sistema e precisa ser classificado. O desafio exige que categorias existam e que o comportamento de exclusão de categoria com produtos seja definido. Era necessário decidir se um produto pertence a uma ou a múltiplas categorias.

### Opções consideradas

1. **1:N** — uma Categoria pode classificar muitos Produtos; cada Produto pertence a exatamente uma Categoria. FK de Categoria fica no lado Produto.
2. **N:N** — um Produto pode pertencer a múltiplas Categorias; uma Categoria pode classificar múltiplos Produtos. Exige tabela de associação.

### Decisão

Relacionamento **1:N**.

Uma Categoria pode classificar zero ou muitos Produtos. Cada Produto pertence obrigatoriamente a exatamente uma Categoria.

### Justificativa

- O desafio não exige múltiplas categorias por produto.
- A relação 1:N atende integralmente ao escopo solicitado.
- Evita tabela associativa e a complexidade de gerenciamento de associações (adicionar, remover, validar duplicidade).
- Simplifica as operações de CRUD, validação e a política de exclusão de categoria.
- Mantém o domínio mais fácil de compreender e defender tecnicamente.

### Consequências

- Produto terá uma Categoria obrigatória (FK não nula para Categoria).
- Uma Categoria pode possuir zero ou muitos Produtos.
- No modelo relacional, a FK `category_id` estará na tabela de Produto.
- A política de exclusão de Categoria com Produtos associados continua dependendo de DOM-013 (ainda OPEN).
- Se no futuro o projeto evoluir para múltiplas categorias por produto, uma refatoração de schema seria necessária.

---

## DEC-009 — Cardinalidade Fornecedor–Produto

Status: ACCEPTED

### Contexto

A loja possui múltiplos fornecedores e precisa saber quem fornece cada produto. Era necessário decidir se um produto pode ter um ou vários fornecedores cadastrais.

### Opções consideradas

1. **1:N** — um Fornecedor pode fornecer muitos Produtos; cada Produto possui exatamente um Fornecedor cadastral. FK de Fornecedor fica no lado Produto.
2. **N:N** — um Produto pode ter múltiplos Fornecedores; um Fornecedor pode fornecer múltiplos Produtos. Exige tabela de associação `product_supplier`.

### Decisão

Relacionamento **1:N**.

Um Fornecedor pode fornecer zero ou muitos Produtos. Cada Produto possui obrigatoriamente exatamente um Fornecedor cadastral.

O projeto deliberadamente não implementará Produto ↔ Fornecedor N:N neste escopo.

### Justificativa

- O enunciado do desafio não exige múltiplos fornecedores por produto.
- A presença de múltiplos fornecedores na loja não implica que um mesmo produto seja fornecido por vários deles simultaneamente.
- A relação 1:N satisfaz o domínio solicitado de forma mais simples.
- Evita tabela associativa e a ambiguidade de "qual fornecedor está associado a qual movimentação" sem contexto adicional.
- Mantém CRUD e consultas mais simples.
- A complexidade de N:N (gestão de associações, ambiguidade no filtro histórico) não traz benefício dentro do escopo atual.

### Consequências

- Cada Produto possui um fornecedor cadastral único (`supplier_id` obrigatório em Produto).
- Um Fornecedor pode possuir muitos Produtos.
- Alteração do fornecedor de um produto no futuro é possível conceitualmente (atualização do `supplier_id` do produto).
- Como a alteração do fornecedor cadastral afeta a rastreabilidade histórica, isso leva diretamente à decisão DEC-010.
- Se o projeto evoluir para múltiplos fornecedores por produto no futuro, uma refatoração de schema seria necessária.

---

## DEC-010 — Referência histórica de Fornecedor na Movimentação

Status: ACCEPTED

### Contexto

O desafio exige que movimentações sejam filtráveis por fornecedor. Com a decisão DEC-009 (Produto 1:N Fornecedor), é possível obter o fornecedor de uma movimentação por JOIN: `Movimentação → Produto → Fornecedor`. Porém, se o fornecedor cadastral de um Produto for atualizado no futuro, esse JOIN associaria movimentações antigas ao novo fornecedor, distorcendo o histórico. Era necessário decidir como garantir rastreabilidade histórica correta.

### Opções consideradas

1. **JOIN indireto via Produto** — não armazenar fornecedor na movimentação; obtê-lo sempre via `Movimentação → Produto → Fornecedor`. Simples, mas historicamente impreciso se o fornecedor do produto mudar.
2. **Referência direta histórica na Movimentação** — armazenar `supplier_id` diretamente na movimentação, capturado do Produto no momento da criação da movimentação.

### Decisão

A Movimentação armazenará uma **referência direta e histórica** ao Fornecedor.

A relação conceitual é: **Fornecedor 1:N Movimentação**.

Cada Movimentação registra o fornecedor que estava associado ao Produto no momento em que a movimentação foi criada.

**Regra operacional:** o cliente da API não escolhe livremente o `supplier_id` da movimentação. Ao criar uma movimentação, o sistema:

1. identifica o Produto informado;
2. lê o `supplier_id` cadastral atual daquele Produto;
3. registra esse valor na Movimentação;
4. cria a Movimentação e atualiza o estoque dentro da mesma fronteira transacional.

### Justificativa

A referência direta preserva o fornecedor associado ao Produto no momento do evento, garantindo significado histórico permanente ao filtro obrigatório por fornecedor. Se o fornecedor cadastral do Produto for alterado no futuro, movimentações anteriores continuarão referenciando o fornecedor histórico correto. O JOIN indireto quebraria esse invariante silenciosamente.

### Consequências

- Movimentação possuirá futuramente uma FK para Fornecedor (`supplier_id`).
- `supplier_id` em Movimentação é determinado pela aplicação a partir do Produto no momento da criação; o cliente não o informa diretamente.
- `Product.supplier_id` = fornecedor cadastral atual do Produto.
- `StockMovement.supplier_id` = fornecedor associado ao Produto no momento daquela movimentação específica.
- A duplicação entre os dois campos é deliberada: eles possuem semânticas temporais diferentes.
- `supplier_id` numa movimentação de saída não significa que o fornecedor "causou" a saída; representa apenas o fornecedor cadastral histórico do Produto naquele momento.
- Não será implementado snapshot dos dados do fornecedor (nome, CNPJ etc.); apenas a FK é preservada.
- A política de exclusão de Fornecedor com movimentações associadas continua dependendo de DOM-008 (ainda OPEN).
- A captura do fornecedor e a criação da movimentação deverão participar da mesma fronteira transacional da atualização de estoque (a ser implementada na Fase 4).

---

## PEND-003 — Relação Produto–Fornecedor

Status: SUPERSEDED por DEC-009

Questão original:

Um produto terá apenas um fornecedor ou poderá possuir múltiplos fornecedores?

O enunciado deve ser analisado antes da modelagem para evitar uma relação arbitrária.

Resolução: ver DEC-009.

---

## PEND-004 — Estoque mínimo

Status: PROPOSED

Questão:

O requisito de consulta de produtos no estoque mínimo exige uma referência persistida de estoque mínimo por produto.

Devem ser definidos:

- nome do campo;
- tipo;
- valor padrão;
- regras de validação.

---

## PEND-005 — SQLAlchemy síncrono ou assíncrono

Status: PROPOSED

Questão:

A aplicação utilizará SQLAlchemy síncrono ou assíncrono?

A escolha deve considerar simplicidade, objetivo educacional e necessidades reais do desafio.

---

## PEND-006 — Regras de exclusão

Status: PROPOSED

Questão:

Além da restrição explícita envolvendo categorias com produtos associados, quais comportamentos serão adotados na exclusão de fornecedores e produtos relacionados a registros históricos?

A decisão deverá preservar integridade referencial e auditoria.

---

## PEND-007 — Formato padronizado de erros

Status: PROPOSED

Questão:

Qual será o envelope padrão das respostas de erro?

A decisão deve ser tomada antes da consolidação dos exception handlers.

---

## PEND-008 — Estratégia de concorrência

Status: PROPOSED

Questão:

Caso o diferencial de concorrência seja implementado, qual estratégia será utilizada para impedir saídas simultâneas inconsistentes?

Possibilidades a estudar:

- locking pessimista;
- locking otimista;
- atualização atômica condicionada.

A decisão somente será aceita após entendimento do problema de race condition.

---

## Regra para novas decisões

Quando uma decisão pendente for resolvida:

1. não apagar o contexto histórico;
2. criar ou atualizar uma entrada DEC;
3. registrar as alternativas consideradas;
4. registrar a escolha adotada;
5. explicar a justificativa;
6. registrar consequências relevantes.
