from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.fornecedor import Fornecedor
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.auth import require_roles
from app.models.usuario import Role

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

def validar_relacionamentos(db: Session, categoria_id: int, fornecedor_id: int):
    if not db.get(Categoria, categoria_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    if not db.get(Fornecedor, fornecedor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )

@router.post(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
    description=(
        "Cria um produto. Requer autenticação com papel `ADMIN`. O SKU deve ser "
        "único, e `categoria_id` e `fornecedor_id` devem identificar registros "
        "existentes. Todo produto nasce com `quantidade_em_estoque=0`; esse saldo "
        "não integra o corpo de criação e somente pode ser alterado por "
        "movimentações. As restrições dos preços decimais estão descritas no "
        "schema do corpo da requisição."
    ),
    responses={
        201: {
            "model": ProdutoResponse,
            "description": "Produto criado com saldo inicial igual a zero.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Teclado Mecânico",
                        "sku": "TEC-MEC-001",
                        "preco_custo": "100.00",
                        "preco_venda": "150.00",
                        "estoque_minimo": 5,
                        "categoria_id": 2,
                        "fornecedor_id": 3,
                        "id": 7,
                        "quantidade_em_estoque": 0,
                        "data_cadastro": "2026-10-21T12:30:00Z"
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token ausente, inválido ou expirado.",
            "headers": {
                "WWW-Authenticate": {
                    "description": "Esquema de autenticação exigido.",
                    "schema": {"type": "string", "example": "Bearer"}
                }
            },
            "content": {
                "application/json": {
                    "example": {
                        "status": 401,
                        "error": "unauthorized",
                        "message": "Credenciais inválidas.",
                        "details": None
                    }
                }
            }
        },
        403: {
            "model": ErrorResponse,
            "description": "Usuário autenticado sem papel ADMIN.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 403,
                        "error": "forbidden",
                        "message": "Você não possui permissão para executar esta operação.",
                        "details": None
                    }
                }
            }
        },
        404: {
            "model": ErrorResponse,
            "description": "Categoria ou fornecedor informado não encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "error": "not_found",
                        "message": "Categoria não encontrada.",
                        "details": None
                    }
                }
            }
        },
        409: {
            "model": ErrorResponse,
            "description": (
                "SKU duplicado ou referência removida concorrentemente antes da "
                "persistência."
            ),
            "content": {
                "application/json": {
                    "examples": {
                        "sku_duplicado": {
                            "summary": "SKU já cadastrado",
                            "value": {
                                "status": 409,
                                "error": "conflict",
                                "message": "Já existe um produto com este SKU.",
                                "details": None
                            }
                        },
                        "referencia_invalida": {
                            "summary": "Relacionamento removido concorrentemente",
                            "value": {
                                "status": 409,
                                "error": "conflict",
                                "message": "Referência inválida para categoria ou fornecedor.",
                                "details": None
                            }
                        }
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": (
                "Corpo inválido, inclusive campo controlado pelo servidor ou "
                "preço fora das restrições do schema."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["body", "quantidade_em_estoque"],
                                "msg": "Extra inputs are not permitted",
                                "type": "extra_forbidden"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 500,
                        "error": "internal_error",
                        "message": "Erro interno do servidor.",
                        "details": None
                    }
                }
            }
        }
    }
)
def criar_produto(produto_in: ProdutoCreate, db: Session = Depends(get_db)):
    validar_relacionamentos(db, produto_in.categoria_id, produto_in.fornecedor_id)
    
    novo_produto = Produto(
        nome=produto_in.nome,
        sku=produto_in.sku,
        preco_custo=produto_in.preco_custo,
        preco_venda=produto_in.preco_venda,
        estoque_minimo=produto_in.estoque_minimo,
        categoria_id=produto_in.categoria_id,
        fornecedor_id=produto_in.fornecedor_id
    )
    
    db.add(novo_produto)
    try:
        db.commit()
        db.refresh(novo_produto)
        return novo_produto
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate"):
            if e.orig.sqlstate == "23505":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um produto com este SKU."
                )
            elif e.orig.sqlstate == "23503":
                # Condição de corrida onde categoria ou fornecedor foi apagado concorrentemente
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Referência inválida para categoria ou fornecedor."
                )
        raise e

@router.get(
    "/consultas/estoque-minimo",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[ProdutoResponse],
    summary="Listar produtos no estoque mínimo",
    description=(
        "Retorna, para usuários `ADMIN` ou `FUNCIONARIO`, os produtos cuja "
        "`quantidade_em_estoque` é menor ou igual a `estoque_minimo`, incluindo "
        "os produtos exatamente no limite. Uma consulta válida sem resultados "
        "retorna `200` com `[]`."
    ),
    responses={
        200: {
            "description": "Produtos no limite ou abaixo dele; pode ser uma lista vazia.",
            "content": {
                "application/json": {
                    "examples": {
                        "no_limite": {
                            "summary": "Produto exatamente no estoque mínimo",
                            "value": [
                                {
                                    "nome": "Teclado Mecânico",
                                    "sku": "TEC-MEC-001",
                                    "preco_custo": "100.00",
                                    "preco_venda": "150.00",
                                    "estoque_minimo": 5,
                                    "categoria_id": 2,
                                    "fornecedor_id": 3,
                                    "id": 7,
                                    "quantidade_em_estoque": 5,
                                    "data_cadastro": "2026-10-21T12:30:00Z"
                                }
                            ]
                        },
                        "sem_resultados": {
                            "summary": "Consulta válida sem resultados",
                            "value": []
                        }
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token ausente, inválido ou expirado.",
            "headers": {
                "WWW-Authenticate": {
                    "description": "Esquema de autenticação exigido.",
                    "schema": {"type": "string", "example": "Bearer"}
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos."
        }
    }
)
def listar_produtos_estoque_minimo(db: Session = Depends(get_db)):
    stmt = select(Produto).where(Produto.quantidade_em_estoque <= Produto.estoque_minimo).order_by(Produto.id)
    return db.scalars(stmt).all()

@router.get(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[ProdutoResponse],
    summary="Listar produtos",
    description=(
        "Lista os produtos cadastrados para usuários `ADMIN` ou `FUNCIONARIO`. "
        "O saldo retornado é mantido pelas movimentações de estoque; os fluxos "
        "de criação e atualização de produto não o alteram. Uma listagem sem "
        "produtos retorna `200` com `[]`."
    ),
    responses={
        200: {
            "description": "Produtos cadastrados; pode ser uma lista vazia.",
            "content": {
                "application/json": {
                    "examples": {
                        "produtos": {
                            "summary": "Lista de produtos",
                            "value": [
                                {
                                    "nome": "Teclado Mecânico",
                                    "sku": "TEC-MEC-001",
                                    "preco_custo": "100.00",
                                    "preco_venda": "150.00",
                                    "estoque_minimo": 5,
                                    "categoria_id": 2,
                                    "fornecedor_id": 3,
                                    "id": 7,
                                    "quantidade_em_estoque": 12,
                                    "data_cadastro": "2026-10-21T12:30:00Z"
                                }
                            ]
                        },
                        "sem_resultados": {
                            "summary": "Listagem sem produtos",
                            "value": []
                        }
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token ausente, inválido ou expirado.",
            "headers": {
                "WWW-Authenticate": {
                    "description": "Esquema de autenticação exigido.",
                    "schema": {"type": "string", "example": "Bearer"}
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos."
        }
    }
)
def listar_produtos(db: Session = Depends(get_db)):
    stmt = select(Produto).order_by(Produto.id)
    return db.scalars(stmt).all()

@router.get(
    "/{produto_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=ProdutoResponse,
    summary="Buscar produto por ID",
    description=(
        "Retorna um produto pelo identificador inteiro para usuários `ADMIN` ou "
        "`FUNCIONARIO`. Produto inexistente retorna `404`; um identificador que "
        "não seja inteiro retorna `422`."
    ),
    responses={
        200: {
            "model": ProdutoResponse,
            "description": "Produto encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Teclado Mecânico",
                        "sku": "TEC-MEC-001",
                        "preco_custo": "100.00",
                        "preco_venda": "150.00",
                        "estoque_minimo": 5,
                        "categoria_id": 2,
                        "fornecedor_id": 3,
                        "id": 7,
                        "quantidade_em_estoque": 12,
                        "data_cadastro": "2026-10-21T12:30:00Z"
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token ausente, inválido ou expirado.",
            "headers": {
                "WWW-Authenticate": {
                    "description": "Esquema de autenticação exigido.",
                    "schema": {"type": "string", "example": "Bearer"}
                }
            }
        },
        404: {
            "model": ErrorResponse,
            "description": "Produto não encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "error": "not_found",
                        "message": "Produto não encontrado.",
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "produto_id não é um inteiro válido.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["path", "produto_id"],
                                "msg": "Input should be a valid integer, unable to parse string as an integer",
                                "type": "int_parsing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos."
        }
    }
)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    return produto

@router.put(
    "/{produto_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=ProdutoResponse,
    summary="Atualizar produto",
    description=(
        "Substitui os campos editáveis de um produto e requer papel `ADMIN`. O "
        "corpo completo definido por `ProdutoUpdate` é obrigatório; esta operação "
        "não possui semântica de PATCH. O SKU permanece único, e `categoria_id` e "
        "`fornecedor_id` devem existir. A atualização não recebe nem altera "
        "`quantidade_em_estoque`, que continua controlada exclusivamente por "
        "movimentações."
    ),
    responses={
        200: {
            "model": ProdutoResponse,
            "description": "Produto atualizado; o saldo existente é preservado.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Teclado Mecânico Atualizado",
                        "sku": "TEC-MEC-001",
                        "preco_custo": "110.00",
                        "preco_venda": "160.00",
                        "estoque_minimo": 8,
                        "categoria_id": 2,
                        "fornecedor_id": 3,
                        "id": 7,
                        "quantidade_em_estoque": 12,
                        "data_cadastro": "2026-10-21T12:30:00Z"
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token ausente, inválido ou expirado.",
            "headers": {
                "WWW-Authenticate": {
                    "description": "Esquema de autenticação exigido.",
                    "schema": {"type": "string", "example": "Bearer"}
                }
            }
        },
        403: {
            "model": ErrorResponse,
            "description": "Usuário autenticado sem papel ADMIN."
        },
        404: {
            "model": ErrorResponse,
            "description": "Produto, categoria ou fornecedor não encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "error": "not_found",
                        "message": "Produto não encontrado.",
                        "details": None
                    }
                }
            }
        },
        409: {
            "model": ErrorResponse,
            "description": (
                "SKU duplicado ou referência removida concorrentemente antes da "
                "persistência."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "status": 409,
                        "error": "conflict",
                        "message": "Já existe um produto com este SKU.",
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Corpo incompleto ou inválido.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["body", "nome"],
                                "msg": "Field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos."
        }
    }
)
def atualizar_produto(produto_id: int, produto_in: ProdutoUpdate, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    validar_relacionamentos(db, produto_in.categoria_id, produto_in.fornecedor_id)
    
    produto.nome = produto_in.nome
    produto.sku = produto_in.sku
    produto.preco_custo = produto_in.preco_custo
    produto.preco_venda = produto_in.preco_venda
    produto.estoque_minimo = produto_in.estoque_minimo
    produto.categoria_id = produto_in.categoria_id
    produto.fornecedor_id = produto_in.fornecedor_id
    
    try:
        db.commit()
        db.refresh(produto)
        return produto
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate"):
            if e.orig.sqlstate == "23505":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Já existe um produto com este SKU."
                )
            elif e.orig.sqlstate == "23503":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Referência inválida para categoria ou fornecedor."
                )
        raise e

@router.delete(
    "/{produto_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir produto",
    description=(
        "Exclui um produto e requer papel `ADMIN`. Retorna `204` sem corpo quando "
        "a exclusão é concluída. Produto inexistente retorna `404`; um produto com "
        "movimentações históricas relacionadas não pode ser removido e retorna "
        "`409`."
    ),
    responses={
        204: {"description": "Produto excluído com sucesso; resposta sem corpo."},
        401: {
            "model": ErrorResponse,
            "description": "Token ausente, inválido ou expirado.",
            "headers": {
                "WWW-Authenticate": {
                    "description": "Esquema de autenticação exigido.",
                    "schema": {"type": "string", "example": "Bearer"}
                }
            }
        },
        403: {
            "model": ErrorResponse,
            "description": "Usuário autenticado sem papel ADMIN."
        },
        404: {
            "model": ErrorResponse,
            "description": "Produto não encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "error": "not_found",
                        "message": "Produto não encontrado.",
                        "details": None
                    }
                }
            }
        },
        409: {
            "model": ErrorResponse,
            "description": "Produto possui movimentações históricas relacionadas.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 409,
                        "error": "conflict",
                        "message": (
                            "O produto não pode ser removido pois possui "
                            "movimentações relacionadas."
                        ),
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "produto_id não é um inteiro válido.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["path", "produto_id"],
                                "msg": "Input should be a valid integer, unable to parse string as an integer",
                                "type": "int_parsing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos."
        }
    }
)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    
    try:
        from sqlalchemy import delete
        stmt = delete(Produto).where(Produto.id == produto_id)
        db.execute(stmt)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O produto não pode ser removido pois possui movimentações relacionadas."
            )
        raise e
