from app.store import Store, Entry
from app.errors import WrongTypeError, InvalidArgumentError


def set_command(store: Store, key: str, value: str) -> str:
    store.set_entry(key, Entry("string", value))
    return "OK"


def get_command(store: Store, key: str) -> str | None:
    entry = store.get_entry(key)

    if entry is None:
        return None
    if entry.type != "string":
        raise WrongTypeError("Key exists with a different data type")

    return entry.value


def delete_command(store: Store, key: str) -> int:
    deleted = store.delete_entry(key)
    return 1 if deleted else 0


def incr_command(store: Store, key: str) -> int:
    with store.lock:
        entry = store.get_entry(key)

        if entry is None:
            new_value = 1
            store.set_entry(key, Entry("string", str(new_value)))
            return new_value

        if entry.type != "string":
            raise WrongTypeError("Key exists with a different data type")

        try:
            current_value = int(entry.value)
        except ValueError:
            raise InvalidArgumentError("Value is not an integer")

        new_value = current_value + 1
        entry.value = str(new_value)
        return new_value