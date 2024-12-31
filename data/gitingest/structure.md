Directory structure:
└── cyclotruc-gitingest/
    ├── docs/
    ├── .pre-commit-config.yaml
    ├── .github/
    │   └── workflows/
    │       ├── publish.yml
    │       └── ci.yml
    ├── requirements-dev.txt
    ├── .dockerignore
    ├── requirements.txt
    ├── pyproject.toml
    ├── CODE_OF_CONDUCT.md
    ├── setup.py
    ├── SECURITY.md
    ├── pytest.ini
    ├── Dockerfile
    ├── LICENSE
    ├── README.md
    └── src/
        ├── config.py
        ├── main.py
        ├── server_utils.py
        ├── __init__.py
        ├── routers/
        │   ├── download.py
        │   ├── __init__.py
        │   ├── dynamic.py
        │   └── index.py
        ├── gitingest/
        │   ├── parse_query.py
        │   ├── ingest.py
        │   ├── tests/
        │   │   ├── test_clone.py
        │   │   ├── __init__.py
        │   │   ├── conftest.py
        │   │   ├── test_ingest.py
        │   │   └── test_parse_query.py
        │   ├── ignore_patterns.py
        │   ├── __init__.py
        │   ├── cli.py
        │   ├── clone.py
        │   ├── ingest_from_query.py
        │   └── utils.py
        ├── process_query.py
        ├── templates/
        │   ├── base.jinja
        │   ├── index.jinja
        │   ├── components/
        │   │   ├── footer.jinja
        │   │   ├── result.jinja
        │   │   ├── navbar.jinja
        │   │   └── github_form.jinja
        │   ├── github.jinja
        │   └── api.jinja
        └── static/
            ├── robots.txt
            └── js/
                ├── utils.js
                └── snow.js