=======
History
=======

2.0 (2026-07-19)
------------------

* Revived for modern Python: works on Python 3.9-3.13 (the removal of
  ``asyncio.coroutine`` in Python 3.11 had made the library unusable there).
* Handlers may return a ``(data, status)`` tuple to set the response status.
* Plain (non-async) handlers are still supported.
* Type hints and a ``py.typed`` marker.
* Modern packaging (``pyproject.toml``), tests on GitHub Actions, releases
  via PyPI trusted publishing.


1.0.0 (2016-12-12)
------------------

* Better documentation.
* Updated requirements.
* Out of alpha!


0.1.0 (2016-10-12)
------------------

* First release on PyPI.
