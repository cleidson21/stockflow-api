from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.fornecedor import Fornecedor
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate, FornecedorResponse
from app.schemas.erro import ErrorResponse, ValidationErrorResponse
from app.security.auth import require_roles
from app.models.usuario import Role

router = APIRouter(
    prefix="/fornecedores",
    tags=["Fornecedores"]
)

@router.post(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=FornecedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar fornecedor",
    description=(
        "Cria um fornecedor e requer autenticação Bearer JWT com papel `ADMIN`. "
        "O corpo deve informar nome (até 150 caracteres), CNPJ com exatamente "
        "14 dígitos numéricos, telefone (até 20 caracteres) e email como string "
        "de até 254 caracteres. CNPJ e email devem ser únicos. A validação do "
        "CNPJ é apenas sintática, sem cálculo dos dígitos verificadores, e o "
        "email não é validado com `EmailStr`."
    ),
    responses={
        201: {
            "model": FornecedorResponse,
            "description": "Fornecedor criado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Distribuidora Exemplo",
                        "cnpj": "12345678000199",
                        "telefone": "75999999999",
                        "email": "contato@distribuidora.example",
                        "id": 4
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token Bearer ausente, inválido ou expirado.",
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
            "description": "CNPJ ou email já cadastrado.",
            "content": {
                "application/json": {
                    "examples": {
                        "cnpj_duplicado": {
                            "summary": "CNPJ já cadastrado",
                            "value": {
                                "status": 409,
                                "error": "conflict",
                                "message": "Já existe um fornecedor com este CNPJ.",
                                "details": None
                            }
                        },
                        "email_duplicado": {
                            "summary": "Email já cadastrado",
                            "value": {
                                "status": 409,
                                "error": "conflict",
                                "message": "Já existe um fornecedor com este email.",
                                "details": None
                            }
                        },
                        "unicidade_generica": {
                            "summary": "Constraint de unicidade não identificada",
                            "value": {
                                "status": 409,
                                "error": "conflict",
                                "message": "CNPJ ou email já cadastrado.",
                                "details": None
                            }
                        }
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Corpo ausente ou incompatível com FornecedorCreate.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["body", "cnpj"],
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
def criar_fornecedor(fornecedor_in: FornecedorCreate, db: Session = Depends(get_db)):
    novo_fornecedor = Fornecedor(
        nome=fornecedor_in.nome,
        cnpj=fornecedor_in.cnpj,
        telefone=fornecedor_in.telefone,
        email=fornecedor_in.email
    )
    db.add(novo_fornecedor)
    try:
        db.commit()
        db.refresh(novo_fornecedor)
        return novo_fornecedor
    except IntegrityError as e:
        db.rollback()
        # Verificar o SQLSTATE
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
            diag = getattr(e.orig, "diag", None)
            constraint_name = getattr(diag, "constraint_name", "") if diag else ""
            
            if "cnpj" in constraint_name:
                mensagem = "Já existe um fornecedor com este CNPJ."
            elif "email" in constraint_name:
                mensagem = "Já existe um fornecedor com este email."
            else:
                mensagem = "CNPJ ou email já cadastrado."
                
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=mensagem
            )
        raise e

@router.get(
    "",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=List[FornecedorResponse],
    summary="Listar fornecedores",
    description=(
        "Lista os fornecedores cadastrados. Requer autenticação Bearer JWT com "
        "papel `ADMIN` ou `FUNCIONARIO`. Uma consulta válida sem fornecedores "
        "retorna `200` com `[]`."
    ),
    responses={
        200: {
            "description": "Fornecedores cadastrados; pode ser uma lista vazia.",
            "content": {
                "application/json": {
                    "examples": {
                        "fornecedores": {
                            "summary": "Lista com fornecedores",
                            "value": [
                                {
                                    "nome": "Distribuidora Exemplo",
                                    "cnpj": "12345678000199",
                                    "telefone": "75999999999",
                                    "email": "contato@distribuidora.example",
                                    "id": 4
                                },
                                {
                                    "nome": "Comercial Modelo",
                                    "cnpj": "98765432000100",
                                    "telefone": "7133334444",
                                    "email": "vendas@comercial.example",
                                    "id": 5
                                }
                            ]
                        },
                        "sem_resultados": {
                            "summary": "Listagem sem fornecedores",
                            "value": []
                        }
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token Bearer ausente, inválido ou expirado.",
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
def listar_fornecedores(db: Session = Depends(get_db)):
    stmt = select(Fornecedor).order_by(Fornecedor.id)
    return db.scalars(stmt).all()

@router.get(
    "/{fornecedor_id}",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.FUNCIONARIO))],
    response_model=FornecedorResponse,
    summary="Buscar fornecedor por ID",
    description=(
        "Retorna um fornecedor pelo identificador inteiro obrigatório. Requer "
        "autenticação Bearer JWT com papel `ADMIN` ou `FUNCIONARIO`. Fornecedor "
        "inexistente retorna `404`; identificador que não seja inteiro retorna "
        "`422`."
    ),
    responses={
        200: {
            "model": FornecedorResponse,
            "description": "Fornecedor encontrado.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Distribuidora Exemplo",
                        "cnpj": "12345678000199",
                        "telefone": "75999999999",
                        "email": "contato@distribuidora.example",
                        "id": 4
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token Bearer ausente, inválido ou expirado.",
            "headers": {
                "WWW-Authenticate": {
                    "description": "Esquema de autenticação exigido.",
                    "schema": {"type": "string", "example": "Bearer"}
                }
            }
        },
        404: {
            "model": ErrorResponse,
            "description": "Fornecedor não encontrado.",
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
            "description": "fornecedor_id não é um inteiro válido.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 422,
                        "error": "validation_error",
                        "message": "Dados de entrada inválidos.",
                        "details": [
                            {
                                "loc": ["path", "fornecedor_id"],
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
def buscar_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    return fornecedor

@router.put(
    "/{fornecedor_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    response_model=FornecedorResponse,
    summary="Atualizar fornecedor",
    description=(
        "Substitui os campos editáveis de um fornecedor e requer autenticação "
        "Bearer JWT com papel `ADMIN`. O corpo completo definido por "
        "`FornecedorUpdate` é obrigatório; esta operação não possui semântica de "
        "PATCH. CNPJ e email devem permanecer únicos e obedecer às mesmas "
        "restrições documentadas na criação."
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Distribuidora Atualizada",
                        "cnpj": "12345678000199",
                        "telefone": "7533335555",
                        "email": "atendimento@distribuidora.example"
                    }
                }
            }
        }
    },
    responses={
        200: {
            "model": FornecedorResponse,
            "description": "Fornecedor atualizado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Distribuidora Atualizada",
                        "cnpj": "12345678000199",
                        "telefone": "7533335555",
                        "email": "atendimento@distribuidora.example",
                        "id": 4
                    }
                }
            }
        },
        401: {
            "model": ErrorResponse,
            "description": "Token Bearer ausente, inválido ou expirado.",
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
            "description": "Fornecedor não encontrado."
        },
        409: {
            "model": ErrorResponse,
            "description": "CNPJ ou email já cadastrado.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 409,
                        "error": "conflict",
                        "message": "CNPJ ou email já cadastrado.",
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
def atualizar_fornecedor(fornecedor_id: int, fornecedor_in: FornecedorUpdate, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    
    fornecedor.nome = fornecedor_in.nome
    fornecedor.cnpj = fornecedor_in.cnpj
    fornecedor.telefone = fornecedor_in.telefone
    fornecedor.email = fornecedor_in.email
    
    try:
        db.commit()
        db.refresh(fornecedor)
        return fornecedor
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
            diag = getattr(e.orig, "diag", None)
            constraint_name = getattr(diag, "constraint_name", "") if diag else ""
            
            if "cnpj" in constraint_name:
                mensagem = "Já existe um fornecedor com este CNPJ."
            elif "email" in constraint_name:
                mensagem = "Já existe um fornecedor com este email."
            else:
                mensagem = "CNPJ ou email já cadastrado."
                
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=mensagem
            )
        raise e

@router.delete(
    "/{fornecedor_id}",
    dependencies=[Depends(require_roles(Role.ADMIN))],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir fornecedor",
    description=(
        "Exclui um fornecedor e requer autenticação Bearer JWT com papel `ADMIN`. "
        "Retorna `204` sem corpo quando a exclusão é concluída. A integridade "
        "referencial bloqueia a exclusão com `409` se houver produtos ou "
        "movimentações históricas relacionados; não há exclusão em cascata nem "
        "recálculo da referência histórica."
    ),
    responses={
        204: {"description": "Fornecedor excluído com sucesso; resposta sem corpo."},
        401: {
            "model": ErrorResponse,
            "description": "Token Bearer ausente, inválido ou expirado.",
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
            "description": "Fornecedor não encontrado."
        },
        409: {
            "model": ErrorResponse,
            "description": "Fornecedor possui produtos ou movimentações relacionados.",
            "content": {
                "application/json": {
                    "example": {
                        "status": 409,
                        "error": "conflict",
                        "message": (
                            "O fornecedor não pode ser removido pois possui "
                            "registros relacionados."
                        ),
                        "details": None
                    }
                }
            }
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "fornecedor_id não é um inteiro válido."
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno inesperado, sem exposição de detalhes internos."
        }
    }
)
def excluir_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado."
        )
    
    try:
        from sqlalchemy import delete
        stmt = delete(Fornecedor).where(Fornecedor.id == fornecedor_id)
        db.execute(stmt)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        if e.orig and hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23503":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O fornecedor não pode ser removido pois possui registros relacionados."
            )
        raise e
