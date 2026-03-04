from typing import Any


class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        error_type: str = 'AppError',
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, message: str = 'Resource not found.', details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            error_type='NotFoundError',
            status_code=404,
            details=details,
        )


class DatabaseError(AppError):
    def __init__(self, message: str = 'Database operation failed.', details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            error_type='DatabaseError',
            status_code=500,
            details=details,
        )
