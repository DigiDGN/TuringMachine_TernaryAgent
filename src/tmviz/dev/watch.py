"""Live-reload watcher for agent spec files.

Watches a directory for changes to ``*.agent.json`` files and triggers
recompilation.  Requires the ``watchfiles`` package (optional dep).

Usage::

    from tmviz.dev.watch import watch_and_reload
    watch_and_reload("examples/", callback=my_reload_fn)

Or from the CLI::

    tmviz-cli compile --watch examples/minimal_three_office.agent.json

"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from tmviz.trace.logger import get_logger

_log = get_logger(__name__)


def watch_and_reload(
    path: Path | str,
    callback: Callable[[dict[str, Any]], None] | None = None,
    *,
    pattern: str = "*.agent.json",
) -> None:
    """Block and watch *path* for spec file changes.

    Parameters
    ----------
    path:
        File or directory to watch.  If a directory, watches all files
        matching *pattern*.
    callback:
        Called with the compiled mapping dict on each detected change.
        If *None*, prints the compiled JSON to stdout.
    pattern:
        Glob pattern for files to watch when *path* is a directory.

    Raises
    ------
    ImportError
        If ``watchfiles`` is not installed.
    """

    try:
        from watchfiles import watch, Change
    except ImportError as exc:
        raise ImportError(
            "watchfiles is required for live reload. "
            "Install with: pip install tmviz[watch]"
        ) from exc

    from tmviz.compiler import compile_agent_mapping

    target = Path(path)
    if target.is_file():
        watch_dir = target.parent
        watch_files = {target.resolve()}
    else:
        watch_dir = target
        watch_files = None

    _log.info("watch.start", path=str(target), pattern=pattern)

    for changes in watch(watch_dir):
        for change_type, changed_path in changes:
            changed = Path(changed_path)

            # filter to matching files
            if watch_files and changed.resolve() not in watch_files:
                continue
            if not watch_files and not changed.match(pattern):
                continue
            if change_type not in (Change.modified, Change.added):
                continue

            _log.info("watch.change", file=str(changed), type=change_type.name)
            try:
                raw = json.loads(changed.read_text(encoding="utf8"))
                compiled = compile_agent_mapping(raw)
                mapping = compiled.to_mapping(include_metadata=True)

                if callback:
                    callback(mapping)
                else:
                    print(json.dumps(mapping, indent=2))

                _log.info("watch.recompiled", name=compiled.name)
            except Exception as exc:
                _log.error("watch.error", error=str(exc))
