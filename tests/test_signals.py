"""Tests for the centralized Blinker signal registry."""

from tmviz.events.signals import (
    DummySignal,
    compile_finished,
    compile_highways,
    compile_started,
    get_signal,
    machine_halted,
    step_committed,
    trace_flushed,
    trace_started,
)


def test_get_signal_returns_same_instance_for_same_name():
    sig_a = get_signal("test.foo")
    sig_b = get_signal("test.foo")
    assert sig_a is sig_b


def test_signal_send_receive():
    sig = get_signal("test.roundtrip")
    received = []

    def handler(*_args, **kwargs):
        received.append(kwargs)

    sig.connect(handler)
    sig.send(key="value", num=42)
    assert len(received) == 1
    assert received[0]["key"] == "value"
    assert received[0]["num"] == 42


def test_signal_disconnect():
    sig = get_signal("test.disconnect")
    received = []

    def handler(*_args, **kwargs):
        received.append(kwargs)

    sig.connect(handler)
    sig.send(x=1)
    assert len(received) == 1

    sig.disconnect(handler)
    sig.send(x=2)
    assert len(received) == 1  # no new event


def test_dummy_signal_noop():
    dummy = DummySignal("noop")
    assert dummy.name == "noop"
    assert dummy.send(foo="bar") == []
    dummy.connect(lambda: None)
    dummy.disconnect(lambda: None)


def test_all_named_signals_exist():
    """Verify that all registry-level signals are importable and non-None."""
    for sig in (
        compile_started,
        compile_highways,
        compile_finished,
        step_committed,
        machine_halted,
        trace_started,
        trace_flushed,
    ):
        assert sig is not None
