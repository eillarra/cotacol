import pytest

from django.urls import reverse
from cotacol.services.parser import update_cotacol_data


@pytest.mark.parametrize("route_name", ["homepage", "account_signup"])
def test_page(client, db, route_name):
    assert client.get(reverse(route_name)).status_code == status.HTTP_200_OK
