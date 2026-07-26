import sys
import os
import glob
eplus_installs = glob.glob("C:\\EnergyPlusV*")
if eplus_installs:
    eplus_installs.sort(reverse=True)
    sys.path.append(eplus_installs[0])
from pyenergyplus.api import EnergyPlusAPI
from pyenergyplus.api import EnergyPlusAPI

api = EnergyPlusAPI()
state = api.state_manager.new_state()

def on_begin_new_environment(state_arg):
    print("Environment began!")

api.runtime.callback_begin_new_environment(state, on_begin_new_environment)
api.runtime.run_energyplus(
    state,
    [
        "-d", "out_test",
        "-w", "d:/Hackathon/models/energyplus/weather.epw",
        "d:/Hackathon/models/energyplus/building.epJSON"
    ]
)
