"""Export actual EnergyPlus exchange points for the versioned reference model."""

from __future__ import annotations

import sys
from pathlib import Path

ENERGYPLUS_ROOT = Path(r"C:\EnergyPlusV26-1-0")
if str(ENERGYPLUS_ROOT) not in sys.path:
    sys.path.append(str(ENERGYPLUS_ROOT))

from pyenergyplus.api import EnergyPlusAPI  # noqa: E402


def main() -> None:
    """Run until exchange data is ready, then export it and stop safely."""

    root = Path(__file__).resolve().parents[1]
    output_directory = root / "data" / "runtime" / "api-inspection"
    output_directory.mkdir(parents=True, exist_ok=True)
    api = EnergyPlusAPI()
    state = api.state_manager.new_state()
    exported = False

    def export_exchange_points(callback_state: object) -> None:
        nonlocal exported
        if exported or not api.exchange.api_data_fully_ready(callback_state):
            return
        (output_directory / "available_api_data.csv").write_bytes(
            api.exchange.list_available_api_data_csv(callback_state)
        )
        exported = True
        api.runtime.stop_simulation(callback_state)

    api.runtime.callback_begin_zone_timestep_after_init_heat_balance(state, export_exchange_points)
    result = api.runtime.run_energyplus(
        state,
        [
            "-w",
            str(root / "models" / "energyplus" / "weather.epw"),
            "-d",
            str(output_directory),
            str(root / "models" / "energyplus" / "building.epJSON"),
        ],
    )
    api.state_manager.delete_state(state)
    if result != 0 or not exported:
        raise RuntimeError("EnergyPlus did not export available API data.")


if __name__ == "__main__":
    main()
