"""Integration tests for the Simulation Adapter."""

from unittest.mock import MagicMock

import pytest

from packages.sim_adapter.actuator import ActuatorAdapter, InvalidActuatorError
from packages.sim_adapter.contracts import ActionCommandV1
from packages.sim_adapter.parser import TelemetryParser
from packages.sim_adapter.runner import SimulationAdapter


def test_parser_fixture_identifies_fields():
    """Verifies that the parser correctly extracts telemetry from API."""
    mock_api = MagicMock()
    mock_state = MagicMock()

    mock_api.exchange.year.return_value = 2024
    mock_api.exchange.month.return_value = 7
    mock_api.exchange.day_of_month.return_value = 25
    mock_api.exchange.hour.return_value = 14
    mock_api.exchange.current_time.return_value = 14.5
    mock_api.exchange.day_of_year.return_value = 207

    mock_api.exchange.get_variable_value.side_effect = lambda state, handle: {
        100: 24.5,  # zone_1 temp
        101: 30.0,  # outdoor_temp
        102: 1500.0,  # hvac_power
    }[handle]

    handles = {"temp_zone_1": 100, "outdoor_temp": 101, "hvac_power": 102}

    parser = TelemetryParser(mock_api, mock_state, handles)
    telemetry = parser.parse()

    assert telemetry.zone_temperatures["zone_1"] == 24.5
    assert telemetry.outdoor_temperature == 30.0
    assert telemetry.hvac_power == 1500.0


def test_command_allow_list_rejects_invalid():
    """Checks that actuator adapter rejects invalid commands."""
    mock_api = MagicMock()
    mock_state = MagicMock()
    handles = {"zone_1_cooling_setpoint": 200}

    actuator = ActuatorAdapter(mock_api, mock_state, handles)

    bad_command = ActionCommandV1(actuator_id="fan_power_override", value=0.0)

    with pytest.raises(InvalidActuatorError, match="not in the allow-list"):
        actuator.apply_action(bad_command)


def test_manual_safe_override_applied():
    """Validates the manual safe override command."""
    mock_api = MagicMock()
    mock_state = MagicMock()
    handles = {"zone_1_cooling_setpoint": 200}

    actuator = ActuatorAdapter(mock_api, mock_state, handles)

    good_command = ActionCommandV1(actuator_id="zone_1_cooling_setpoint", value=22.0)
    actuator.apply_action(good_command)

    mock_api.exchange.set_actuator_value.assert_called_once_with(mock_state, 200, 22.0)


def test_runner_acknowledges_actions():
    """Simulates a simulation tick applying actions and returning acks."""
    # We mock EnergyPlusAPI inside the runner by replacing self.api

    from pathlib import Path

    runner = SimulationAdapter(Path("dummy.epJSON"), Path("dummy.epw"), Path("out"))
    runner.api = MagicMock()
    runner.api.exchange.year.return_value = 2024
    runner.api.exchange.day_of_year.return_value = 1
    runner.api.exchange.current_time.return_value = 0.0
    runner.api.exchange.api_data_fully_ready.return_value = False
    runner.state = MagicMock()

    runner.actuator_handles = {"zone_1_cooling_setpoint": 200}
    runner.actuator = ActuatorAdapter(runner.api, runner.state, runner.actuator_handles)
    runner.parser = MagicMock()

    cmd_good = ActionCommandV1(actuator_id="zone_1_cooling_setpoint", value=22.0)
    cmd_bad = ActionCommandV1(actuator_id="invalid_actuator", value=0)

    runner.apply_action(cmd_good)
    runner.apply_action(cmd_bad)

    # Manually invoke the callback to process actions
    runner._on_begin_zone_timestep(runner.state)

    acks = runner.acknowledge()

    assert len(acks) == 2

    assert acks[0].command_id == cmd_good.command_id
    assert acks[0].accepted is True

    assert acks[1].command_id == cmd_bad.command_id
    assert acks[1].accepted is False
    assert "allow-list" in acks[1].message

    runner.stop()
