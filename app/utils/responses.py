from typing import Any

from fastapi.responses import JSONResponse


def success_response(payload: dict[str, Any], status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=payload)


def error_response(
    error_type: str,
    message: str,
    details: dict[str, Any] | None = None,
    status_code: int = 500,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            'error': {
                'type': error_type,
                'message': message,
                'details': details,
            }
        },
    )
