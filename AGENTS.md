# AGENTS.md

## 1. Project Overview

StockFlow API is a Back-End academic technical challenge focused on inventory management.

The application will provide a REST API for managing products, suppliers, categories and stock movements.

The project must prioritize correctness, readability, traceability and the developer's understanding of every implemented technical decision.

## 2. Mandatory Technologies

The application must use:

- Python
- FastAPI
- PostgreSQL

SQLAlchemy will be used for database communication and Alembic for database schema migrations.

Do not replace the mandatory technologies without explicit authorization.

## 3. Core Domain

The main entities are:

- Product
- Supplier
- Category
- Stock Movement

Mandatory domain requirements include:

### Product

At minimum:

- id
- name
- unique SKU/code
- cost price
- sale price
- stock quantity
- registration date

Additional fields may only be introduced when they serve an identified business requirement.

### Supplier

At minimum:

- id
- name
- unique CNPJ
- phone
- unique email

### Category

At minimum:

- id
- unique name

### Stock Movement

At minimum:

- id
- type (entry or exit)
- quantity
- date

Stock movements are audit records and are immutable.

After creation, a stock movement must not be editable or deletable through the API.

Creating a stock movement must update the corresponding available stock according to the business rules.

## 4. Business Rules

Business rules must be treated as first-class application requirements.

Important examples include:

- A product SKU must be unique.
- Supplier CNPJ must be unique.
- Supplier email must be unique.
- Category name must be unique.
- Stock movements must remain immutable.
- Stock movements must correctly affect available stock.
- Invalid operations must not leave the database in an inconsistent state.
- Category deletion must consider products associated with that category.
- The API must support identifying products at or below minimum stock.
- Stock movement history must support useful filtering, including period and supplier when applicable.

When a requirement is ambiguous, do not silently invent a business rule. Report the ambiguity and request a decision.

## 5. Development Approach

Work incrementally.

Each task must be small enough to be understood, reviewed and tested independently.

Before modifying code:

1. Inspect the relevant existing files.
2. Explain briefly what will be changed and why.
3. Restrict changes to the current requested task.

After modifying code:

1. Report every file created or changed.
2. Explain the important implementation decisions.
3. Explain how the change can be tested.
4. Mention any assumptions made.
5. Mention any remaining risks or unresolved decisions.

Do not implement future phases merely because they appear logically related to the current task.

Avoid unnecessary abstractions and premature architecture.

Prefer the simplest structure that satisfies the current requirements while remaining maintainable.

## 6. Learning and Technical Defense

This project includes a technical defense.

Code must therefore be understandable and defensible by the developer.

When introducing an important concept, explain:

- what it is;
- why it is being used;
- what problem it solves;
- relevant alternatives when appropriate;
- consequences of the chosen approach.

Do not generate large unexplained blocks of code.

Do not hide important business logic behind unnecessary abstraction.

## 7. Code Quality

Prefer clear and explicit code over clever code.

Use meaningful names.

Use type annotations where appropriate.

Keep responsibilities separated when that improves clarity.

Avoid duplicated business logic.

Code should explain what it does.

Comments should primarily explain why a non-obvious decision exists, especially for:

- business rules;
- database transactions;
- concurrency control;
- architectural decisions;
- unusual implementation constraints.

Do not add comments that merely repeat obvious code behavior.

## 8. Database Integrity

Database integrity is a critical requirement.

Operations involving multiple dependent changes must be evaluated for transactional consistency.

Stock updates and creation of stock movement audit records must not result in partial state.

Do not introduce database behavior that can produce negative or inconsistent stock without explicitly addressing the relevant business rule.

Concurrency strategies must not be introduced casually. When the project reaches that phase, explain the chosen locking or transaction strategy before implementation.

## 9. API Behavior

Use appropriate HTTP semantics.

Successful operations must use appropriate 2xx responses.

Invalid requests and business-rule violations must not be returned as HTTP 200.

Resources that do not exist should use an appropriate 404 response.

Unexpected internal failures must not expose stack traces or sensitive implementation details to API clients.

Error responses should follow a consistent and understandable structure.

## 10. Documentation

Every endpoint must eventually be documented through FastAPI/OpenAPI and project documentation.

Documentation should describe:

- HTTP method;
- route;
- path parameters;
- query parameters;
- request body when applicable;
- successful responses;
- expected error responses.

Keep README.md synchronized with the actual project as the implementation evolves.

## 11. Testing

Every important business rule must be designed so that it can be tested.

Do not rely exclusively on manual testing.

Automated tests will be introduced incrementally.

Whenever implementing a feature, identify the relevant success cases, validation cases and failure cases.

Do not change production behavior merely to make a test pass.

## 12. Security and Configuration

Never commit passwords, database credentials, tokens or secrets.

Local secrets must be kept outside version control.

Use environment variables for environment-specific configuration when configuration is introduced.

Do not expose internal errors or sensitive configuration through API responses.

## 13. Git Rules

The project uses Conventional Commits.

Examples of valid prefixes include:

- feat:
- fix:
- docs:
- test:
- refactor:
- chore:
- ci:

Commits must represent meaningful incremental progress.

Do not execute git commit, git push, force push, rebase, reset or history-rewriting operations unless explicitly authorized by the developer.

Never fabricate, backdate or manipulate Git history to simulate development progress.

Before suggesting a commit, summarize the changes that would be included and propose an appropriate Conventional Commit message.

## 14. Scope Control

Do not modify files unrelated to the current task.

Do not install packages without explaining why they are required.

Do not introduce a framework, architectural pattern, dependency or infrastructure component solely because it is common in other projects.

Do not implement optional challenge differentials until the mandatory requirements are stable, unless explicitly instructed otherwise.

Do not make irreversible architectural decisions when the relevant architecture has not yet been discussed.

## 15. Interaction Rule

If the requested task can be completed safely and unambiguously, execute it within the defined scope.

If an important requirement or architectural decision is ambiguous, stop before implementing that decision and explain the available options.

The browser ChatGPT conversation is being used as the project's planning and architectural control point. Major architecture and business-rule decisions should therefore remain explicit rather than being silently chosen by the coding agent.
