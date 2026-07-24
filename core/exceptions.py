from fastapi import HTTPException, status


class VitalisException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(VitalisException):
    def __init__(self, detail: str = "Recurso não encontrado"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(VitalisException):
    def __init__(self, detail: str = "Não autorizado"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(VitalisException):
    def __init__(self, detail: str = "Acesso proibido"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ConflictException(VitalisException):
    def __init__(self, detail: str = "Conflito de dados"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ValidationException(VitalisException):
    def __init__(self, detail: str = "Erro de validação"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ServiceUnavailableException(VitalisException):
    def __init__(self, detail: str = "Serviço indisponível"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
