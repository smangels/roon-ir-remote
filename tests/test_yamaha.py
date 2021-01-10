
import pytest
import pytest_mock
from app import Yamaha
import requests


@pytest.fixture(scope="module")
def yamaha():
    y = Yamaha('yamaha.home.mangelsen.se')
    y.set_volume(level_percent=50)
    yield y
    del y

@pytest.mark.parametrize(
    argnames="http_code, expected_to_fail",
    argvalues=[
        (200, False),
        (404, True)
    ],
    ids=[
        "200, OK",
        "404, Failed"
    ]
)
def test_set_volume(mocker, yamaha, http_code, expected_to_fail):
    r = requests.Response()
    r.status_code = http_code
    mocker.patch("requests.get", return_value=r)
    if expected_to_fail:
        assert not yamaha.set_volume(level_percent=80)
    else:
        assert yamaha.set_volume(level_percent=80)


def test_mute(mocker, yamaha):
    r = requests.Response()
    r.status_code = 200
    mocker.patch("requests.get", return_value=r)
    yamaha.mute()


def test_unmute(mocker, yamaha):
    mocker.patch("requests.get")
    yamaha.unmute()
