import pytest
from app.store import Store
from app.commands.zset_commands import zadd_command, zrange_command, zrem_command, zscore_command
from app.commands.string_commands import set_command
from app.errors import WrongTypeError


def test_zadd_new_member_returns_one():
    store = Store()
    assert zadd_command(store, "leaderboard", 150, "player1") == 1


def test_zadd_update_existing_score_returns_zero():
    store = Store()
    zadd_command(store, "leaderboard", 150, "player1")
    assert zadd_command(store, "leaderboard", 200, "player1") == 0


def test_zrange_returns_ascending_by_score():
    store = Store()
    zadd_command(store, "leaderboard", 150, "player1")
    zadd_command(store, "leaderboard", 120, "player2")
    assert zrange_command(store, "leaderboard", 0, -1) == ["player2", "player1"]


def test_zrange_equal_scores_sorted_by_member_name():
    store = Store()
    zadd_command(store, "leaderboard", 100, "zeynep")
    zadd_command(store, "leaderboard", 100, "ahmet")
    assert zrange_command(store, "leaderboard", 0, -1) == ["ahmet", "zeynep"]


def test_zrange_missing_key_returns_empty_list():
    store = Store()
    assert zrange_command(store, "nonexistent", 0, -1) == []


def test_zrem_existing_member_returns_one():
    store = Store()
    zadd_command(store, "leaderboard", 150, "player1")
    assert zrem_command(store, "leaderboard", "player1") == 1


def test_zrem_missing_member_returns_zero():
    store = Store()
    zadd_command(store, "leaderboard", 150, "player1")
    assert zrem_command(store, "leaderboard", "player2") == 0


def test_zscore_returns_score():
    store = Store()
    zadd_command(store, "leaderboard", 150, "player1")
    assert zscore_command(store, "leaderboard", "player1") == 150


def test_zscore_missing_member_returns_none():
    store = Store()
    zadd_command(store, "leaderboard", 150, "player1")
    assert zscore_command(store, "leaderboard", "player2") is None


def test_zadd_on_wrong_type_raises_error():
    store = Store()
    set_command(store, "leaderboard", "just a string")
    with pytest.raises(WrongTypeError):
        zadd_command(store, "leaderboard", 150, "player1")


#ZRANGE maliyet ölçme

import time


def test_zrange_performance_at_scale():
    store = Store()

    for i in range(10000):
        zadd_command(store, "leaderboard", i, "player" + str(i))

    start = time.perf_counter()
    zrange_command(store, "leaderboard", 0, -1)
    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000
    print("\n10000 uye -> ZRANGE suresi: " + str(round(elapsed_ms, 3)) + " ms")    