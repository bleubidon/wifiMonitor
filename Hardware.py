import RPi.GPIO as GPIO
# Hardware functionality to keep in mind: due to "dtoverlay=gpio-poweroff" line in /boot/config.txt, the red led pin will be set high when the rpi will be shut down

class Hardware:
    ledGreenPin = 13
    buttonOffPin = 27  # ln on ti
    buttonTogglePin = 22  # math on ti

    triggerShutdownRpi_attr = False
    triggerToggleWifiMonitor_attr = False

    myattr = True

    def __init__(self):
        pass

    @classmethod
    def getGPIOTriggerState(cls, channel):
        return GPIO.input(channel) == GPIO.HIGH

    @classmethod
    def triggerShutdownRpi(cls, channel):
        if Hardware.getGPIOTriggerState(channel):
            Hardware.triggerShutdownRpi_attr = True

    @classmethod
    def triggerToggleWifiMonitor(cls, channel):
        if Hardware.getGPIOTriggerState(channel):
            Hardware.triggerToggleWifiMonitor_attr = True

    @classmethod
    def setupHardware(cls):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Inputs
        GPIO.setup(cls.buttonOffPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(cls.buttonOffPin, GPIO.BOTH, callback=cls.triggerShutdownRpi)
        GPIO.setup(cls.buttonTogglePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(cls.buttonTogglePin, GPIO.BOTH, callback=cls.triggerToggleWifiMonitor)
        # Outputs
        GPIO.setup(cls.ledGreenPin, GPIO.OUT, initial=GPIO.LOW)

    @classmethod
    def setLed(cls, status):
        if status not in ("on", "off"):
            return "Wrong argument"
        if status == "on":
            GPIO.output(cls.ledGreenPin, GPIO.HIGH)
        elif status == "off":
            GPIO.output(cls.ledGreenPin, GPIO.LOW)

    @classmethod
    def getButtonStatus(cls, buttonName):
        if buttonName not in ("off", "toggle"):
            return "Wrong argument"
        if buttonName == "off":
            return GPIO.input(cls.buttonOffPin)
        elif buttonName == "toggle":
            return GPIO.input(cls.buttonTogglePin)
