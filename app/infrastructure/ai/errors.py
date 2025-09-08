class AppError(Exception):
    code: str = "APP_ERROR"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class BadRequestError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="BAD_REQUEST")


class UnauthorizedError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="UNAUTHORIZED")


class ForbiddenError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="FORBIDDEN")


class RateLimitError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="RATE_LIMIT")


class TimeoutError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="TIMEOUT")


class ServerError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="SERVER_ERROR")

