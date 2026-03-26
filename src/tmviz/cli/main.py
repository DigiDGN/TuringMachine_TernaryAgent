"""Typer + Rich operator shell for tmviz.

Entry point: ``tmviz-cli``

Subcommands:
    compile   Compile an AgentSpec JSON to flat TM JSON.
    run       Compile, execute N steps, and persist the run.
    runs      List persisted runs.
    inspect   Inspect a persisted run (summary + snapshots).
    examples  Generate compiled artifacts for example specs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="tmviz-cli",
    help="Turing Machine Ternary Agent operator shell.",
    no_args_is_help=True,
)
console = Console()


# ── compile ──────────────────────────────────────────────────────────


@app.command()
def compile(
    spec: Path = typer.Argument(..., help="Path to agent spec JSON."),
    out: Optional[Path] = typer.Argument(None, help="Output file (default: stdout)."),
) -> None:
    """Compile an AgentSpec JSON file into a flat TM JSON file."""

    from tmviz.compiler import compile_agent_mapping

    raw = json.loads(spec.read_text(encoding="utf8"))
    compiled_obj = compile_agent_mapping(raw)
    try:
        mapping = compiled_obj.to_mapping(include_metadata=True)
    except TypeError:
        mapping = compiled_obj.to_mapping()

    text = json.dumps(mapping, ensure_ascii=False, indent=2)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf8")
        console.print(f"[green]Wrote[/green] {out}")
    else:
        console.print_json(text)


# ── run ──────────────────────────────────────────────────────────────


@app.command()
def run(
    spec: Path = typer.Argument(..., help="Path to agent spec JSON."),
    steps: int = typer.Option(100, "--steps", "-n", help="Maximum steps to execute."),
    db: Optional[str] = typer.Option(None, "--db", help="SQLite path (default: ~/.tmviz/runs.db)."),
    trace: Optional[Path] = typer.Option(None, "--trace", help="Also write NDJSON trace file."),
) -> None:
    """Compile, execute, and persist a run with snapshots."""

    from tmviz.compiler import compile_agent_mapping
    from tmviz.factory.machine_factory import MachineSpecFactory
    from tmviz.storage.runs import RunStore
    from tmviz.trace.snapshot import capture
    from tmviz.trace.replay import TraceWriter

    raw = json.loads(spec.read_text(encoding="utf8"))
    compiled = compile_agent_mapping(raw)
    factory = MachineSpecFactory()
    machine = factory.from_mapping(compiled.to_mapping())

    store = RunStore(db_path=db or None)
    run_id = store.create_run(
        name=f"{compiled.name}_{steps}s",
        spec_name=compiled.name,
        start_state=compiled.start_state,
        start_integrity=compiled.start_state.split("__")[-1],
        alphabet=list(compiled.alphabet),
        metadata=compiled.to_mapping().get("metadata"),
    )

    writer = TraceWriter(trace) if trace else None
    try:
        for _ in range(steps):
            if machine.halted:
                break
            rule = machine.lookup_rule()
            snap = capture(machine, rule=rule)
            store.record_snapshot(run_id, snap)
            if writer:
                writer.write(snap)
            machine.step()
    finally:
        if writer:
            writer.close()

    store.finish_run(
        run_id=run_id,
        total_steps=machine.step_count,
        halted=machine.halted,
        halt_reason=machine.halt_reason,
    )

    console.print(f"[green]Run {run_id}[/green] completed: {machine.step_count} steps", highlight=False)
    if machine.halted:
        console.print(f"  Halted: {machine.halt_reason}")
    if trace:
        console.print(f"  Trace: {trace}")


# ── runs ─────────────────────────────────────────────────────────────


@app.command()
def runs(
    limit: int = typer.Option(20, "--limit", "-n", help="Max runs to show."),
    db: Optional[str] = typer.Option(None, "--db", help="SQLite path."),
) -> None:
    """List persisted runs."""

    from tmviz.storage.runs import RunStore

    store = RunStore(db_path=db or None)
    records = store.list_runs(limit=limit)

    if not records:
        console.print("[dim]No runs found.[/dim]")
        return

    table = Table(title="Runs", show_lines=False)
    table.add_column("ID", style="bold cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Spec")
    table.add_column("Steps", justify="right")
    table.add_column("Halted")
    table.add_column("Created")

    for r in records:
        table.add_row(
            str(r.id),
            r.name,
            r.spec_name,
            str(r.total_steps),
            r.halt_reason or ("yes" if r.halted else "-"),
            r.created_at[:19],
        )

    console.print(table)


# ── inspect ──────────────────────────────────────────────────────────


@app.command()
def inspect(
    run_id: int = typer.Argument(..., help="Run ID to inspect."),
    limit: int = typer.Option(20, "--limit", "-n", help="Max snapshots to show."),
    offset: int = typer.Option(0, "--offset", help="Skip first N snapshots."),
    db: Optional[str] = typer.Option(None, "--db", help="SQLite path."),
) -> None:
    """Inspect a persisted run: summary and snapshots."""

    from tmviz.storage.runs import RunStore

    store = RunStore(db_path=db or None)
    record = store.get_run(run_id)
    if record is None:
        console.print(f"[red]Run {run_id} not found.[/red]")
        raise typer.Exit(1)

    console.print(f"[bold cyan]Run {record.id}[/bold cyan]: {record.name}")
    console.print(f"  Spec: {record.spec_name}")
    console.print(f"  Start: {record.start_state} ({record.start_integrity})")
    console.print(f"  Steps: {record.total_steps}")
    if record.halted:
        console.print(f"  Halted: {record.halt_reason}")
    console.print(f"  Created: {record.created_at}")
    if record.finished_at:
        console.print(f"  Finished: {record.finished_at}")

    total = store.snapshot_count(run_id)
    console.print(f"  Snapshots: {total}")
    console.print()

    snapshots = store.get_snapshots(run_id, offset=offset, limit=limit)
    if not snapshots:
        console.print("[dim]No snapshots in range.[/dim]")
        return

    table = Table(title=f"Snapshots (offset={offset}, limit={limit})")
    table.add_column("Step", style="bold", justify="right")
    table.add_column("State", style="cyan")
    table.add_column("Head", justify="right")
    table.add_column("Read")
    table.add_column("Write")
    table.add_column("Move")
    table.add_column("Next State")

    for s in snapshots:
        # Parse office and integrity from compiled state name
        state_display = s.current_state
        if "__" in s.current_state:
            office, integrity = s.current_state.rsplit("__", 1)
            style = {"life": "green", "seed": "yellow", "death": "red"}.get(integrity, "")
            state_display = f"[{style}]{office}[/{style}] [dim]{integrity}[/dim]"

        table.add_row(
            str(s.step_count),
            state_display,
            str(s.head_position),
            s.read_symbol or "-",
            s.write_symbol or "-",
            s.move_direction or "-",
            s.next_state or "-",
        )

    console.print(table)


# ── examples ─────────────────────────────────────────────────────────


@app.command()
def examples(
    directory: Optional[Path] = typer.Argument(None, help="Examples directory."),
) -> None:
    """Generate compiled TM artifacts for example agent specs."""

    from tmviz.cli.generate_examples import main as gen_main

    code = gen_main(directory)
    raise typer.Exit(code)


# ── main ─────────────────────────────────────────────────────────────


def main() -> None:
    app()


if __name__ == "__main__":
    main()
