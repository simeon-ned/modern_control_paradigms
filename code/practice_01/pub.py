from transport.interface import LCM_Interface
import transport.protocol as lcm_package
from time import perf_counter

lcm = LCM_Interface(lcm_package)

try:
    while True:

        lcm.plant_t.timestamp = int(perf_counter()*1E6)
        lcm.plant_t.state = [1, 2]
        lcm.plant_t.publish()

        lcm.controller_t.timestamp = int(perf_counter()*1E6)
        lcm.controller_t.control = 1
        lcm.controller_t.publish()

except KeyboardInterrupt:
    print('Over')
