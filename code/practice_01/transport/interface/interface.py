

import lcm
import select as select
import pkgutil


# TODO: MOVE EVERYTHING TO CLASS

# address =
UDP_MULTICAST = "udpm://239.255.76.67:7667?ttl=1"
UDP_MULTICAST = ""

# TODO:
# - handle multiple subscriptions
# - parser from .lcm files
# - handler to assemble LCM system from dict of protocol structs and channel names


def handle(lcm, blocking=False):
    handled = False
    if not blocking:
        rfds, _, _ = select.select([lcm.fileno()], [], [], 0.)
        if rfds:
            lcm.handle()
            handled = True
    else:
        lcm.handle()
        handled = True
    return handled



class LCM_Channel(object):
    def __init__(self, lcm, struct, name=None):
        self.struct = struct
        self.slots = self.struct.__slots__

        if name is not None and isinstance(name, str):
            self.__name = name
        else:
            self.__name = struct.__name__

        # print(self.__name)

        # self.lcm = lcm
        self.lc = lcm

        # print(self.__name)
        self.update = self.__update_channel

        self.subscription = None
        self.message = struct()
        self.__msg2attr()

    def __msg2attr(self):
        for slot in self.slots:
            vars(self)[slot] = getattr(self.message, slot)

    def __attr2msg(self):
        for slot in self.slots:
            setattr(self.message, slot, getattr(self, slot))

    def __update_channel(self, channel, data):
        channel_data = self.struct.decode(data)
        for slot in self.slots:
            vars(self)[slot] = getattr(channel_data, slot)
        # self.__msg2attr()

    def subscribe(self):
        # print(self.__name)
        # self.__name = 'example'

        if self.subscription is not None:
            print(f'[LCM] Already subscribed to "{self.__name}" channel')
        else:
            self.subscription = self.lc.subscribe(
                self.__name, self.__update_channel)
            # self.lcm.subscriptions[self.__name] = self.__name
            print(f'[LCM] Subscribed to "{self.__name}" channel')

    def publish(self, update_message=True):
        # self.__name = 'example'
        if update_message:
            self.__attr2msg()
        self.lc.publish(self.__name, self.message.encode())

    def unsubscribe(self):
        if self.subscription is not None:
            self.lc.unsubscribe(self.subscription)
            self.subscription = None
            print(f'[LCM] Unsubscribed from "{self.__name}" channel')

        else:
            print(f'[LCM] There is no subscription to "{self.__name}" channel')


# TODO:
# add subscribe/unsubscribe to all channels

class LCM_Interface(object):

    def __init__(self,
                 package = None,
                 package_path = None, 
                 address=UDP_MULTICAST):
        
        self.structs = []
        self.channels = []
        self.lc = lcm.LCM(address)
        
        self.handle = lambda blocking = False: handle(self.lc, blocking=blocking)
        # self.lc = self.__handler.lc

        self.__package = package

        # self.__handler = lambda : handle(lcm = self.lc, blocking=False)
        for _, structname, _ in pkgutil.iter_modules(self.__package.__path__):
            struct = getattr(self.__package, structname)
            lcm_channel = LCM_Channel(self.lc, struct)
            self.structs.append(struct)
            self.channels.append(lcm_channel)
            setattr(self, structname, lcm_channel)

        # self.lc = self.__handler.lc