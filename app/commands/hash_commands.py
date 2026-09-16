from app.store import Store, Entry
from app.errors import WrongTypeError


def hset_command(store: Store, key: str, field: str, value: str) -> int:
    entry = store.get_entry(key)

    if entry is None:
        entry = Entry("hash", {})
        store.set_entry(key, entry)
    elif entry.type != "hash":
        raise WrongTypeError("Key exists with a different data type")

    is_new_field = field not in entry.value
    entry.value[field] = value
    return 1 if is_new_field else 0


def hget_command(store: Store, key: str, field: str) -> str | None:
    entry = store.get_entry(key)

    if entry is None:
        return None
    if entry.type != "hash":
        raise WrongTypeError("Key exists with a different data type")

    return entry.value.get(field)


def hdel_command(store: Store, key: str, field: str) -> int:
    entry = store.get_entry(key)

    if entry is None:
        return 0
    if entry.type != "hash":
        raise WrongTypeError("Key exists with a different data type")

    if field in entry.value:
        del entry.value[field]
        return 1
    return 0


def hgetall_command(store: Store, key: str) -> dict:
    entry = store.get_entry(key)

    if entry is None:
        return {}
    if entry.type != "hash":
        raise WrongTypeError("Key exists with a different data type")

    return entry.value