import logging
from typing import Annotated, List, Optional
from pydantic import AwareDatetime
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.produto import Produto
from app.models.movimentacao import MovimentacaoEstoque
from app.models.fornecedor import Fornecedor
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoResponse, TipoMovimentacao
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.auth import require_roles
from app.models.usuario import Role

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações"]
)

@router.post(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=MovimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimentação de estoque",
    description=(
        "Registra uma movimentação de estoque. Requer autenticação com papel "
        "`ADMIN` ou `FUNCIONARIO`. `ENTRADA` acrescenta a quantidade ao saldo e "
        "`SAIDA` a desconta; a quantidade deve ser positiva e uma saída sem saldo "
        "suficiente retorna `409`. A data é gerada pelo servidor e `fornecedor_id` "
        "registra o fornecedor cadastrado no produto no momento da movimentação. "
        "A atualização do saldo e o registro da movimentação são persistidos na "
        "mesma transação. Essa garantia não abrange todas as falhas de concorrência "
        "possíveis."
    ),
    responses={
        201: {
            "model": MovimentacaoResponse,
            "description": "Movimentação criada e saldo do produto atualizado.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 101,
                        "tipo": "ENTRADA",
                        "quantidade": 25,
                        "data": "2026-10-20T12:30:00Z",
                        "produto_id": 7,
                        "fornecedor_id": 3
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
        404: {
            "model": ErrorResponse,
            "description": "Produto informado não encontrado.",
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
            "description": "Estoque insuficiente para a saída solicitada.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 409,
                        "error": "conflict",
                        "message": "Estoque insuficiente para a saída solicitada.",
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Corpo inválido, inclusive quantidade não positiva.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["body", "quantidade"],
                                "msg": "Input should be greater than 0",
                                "type": "greater_than"
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
def criar_movimentacao(
    mov_in: Annotated[
        MovimentacaoCreate,
        Body(
            openapi_examples={
                "entrada": {
                    "summary": "Entrada de estoque",
                    "value": {
                        "produto_id": 7,
                        "tipo": "ENTRADA",
                        "quantidade": 25
                    }
                },
                "saida": {
                    "summary": "Saída de estoque",
                    "value": {
                        "produto_id": 7,
                        "tipo": "SAIDA",
                        "quantidade": 4
                    }
                }
            }
        )
    ],
    db: Session = Depends(get_db)
):
    try:
        stmt = select(Produto).where(Produto.id == mov_in.produto_id).with_for_update()
        produto = db.scalars(stmt).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )
        
        if mov_in.tipo == TipoMovimentacao.ENTRADA:
            produto.quantidade_em_estoque += mov_in.quantidade
        elif mov_in.tipo == TipoMovimentacao.SAIDA:
            if mov_in.quantidade > produto.quantidade_em_estoque:
                logger.warning(
                    "Saída de estoque rejeitada por saldo insuficiente | "
                    "event_type=%s product_id=%s requested_quantity=%s available_quantity=%s",
                    "stock_exit_rejected_insufficient_stock",
                    produto.id,
                    mov_in.quantidade,
                    produto.quantidade_em_estoque,
                    extra={
                        "event_type": "stock_exit_rejected_insufficient_stock",
                        "product_id": produto.id,
                        "requested_quantity": mov_in.quantidade,
                        "available_quantity": produto.quantidade_em_estoque,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Estoque insuficiente para a saída solicitada."
                )
            produto.quantidade_em_estoque -= mov_in.quantidade
            
        nova_movimentacao = MovimentacaoEstoque(
            tipo=mov_in.tipo.value,
            quantidade=mov_in.quantidade,
            produto_id=produto.id,
            fornecedor_id=produto.fornecedor_id
        )
        db.add(nova_movimentacao)
        db.commit()
        
        db.refresh(nova_movimentacao)
        logger.info(
            "Movimentação de estoque concluída | "
            "event_type=%s movement_id=%s movement_type=%s product_id=%s "
            "supplier_id=%s quantity=%s",
            "stock_movement_completed",
            nova_movimentacao.id,
            nova_movimentacao.tipo,
            nova_movimentacao.produto_id,
            nova_movimentacao.fornecedor_id,
            nova_movimentacao.quantidade,
            extra={
                "event_type": "stock_movement_completed",
                "movement_id": nova_movimentacao.id,
                "movement_type": nova_movimentacao.tipo,
                "product_id": nova_movimentacao.produto_id,
                "supplier_id": nova_movimentacao.fornecedor_id,
                "quantity": nova_movimentacao.quantidade,
            },
        )
        return nova_movimentacao
    except IntegrityError as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise e




@router.get(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[MovimentacaoResponse],
    summary="Listar histórico de movimentações",
    description=(
        "Retorna o histórico de movimentações para usuários `ADMIN` ou "
        "`FUNCIONARIO`. Os filtros `data_inicio`, `data_fim` e `fornecedor_id` são "
        "opcionais e podem ser combinados. Os limites de data são inclusivos e "
        "exigem timezone; um intervalo invertido retorna `400`. O filtro por "
        "fornecedor usa a referência histórica gravada na movimentação, não o "
        "fornecedor atualmente cadastrado no produto. Fornecedor inexistente "
        "retorna `404`; uma consulta válida sem resultados retorna `200` com `[]`."
    ),
    responses={
        200: {
            "description": "Histórico filtrado; pode ser uma lista vazia.",
            "content": {
                "application/json": {
                    "examples": {
                        "historico": {
                            "summary": "Entrada e saída no período",
                            "value": [
                                {
                                    "id": 101,
                                    "tipo": "ENTRADA",
                                    "quantidade": 25,
                                    "data": "2026-10-20T12:30:00Z",
                                    "produto_id": 7,
                                    "fornecedor_id": 3
                                },
                                {
                                    "id": 102,
                                    "tipo": "SAIDA",
                                    "quantidade": 4,
                                    "data": "2026-10-20T15:45:00Z",
                                    "produto_id": 7,
                                    "fornecedor_id": 3
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
        400: {
            "model": ErrorResponse,
            "description": "data_inicio é posterior a data_fim.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 400,
                        "error": "bad_request",
                        "message": "data_inicio não pode ser posterior a data_fim.",
                        "details": None
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
            "description": "Fornecedor informado não encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "error": "not_found",
                        "message": "Fornecedor não encontrado.",
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Filtro inválido, inclusive data sem timezone.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["query", "data_inicio"],
                                "msg": "Input should have timezone info",
                                "type": "timezone_aware"
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
def listar_movimentacoes(
    db: Session = Depends(get_db),
    data_inicio: Annotated[
        Optional[AwareDatetime],
        Query(
            description=(
                "Limite inicial inclusivo do período. Deve ser uma data e hora ISO 8601 "
                "com timezone explícito."
            ),
            examples=["2026-10-01T00:00:00Z"]
        )
    ] = None,
    data_fim: Annotated[
        Optional[AwareDatetime],
        Query(
            description=(
                "Limite final inclusivo do período. Deve ser uma data e hora ISO 8601 "
                "com timezone explícito."
            ),
            examples=["2026-10-31T23:59:59-03:00"]
        )
    ] = None,
    fornecedor_id: Annotated[
        Optional[int],
        Query(
            description=(
                "Identificador do fornecedor histórico registrado na movimentação; "
                "não consulta o fornecedor atual do produto."
            ),
            examples=[3]
        )
    ] = None
):
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="data_inicio não pode ser posterior a data_fim."
        )

    stmt = select(MovimentacaoEstoque)

    if fornecedor_id is not None:
        if not db.get(Fornecedor, fornecedor_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor não encontrado."
            )
        stmt = stmt.where(MovimentacaoEstoque.fornecedor_id == fornecedor_id)

    if data_inicio:
        stmt = stmt.where(MovimentacaoEstoque.data >= data_inicio)
    if data_fim:
        stmt = stmt.where(MovimentacaoEstoque.data <= data_fim)

    stmt = stmt.order_by(MovimentacaoEstoque.id)
    return db.scalars(stmt).all()

@router.get(
    "/{movimentacao_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=MovimentacaoResponse,
    summary="Buscar movimentação por ID",
    description=(
        "Retorna uma movimentação quando o identificador inteiro obrigatório é "
        "encontrado. Requer autenticação com papel `ADMIN` ou `FUNCIONARIO`. "
        "Movimentações compõem um histórico imutável e não possuem operações de "
        "edição ou exclusão pela API."
    ),
    responses={
        200: {
            "model": MovimentacaoResponse,
            "description": "Movimentação encontrada.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 102,
                        "tipo": "SAIDA",
                        "quantidade": 4,
                        "data": "2026-10-20T15:45:00Z",
                        "produto_id": 7,
                        "fornecedor_id": 3
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
            "description": "Movimentação não encontrada.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "error": "not_found",
                        "message": "Movimentação não encontrada.",
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "movimentacao_id não é um inteiro válido.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["path", "movimentacao_id"],
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
def buscar_movimentacao(
    movimentacao_id: Annotated[
        int,
        Path(
            description="Identificador inteiro obrigatório da movimentação.",
            examples=[102]
        )
    ],
    db: Session = Depends(get_db)
):
    movimentacao = db.get(MovimentacaoEstoque, movimentacao_id)
    if not movimentacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimentação não encontrada."
        )
    return movimentacao
