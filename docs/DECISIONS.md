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

## DEC-021 — Estratégia de identificadores no Modelo Físico

Status: ACCEPTED

### Contexto

Era necessário definir a representação física no PostgreSQL para as chaves primárias (PKs) de todas as tabelas (Categoria, Fornecedor, Produto, Movimentacao_Estoque) e suas respectivas chaves estrangeiras (FKs).

### Opções consideradas

1. `BIGINT` ou `BIGSERIAL` (maior capacidade).
2. `UUID` (geração globalmente única).
3. `INTEGER` com o legado `SERIAL`.
4. `INTEGER` com o mecanismo moderno `GENERATED BY DEFAULT AS IDENTITY`.

### Decisão

Todas as PKs e FKs utilizarão `INTEGER`. A geração automática das PKs pelo PostgreSQL utilizará `GENERATED BY DEFAULT AS IDENTITY`.

### Justificativa

O volume esperado do projeto (uma API de controle de estoque de propósito educacional/desafio técnico) não exige a escala de `BIGINT`. O `INTEGER` produz chaves e índices mais compactos, favorecendo a performance de JOINs. O `UUID` não resolve nenhuma necessidade de concorrência descentralizada presente no escopo atual. Além disso, a sintaxe `IDENTITY` é o padrão moderno no PostgreSQL (desde a versão 10), substituindo o `SERIAL` (que tem problemas em certas migrações e de acoplamento de sequências).

### Consequências

- Todas as PKs e FKs terão consistência absoluta usando `INTEGER`.
- O mecanismo moderno de `IDENTITY` será usado no modelo físico, o que exige compatibilidade no Alembic/SQLAlchemy (TSK-2.8).

---

## DEC-022 — Tipos físicos de textos e identificadores textuais

Status: ACCEPTED

### Contexto

Decidir o tipo físico e restrições de tamanho no SGBD para campos de texto (nome, email) e identificadores que possuem formatação ou regras específicas (CNPJ, telefone, SKU).

### Opções consideradas

1. Utilizar tipos estritamente numéricos para CNPJ/telefone (`BIGINT`).
2. Utilizar `TEXT` sem limite para todos.
3. Utilizar `VARCHAR(n)` fixando um limite máximo.

### Decisão

Utilizaremos `VARCHAR` para todos os campos textuais:
- CATEGORIA.nome → `VARCHAR(100)`
- FORNECEDOR.nome → `VARCHAR(150)`
- FORNECEDOR.cnpj → `VARCHAR(14)` (sem pontuação)
- FORNECEDOR.telefone → `VARCHAR(20)`
- FORNECEDOR.email → `VARCHAR(254)`
- PRODUTO.nome → `VARCHAR(150)`
- PRODUTO.sku → `VARCHAR(50)`

### Justificativa

Identificadores como CNPJ, SKU e Telefone não devem ser numéricos (`BIGINT`) porque eles não participam de operações matemáticas, podem iniciar com zero e precisam preservar sua integridade original de caracteres. A restrição explícita com `VARCHAR(n)` previne o armazenamento não intencional de lixo na base (segurança de integridade), embora a performance no PostgreSQL entre VARCHAR e TEXT seja similar.

### Consequências

- O `CNPJ` será armazenado normalizado e sem máscaras. A restrição de dígitos `CHECK` exata pertencerá a uma etapa futura de constraints lógicas. *Resolvido posteriormente na consolidação do modelo físico (DEC-026/DEC-027).*
- O limite máximo deverá ser validado pela API (via Pydantic futuramente) antes da persistência para garantir status 422 adequado em vez de erro SQL genérico.

---

## DEC-023 — Tipos físicos monetários e quantitativos

Status: ACCEPTED

### Contexto

Definir os tipos SQL para armazenar valores monetários (preços de venda/custo) e quantitativos (saldos, estoques, quantidades).

### Opções consideradas

1. `FLOAT` ou `DOUBLE PRECISION` para valores monetários.
2. `INTEGER` em centavos para dinheiro (padrão de alguns gateways).
3. `NUMERIC(p, s)` para exatidão monetária.
4. `NUMERIC` para quantidades (permitindo fração).
5. `INTEGER` para quantidades.

### Decisão

- Preços (Produto.`preco_custo`, Produto.`preco_venda`) utilizarão `NUMERIC(12,2)`.
- Quantidades (Produto.`quantidade_em_estoque`, Produto.`estoque_minimo`, Movimentacao.`quantidade`) utilizarão `INTEGER`.

### Justificativa

Tipos de ponto flutuante (`FLOAT`) introduzem imprecisões de arredondamento em binário (inaceitáveis para dinheiro). `NUMERIC(12,2)` assegura representação decimal exata com 2 casas decimais. As quantidades utilizarão `INTEGER` pois o domínio foi aprovado conceitualmente como unidades exatas inteiras, não havendo requisito para fracionamento de medida (como kg ou litro).

### Consequências

- A precisão monetária é exata, porém o tipo `NUMERIC` é computacionalmente mais lento do que operações com inteiros, embora isto não afete a escala da aplicação.
- A API rejeitará movimentações fracionadas automaticamente. Regras de `>0` ou `>=0` receberão as restrições `CHECK` posteriormente.

---

## DEC-024 — Tipos físicos temporais

Status: ACCEPTED

### Contexto

Definir o tipo físico para campos de registro temporal de criação (`data_cadastro`, `data`).

### Opções consideradas

1. `TIMESTAMP` (sem timezone).
2. `TIMESTAMPTZ` (`TIMESTAMP WITH TIME ZONE`).
3. `VARCHAR` ou formato numérico `UNIX EPOCH`.

### Decisão

Todos os campos temporais (Produto.`data_cadastro`, Movimentacao.`data`) utilizarão `TIMESTAMPTZ`.

### Justificativa

Datas e horas em uma aplicação devem sempre referenciar instantes reais absolutos. O uso de `TIMESTAMPTZ` no PostgreSQL permite que o SGBD lide corretamente com conversões de timezone, rejeitando ambiguidade se os servidores ou conexões divergirem de configuração de timezone local no futuro.

### Consequências

- Será necessário definir posteriormente uma política operacional de UTC ou Fuso local claro na camada da API (FastAPI) na passagem do valor, bem como os valores default físicos. *Resolvido posteriormente por DEC-030.*

---

## DEC-025 — Representação física do tipo de movimentação

Status: ACCEPTED

### Contexto

Como armazenar fisicamente os tipos da movimentação ("ENTRADA", "SAÍDA") de forma eficiente e aderente ao modelo (DEC-016).

### Opções consideradas

1. Booleano (`is_entrada = True/False`).
2. Enumeração nativa do banco (`CREATE TYPE ... AS ENUM`).
3. Texto com restrição (`VARCHAR` com `CHECK`).

### Decisão

O tipo de movimentação será representado como `VARCHAR(7)` associado a uma constraint `CHECK (tipo IN ('ENTRADA', 'SAIDA'))`. *Constraint já aprovada em DEC-025. Resolvido posteriormente por DEC-025.*

### Justificativa

Um booleano perde muita expressividade no banco, reduzindo legibilidade da auditoria. A Enumeração do SGBD cria acoplamento extra no banco, e gerenciar migrações de adição de valores num `ENUM` nativo no PostgreSQL é uma operação menos flexível e mais dolorosa do que alterar um `CHECK` ou ter um simples varchar num domínio estático. Com `VARCHAR(7)`, cobrimos exatamente as duas opções limitando o armazenamento ao essencial, enquanto o controle fica simplificado.

### Consequências

- Não utilizaremos PostgreSQL ENUM. O suporte do SQLAlchemy/Alembic usará mapeamento para VARCHAR. O sistema na API (Python) é livre para usar Enums lógicos para padronização no código.

---

## DEC-026 — Constraints de obrigatoriedade e unicidade

Status: ACCEPTED

### Contexto

Definir fisicamente quais campos não aceitam valores nulos (`NOT NULL`) e quais exigem unicidade (`UNIQUE`), complementando a semântica do MER e do Modelo Relacional.

### Opções consideradas

1. Aplicar `NOT NULL` apenas nas PKs.
2. Aplicar `UNIQUE` em múltiplos campos não determinantes (como telefone, nome de Produto).
3. Aplicar rigor apenas aos campos definidos conceitualmente como obrigatórios e chaves naturais exclusivas.

### Decisão

- `NOT NULL` será aplicado a todos os campos essenciais do domínio: Categoria (nome); Fornecedor (nome, cnpj, telefone, email); Produto (nome, sku, preco_custo, preco_venda, quantidade_em_estoque, estoque_minimo, data_cadastro, categoria_id, fornecedor_id); Movimentação (tipo, quantidade, data, produto_id, fornecedor_id). As PKs já o possuem nativamente.
- `UNIQUE` será aplicado a chaves naturais e regras de negócios específicas: Categoria (nome), Fornecedor (cnpj, email), Produto (sku).

### Justificativa

Não se aplica `UNIQUE` em campos como nome de fornecedor ou telefone para evitar falsas restrições (empresas podem ter telefones em comum ou mesma razão social para filiais distintas caso não usemos CNPJ completo). A obrigatoriedade `NOT NULL` protege a base contra dados incompletos. `CITEXT` e índices funcionais case-insensitive não serão discutidos nesta etapa.

### Consequências

- Inserções sem dados obrigatórios serão bloqueadas pelo banco.
- O PostgreSQL criará automaticamente índices exclusivos por baixo dos panos para as constraints `UNIQUE`.

---

## DEC-027 — Defaults e checks de domínio

Status: ACCEPTED

### Contexto

Definir os valores padrão gerados pelo banco de dados (`DEFAULT`) e as validações de dados diretas no nível físico (`CHECK`), traduzindo as regras de negócio em segurança estrutural.

### Opções consideradas

1. Deixar toda a validação apenas na camada de aplicação.
2. Adicionar `CHECK` de saldo (Saída <= Saldo disponível) e regras dinâmicas no banco via Triggers.
3. Usar `DEFAULT` e `CHECK` simples, mantendo regras dependentes de estado (saldo) para transações na aplicação.

### Decisão

- **Defaults**: `quantidade_em_estoque` terá `DEFAULT 0`. `data_cadastro` e `data` terão `DEFAULT CURRENT_TIMESTAMP`. Outros campos não recebem default.
- **Checks de Produto**: `preco_custo >= 0`, `preco_venda >= 0`, `quantidade_em_estoque >= 0`, `estoque_minimo >= 0`. (A regra `preco_venda >= preco_custo` não é requisito e fica de fora).
- **Checks de Movimentação**: `quantidade > 0`, `tipo IN ('ENTRADA', 'SAIDA')`.
- **Check de CNPJ (Formato)**: Garantir comprimento exato de 14 dígitos numéricos via `char_length(cnpj) = 14 AND cnpj ~ '^[0-9]+$'`.

### Justificativa

Checks simples impedem que a aplicação grave, por erro sistêmico, valores absurdos (ex: quantidade negativa, tipos de movimentação não previstos). O `DEFAULT 0` para estoque reforça a semântica de que o produto nasce zerado (embora a API deva garantir que o cliente não informe outro valor inicial). A regra vital de "Saída não pode superar o saldo" não foi transformada em CHECK físico porque ela depende do estado atual do Produto, exigindo bloqueio e validação transacional da aplicação. O CNPJ terá apenas validação de formato; algoritmo de dígito verificador não é responsabilidade do banco (evitando extensões ou PL/pgSQL).

### Consequências

- Tentativas de inserir `tipo` diferente de 'ENTRADA' ou 'SAIDA' darão erro de constraint.
- A imutabilidade da Movimentação (sem UPDATE/DELETE) continuará garantida pela aplicação, sem uso de Triggers ou Rules físicas nesta fase.

---

## DEC-028 — Integridade referencial / ON DELETE

Status: ACCEPTED

### Contexto

Materializar fisicamente as regras aprovadas conceitualmente para o momento em que entidades "pai" (Categoria, Fornecedor, Produto) forem excluídas, afetando as dependentes.

### Opções consideradas

1. `ON DELETE CASCADE`.
2. `ON DELETE SET NULL`.
3. `ON DELETE RESTRICT`.

### Decisão

Aplicar `ON DELETE RESTRICT` a todas as chaves estrangeiras:
- Produto.`categoria_id` (RESTRICT)
- Produto.`fornecedor_id` (RESTRICT)
- Movimentacao.`produto_id` (RESTRICT)
- Movimentacao.`fornecedor_id` (RESTRICT)

### Justificativa

- Categoria e Fornecedor não podem ser apagados se estiverem sendo referenciados por Produtos ou Históricos (RESTRICT preserva o negócio).
- Produto não pode ser apagado se possuir Movimentações (RESTRICT protege a auditoria).
- `CASCADE` destruiria dados de auditoria em cadeia. `SET NULL` deixaria itens órfãos e violaria os `NOT NULL`. Soft delete está fora do escopo. Para `ON UPDATE`, mantemos o comportamento padrão do banco, pois não há fluxo para alterar PKs.

### Consequências

- Excluir qualquer registro que possua dependências lançará erro de FK no banco.
- Esta decisão encerra a materialização do bloqueio de exclusões exigido na fase conceitual.

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
- A política de exclusão de Categoria com Produtos associados continua dependendo de DOM-013 (ainda OPEN). *Resolvido posteriormente por DEC-018.*
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
- A política de exclusão de Fornecedor com movimentações associadas continua dependendo de DOM-008 (ainda OPEN). *Resolvido posteriormente por DEC-020.*
- A captura do fornecedor e a criação da movimentação deverão participar da mesma fronteira transacional da atualização de estoque. *Estrategia transacional formalizada em DEC-031.*

---

## PEND-003 — Relação Produto–Fornecedor

Status: SUPERSEDED por DEC-009

Questão original:

Um produto terá apenas um fornecedor ou poderá possuir múltiplos fornecedores?

O enunciado deve ser analisado antes da modelagem para evitar uma relação arbitrária.

Resolução: ver DEC-009.

---

## DEC-011 — Estoque mínimo

Status: ACCEPTED

### Contexto

O desafio exige a consulta de produtos no estoque mínimo ou abaixo dele. Para que essa consulta seja possível, é necessária uma referência para comparação.

### Opções consideradas

1. **Atributo no Produto:** Um campo `estoque_minimo` em Produto.
2. **Valor global fixo:** Um valor padrão para todos os produtos (ex: 10 unidades).
3. **Parâmetro de query:** Informado no momento da requisição pela API.

### Decisão

O Produto terá o atributo conceitual: `estoque_minimo`.

**Semântica:** `quantidade_em_estoque <= estoque_minimo` significa que o Produto está no estoque mínimo ou abaixo dele.

**Regras aprovadas:**
- Pertence ao Produto.
- Representa quantidade de unidades (tipo conceitual inteiro).
- É obrigatório e deve aceitar zero.
- Não deve aceitar valor negativo.
- Não terá um default implícito nesta etapa.
- Deverá ser informado conscientemente no cadastro do Produto.

### Justificativa

- A consulta exigida precisa de um valor de referência por Produto, pois produtos diferentes podem possuir necessidades diferentes.
- Um valor global ou parâmetro de consulta não representa corretamente essa característica específica do Produto.

### Consequências

- `estoque_minimo` será um campo obrigatório (NOT NULL) no cadastro de produto.
- Precisará de validação de valor >= 0.
- A modelagem do modelo físico PostgreSQL deverá prever o tipo numérico correspondente a essa regra, porém os tipos físicos serão definidos posteriormente.

---

## PEND-004 — Estoque mínimo

Status: SUPERSEDED por DEC-011

Questão original:

O requisito de consulta de produtos no estoque mínimo exige uma referência persistida de estoque mínimo por produto.

Devem ser definidos:

- nome do campo;
- tipo;
- valor padrão;
- regras de validação.

Resolução: ver DEC-011.

---

## DEC-012 — Controle de quantidade_em_estoque

Status: ACCEPTED

### Contexto

O desafio exige que a movimentação de estoque reflita automaticamente na quantidade disponível do produto. Além disso, as movimentações representam registros de auditoria imutáveis. Era preciso definir como a `quantidade_em_estoque` seria mantida e alterada no sistema.

### Opções consideradas

1. **Alteração livre no CRUD:** O cliente pode atualizar a `quantidade_em_estoque` livremente via endpoint `PUT/PATCH` em Produto.
2. **Atualização exclusiva via Movimentação:** A quantidade_em_estoque não pode ser alterada diretamente pelo CRUD, toda e qualquer alteração de saldo exige a criação de uma movimentação correspondente.

### Decisão

A `quantidade_em_estoque` pertence a Produto e representa o saldo atual persistido.

Sua atualização será **exclusiva via Movimentação**. Não poderá ser alterada diretamente pelo CRUD de Produto.
A criação da Movimentação e a atualização do saldo deverão futuramente ocorrer na mesma transação. (Não implementar essa transação agora).

### Justificativa

- Preservar a rastreabilidade integral.
- Evitar alterações de saldo sem histórico associado.
- Manter responsabilidades separadas: Produto cadastra o item; Movimentação altera o estoque.

### Consequências

- O modelo não usará cálculo em tempo real a cada consulta, o saldo é de fato persistido e cacheado na entidade Produto.
- Endpoints de criação/edição de Produto não poderão alterar o estoque livremente.

---

## DEC-013 — Estoque inicial

Status: ACCEPTED

### Contexto

No momento da criação de um novo Produto, era necessário determinar como o estoque inicial do item seria registrado, respeitando a regra de que o saldo deve sempre corresponder ao histórico de movimentações.

### Opções consideradas

1. **Estoque livre na criação:** O cliente informa uma quantidade inicial e o Produto nasce com esse saldo (sem movimentação associada).
2. **Movimentação automática:** O cliente informa o saldo inicial no momento de criação do Produto, e a API automaticamente gera uma Movimentação de entrada.
3. **Estoque inicial sempre zero:** Todo Produto é criado com quantidade_em_estoque = 0. Para adicionar estoque inicial, o cliente deve posteriormente criar uma Movimentação explícita.

### Decisão

**Estoque inicial sempre zero.**

- Todo Produto é criado com `quantidade_em_estoque = 0`.
- O cliente não informa livremente um estoque inicial no cadastro.
- Para adicionar estoque inicial, deve criar posteriormente uma Movimentação do tipo entrada.
- Criação de Produto NÃO gera Movimentação automaticamente.
- Produto com estoque zero é um estado válido.

### Justificativa

- Evitar efeitos colaterais ocultos na criação de Produto (criar movimentações implicitamente).
- Manter a implementação e defesa simples.
- Consolidar a regra de que *toda alteração* de estoque (inclusive a primeira) tem a exata mesma forma e origem.

### Consequências

- O campo `quantidade_em_estoque` terá valor inicial zero na criação de um produto.
- Fluxos de negócio que exigem cadastrar e já dar entrada no item precisarão de duas requisições na API.

---

## DEC-014 — Quantidade da Movimentação

Status: ACCEPTED

### Contexto

Para garantir a consistência das movimentações e do saldo, era necessário definir quais valores são válidos para a quantidade de uma Movimentação (se aceitaria zero, valores negativos ou apenas estritamente positivos).

### Opções consideradas

1. **Valores negativos para saída:** Representar saídas com quantidade negativa e entradas com positiva.
2. **Quantidade apenas como magnitude:** A quantidade é estritamente maior que zero (magnitude) e o `tipo` da movimentação define a direção.

### Decisão

A quantidade de uma Movimentação deve ser **estritamente maior que zero**.

- Zero é inválido.
- Valor negativo é inválido.
- O campo `tipo` já determina a direção da operação (entrada aumenta estoque; saída diminui estoque).
- A quantidade representa somente a magnitude da movimentação.

*(Nota: Não definir ainda o tipo físico PostgreSQL, CHECK constraint física ou status HTTP para erro de validação).*

### Justificativa

Utilizar a quantidade como magnitude absoluta combinada ao campo `tipo` explícito torna a intenção da operação mais clara, evita confusões semânticas (como "saída de -10") e facilita a manutenção dos registros de auditoria.

### Consequências

- A validação de criação da Movimentação exigirá quantidade > 0.
- A lógica de atualização de saldo deverá somar para entrada e subtrair a magnitude para saída.

---

## DEC-015 — Saída acima do estoque disponível

Status: ACCEPTED

### Contexto

O desafio não especifica explicitamente o comportamento quando uma Movimentação de saída tenta retirar mais itens do que o saldo atual do Produto. É necessário decidir como o domínio lida com estoque insuficiente.

### Opções consideradas

1. **Permitir estoque negativo:** Efetuar a saída e deixar o saldo negativo (útil se houvesse suporte a backorders/reservas).
2. **Bloquear saída:** A operação é cancelada se não houver saldo suficiente.

### Decisão

Uma Movimentação do tipo saída somente pode ser criada quando:
`quantidade <= quantidade_em_estoque atual do Produto`

**Regras aprovadas:**
- Saída igual ao saldo disponível é válida e pode levar o estoque a zero.
- Saída maior que o saldo disponível é inválida.
- Estoque negativo não é permitido pelo domínio.
- Se a saída for inválida:
  - a Movimentação NÃO deve ser criada;
  - o saldo do Produto NÃO deve ser alterado.
- A criação da Movimentação e a alteração do saldo deverão futuramente ocorrer atomicamente (não implementar essa atomicidade agora).

### Justificativa

No escopo atual, saldos negativos não fazem sentido sem fluxos avançados de vendas/reservas. A rejeição atua como salvaguarda da integridade do estoque físico e dos registros do sistema.

### Consequências

- Será necessária uma validação contra o saldo atual persistido do Produto antes de aprovar uma saída.
- **Risco de Concorrência Registrado:** Duas saídas concorrentes podem tentar consumir o mesmo saldo. A regra de domínio deverá ser preservada também sob concorrência. A estratégia para lidar com isso (locking, isolamento, retry) será decidida na etapa própria já prevista no projeto, não devendo ser antecipada.

---

## DEC-016 — Tipo da Movimentação

Status: ACCEPTED

### Contexto

Para registrar movimentações de estoque de forma consistente, era necessário definir como os tipos de movimentação seriam representados conceitualmente na entidade Movimentação.

### Opções consideradas

1. **Booleano:** Representar a movimentação como um booleano (ex.: `is_entrada` verdadeiro ou falso).
2. **Conjunto fechado de valores explícitos:** Representar com tipos semânticos específicos e claros, como ENTRADA e SAÍDA.

### Decisão

O atributo conceitual `tipo` da Movimentação representa um conjunto fechado com **exatamente dois valores semânticos**:

- ENTRADA
- SAÍDA

**Regras aprovadas:**
- ENTRADA aumenta o saldo do Produto.
- SAÍDA diminui o saldo do Produto.
- Nenhum terceiro tipo (como ajuste, inventário, devolução, transferência, etc.) está previsto no escopo atual.
- Booleano não será utilizado como representação conceitual, pois é menos expressivo.

*(Nota: A escolha física entre PostgreSQL ENUM, VARCHAR + CHECK ou outra implementação não será feita nesta etapa).*

### Justificativa

Um domínio estrito com ENTRADA e SAÍDA abrange totalmente os requisitos do desafio. Usar nomes explícitos em vez de booleanos torna a regra de negócio expressiva, clara e robusta, facilitando a leitura de código e de registros de auditoria. Evitar novos tipos simplifica a solução e mantém o foco no requisito principal.

### Consequências

- A validação da Movimentação exigirá que o atributo `tipo` seja estritamente um dos dois valores.
- A aplicação terá que lidar com qualquer fluxo excepcional convertendo-o para uma entrada ou saída básica.

---

## DEC-017 — Data da Movimentação

Status: ACCEPTED

### Contexto

Cada movimentação de estoque funciona como um registro de auditoria, exigindo o armazenamento de data e hora para ordenação e filtro histórico. Era necessário decidir a origem e granularidade desse valor.

### Opções consideradas

1. **Informada pelo cliente (Payload):** O cliente envia a data desejada na requisição (permitindo registros retroativos).
2. **Determinada pelo servidor:** O backend captura a data/hora no momento de processamento da criação.

### Decisão

A data/hora da Movimentação será **determinada pelo servidor no momento da criação**.

**Regras aprovadas:**
- O cliente não informa livremente essa data/hora.
- Não haverá registro retroativo nesta versão do projeto.
- O valor representa o momento exato em que a Movimentação é registrada pelo sistema.
- A informação precisa permitir ordenação temporal e filtro por período.
- Conceitualmente, deve possuir precisão de data e hora (não apenas o dia).

*(Nota: Detalhes como TIMESTAMP vs TIMESTAMPTZ, timezone, UTC ou default físico no PostgreSQL serão definidos no modelo físico.) Resolvido posteriormente por DEC-024 e DEC-030.*

### Justificativa

Como a Movimentação é um registro de auditoria crítico para o sistema, gerar a data no servidor reduz o risco de manipulação ou erro de data. Lançamentos retroativos não são requisitos do desafio e a sua ausência simplifica bastante o contrato da API.

### Consequências

- A data/hora não integra o contrato gravável de criação da Movimentação. O comportamento genérico para campos extras pertence à futura definição dos schemas/validação da API.
- A própria camada de aplicação ou banco de dados injetará o valor atual.

## DEC-018 — Exclusão de Categoria (RESTRICT)

Status: ACCEPTED

### Contexto

O desafio explicita que "não deve ser possível excluir uma categoria que tenha produtos associados". Era preciso formalizar essa regra de domínio (DOM-013) e decidir como lidar com as opções de bloqueio, soft delete ou exclusão em cascata.

### Opções consideradas

1. **RESTRICT (Bloqueio duro):** Impede a exclusão da Categoria se houver Produto associado.
2. **SET NULL / CASCADE:** (Inválido para o escopo).
3. **Soft delete:** Marcador lógico.

### Decisão

A exclusão da Categoria deve respeitar as seguintes regras:
- Categoria sem Produtos associados pode ser excluída.
- Categoria com um ou mais Produtos associados **NÃO** pode ser excluída.
- Os Produtos NÃO são excluídos em cascata.
- Os Produtos NÃO ficam sem Categoria.
- Soft delete não será adotado no escopo atual.

*(Nota: Detalhes de implementação como ON DELETE SQL, tratamento do erro e status HTTP não serão definidos agora).*

### Justificativa

Cada Produto possui obrigatoriamente uma Categoria. A exclusão da Categoria não deve alterar ou destruir Produtos implicitamente. A política RESTRICT atua como uma REGRA DE DOMÍNIO preservando a integridade.

### Consequências

- Operações de exclusão de Categoria poderão falhar se o recurso estiver em uso.

---

## DEC-019 — Exclusão de Produto (RESTRICT)

Status: ACCEPTED

### Contexto

Quando um Produto é excluído, era necessário determinar o impacto nas Movimentações históricas a ele associadas (DOM-007).

### Opções consideradas

1. **CASCADE / SET NULL:** Destruir histórico ou quebrar a referência ao Produto.
2. **RESTRICT:** Impedir a exclusão do Produto se ele possuir movimentações.

### Decisão

A exclusão do Produto deve respeitar as seguintes regras:
- Produto sem Movimentações pode ser excluído.
- Produto que possui uma ou mais Movimentações **NÃO** pode ser excluído.
- Movimentações NÃO são excluídas em cascata.
- O `produto_id` histórico NÃO será colocado como NULL.
- Soft delete não será adotado no escopo atual.

### Justificativa

Movimentações são registros imutáveis de auditoria e precisam manter uma referência válida ao Produto histórico. Destruir ou invalidar essa ligação violaria os requisitos do domínio.

### Consequências

- A exclusão de um produto será bloqueada assim que a primeira movimentação for vinculada a ele.

---

## DEC-020 — Exclusão de Fornecedor (RESTRICT)

Status: ACCEPTED

### Contexto

Ao tentar excluir um Fornecedor, era preciso analisar o impacto sobre os Produtos cadastrados e as Movimentações históricas associadas (DOM-008).

### Opções consideradas

1. **CASCADE / SET NULL:** Apagar o histórico e desvincular do cadastro dos produtos.
2. **RESTRICT:** Bloquear exclusão se existirem associações.

### Decisão

O Fornecedor pode ser excluído **somente quando**:
- Não possuir Produtos associados.
- Não possuir Movimentações históricas associadas.

Se qualquer uma dessas referências existir, a exclusão deve ser bloqueada. Não utilizar CASCADE, SET NULL ou soft delete no escopo atual.

### Justificativa

O Fornecedor participa tanto do cadastro atual dos Produtos quanto da referência histórica das Movimentações. Bloquear a exclusão garante que o banco mantenha consistência sem destruir informações críticas, seguindo a semântica de RESTRICT como regra de domínio.

### Consequências

- Será impossível excluir fornecedores com qualquer histórico ativo.

---

## DEC-029 — Estratégia de Índices e Padrões de Acesso

Status: ACCEPTED

### Contexto

Definir a estratégia inicial de índices para suportar as consultas obrigatórias (por período, fornecedor, e por ambos combinados), os relacionamentos (JOINs e exclusões restritas) e otimizar acessos sem sobre-indexar as tabelas.

### Opções consideradas

1. Criar índices para todas as colunas frequentemente lidas.
2. Criar índices preventivos baseados em cenários não documentados no desafio.
3. Criar índices especializados para a regra de estoque mínimo.
4. Adicionar estritamente os índices justificados pelos padrões de consulta obrigatórios e integridade referencial.

### Decisão

- Índices de PK e UNIQUE já geram suas estruturas nativamente e não devem ser duplicados.
- Criaremos índices adicionais para as Foreign Keys que participam de JOINs lógicos e verificações de integridade de deleção RESTRICT: `Produto(categoria_id)`, `Produto(fornecedor_id)` e `Movimentacao_Estoque(produto_id)`.
- Criaremos índices para buscas da auditoria: `Movimentacao_Estoque(data)` (para filtros de período isolado) e `Movimentacao_Estoque(fornecedor_id, data)` (para filtros de fornecedor, aproveitando prefixo à esquerda para fornecedor + período).
- NÃO criaremos índice para `estoque_minimo` ou `quantidade_em_estoque` para resolver a consulta de "estoque mínimo" neste momento.
- NÃO duplicaremos índices apenas para ORDER BY em campos que já possuem índice B-tree, pois este pode ser percorrido de trás para a frente (ordem decrescente).

### Justificativa

Os índices aceleram o processo de leitura e localização dos registros, mas geram custos em armazenamento, e retardam as operações de escrita (INSERT, UPDATE, DELETE). A criação de índices baseia-se num equilíbrio entre as consultas realmente exigidas (filtro por data, fornecedor, relacionamento) e a contenção do impacto nas escritas.

A consulta de estoque mínimo compara duas colunas da mesma tabela (`quantidade_em_estoque <= estoque_minimo`). Índices simples ou parciais para essa funcionalidade trariam custo extra de atualização num cenário de pouca escala comprovada, não compensando uma otimização prematura. A efetividade destas e outras otimizações deverá ser validada futuramente via EXPLAIN/EXPLAIN ANALYZE, caso o volume assim exija.

O índice composto `(fornecedor_id, data)` aproveita eficientemente o prefixo à esquerda (`fornecedor_id`) quando se quer apenas o fornecedor, assim evitamos criar um índice adicional só para `fornecedor_id`. Mas esse mesmo índice não tem capacidade de otimizar consultas apenas por `data`, por isto o índice isolado `(data)` foi incluído.

### Consequências

- Serão definidos no futuro (migrations/SQLAlchemy) apenas índices explícitos com as regras listadas, utilizando nomes consistentes (por exemplo, `ix_movimentacao_fornecedor_data`).
- Alterações em massa de movimentações e produtos pagarão o custo de escrita destes índices recém aprovados.
- Qualquer gargalo não coberto por esse modelo inicial de índices só deve justificar criação de novo índice após ser evidenciado em plano de execução.

---

## DEC-030 — Política Operacional de Timezone

Status: ACCEPTED

### Contexto

O banco de dados utilizará o tipo físico `TIMESTAMPTZ` para campos que representam um instante temporal (`Produto.data_cadastro` e `Movimentacao_Estoque.data`). Era necessário estabelecer uma política consistente para lidar com datas e horários entre a aplicação e o banco, a fim de evitar ambiguidades em filtros históricos, ordenações e registros de auditoria.

### Opções consideradas

1. Armazenar um campo separado para o fuso horário (timezone) do usuário.
2. Utilizar datetimes *naive* (ingênuos) assumindo implicitamente que são todos da mesma região.
3. Usar UTC como referência operacional interna, tratando fuso horário apenas na camada de apresentação/API.

### Decisão

A política temporal operacional será:
- UTC será a referência temporal operacional interna em todo o backend.
- Os campos que representam instantes absolutos permanecem como `TIMESTAMPTZ`.
- O backend trabalhará futuramente apenas com datetimes *timezone-aware* (cientes de fuso horário). Datetimes ingênuos não serão tratados como timestamps válidos.
- A conversão para o timezone local do usuário pertencerá unicamente à apresentação/contexto da API (frontend ou formatação de resposta).
- O timezone local não será armazenado como um atributo separado nesta versão.

Para as movimentações de estoque, a data/hora continua sendo determinada pelo sistema (`DEFAULT CURRENT_TIMESTAMP`), o cliente não informa o valor e regras de retroatividade seguem inalteradas.

### Justificativa

O `TIMESTAMPTZ` no PostgreSQL não preserva o nome do timezone original (apenas armazena o instante absoluto convertido para UTC). Um instante absoluto é o mesmo em qualquer lugar do mundo (ex: `2026-09-29 14:00:00-03:00` é idêntico a `2026-09-29 17:00:00+00:00`). Adotar o UTC como referência operacional backend elimina ambiguidades, garantindo que ordenações e cálculos de período funcionem corretamente independente da configuração regional do servidor ou da conexão do banco. Tratar a conversão apenas na camada de apresentação respeita a separação de responsabilidades.

### Consequências

- Futuros filtros por período deverão comparar os instantes de maneira *timezone-aware*.
- A configuração da aplicação (Python/FastAPI) e dos schemas (Pydantic) precisará garantir que os dados trafegados e processados respeitem o formato com timezone explícito (como ISO-8601 com sufixo `Z` ou offset).

---

## DEC-031 — Estratégia Transacional e Controle de Concorrência das Movimentações

Status: ACCEPTED

### Contexto
Se duas ou mais requisições tentarem movimentar o estoque do mesmo Produto simultaneamente (*race condition*), elas podem ler o mesmo saldo base obsoleto e aprovar saídas que resultariam em estoque negativo, ou sobrescrever o saldo incorretamente. Era necessário definir como garantir a consistência sob concorrência.

### Alternativas consideradas
1. **UPDATE condicional atômico**: `UPDATE produto SET quantidade_em_estoque = quantidade_em_estoque - quantidade WHERE id = produto_id AND quantidade_em_estoque >= quantidade RETURNING ...`. Evita a race condition de forma efetiva.
2. **PostgreSQL SERIALIZABLE / REPEATABLE READ**: Elevar o nível de isolamento transacional para lidar globalmente com as leituras repetíveis e escritas concorrentes.
3. **Lock Pessimista (FOR UPDATE)**: Travar explicitamente a linha do Produto para leitura e atualização exclusivas.

### Decisão
Toda criação de Movimentação ocorrerá dentro de **UMA única transação**. 
A unidade de concorrência será a **linha do Produto**.
A linha do Produto afetado será obtida com bloqueio pessimista: `SELECT ... FOR UPDATE` aliado ao isolamento padrão `READ COMMITTED` do PostgreSQL.

A fronteira transacional será:
`BEGIN`
1. Localizar Produto pelo id com `FOR UPDATE`. Se não existir, interromper.
2. Ler `quantidade_em_estoque` e `fornecedor_id`.
3. Validar a Movimentação (Para saída: `quantidade <= saldo atual`. Se faltar saldo, interromper sem alterar nada e sem criar Movimentação).
4. Calcular novo saldo.
5. Atualizar `quantidade_em_estoque` do Produto.
6. Criar a `MOVIMENTACAO_ESTOQUE` capturando o fornecedor histórico do Produto bloqueado.
`COMMIT` (ou `ROLLBACK` em caso de falha após o BEGIN).

Entradas e saídas utilizarão a mesma mecânica de bloqueio.

### Justificativa
O lock pessimista (`FOR UPDATE`) torna o fluxo explícito, unitário e fácil de compreender. Precisamos ler o saldo atual e o `fornecedor_id` cadastral do produto de maneira sincronizada antes da criação. Esse bloqueio explícito resolve a concorrência perfeitamente junto ao isolamento padrão `READ COMMITTED`, sem necessitar de *retry loops* ou a sobrecarga global de `SERIALIZABLE`. A alternativa por `UPDATE` atômico direto foi considerada, porém optou-se pelo `FOR UPDATE` para utilizar o mesmo caminho lógico visível tanto para entradas quanto saídas e expor de maneira muito clara a unidade crítica de lock no código.

### Consequências
- A aplicação serializará requisições simultâneas para o **mesmo Produto** no nível do banco (uma aguarda a liberação da linha enquanto a outra processa).
- Transações de **Produtos diferentes** prosseguirão em paralelo normalmente (escopo do lock reduzido à linha).
- A imutabilidade é garantida.
- Fornecedor histórico inserido na Movimentação estará perfeitamente sincronizado com o Produto atual.
- O risco de *deadlock* é baixo pois as movimentações travam apenas uma única linha de Produto por vez.

### Limitações
- Não definimos nem implementaremos *retry* automático, timeout customizado ou *recovery* de deadlock. Só serão considerados se absolutamente necessários nos testes práticos.
- O mapeamento de erros HTTP desta fronteira (400, 404, 409, 422) será definido na etapa respectiva.

---

## PEND-005 — SQLAlchemy síncrono ou assíncrono

Status: PROPOSED

Questão:

A aplicação utilizará SQLAlchemy síncrono ou assíncrono?

A escolha deve considerar simplicidade, objetivo educacional e necessidades reais do desafio.

---

## PEND-006 — Regras de exclusão

Status: SUPERSEDED por DEC-018, DEC-019 e DEC-020

Questão:

Além da restrição explícita envolvendo categorias com produtos associados, quais comportamentos serão adotados na exclusão de fornecedores e produtos relacionados a registros históricos?

A decisão deverá preservar integridade referencial e auditoria.

Resolução: A política conceitual escolhida é RESTRICT para todas as entidades centrais, conforme definido em DEC-018, DEC-019 e DEC-020.

---

## PEND-007 — Formato padronizado de erros

Status: PROPOSED

Questão:

Qual será o envelope padrão das respostas de erro?

A decisão deve ser tomada antes da consolidação dos exception handlers.

---

## PEND-008 — Estratégia de concorrência

Status: SUPERSEDED por DEC-031

Questão:

Caso o diferencial de concorrência seja implementado, qual estratégia será utilizada para impedir saídas simultâneas inconsistentes?

Possibilidades a estudar:

- locking pessimista;
- locking otimista;
- atualização atômica condicionada.

A decisão somente será aceita após entendimento do problema de race condition.

Resolução: A estratégia formalizada é o lock pessimista (`SELECT FOR UPDATE`) focado na linha do Produto (unidade de lock), operando em `READ COMMITTED`. Detalhes em DEC-031.

---

## DEC-032 — Estratégia de configuração e variáveis de ambiente

Status: ACCEPTED

### Contexto

Como a aplicação será conectada ao banco de dados e como as credenciais serão gerenciadas de maneira segura antes de prosseguir com a implementação do ORM (SQLAlchemy).

### Decisão

A configuração da aplicação usará variáveis de ambiente através da biblioteca `pydantic-settings`.

- Os componentes da conexão com o banco (Host, Porta, Nome, Usuário, Senha) serão injetados por variáveis separadas (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).
- As configurações locais (para desenvolvimento) serão carregadas de um arquivo `.env` (ignorado pelo Git).
- Um arquivo `.env.example` versionável proverá a documentação dos campos e valores seguros de fallback (`CHANGE_ME` para a senha).
- A aplicação construirá a connection string PostgreSQL de forma segura usando esses componentes separadamente na inicialização, escapando caracteres especiais.
- A escolha do driver específico (`psycopg`, `asyncpg`, etc.) permanece postergada (TSK-2.7). A connection string usará a representação conceitual base (`postgresql://`).

### Justificativa

Essa abordagem segue os princípios do "12-Factor App", mantendo a configuração separada do código e blindando senhas e dados sensíveis de vazamentos no versionamento. O uso do Pydantic simplifica a validação, parse de tipos fortes e fornece uma abstração limpa de tipagem. A divisão dos campos em componentes separados em vez de uma única `DATABASE_URL` permite fácil auditoria individual de falhas e mais clareza sem vazamento acidental da senha completa nos logs.

### Consequências

- A inicialização do banco depende da classe `Settings` do módulo `app/config.py`.
- O SQLAlchemy ainda não está configurado.
- A configuração ainda não resolveu a escolha do motor assíncrono vs síncrono.

---

## Regra para novas decisões

Quando uma decisão pendente for resolvida:

1. não apagar o contexto histórico;
2. criar ou atualizar uma entrada DEC;
3. registrar as alternativas consideradas;
4. registrar a escolha adotada;
5. explicar a justificativa;
6. registrar consequências relevantes.
