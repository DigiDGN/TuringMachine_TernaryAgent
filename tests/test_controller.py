from pathlib import Path

from tmviz.app.commands import LoadMachineCommand, RunCommand, SetSpeedCommand, StepCommand
from tmviz.app.controller import AppController
from tmviz.factory.machine_factory import MachineSpecFactory
from tmviz.infra.event_bus import EventBus


def build_controller() -> AppController:
    controller = AppController(factory=MachineSpecFactory(), event_bus=EventBus())
    controller.boot_complete()
    return controller


def test_controller_loads_machine_and_single_steps() -> None:
    controller = build_controller()
    spec = Path(__file__).resolve().parents[1] / "specs" / "unary_increment.json"

    controller.execute(LoadMachineCommand(spec))
    controller.execute(StepCommand())

    assert controller.state == "loaded"
    assert controller.machine is not None
    assert controller.machine.step_count == 1
    assert controller.machine.head_position == 1


def test_controller_runs_until_halt() -> None:
    controller = build_controller()
    spec = Path(__file__).resolve().parents[1] / "specs" / "unary_increment.json"

    controller.execute(LoadMachineCommand(spec))
    controller.execute(SetSpeedCommand(5.0))
    controller.execute(RunCommand())
    for _ in range(5):
        controller.update(1.0)
        if controller.state == "halted":
            break

    assert controller.state == "halted"
    assert controller.machine is not None
    assert controller.machine.halt_reason == "accept"
    assert controller.machine.step_count == 4


def test_controller_loads_high_level_agent_spec_and_steps() -> None:
    controller = build_controller()
    spec = Path(__file__).resolve().parents[1] / "examples" / "minimal_three_office.agent.json"

    controller.execute(LoadMachineCommand(spec))
    controller.execute(StepCommand())

    assert controller.state == "loaded"
    assert controller.machine is not None
    assert controller.machine.current_state == "arbiter__life"
    assert controller.machine.step_count == 1

