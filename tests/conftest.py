import os
import pytest
import tempfile

from cotacol.app import create_app


app = create_app()


@pytest.fixture
def client():
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            pass
            # flaskr.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])
