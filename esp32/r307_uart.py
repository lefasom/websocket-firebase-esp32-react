from machine import UART
import time

uart = UART(2, baudrate=57600, tx=17, rx=16)


def send_command(packet):
    uart.read()  # Limpiar buffer
    uart.write(packet)
    time.sleep(0.5)
    return uart.read()


def get_uart():
    return uart
