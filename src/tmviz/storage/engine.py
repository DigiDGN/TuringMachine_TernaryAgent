"""SQLite engine factory and database initialization."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

_DEFAULT_DB_PATH = Path.home() / ".tmviz" / "runs.db"

_engine: Engine | None = None


def get_engine(db_path: Path | str | None = None, echo: bool = False) -> Engine:
    """Return a shared SQLite engine, creating it on first call.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Defaults to
        ``~/.tmviz/runs.db``.  Use ``":memory:"`` for tests.
    echo:
        Forward SQL statements to the logger when *True*.
    """

    global _engine
    if _engine is not None:
        return _engine

    path = Path(db_path) if db_path and db_path != ":memory:" else None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{path}"
    else:
        url = "sqlite://" if db_path == ":memory:" else f"sqlite:///{_DEFAULT_DB_PATH}"
        if db_path != ":memory:":
            _DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(url, echo=echo)
    return _engine


def init_db(engine: Engine | None = None) -> None:
    """Create all tables if they don't exist."""

    engine = engine or get_engine()
    SQLModel.metadata.create_all(engine)


def reset_engine() -> None:
    """Drop the cached engine (useful in tests)."""

    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None
