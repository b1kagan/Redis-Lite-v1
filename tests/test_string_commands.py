import pytest
from app.store import Store
from app.commands.string_commands import set_command, get_command, delete_command, incr_command
from app.errors import WrongTypeError, InvalidArgumentError


def test_set_and_get_returns_same_value():
    store = Store()
    set_command(store, "user:1", "Cuneyt")
    assert get_command(store, "user:1") == "Cuneyt"


def test_set_overwrites_existing_value():
    store = Store()
    set_command(store, "user:1", "Cuneyt")
    set_command(store, "user:1", "Ayse")
    assert get_command(store, "user:1") == "Ayse"


def test_get_missing_key_returns_none():
    store = Store()
    assert get_command(store, "nonexistent") is None


def test_get_on_wrong_type_raises_error():
    from app.commands.hash_commands import hset_command
    store = Store()
    hset_command(store, "user:1", "name", "Ayse")
    with pytest.raises(WrongTypeError):
        get_command(store, "user:1")


def test_delete_existing_key_returns_one():
    store = Store()
    set_command(store, "user:1", "Cuneyt")
    assert delete_command(store, "user:1") == 1


def test_delete_missing_key_returns_zero():
    store = Store()
    assert delete_command(store, "nonexistent") == 0


def test_incr_starts_from_zero_when_key_missing():
    store = Store()
    assert incr_command(store, "counter") == 1


def test_incr_increments_existing_integer():
    store = Store()
    set_command(store, "counter", "5")
    assert incr_command(store, "counter") == 6


def test_incr_rejects_non_integer_value():
    store = Store()
    set_command(store, "counter", "abc")
    with pytest.raises(InvalidArgumentError):
        incr_command(store, "counter")