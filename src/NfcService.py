from pn532pi import Pn532
from pn532pi import Pn532Hsu
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi
from collections import deque
import cbor2 as cbor

APDU_COMMAND_CONNECTED = bytes([0x01])
APDU_COMMAND_REJECTED = bytes([0x02])
APDU_COMMAND_REQUEST = bytearray([0x03])
APDU_COMMAND_RECEIVED = bytes([0x04])
APDU_COMMAND_FROM_ATM = bytes([0x05])
APDU_COMMAND_FROM_CLIENT = bytes([0x06])
APDU_COMMAND_END_OF_MESSAGE = bytes([0x07])
APDU_COMMAND_WAIT = bytes([0x08])
APDU_COMMAND_ERROR = bytes([0x09])
APDU_SELECT = bytearray([0x00,  # CLA
                         0xA4,  # INS
                         0x04,  # P1
                         0x00,  # P2
                         0x07,  # Length of AID
                         0xF1, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06,  # AID defined on Android App
                         0x00  # Le
                         ])


def split_bytes(data: bytearray, split_size: int = 94) -> deque:
    """
    Split bytearray into list of shorter ByteArrays to send via PN532
    :param data:
    :param split_size:
    :return: reversed and split ArrayList of ByteArray
    """
    buffer = deque()
    buffer.append(APDU_COMMAND_END_OF_MESSAGE)
    while len(data) > 0:
        length = len(data)
        part = data[length - split_size:length]
        buffer.append(bytearray(part))
        del data[length - split_size:length]
    buffer.append(APDU_COMMAND_FROM_ATM)
    return buffer


class NfcService:
    nfc: Pn532

    def __init__(self, nfc: Pn532):
        self.nfc = nfc

    def listen_for_connection(self, callback):
        print("Searching for Android device")
        while True:
            yield
            success = self.nfc.inListPassiveTarget()
            if success:
                print("Found something!")
                success, response = self.nfc.inDataExchange(APDU_SELECT)
                if success and len(response) != 62 and response == APDU_COMMAND_CONNECTED:
                    print("Connected")
                    callback(self)
                else:
                    print("Not connected")

    def send_to_client(self, data: dict):
        """Отправляет пакет данных на устройство клиента
        :param data: пакет данных, который будет отправлен на устройство клиента
        """

        buff = cbor.dumps(data)
        send_buffer = split_bytes(bytearray(buff))
        while len(send_buffer) > 0:
            bytes_to_send = send_buffer.pop()
            while True:
                success, response = self.nfc.inDataExchange(bytes_to_send)
                if response == APDU_COMMAND_RECEIVED:
                    break
        return

    def receive_from_client(self) -> bytearray:
        """Ожидает пакет данных от устройства клиента
        :return: пакет данных, который пришел с устройства клиента
        """
        receive_buffer = bytearray()
        while True:
            success, response = self.nfc.inDataExchange(APDU_COMMAND_REQUEST)
            if success and response == APDU_COMMAND_FROM_CLIENT:
                while True:
                    success, received_bytes = self.nfc.inDataExchange(APDU_COMMAND_REQUEST)
                    if received_bytes == APDU_COMMAND_END_OF_MESSAGE:
                        return receive_buffer
                    else:
                        receive_buffer.extend(received_bytes)


class NfcServiceFactory:
    @staticmethod
    def create_nfc_socket() -> NfcService:
        # Set the desired interface to True
        SPI = False
        I2C = False
        HSU = True

        if HSU:
            pn532_hsu = Pn532Hsu(Pn532Hsu.RPI_MINI_UART)
            nfc = Pn532(pn532_hsu)

        elif SPI:
            pn532_spi = Pn532Spi(Pn532Spi.SS0_GPIO8)
            nfc = Pn532(pn532_spi)

        elif I2C:
            pn532_i2c = Pn532I2c(1)
            nfc = Pn532(pn532_i2c)

        nfc.begin()
        versiondata = nfc.getFirmwareVersion()
        if not versiondata:
            print("Didn't find PN53x board")
            raise RuntimeError("Didn't find PN53x board")  # halt
        # Got ok data, print it out!
        print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF,
                                                                    (versiondata >> 16) & 0xFF,
                                                                    (versiondata >> 8) & 0xFF))
        # Set the max number of retry attempts to read from a card
        # This prevents us from waiting forever for a card, which is
        # the default behaviour of the PN532.
        # nfc.setPassiveActivationRetries(0xFF)

        nfc.SAMConfig()
        return NfcService(nfc)
