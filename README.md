Cotacol
=======

[![github-tests-badge]][github-tests]
[![codecov-badge]][codecov]
[![license-badge]](LICENSE)


The Cotacol API/website uses [Flask][flask].

Application dependencies
------------------------

The application uses [Pipenv][pipenv] to manage Python packages. While in development, you will need to install
all dependencies (includes packages like `debug_toolbar`):

    $ pipenv shell
    $ pipenv install --dev

Update dependencies (and manually update `requirements.txt`):

    $ pipenv update --dev && pipenv lock -r

Running the server
------------------

    $ flask run

There is an environment variable called `FLASK_ENV` that has to be set to `development`
if you want to run Flask in debug mode with autoreload

Running tests
-------------

    $ pytest --cov=cotacol

Style guide
-----------

Tab size is 4 spaces. Maximum line length is 120. You should run `black` before commiting any change.

    $ black cotacol


[codecov]: https://codecov.io/gh/eillarra/cotacol
[codecov-badge]: https://codecov.io/gh/eillarra/cotacol/branch/master/graph/badge.svg
[flask]: https://flask.pocoo.org/
[github-tests]: https://github.com/eillarra/cotacol/actions?query=workflow%3A%22tests%22
[github-tests-badge]: https://github.com/eillarra/cotacol/workflows/tests/badge.svg
[license-badge]: https://img.shields.io/badge/license-MIT-blue.svg
[pipenv]: https://docs.pipenv.org/#install-pipenv-today
