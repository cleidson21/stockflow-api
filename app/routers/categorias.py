from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.auth import require_roles
from app.models.usuario import Role

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"]
)

@router.post(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
    description=(
        "Cria uma categoria e requer autenticação com papel `ADMIN`. O nome deve "
        "ser único; uma tentativa de cadastro com nome já existente retorna `409`."
    ),
    responses={
        201: {
            "model": CategoriaResponse,
            "description": "Categoria criada com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Eletrônicos",
                        "id": 1
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
        409: {
            "model": ErrorResponse,
            "description": "Já existe uma categoria com o nome informado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 409,
                        "error": "conflict",
                        "message": "Já existe uma categoria com este nome.",
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Corpo inválido conforme o schema CategoriaCreate.",
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
def criar_categoria(categoria_in: CategoriaCreate, db: Session = Depends(get_db)):
    nova_categoria = Categoria(nome=categoria_in.nome)
    db.add(nova_categoria)
    try:
        db.commit()
        db.refresh(nova_categoria)
        return nova_categoria
    except IntegrityError as e:
        db.rollback()
        # Verificar o SQLSTATE original do driver psycopg
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma categoria com este nome."
            )
        # Se for outro IntegrityError não previsto, repassa
        raise e

@router.get(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[CategoriaResponse],
    summary="Listar categorias",
    description=(
        "Lista as categorias cadastradas para usuários `ADMIN` ou `FUNCIONARIO`. "
        "Uma consulta válida sem categorias retorna `200` com `[]`."
    ),
    responses={
        200: {
            "description": "Categorias cadastradas; pode ser uma lista vazia.",
            "content": {
                "application/json": {
                    "examples": {
                        "categorias": {
                            "summary": "Lista com categorias",
                            "value": [
                                {"nome": "Eletrônicos", "id": 1},
                                {"nome": "Móveis", "id": 2}
                            ]
                        },
                        "sem_resultados": {
                            "summary": "Listagem sem categorias",
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
def listar_categorias(db: Session = Depends(get_db)):
    stmt = select(Categoria).order_by(Categoria.id)
    resultado = db.scalars(stmt).all()
    return resultado

@router.get(
    "/{categoria_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=CategoriaResponse,
    summary="Buscar categoria por ID",
    description=(
        "Retorna uma categoria pelo identificador inteiro para usuários `ADMIN` "
        "ou `FUNCIONARIO`. Categoria inexistente retorna `404`; um identificador "
        "que não seja inteiro retorna `422`."
    ),
    responses={
        200: {
            "model": CategoriaResponse,
            "description": "Categoria encontrada.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Eletrônicos",
                        "id": 1
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
            "description": "Categoria não encontrada.",
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
        422: {
            "model": ValidationErrorResponse,
            "description": "categoria_id não é um inteiro válido.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["path", "categoria_id"],
                                "msg": (
                                    "Input should be a valid integer, unable to "
                                    "parse string as an integer"
                                ),
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
def buscar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    return categoria

@router.put(
    "/{categoria_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=CategoriaResponse,
    summary="Atualizar categoria",
    description=(
        "Substitui os campos editáveis de uma categoria e requer papel `ADMIN`. "
        "O corpo completo definido por `CategoriaUpdate` é obrigatório, e o novo "
        "nome deve permanecer único. Esta operação não possui semântica de PATCH."
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Periféricos"
                    }
                }
            }
        }
    },
    responses={
        200: {
            "model": CategoriaResponse,
            "description": "Categoria atualizada com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Periféricos",
                        "id": 1
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
            "description": "Categoria não encontrada."
        },
        409: {
            "model": ErrorResponse,
            "description": "Já existe uma categoria com o nome informado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 409,
                        "error": "conflict",
                        "message": "Já existe uma categoria com este nome.",
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Corpo completo ausente ou inválido."
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos."
        }
    }
)
def atualizar_categoria(categoria_id: int, categoria_in: CategoriaUpdate, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    
    categoria.nome = categoria_in.nome
    try:
        db.commit()
        db.refresh(categoria)
        return categoria
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma categoria com este nome."
            )
        raise e

@router.delete(
    "/{categoria_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria",
    description=(
        "Exclui uma categoria e requer papel `ADMIN`. Retorna `204` sem corpo "
        "quando a exclusão é concluída. Categoria inexistente retorna `404`; uma "
        "categoria vinculada a produtos não pode ser removida e retorna `409`."
    ),
    responses={
        204: {"description": "Categoria excluída com sucesso; resposta sem corpo."},
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
            "description": "Categoria não encontrada."
        },
        409: {
            "model": ErrorResponse,
            "description": "Categoria vinculada a produtos não pode ser removida.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 409,
                        "error": "conflict",
                        "message": (
                            "A categoria não pode ser removida pois possui "
                            "produtos relacionados."
                        ),
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "categoria_id não é um inteiro válido."
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos."
        }
    }
)
def excluir_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada."
        )
    
    try:
        from sqlalchemy import delete
        stmt = delete(Categoria).where(Categoria.id == categoria_id)
        db.execute(stmt)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A categoria não pode ser removida pois possui produtos relacionados."
            )
        raise e
