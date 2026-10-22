# StockFlow API — Project Plan

## 1. Objetivo

Este documento acompanha o desenvolvimento incremental do StockFlow API.

Cada tarefa deve ser concluída, compreendida, testada e revisada antes do avanço para tarefas dependentes.

O projeto deve priorizar primeiro todos os requisitos obrigatórios do desafio técnico. Os diferenciais devem ser implementados somente quando a base obrigatória estiver estável.

Prazo vigente de entrega: **24/10/2026**, conforme prorrogação posteriormente comunicada ao desenvolvedor pela organização. O prazo original de **16/10/2026** permanece registrado como referência histórica.

O [enunciado de referência](referencias/prosel-2026.2/desafio-tecnico-backend-prosel-2026.2.md) do Prosel 2026.2 foi obtido de um colega, tem versão não confirmada e pode corresponder a uma versão anterior. A prorrogação e o cancelamento da defesa oral são comunicações posteriores recebidas pelo desenvolvedor; não há evidência, nesta revisão, de sua publicação formal no enunciado anexado.

---

## 2. Convenções de status

- [ ] Não iniciada
- [~] Em andamento
- [x] Concluída
- [!] Bloqueada ou aguardando decisão

Os períodos indicados nas fases pertencem ao planejamento original; não representam datas comprovadas de execução. Os itens concluídos preservam os marcos já registrados. A validação final após as revisões permanece separada desses resultados históricos, conforme TSK-8.5.

---

## 3. Fase 0 — Fundação e Governança

Meta: preparar um repositório limpo, rastreável e estruturado para o desenvolvimento assistido por ferramentas de IA.

### TSK-0.1 — Definição do projeto

- [x] Definir o nome StockFlow API.
- [x] Definir o nome do repositório como stockflow-api.

### TSK-0.2 — Repositório remoto

- [x] Criar o repositório no GitHub.

### TSK-0.3 — Repositório local

- [x] Criar a pasta local stockflow-api.
- [x] Inicializar o Git.
- [x] Padronizar a branch principal como main.
- [x] Vincular origin ao GitHub.

### TSK-0.4 — Arquivos iniciais

- [x] Criar README.md inicial.
- [x] Criar .gitignore.
- [x] Realizar primeiro Conventional Commit.
- [x] Realizar primeiro push.

### TSK-0.10 — Auditoria inicial

- [x] Verificar estrutura do repositório.
- [x] Verificar branch e remote.
- [x] Confirmar working tree limpa.

### TSK-0.11 — Instruções para agentes

- [x] Criar AGENTS.md.
- [x] Definir regras de escopo.
- [x] Definir regras de Git.
- [x] Definir compromisso com aprendizado e defesa técnica.

### TSK-0.12 — Planejamento interno

- [x] Criar docs/PROJECT_PLAN.md.
- [x] Criar docs/DECISIONS.md.
- [x] Revisar os dois documentos.
- [x] Realizar commit da documentação.

---

## 4. Fase 1 — Ambiente Python e FastAPI mínimo

Meta: obter uma aplicação FastAPI mínima funcionando localmente antes de adicionar banco de dados.

Período planejado: 25/09 a 26/09.

### TSK-1.1 — Ambiente Python

- [x] Verificar a versão do Python instalada.
- [x] Confirmar compatibilidade com as dependências pretendidas.
- [x] Registrar a versão adotada.

### TSK-1.2 — Ambiente virtual

- [x] Entender a finalidade de um ambiente virtual.
- [x] Criar .venv.
- [x] Ativar o ambiente virtual.
- [x] Confirmar que python e pip apontam para .venv.
- [x] Validar que .venv permanece ignorado pelo Git.

### TSK-1.3 — Estratégia de dependências

- [x] Discutir requirements.txt versus pyproject.toml.
- [x] Escolher conscientemente uma abordagem.
- [x] Registrar a decisão em DECISIONS.md.

### TSK-1.4 — Dependências iniciais

- [x] Instalar FastAPI.
- [x] Instalar servidor ASGI apropriado.
- [x] Registrar versões das dependências.
- [x] Entender a função de cada dependência instalada.

### TSK-1.5 — Aplicação mínima

- [x] Definir a estrutura mínima da aplicação.
- [x] Criar o ponto de entrada FastAPI.
- [x] Criar uma primeira rota simples.
- [x] Executar a aplicação localmente.

### TSK-1.6 — HTTP e FastAPI

- [x] Entender request e response.
- [x] Entender endpoint e rota.
- [x] Entender método HTTP.
- [x] Entender status code.
- [x] Entender ASGI.
- [x] Entender a função do servidor de aplicação.

### TSK-1.7 — Documentação automática

- [x] Acessar /docs.
- [x] Entender Swagger UI.
- [x] Entender OpenAPI.
- [x] Verificar a documentação automática da primeira rota.

### TSK-1.8 — Health Check

- [x] Criar endpoint de health check.
- [x] Definir resposta esperada.
- [x] Validar manualmente.
- [x] Revisar alterações.
- [x] Realizar Conventional Commit.

---

## 5. Fase 2 — Modelagem e PostgreSQL

Meta: definir conscientemente o modelo relacional e conectar a aplicação ao PostgreSQL.

Período planejado: 27/09 a 29/09.

> `docs/DOMAIN_MODELING.md` é o documento vivo da modelagem de domínio e dados desta fase.

### TSK-2.1 — Análise de domínio

- [x] Revisar Produto.
- [x] Revisar Fornecedor.
- [x] Revisar Categoria.
- [x] Revisar Movimentação de Estoque.
- [x] Identificar regras obrigatórias.
- [x] Identificar ambiguidades do enunciado.

### TSK-2.2 — Relacionamentos

- [x] Decidir a relação Produto–Categoria.
- [x] Decidir a relação Produto–Fornecedor.
- [x] Decidir como Movimentação referencia Produto.
- [x] Avaliar necessidade de referência indireta ou direta ao Fornecedor.
- [x] Definir regras de integridade referencial.
- [x] Registrar decisões.

### TSK-2.3 — Estoque mínimo

- [x] Analisar a exigência de consulta por estoque mínimo.
- [x] Decidir como representar estoque mínimo em Produto.
- [x] Definir nome, tipo e comportamento do campo.
- [x] Registrar justificativa.

### TSK-2.4 — Tipos de dados

- [x] Definir tipos de identificadores.
- [x] Definir estratégia para valores monetários.
- [x] Definir tipos para quantidades.
- [x] Definir campos de data/hora.
- [x] Definir constraints de unicidade.
- [x] Avaliar índices necessários.

### TSK-2.5 — PostgreSQL

- [x] Verificar instalação/disponibilidade do PostgreSQL.
- [x] Criar banco de desenvolvimento.
- [x] Criar usuário/configuração necessária.
- [x] Manter credenciais fora do Git.
- [x] Validar conexão manualmente.

### TSK-2.6 — Configuração da aplicação

- [x] Definir estratégia de variáveis de ambiente.
- [x] Criar exemplo seguro de configuração.
- [x] Configurar URL do banco.
- [x] Entender cada componente da connection string.

### TSK-2.7 — SQLAlchemy

- [x] Entender ORM.
- [x] Discutir abordagem síncrona versus assíncrona.
- [x] Escolher abordagem adequada à escala do desafio.
- [x] Configurar engine.
- [x] Configurar sessões.
- [x] Validar conexão.

### TSK-2.8 — Alembic

- [x] Entender migrations.
- [x] Inicializar Alembic.
- [x] Integrar Alembic aos modelos.
- [x] Criar migration inicial.
- [x] Revisar SQL/schema gerado.
- [x] Aplicar migration.
- [x] Validar tabelas no PostgreSQL.

---

## 6. Fase 3 — CRUD das entidades principais

Meta: implementar gerenciamento consistente de Categoria, Fornecedor e Produto.

Período planejado: 30/09 a 03/10.

### TSK-3.1 — Categoria

- [x] Definir modelo.
- [x] Definir schemas de entrada e saída.
- [x] Criar categoria.
- [x] Listar categorias.
- [x] Consultar categoria por id.
- [x] Atualizar categoria.
- [x] Excluir categoria.
- [x] Garantir unicidade do nome.
- [x] Tratar categoria inexistente.
- [x] Impedir exclusão incompatível com produtos relacionados.
- [x] Documentar endpoints.
- [x] Testar casos principais.

### TSK-3.2 — Fornecedor

- [x] Definir modelo.
- [x] Definir schemas.
- [x] Criar fornecedor.
- [x] Listar fornecedores.
- [x] Consultar fornecedor por id.
- [x] Atualizar fornecedor.
- [x] Excluir fornecedor conforme regra definida.
- [x] Garantir CNPJ único.
- [x] Garantir email único.
- [x] Validar erros de duplicidade.
- [x] Documentar endpoints.
- [x] Testar casos principais.

### TSK-3.3 — Produto

- [x] Definir modelo.
- [x] Definir schemas.
- [x] Criar produto.
- [x] Listar produtos.
- [x] Consultar produto por id.
- [x] Atualizar produto.
- [x] Excluir produto conforme regras definidas.
- [x] Garantir SKU único.
- [x] Validar relacionamentos.
- [x] Validar preços e quantidades.
- [x] Documentar endpoints.
- [x] Testar casos principais.

### TSK-3.4 — Revisão CRUD

- [x] Validar códigos HTTP.
- [x] Validar respostas.
- [x] Validar constraints no banco.
- [x] Validar Swagger/OpenAPI.
- [x] Revisar duplicação de lógica.
- [x] Revisar clareza do código.

---

## 7. Fase 4 — Movimentações de Estoque

Meta: implementar o núcleo transacional do sistema.

Período planejado: 04/10 a 06/10.

### TSK-4.1 — Modelo de movimentação

- [x] Definir campos.
- [x] Definir relacionamento com Produto.
- [x] Definir representação de entrada e saída.
- [x] Definir timestamp.
- [x] Criar migration.

### TSK-4.2 — Imutabilidade

- [x] Implementar criação.
- [x] Implementar consulta.
- [x] Não disponibilizar atualização.
- [x] Não disponibilizar exclusão.
- [x] Confirmar que a API respeita a imutabilidade.

### TSK-4.3 — Entrada de estoque

- [x] Validar quantidade.
- [x] Criar movimentação.
- [x] Incrementar estoque.
- [x] Garantir atomicidade da operação.
- [x] Testar sucesso e falha.

### TSK-4.4 — Saída de estoque

- [x] Validar quantidade.
- [x] Validar estoque disponível.
- [x] Impedir estoque negativo.
- [x] Criar movimentação.
- [x] Decrementar estoque.
- [x] Garantir atomicidade.
- [x] Testar sucesso e falha.

### TSK-4.5 — Transações

- [x] Entender commit.
- [x] Entender rollback.
- [x] Entender atomicidade.
- [x] Garantir que estoque e histórico não possam divergir.
- [x] Documentar a decisão transacional.

---

## 8. Fase 5 — Consultas Avançadas

Meta: implementar as consultas estratégicas exigidas pelo desafio.

Período planejado: 07/10 a 08/10.

### TSK-5.1 — Estoque mínimo

- [x] Criar consulta de produtos no estoque mínimo.
- [x] Incluir produtos abaixo do estoque mínimo.
- [x] Definir endpoint e parâmetros.
- [x] Documentar comportamento.
- [x] Testar limites.

### TSK-5.2 — Histórico por período

- [x] Definir parâmetros de data inicial e final.
- [x] Validar intervalos.
- [x] Filtrar movimentações.
- [x] Definir comportamento sem resultados.
- [x] Documentar endpoint.

### TSK-5.3 — Histórico por fornecedor

- [x] Implementar filtro compatível com o modelo relacional adotado.
- [x] Permitir combinação com período quando apropriado.
- [x] Validar fornecedor inexistente quando aplicável.
- [x] Documentar exemplos.

### TSK-5.4 — Consultas adicionais

- [x] Avaliar filtros adicionais realmente úteis.
- [x] Evitar funcionalidades sem valor para o desafio.
- [x] Implementar somente filtros justificados.

---

## 9. Fase 6 — Tratamento de Erros e Documentação

Meta: tornar o comportamento da API consistente, seguro e compreensível.

Período planejado: 09/10 a 10/10.

### TSK-6.1 — Modelo de erro

- [x] Definir formato padronizado.
- [x] Definir campos da resposta.
- [x] Diferenciar erro de validação, negócio e recurso inexistente.

### TSK-6.2 — Códigos HTTP

- [x] Revisar 2xx.
- [x] Revisar 400.
- [x] Revisar 404.
- [x] Avaliar uso de 409 para conflitos de unicidade/regra.
- [x] Entender validação 422 do FastAPI.
- [x] Garantir uso correto de 500.

### TSK-6.3 — Segurança dos erros

- [x] Não retornar stack traces.
- [x] Não expor credenciais.
- [x] Não expor informações internas desnecessárias.
- [x] Manter logs úteis apenas no servidor.

### TSK-6.4 — OpenAPI/Swagger

Os itens abaixo registram a documentação implementada desde `1b9aa82` e `c686612`. A auditoria posterior foi concluída por arquivo e consolidada nas revisões 15.1 (`e9506c5`), 15.2 (`e844dbd`), 19 (`9343023`), 20 (`d9bebc4`), 21 (`12e289d`) e 22 (`081a607`). A consolidação final do planejamento foi versionada em `b796344` e validada pelo workflow **Tests** `39792984284`.

O OpenAPI consolidado possui **12 caminhos e 22 operações**. As 22 operações têm `summary`, `description` e exemplos representativos; esta revisão final expressa complementou os exemplos de resposta HTTP 200 de `GET /` e `GET /health`, preservando seus retornos reais e o acesso público. As 19 operações protegidas mantêm `HTTPBearer`; `POST /auth/login` continua público. As 20 operações com resposta 401 pertinente — login e rotas protegidas — documentam `WWW-Authenticate: Bearer`. Os filtros de movimentações registram opcionalidade, combinação, limites inclusivos, timezone e referência histórica do fornecedor. `ErrorResponse` e `ValidationErrorResponse` permanecem como modelos padronizados.

Os preços de Produto continuam modelados como `Decimal` e documentados em `app/schemas/produto.py`. O JSON Schema gerado aceita os ramos estruturais `number` e `string`; essa representação não expressa de forma integral, em todos os consumidores OpenAPI, as regras decimais aplicadas pelo Pydantic (`max_digits` e `decimal_places`). A documentação não deve ser interpretada como equivalência total entre JSON Schema e validação em runtime.

- [x] Documentar cada endpoint.
- [x] Documentar parâmetros.
- [x] Documentar request bodies.
- [x] Documentar respostas 2xx.
- [x] Documentar respostas 4xx.
- [x] Documentar respostas 5xx quando apropriado.
- [x] Adicionar exemplos relevantes.

### TSK-6.5 — README

- [x] Documentar pré-requisitos.
- [x] Documentar configuração.
- [x] Documentar criação do banco.
- [x] Documentar migrations.
- [x] Documentar execução da API.
- [x] Documentar testes.
- [x] Documentar acesso ao Swagger.
- [x] Descrever arquitetura.
- [x] Descrever principais regras de negócio.

---

## 10. Fase 7 — Testes, Qualidade e Diferenciais

Meta: consolidar a aplicação obrigatória antes de adicionar diferenciais.

Período planejado: 11/10 a 13/10.

### TSK-7.1 — Testes automatizados

A suíte atual possui **105 casos automatizados**. O commit `c450970` acrescentou quatro testes em `tests/test_movimentacoes.py` para verificar: movimentação de `ENTRADA` concluída; movimentação de `SAIDA` concluída; `SAIDA` rejeitada por saldo insuficiente; e falha controlada no commit, sem emissão indevida de sucesso. O resultado exato registrado no README para esse commit foi `105 passed, 12 warnings in 7.82s`.

Nenhum arquivo de teste foi alterado entre `c450970` e a consolidação `b796344`; portanto, a coleção permaneceu com os mesmos 105 casos, sem confundir funções Python com casos parametrizados coletados. O workflow **Tests** `39792984284`, correspondente a `b796344`, concluiu instalação de dependências, migrations, `alembic current` e `pytest -q` com sucesso: `105 passed, 12 warnings in 9.10s`. Esse total não representa cobertura de código de 100%.

- [x] Definir estratégia de testes.
- [x] Configurar framework.
- [x] Criar ambiente de teste isolado.
- [x] Testar CRUD.
- [x] Testar unicidade.
- [x] Testar movimentações.
- [x] Testar estoque insuficiente.
- [x] Testar imutabilidade.
- [x] Testar consultas avançadas.
- [x] Testar erros relevantes.
- [x] Testar o logging operacional de movimentações e a ausência de sucesso após falha no commit.

### TSK-7.2 — Integração contínua

- [x] Avaliar GitHub Actions.
- [x] Executar testes automaticamente.
- [x] Garantir falha do workflow quando testes falharem.

O workflow `.github/workflows/tests.yml` configura Python 3.12, PostgreSQL 16, instalação de dependências, `alembic upgrade head`, `alembic current` e `pytest -q` em pushes e pull requests para `main`. Para a consolidação `b796344`, o [workflow público Tests](https://github.com/cleidson21/stockflow-api/actions/runs/39792984284) (`39792984284`) foi verificado como `completed/success`, com migrations e `pytest` aprovados. Alterações posteriores devem possuir validação própria antes da submissão, sem antecipar o SHA ou o resultado de uma execução futura.

### TSK-7.3 — Concorrência

- [x] Reproduzir conceitualmente a race condition.
- [x] Entender lock pessimista.
- [x] Entender lock otimista.
- [x] Analisar estratégia apropriada.
- [x] Registrar decisão antes da implementação.
- [x] Implementar controle de concorrência.
- [x] Testar saídas simultâneas.
- [x] Confirmar impossibilidade de estoque negativo.

### TSK-7.4 — Autenticação e autorização

- [x] Implementar somente se os requisitos obrigatórios estiverem estáveis.
- [x] Discutir JWT.
- [x] Definir modelo de usuário.
- [x] Definir autenticação.
- [x] Definir autorização por função se viável.
- [x] Proteger rotas apropriadas.
- [x] Testar acesso autorizado e não autorizado.
- [x] Implementar CLI administrativa de criação de usuários (`app/cli/create_user.py`, presente desde `92ddb88`), com senha solicitada no terminal e hash persistido.

A implementação da CLI e seu uso no README estão confirmados. O texto prospectivo da DEC-034 foi reconciliado em `2d0277f`, preservando a decisão original e registrando a implementação efetiva de `app/cli/create_user.py` desde `92ddb88`.

---

## 11. Fase 8 — Auditoria Final e Revisão de Qualidade

Meta: assegurar a estabilidade operacional da aplicação, a rastreabilidade do repositório e a conformidade técnica e documental com os critérios de avaliação do processo seletivo.

Período planejado: 14/10 a 15/10.

> **Nota histórica de escopo:** Esta fase foi originalmente planejada contemplando a preparação para defesa oral técnica. A organização comunicou posteriormente ao desenvolvedor o cancelamento da defesa oral. O redirecionamento para auditoria e revisão de qualidade já foi registrado em `c58ad3b`; esta comunicação não é apresentada como alteração formal publicada no enunciado de referência. Permanecem preservadas as decisões arquiteturais, as justificativas técnicas e a responsabilidade de compreender a implementação.

As conclusões de TSK-8.1 a TSK-8.4 são marcos históricos registrados em `c686612` (auditoria funcional), `051ee34` (Git), `11f8529` (banco do zero) e `c58ad3b` (instalação limpa). Não constituem nova execução dessas verificações nesta atualização nem encerram a validação final após as revisões.

### TSK-8.1 — Auditoria funcional

- [x] Revisar todos os requisitos obrigatórios.
- [x] Revisar CRUD.
- [x] Revisar movimentações.
- [x] Revisar consultas.
- [x] Revisar erros.
- [x] Revisar documentação.

### TSK-8.2 — Auditoria Git

- [x] Revisar Conventional Commits.
- [x] Confirmar progresso incremental real.
- [x] Confirmar ausência de segredos no histórico.
- [x] Confirmar working tree limpa.

### TSK-8.3 — Auditoria e reconstrução de banco

- [x] Criar banco do zero.
- [x] Aplicar migrations do zero.
- [x] Confirmar funcionamento sem estado local prévio.

### TSK-8.4 — Simulação de instalação limpa

- [x] Clonar o repositório em ambiente limpo.
- [x] Seguir somente o README.
- [x] Configurar aplicação.
- [x] Executar migrations.
- [x] Iniciar servidor.
- [x] Executar testes.

### TSK-8.5 — Revisão Final de Qualidade e Conformidade com o Barema

Substitui a preparação para apresentação oral, concentrando o esforço na auditoria técnica e editorial minuciosa de cada arquivo entregue, executada sob o método rigoroso de **um arquivo por vez** (diagnóstico, proposta de alteração, correção, verificação, relatório individual e aprovação do desenvolvedor).

- [~] Revisão integral da documentação do projeto.
- [~] Revisão minuciosa dos comentários de código.
- [x] Alinhamento das informações documentadas com a implementação real nos arquivos revisados.
- [x] Consistência dos schemas Pydantic e endpoints FastAPI cobertos pelas auditorias OpenAPI.
- [x] Revisão do tratamento de erros e respostas HTTP.
- [x] Verificação específica do mecanismo de logging operacional e seus testes.
- [~] Verificação de boas práticas e qualidade de código.
- [x] Preservação das regras transacionais e isolamento de concorrência nas revisões executadas.
- [x] Auditoria das referências à autoria técnica e ao apoio de ferramentas de IA.
- [x] Verificação de conformidade com a cópia de referência disponível, de versão não confirmada.
- [x] Relatório consolidado da revisão de qualidade — versionado em `b796344`.
- [~] Validação final da suíte de testes e integridade do Git — concluída para `b796344`; alterações posteriores exigem validação própria.

A revisão integral da documentação abrangeu `README.md`, `docs/DECISIONS.md`, `docs/DOMAIN_MODELING.md`, este plano e o enunciado de referência, com consolidação versionada em `b796344`. A revisão minuciosa de comentários continua parcial: comentários relevantes a transações, autenticação, erros e logging foram inspecionados, mas não houve uma auditoria linha a linha de comentários em todos os arquivos do repositório.

O logging verificado distingue três eventos: `stock_movement_completed` em `INFO` após commit e refresh; `stock_exit_rejected_insufficient_stock` em `WARNING` antes do 409; e `unhandled_exception` em `ERROR` pelo handler global. Os dois primeiros são eventos operacionais; o terceiro registra falhas inesperadas. Esses registros usam `LogRecord.extra` com formatter textual, não logging JSON, não possuem promessa de sanitização universal e não substituem o histórico de movimentações persistido no PostgreSQL.

#### Revisões registradas e evidências

Os commits abaixo registram as revisões individuais já incorporadas. Sua conclusão não implica encerramento da revisão integral nem elimina os ajustes residuais identificados.

| Arquivo | Revisão registrada | Evidência Git |
|---|---|---|
| `docs/DECISIONS.md` | Resolução de PEND-007 e atualização da DEC-034 com o estado real da CLI. | `2d0277f` |
| `docs/DOMAIN_MODELING.md` | Sincronização geral e correção do vínculo histórico direto de fornecedor. | `e362010`, `c7edc0d` |
| `docs/PROJECT_PLAN.md` | Redirecionamento da revisão final, atualização de prazo e consolidação das evidências de entrega. | `c58ad3b`, `432e9d5`, `b796344` |
| `app/exceptions.py` | Contexto de requisição nos logs de exceções inesperadas. | `d2f643c` |
| `app/main.py` | Configuração do logging da aplicação. | `e5e3752` |
| `app/security/auth.py` | Simplificação do uso da sessão na autenticação. | `41154d3` |
| `app/security/jwt.py` | Exigência de `sub` e `exp` e rejeição de `sub` vazio. | `45d546e` |
| `tests/test_auth.py` | Ampliação dos testes JWT e dos contratos de falhas de login, incluindo hash não reconhecido. | `d7dcf98`, `a831afc` |
| `app/security/passwords.py` | Esclarecimento dos contratos de hashing e verificação. | `a507b0d` |
| `app/schemas/produto.py` | Revisão 15.1: restrições e exemplos dos preços `Decimal`. | `e9506c5` |
| `app/routers/movimentacoes.py` | Revisões 15.2 e 16.1: OpenAPI das movimentações e logging operacional. | `e844dbd` |
| `tests/test_movimentacoes.py` | Revisão 16.2: quatro cenários do logging operacional. | `c450970` |
| `app/routers/produtos.py` | Revisão 19: documentação OpenAPI das seis operações. | `9343023` |
| `app/routers/categorias.py` | Revisão 20: documentação OpenAPI das cinco operações. | `d9bebc4` |
| `app/routers/fornecedores.py` | Revisão 21: documentação OpenAPI das cinco operações. | `12e289d` |
| `app/routers/auth.py` | Tipagem do login e Revisão 22 da documentação OpenAPI pública. | `0176e5c`, `081a607` |
| `README.md` | Revisões de instalação, autenticação, logging, testes e referência do desafio. | `770ec94`, `c59b90b` |

#### Pendências verificadas e critérios de encerramento

- [x] PEND-007 e DEC-034 reconciliadas em `docs/DECISIONS.md` por `2d0277f`, preservando contexto e registrando a implementação efetiva.
- [x] Responsabilidade histórica direta de `MovimentacaoEstoque.fornecedor_id` corrigida em `docs/DOMAIN_MODELING.md` por `c7edc0d`.
- [x] OpenAPI auditado por router: 12 caminhos, 22 operações, schemas, parâmetros, respostas, exemplos, papéis, filtros, login público e headers 401 pertinentes; revisões 15.1, 15.2 e 19–22 publicadas e consolidadas em `b796344`. Esta revisão final expressa complementa os exemplos HTTP 200 de `GET /` e `GET /health`; sua rastreabilidade pertence ao commit que contiver esta versão do arquivo, sem antecipação de hash.
- [x] Logging de estoque auditado e testado: sucessos em `INFO`, rejeição por regra em `WARNING` e falhas inesperadas em `ERROR`, sem confusão com o histórico persistido.
- [x] Suíte completa aprovada no CI de `b796344`: `105 passed, 12 warnings in 9.10s`, com a coleção preservada desde `c450970`.
- [ ] Revalidar instalação limpa seguindo o README atualizado e aplicar as migrations do zero: `9a91e5d24c23` (schema inicial) → `13056bc612e1` (usuários). A cadeia está presente no repositório; sua reaplicação não foi executada nesta atualização documental.
- [x] CI, remoto público, `main`, links e consistência documental foram conferidos para `b796344`. O processo de entrega deve repetir a conferência para o SHA efetivamente submetido.

#### Critérios de Avaliação do Barema (Registro Histórico para Verificação):

Os pesos e a interpretação de pontuação abaixo são preservados do planejamento registrado em `c58ad3b`. A divergência com a cópia de referência disponível é explicitada sem reescrever silenciosamente o registro histórico. Este documento não estima nota final nem comprova quais pesos são oficialmente vigentes.

##### A. Interpretação histórica registrada

Interpretação histórica: os critérios obrigatórios totalizariam 10 pontos; os diferenciais avaliados (até 2 pontos adicionais) poderiam compensar eventuais deduções pontuais nos itens obrigatórios, respeitado o teto máximo de 10 pontos da avaliação geral.

- **Documentação e comentários (1 ponto):** Clareza técnica, README completo, registro explícito de decisões e comentários de código fundamentados.
- **CRUD de entidades (2 pontos):** Integridade e regras de negócio de Categorias, Fornecedores e Produtos, incluindo unicidade e integridade referencial.
- **Consultas avançadas (2 pontos):** Filtro de estoque mínimo e histórico de movimentações por período e fornecedor.
- **Tratamento de erros e logging (2 pontos):** Respostas semânticas padronizadas, blindagem de detalhes internos sensíveis e registro adequado de logs no servidor (requer avaliação específica nos módulos de produção).
- **Commits padronizados (1 ponto):** Rastreabilidade e evolução incremental através de Conventional Commits.
- **Qualidade de código (2 pontos):** Estrutura limpa, tipagem consistente, ausência de abstrações prematuras e separação clara de responsabilidades.
- **Diferenciais avaliados (até 2 pontos):**
  - Autenticação e autorização RBAC via JWT (até 1 ponto).
  - Testes automatizados abrangentes com pytest (até 1 ponto).

##### B. Pesos presentes no enunciado de referência disponível

A cópia em `docs/referencias/prosel-2026.2/desafio-tecnico-backend-prosel-2026.2.md` distribui **8 pontos básicos**: Documentação e Comentários (1), CRUD (1), Consultas Avançadas (1), Tratamento de Erros e Logging (2), Commits Padronizados (1) e Qualidade de Código (2). Os diferenciais somam **até 2 pontos extras**: Autenticação e Segurança (0,5), Testes Automatizados (0,5) e Concorrência (1). O máximo geral indicado é 10.

##### C. Limite da evidência

Essa cópia foi obtida de terceiro e sua versão não foi confirmada como a vigente. A interpretação histórica e os pesos da referência permanecem separados; não há confirmação oficial adicional nesta revisão.

---

## 12. Entrega

Data limite vigente: **24/10/2026**, conforme comunicação posterior ao desenvolvedor. Prazo original preservado para rastreabilidade: **16/10/2026** (ver seção 1).

- [x] Confirmar repositório público e acessível em `https://github.com/cleidson21/stockflow-api`.
- [x] Confirmar branch `main` sincronizada na consolidação `b796344`.
- [x] Confirmar README revisado e versionado (`770ec94`, `c59b90b`).
- [x] Confirmar OpenAPI gerável com 12 caminhos, 22 operações e exemplos representativos; os exemplos HTTP 200 de `GET /` e `GET /health` foram complementados nesta revisão final expressa.
- [x] Confirmar ausência de `.env`, bancos locais e credenciais reais identificáveis entre os arquivos rastreados; isso não constitui garantia universal contra todo segredo possível.
- [x] Confirmar migrations `9a91e5d24c23` e `13056bc612e1`, aplicadas pelo CI de `b796344`.
- [x] Confirmar workflow **Tests** `39792984284` aprovado em `b796344`: `105 passed, 12 warnings in 9.10s`.
- [x] Confirmar integridade do histórico Git e presença de Conventional Commits até `b796344`.
- [ ] Confirmar, no momento da submissão, o SHA final e o CI correspondente.
- [ ] Enviar link do repositório conforme instruções do desafio.

O CI aprovado não equivale à submissão formal. O envio do link permanece aberto até confirmação expressa do desenvolvedor.

---

## 13. Princípio de execução

O desenvolvedor conduziu a implementação do StockFlow API, atuando como o principal responsável pelas decisões técnicas, pela arquitetura e pela validação das alterações. Ferramentas de IA foram utilizadas como apoio ao desenvolvimento, à revisão técnica e à organização da documentação.

Nenhuma tarefa deve ser marcada como concluída sem validação efetiva. Uma tarefa somente é considerada concluída quando:

1. a implementação ou alteração foi inspecionada e revisada pelo desenvolvedor;
2. a conformidade foi validada de acordo com o escopo da tarefa (execução de testes automatizados para alterações de código; verificação de integridade, formatação e rastreabilidade para alterações exclusivamente documentais);
3. as decisões técnicas, regras de negócio e estrutura adotadas foram compreendidas e podem ser fundamentadas tecnicamente;
4. as modificações atendem aos critérios de qualidade e não introduzem inconsistências com os demais documentos e componentes do projeto;
5. o estado do Git foi auditado (verificação de status e diff, sem arquivos temporários ou alterações não intencionais);
6. a alteração está pronta para um commit semântico independente.
