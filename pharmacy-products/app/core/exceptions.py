from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, detail="No encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class AlreadyExistsException(HTTPException):
    def __init__(self, detail="Ya existe"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)