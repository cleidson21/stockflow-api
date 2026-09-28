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

## PEND-003 — Relação Produto–Fornecedor

Status: PROPOSED

Questão:

Um produto terá apenas um fornecedor ou poderá possuir múltiplos fornecedores?

O enunciado deve ser analisado antes da modelagem para evitar uma relação arbitrária.

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
