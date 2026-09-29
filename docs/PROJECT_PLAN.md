# StockFlow API — Project Plan

## 1. Objetivo

Este documento acompanha o desenvolvimento incremental do StockFlow API.

Cada tarefa deve ser concluída, compreendida, testada e revisada antes do avanço para tarefas dependentes.

O projeto deve priorizar primeiro todos os requisitos obrigatórios do desafio técnico. Os diferenciais devem ser implementados somente quando a base obrigatória estiver estável.

Prazo final de entrega: 16/10/2026.

---

## 2. Convenções de status

- [ ] Não iniciada
- [~] Em andamento
- [x] Concluída
- [!] Bloqueada ou aguardando decisão

---

## 3. Fase 0 — Fundação e Governança

Meta: preparar um repositório limpo, rastreável e adequado ao desenvolvimento assistido por IA.

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

- [ ] Entender ORM.
- [ ] Discutir abordagem síncrona versus assíncrona.
- [ ] Escolher abordagem adequada à escala do desafio.
- [ ] Configurar engine.
- [ ] Configurar sessões.
- [ ] Validar conexão.

### TSK-2.8 — Alembic

- [ ] Entender migrations.
- [ ] Inicializar Alembic.
- [ ] Integrar Alembic aos modelos.
- [ ] Criar migration inicial.
- [ ] Revisar SQL/schema gerado.
- [ ] Aplicar migration.
- [ ] Validar tabelas no PostgreSQL.

---

## 6. Fase 3 — CRUD das entidades principais

Meta: implementar gerenciamento consistente de Categoria, Fornecedor e Produto.

Período planejado: 30/09 a 03/10.

### TSK-3.1 — Categoria

- [ ] Definir modelo.
- [ ] Definir schemas de entrada e saída.
- [ ] Criar categoria.
- [ ] Listar categorias.
- [ ] Consultar categoria por id.
- [ ] Atualizar categoria.
- [ ] Excluir categoria.
- [ ] Garantir unicidade do nome.
- [ ] Tratar categoria inexistente.
- [ ] Impedir exclusão incompatível com produtos relacionados.
- [ ] Documentar endpoints.
- [ ] Testar casos principais.

### TSK-3.2 — Fornecedor

- [ ] Definir modelo.
- [ ] Definir schemas.
- [ ] Criar fornecedor.
- [ ] Listar fornecedores.
- [ ] Consultar fornecedor por id.
- [ ] Atualizar fornecedor.
- [ ] Excluir fornecedor conforme regra definida.
- [ ] Garantir CNPJ único.
- [ ] Garantir email único.
- [ ] Validar erros de duplicidade.
- [ ] Documentar endpoints.
- [ ] Testar casos principais.

### TSK-3.3 — Produto

- [ ] Definir modelo.
- [ ] Definir schemas.
- [ ] Criar produto.
- [ ] Listar produtos.
- [ ] Consultar produto por id.
- [ ] Atualizar produto.
- [ ] Excluir produto conforme regras definidas.
- [ ] Garantir SKU único.
- [ ] Validar relacionamentos.
- [ ] Validar preços e quantidades.
- [ ] Documentar endpoints.
- [ ] Testar casos principais.

### TSK-3.4 — Revisão CRUD

- [ ] Validar códigos HTTP.
- [ ] Validar respostas.
- [ ] Validar constraints no banco.
- [ ] Validar Swagger/OpenAPI.
- [ ] Revisar duplicação de lógica.
- [ ] Revisar clareza do código.

---

## 7. Fase 4 — Movimentações de Estoque

Meta: implementar o núcleo transacional do sistema.

Período planejado: 04/10 a 06/10.

### TSK-4.1 — Modelo de movimentação

- [ ] Definir campos.
- [ ] Definir relacionamento com Produto.
- [ ] Definir representação de entrada e saída.
- [ ] Definir timestamp.
- [ ] Criar migration.

### TSK-4.2 — Imutabilidade

- [ ] Implementar criação.
- [ ] Implementar consulta.
- [ ] Não disponibilizar atualização.
- [ ] Não disponibilizar exclusão.
- [ ] Confirmar que a API respeita a imutabilidade.

### TSK-4.3 — Entrada de estoque

- [ ] Validar quantidade.
- [ ] Criar movimentação.
- [ ] Incrementar estoque.
- [ ] Garantir atomicidade da operação.
- [ ] Testar sucesso e falha.

### TSK-4.4 — Saída de estoque

- [ ] Validar quantidade.
- [ ] Validar estoque disponível.
- [ ] Impedir estoque negativo.
- [ ] Criar movimentação.
- [ ] Decrementar estoque.
- [ ] Garantir atomicidade.
- [ ] Testar sucesso e falha.

### TSK-4.5 — Transações

- [ ] Entender commit.
- [ ] Entender rollback.
- [ ] Entender atomicidade.
- [ ] Garantir que estoque e histórico não possam divergir.
- [ ] Documentar a decisão transacional.

---

## 8. Fase 5 — Consultas Avançadas

Meta: implementar as consultas estratégicas exigidas pelo desafio.

Período planejado: 07/10 a 08/10.

### TSK-5.1 — Estoque mínimo

- [ ] Criar consulta de produtos no estoque mínimo.
- [ ] Incluir produtos abaixo do estoque mínimo.
- [ ] Definir endpoint e parâmetros.
- [ ] Documentar comportamento.
- [ ] Testar limites.

### TSK-5.2 — Histórico por período

- [ ] Definir parâmetros de data inicial e final.
- [ ] Validar intervalos.
- [ ] Filtrar movimentações.
- [ ] Definir comportamento sem resultados.
- [ ] Documentar endpoint.

### TSK-5.3 — Histórico por fornecedor

- [ ] Implementar filtro compatível com o modelo relacional adotado.
- [ ] Permitir combinação com período quando apropriado.
- [ ] Validar fornecedor inexistente quando aplicável.
- [ ] Documentar exemplos.

### TSK-5.4 — Consultas adicionais

- [ ] Avaliar filtros adicionais realmente úteis.
- [ ] Evitar funcionalidades sem valor para o desafio.
- [ ] Implementar somente filtros justificados.

---

## 9. Fase 6 — Tratamento de Erros e Documentação

Meta: tornar o comportamento da API consistente, seguro e compreensível.

Período planejado: 09/10 a 10/10.

### TSK-6.1 — Modelo de erro

- [ ] Definir formato padronizado.
- [ ] Definir campos da resposta.
- [ ] Diferenciar erro de validação, negócio e recurso inexistente.

### TSK-6.2 — Códigos HTTP

- [ ] Revisar 2xx.
- [ ] Revisar 400.
- [ ] Revisar 404.
- [ ] Avaliar uso de 409 para conflitos de unicidade/regra.
- [ ] Entender validação 422 do FastAPI.
- [ ] Garantir uso correto de 500.

### TSK-6.3 — Segurança dos erros

- [ ] Não retornar stack traces.
- [ ] Não expor credenciais.
- [ ] Não expor informações internas desnecessárias.
- [ ] Manter logs úteis apenas no servidor.

### TSK-6.4 — OpenAPI/Swagger

- [ ] Documentar cada endpoint.
- [ ] Documentar parâmetros.
- [ ] Documentar request bodies.
- [ ] Documentar respostas 2xx.
- [ ] Documentar respostas 4xx.
- [ ] Documentar respostas 5xx quando apropriado.
- [ ] Adicionar exemplos relevantes.

### TSK-6.5 — README

- [ ] Documentar pré-requisitos.
- [ ] Documentar configuração.
- [ ] Documentar criação do banco.
- [ ] Documentar migrations.
- [ ] Documentar execução da API.
- [ ] Documentar testes.
- [ ] Documentar acesso ao Swagger.
- [ ] Descrever arquitetura.
- [ ] Descrever principais regras de negócio.

---

## 10. Fase 7 — Testes, Qualidade e Diferenciais

Meta: consolidar a aplicação obrigatória antes de adicionar diferenciais.

Período planejado: 11/10 a 13/10.

### TSK-7.1 — Testes automatizados

- [ ] Definir estratégia de testes.
- [ ] Configurar framework.
- [ ] Criar ambiente de teste isolado.
- [ ] Testar CRUD.
- [ ] Testar unicidade.
- [ ] Testar movimentações.
- [ ] Testar estoque insuficiente.
- [ ] Testar imutabilidade.
- [ ] Testar consultas avançadas.
- [ ] Testar erros relevantes.

### TSK-7.2 — Integração contínua

- [ ] Avaliar GitHub Actions.
- [ ] Executar testes automaticamente.
- [ ] Garantir falha do workflow quando testes falharem.

### TSK-7.3 — Concorrência

- [x] Reproduzir conceitualmente a race condition.
- [x] Entender lock pessimista.
- [x] Entender lock otimista.
- [x] Analisar estratégia apropriada.
- [x] Registrar decisão antes da implementação.
- [ ] Implementar controle de concorrência.
- [ ] Testar saídas simultâneas.
- [ ] Confirmar impossibilidade de estoque negativo.

### TSK-7.4 — Autenticação e autorização

- [ ] Implementar somente se os requisitos obrigatórios estiverem estáveis.
- [ ] Discutir JWT.
- [ ] Definir modelo de usuário.
- [ ] Definir autenticação.
- [ ] Definir autorização por função se viável.
- [ ] Proteger rotas apropriadas.
- [ ] Testar acesso autorizado e não autorizado.

---

## 11. Fase 8 — Auditoria Final e Defesa Técnica

Meta: entregar um projeto que funcione e que possa ser explicado integralmente pelo desenvolvedor.

Período planejado: 14/10 a 15/10.

### TSK-8.1 — Auditoria funcional

- [ ] Revisar todos os requisitos obrigatórios.
- [ ] Revisar CRUD.
- [ ] Revisar movimentações.
- [ ] Revisar consultas.
- [ ] Revisar erros.
- [ ] Revisar documentação.

### TSK-8.2 — Auditoria Git

- [ ] Revisar Conventional Commits.
- [ ] Confirmar progresso incremental real.
- [ ] Confirmar ausência de segredos no histórico.
- [ ] Confirmar working tree limpa.

### TSK-8.3 — Auditoria de banco

- [ ] Criar banco do zero.
- [ ] Aplicar migrations do zero.
- [ ] Confirmar funcionamento sem estado local prévio.

### TSK-8.4 — Simulação de instalação

- [ ] Clonar o repositório em ambiente limpo.
- [ ] Seguir somente o README.
- [ ] Configurar aplicação.
- [ ] Executar migrations.
- [ ] Iniciar servidor.
- [ ] Executar testes.

### TSK-8.5 — Preparação da defesa

- [ ] Explicar arquitetura sem consultar código.
- [ ] Explicar modelos e relacionamentos.
- [ ] Explicar schemas.
- [ ] Explicar SQLAlchemy.
- [ ] Explicar Alembic.
- [ ] Explicar transações.
- [ ] Explicar imutabilidade das movimentações.
- [ ] Explicar tratamento de erros.
- [ ] Explicar concorrência, se implementada.
- [ ] Explicar cada dependência externa utilizada.
- [ ] Revisar principais commits e decisões.

---

## 12. Entrega

Data limite: 16/10/2026.

- [ ] Confirmar repositório acessível.
- [ ] Confirmar branch main atualizada.
- [ ] Confirmar README final.
- [ ] Confirmar Swagger funcional.
- [ ] Confirmar ausência de credenciais.
- [ ] Confirmar commit final.
- [ ] Enviar link do repositório conforme instruções do desafio.

---

## 13. Princípio de execução

Nenhuma caixa deve ser marcada como concluída apenas porque um agente de IA gerou o código.

Uma tarefa somente é considerada concluída quando:

1. a implementação foi revisada;
2. o comportamento foi validado;
3. o desenvolvedor compreende o código;
4. as decisões relevantes podem ser justificadas;
5. o estado do Git foi revisado;
6. a alteração está pronta para um commit semanticamente coerente.
