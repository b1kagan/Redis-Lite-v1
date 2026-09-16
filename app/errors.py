class RedisLiteError(Exception):
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class WrongTypeError(RedisLiteError):
    code = "WRONG_TYPE"


class InvalidArgumentError(RedisLiteError):
    code = "INVALID_ARGUMENT"


class UnknownCommandError(RedisLiteError):
    code = "UNKNOWN_COMMAND"


class InvalidArgumentCountError(RedisLiteError):
    code = "INVALID_ARGUMENT_COUNT"