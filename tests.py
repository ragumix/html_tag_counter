import pytest
import requests

from tagcounter.main import get_from_db, check_in_dict, insert_to_db, count


def test_get():
    with pytest.raises(TypeError):
        get_from_db("wwwsomesite")
    with pytest.raises(TypeError):
        get_from_db("{'html':1, 'div':1}","wwwsomesite")
    assert get_from_db("google.com")


def test_count():
    with pytest.raises(requests.exceptions.ConnectionError):
        count("wwwsomesite")
    with pytest.raises(requests.exceptions.ConnectionError):
        count("test")
    assert count("google.com")
    assert count("facebook.com")


def test_insert():
    with pytest.raises(TypeError):
        insert_to_db("wwwsomesite")
    with pytest.raises(TypeError):
        insert_to_db("{'html':1, 'div':1}","wwwsomesite")
    assert insert_to_db("{'html':1, 'div':1}","google.com","2021-08-06 12:00:00.000")


def test_check():
    with pytest.raises(TypeError):
        check_in_dict("{'html':1, 'div':1}","wwwsomesite")
    assert check_in_dict("ggl")