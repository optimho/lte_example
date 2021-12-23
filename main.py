import time
from machine import RTC
from network import LTE

NTP_SERVER = "au.pool.ntp.org"

# Need to use global variables.
# If in each function you delare a new reference, functionality is broken
lte = LTE()
rtc = RTC()

# Returns a network.LTE object with an active Internet connection.


def getLTE():

    # If already used, the lte device will have an active connection.
    # If not, need to set up a new connection.
    if lte.isconnected():
        return lte

    # Modem does not connect successfully without first being reset.
    print("Resetting LTE modem ... ", end='')
    lte.send_at_cmd('AT^RESET')
    print("OK")
    time.sleep(1)

    # While the configuration of the CGDCONT register survives resets,
    # the other configurations don't. So just set them all up every time.
    print("Configuring LTE ", end='')
    lte.send_at_cmd('AT+CGDCONT=1,"IP","hologram"')
    print(".", end='')
    lte.send_at_cmd('AT!="RRC::addscanfreq band=28 dl-earfcn=9410"')
    print(".", end='')
    lte.send_at_cmd('AT+CFUN=1')
    print(" OK")

    # If correctly configured for carrier network, attach() should succeed.
    if not lte.isattached():
        print("Attaching to LTE network ", end='')
        lte.attach()
        while(True):
            if lte.isattached():
                print(" OK")
                break
            print('.', end='')
            time.sleep(1)

    # Once attached, connect() should succeed.
    if not lte.isconnected():
        print("Connecting on LTE network ", end='')
        lte.connect()
        while(True):
            if lte.isconnected():
                print(" OK")
                break
            print('.', end='')
            time.sleep(1)

    # Once connect() succeeds, any call requiring Internet access will
    # use the active LTE connection.
    return lte

# Clean disconnection of the LTE network is required for future
# successful connections without a complete power cycle between.


def endLTE():

    print("Disonnecting LTE ... ", end='')
    lte.disconnect()
    print("OK")
    time.sleep(1)
    print("Detaching LTE ... ", end='')
    lte.dettach()
    print("OK")

# Sets the internal real-time clock.
# Needs LTE for Internet access.


def setRTC():

    # Ensures LTE session is connected before attempting NTP sync.
    lte = getLTE()

    print("Updating RTC from {} ".format(NTP_SERVER), end='')
    rtc.ntp_sync(NTP_SERVER)
    while not rtc.synced():
        print('.', end='')
        time.sleep(1)
    print(' OK')

# Only returns an RTC object that has already been synchronised with an NTP server.


def getRTC():

    if not rtc.synced():
        setRTC()
    setRTC()
    return rtc


# Program starts here.
try:
    print("Initially, the RTC is {}".format(
        "set" if rtc.synced() else "unset"))
    rtc = getRTC()
    while(True):
        print("RTC is {}".format(rtc.now() if rtc.synced() else "unset"))
        time.sleep(5)
        break
except Exception:
    pass  # do nothing on error

finally:
    endLTE()
