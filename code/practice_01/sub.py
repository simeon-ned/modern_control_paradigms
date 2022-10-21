from transport.interface import LCM_Interface
import transport.protocol as lcm_package
from time import perf_counter

lcm = LCM_Interface(lcm_package)
for channel in lcm.channels:
    channel.subscribe()
# lcm.second_message_t.subscribe()

t2 = 0

try:
    while True:
        lcm.handle()
        t1 = t2
        t2 = lcm.commands_t.timestamp
        print(lcm.plant_t.state, lcm.plant_t.timestamp, lcm.controller_t.control)
        print(t2 - t1)

except KeyboardInterrupt:
    for channel in lcm.channels:
        channel.unsubscribe()
    print('Over')
