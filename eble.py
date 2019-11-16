# Bluetooth Low Energy Handling

# This module automates the communication with the smartphone app
#
# Use this like:
#   ble = EBLE()
#   command = ble.loop()

from adafruit_ble.uart_server import UARTServer
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket

BLE_DEBUG=False

class EBLECommand:
    def __init__(self, _kind, _value):
        self.kind = _kind
        self.value = _value

class EBLE:
    def __init__(self):
        self.uartServer = UARTServer() # this is the bluetooth
        self.reconnect = True

    def __start(self):
        print("[ble] start advertising")
        self.uartServer.start_advertising()
        self.reconnect = False

    def loop(self):
        # if not connected, start
        if not self.uartServer.connected:
            if self.reconnect is True:
                self.__start()
            return

        # if connected
        if self.reconnect == False:
            print('[ble] new connection')
        self.reconnect = True
        try:
            packet = Packet.from_stream(self.uartServer)
        except:
            return None
        if packet is None:
            return None

        # if has a packet
        if BLE_DEBUG:
            print('new packet: ' + type(packet).__name__)
            print(dir(packet))

        if isinstance(packet, ButtonPacket):
            if packet.pressed:
                return EBLECommand(1, packet.button)
        elif isinstance(packet, ColorPacket):
            return EBLECommand(2, packet.color)
        else:
            print('packet not understood')
            print(type(packet))
            return None
