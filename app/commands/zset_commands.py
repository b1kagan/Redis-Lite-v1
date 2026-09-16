from app.store import Store, Entry
from app.errors import WrongTypeError


def zadd_command(store: Store, key: str, score: float, member: str) -> int:
    entry = store.get_entry(key)

    if entry is None:
        entry = Entry("zset", {})
        store.set_entry(key, entry)
    elif entry.type != "zset":
        raise WrongTypeError("Key exists with a different data type")

    is_new_member = member not in entry.value
    entry.value[member] = score
    return 1 if is_new_member else 0


def zrange_command(store: Store, key: str, start: int, stop: int) -> list[str]:
    entry = store.get_entry(key)

    if entry is None:
        return []
    if entry.type != "zset":
        raise WrongTypeError("Key exists with a different data type")

    sorted_members = sorted(entry.value.items(), key=lambda item: (item[1], item[0]))
    member_names = [member for member, score in sorted_members]

    if stop == -1:
        return member_names[start:]
    return member_names[start:stop + 1]


def zrem_command(store: Store, key: str, member: str) -> int:
    entry = store.get_entry(key)

    if entry is None:
        return 0
    if entry.type != "zset":
        raise WrongTypeError("Key exists with a different data type")

    if member in entry.value:
        del entry.value[member]
        return 1
    return 0


def zscore_command(store: Store, key: str, member: str) -> float | None:
    entry = store.get_entry(key)

    if entry is None:
        return None
    if entry.type != "zset":
        raise WrongTypeError("Key exists with a different data type")

    return entry.value.get(member)