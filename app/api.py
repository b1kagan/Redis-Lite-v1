import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.store import Store
from app.errors import RedisLiteError, UnknownCommandError, InvalidArgumentCountError, InvalidArgumentError
from app.commands.string_commands import set_command, get_command, delete_command, incr_command
from app.commands.hash_commands import hset_command, hget_command, hdel_command, hgetall_command
from app.commands.zset_commands import zadd_command, zrange_command, zrem_command, zscore_command


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("redis_lite")


class CommandRequest(BaseModel):
    command: str
    args: list[str]


store = Store()

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/command")
def handle_command(request: CommandRequest):
    command = request.command.upper()
    args = request.args
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    try:
        result = run_command(command, args)
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_request(request_id, command, duration_ms, "success", None)
        return {"ok": True, "result": result, "error": None}
    except RedisLiteError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_request(request_id, command, duration_ms, "error", e.code)

        if e.code == "WRONG_TYPE":
            status_code = 409
        elif e.code == "INTERNAL_ERROR":
            status_code = 500
        else:
            status_code = 400

        error_body = {"code": e.code, "message": e.message}
        response_body = {"ok": False, "result": None, "error": error_body}
        return JSONResponse(status_code=status_code, content=response_body)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_request(request_id, command, duration_ms, "error", "INTERNAL_ERROR")

        error_body = {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        response_body = {"ok": False, "result": None, "error": error_body}
        return JSONResponse(status_code=500, content=response_body)


def log_request(request_id: str, command: str, duration_ms: float, status: str, error_code: str | None) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(
        "timestamp=%s request_id=%s command=%s duration_ms=%.2f status=%s error_code=%s",
        timestamp, request_id, command, duration_ms, status, error_code,
    )


def run_command(command: str, args: list[str]):
    if command == "SET":
        check_count(args, 2)
        return set_command(store, args[0], args[1])

    if command == "GET":
        check_count(args, 1)
        return get_command(store, args[0])

    if command == "DEL":
        check_count(args, 1)
        return delete_command(store, args[0])

    if command == "INCR":
        check_count(args, 1)
        return incr_command(store, args[0])

    if command == "HSET":
        check_count(args, 3)
        return hset_command(store, args[0], args[1], args[2])

    if command == "HGET":
        check_count(args, 2)
        return hget_command(store, args[0], args[1])

    if command == "HDEL":
        check_count(args, 2)
        return hdel_command(store, args[0], args[1])

    if command == "HGETALL":
        check_count(args, 1)
        return hgetall_command(store, args[0])

    if command == "ZADD":
        check_count(args, 3)
        score = parse_number(args[1])
        return zadd_command(store, args[0], score, args[2])

    if command == "ZRANGE":
        check_count(args, 3)
        start = parse_integer(args[1])
        stop = parse_integer(args[2])
        return zrange_command(store, args[0], start, stop)

    if command == "ZREM":
        check_count(args, 2)
        return zrem_command(store, args[0], args[1])

    if command == "ZSCORE":
        check_count(args, 2)
        return zscore_command(store, args[0], args[1])

    raise UnknownCommandError("Unknown command: " + command)


def check_count(args: list[str], expected_count: int) -> None:
    if len(args) != expected_count:
        message = "Expected " + str(expected_count) + " arguments, got " + str(len(args))
        raise InvalidArgumentCountError(message)


def parse_number(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        raise InvalidArgumentError("Score must be a number")


def parse_integer(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise InvalidArgumentError("Argument must be an integer")