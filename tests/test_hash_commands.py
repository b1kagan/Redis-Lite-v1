import pytest
from app.store import Store
from app.commands.hash_commands import hset_command, hget_command, hdel_command, hgetall_command
from app.commands.string_commands import set_command
from app.errors import WrongTypeError


def test_hset_new_field_returns_one():
    store = Store()
    assert hset_command(store, "user:2", "name", "Ayse") == 1


def test_hset_update_existing_field_returns_zero():
    store = Store()
    hset_command(store, "user:2", "name", "Ayse")
    assert hset_command(store, "user:2", "name", "Fatma") == 0


def test_hget_returns_value():
    store = Store()
    hset_command(store, "user:2", "name", "Ayse")
    assert hget_command(store, "user:2", "name") == "Ayse"


def test_hget_missing_field_returns_none():
    store = Store()
    hset_command(store, "user:2", "name", "Ayse")
    assert hget_command(store, "user:2", "age") is None


def test_hget_missing_key_returns_none():
    store = Store()
    assert hget_command(store, "nonexistent", "name") is None


def test_hdel_existing_field_returns_one():
    store = Store()
    hset_command(store, "user:2", "name", "Ayse")
    assert hdel_command(store, "user:2", "name") == 1


def test_hdel_missing_field_returns_zero():
    store = Store()
    hset_command(store, "user:2", "name", "Ayse")
    assert hdel_command(store, "user:2", "age") == 0


def test_hgetall_returns_all_fields():
    store = Store()
    hset_command(store, "user:2", "name", "Ayse")
    hset_command(store, "user:2", "age", "25")
    assert hgetall_command(store, "user:2") == {"name": "Ayse", "age": "25"}


def test_hgetall_missing_key_returns_empty_dict():
    store = Store()
    assert hgetall_command(store, "nonexistent") == {}


def test_hset_on_wrong_type_raises_error():
    store = Store()
    set_command(store, "user:2", "just a string")
    with pytest.raises(WrongTypeError):
        hset_command(store, "user:2", "name", "Ayse")