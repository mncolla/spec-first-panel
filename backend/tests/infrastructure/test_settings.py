from app.infrastructure.config.settings import as_sqlalchemy_url


def test_railway_postgres_url_uses_psycopg() -> None:
    assert (
        as_sqlalchemy_url("postgresql://user:pass@host:5432/railway")
        == "postgresql+psycopg://user:pass@host:5432/railway"
    )


def test_legacy_postgres_scheme() -> None:
    assert (
        as_sqlalchemy_url("postgres://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


def test_already_psycopg_url_is_unchanged() -> None:
    url = "postgresql+psycopg://lebane:lebane@localhost:5432/lebane"
    assert as_sqlalchemy_url(url) == url
