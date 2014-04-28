from sr import *
import lift, debug, time, anticollisiond, voltaged, motor, serial, pyudev

def find_motor():
    c = pyudev.Context()

    for tty in c.list_devices( subsystem="tty" ):
        p = tty.find_parent( subsystem="usb", device_type = "usb_device" )
        if p is None:
            continue

        if p["ID_VENDOR_ID"].upper() == "0403" and p["ID_MODEL_ID"].upper() == "6001":
            return tty.device_node

R = Robot()

d = debug.Debug()
v = voltaged.Voltaged(R, d)
ser = serial.Serial(find_motor())
d("hallo ich bin ein adhs programm", "main")

l = lift.Lift(R, d)

d("uund ich hab nen lift", "main")

l.daemon = True
l.start()

d("lift laeuft", "main")

l.actionFinished.wait()

d("lift is fertig", "main")

time.sleep(2)

d("ab auf rumfahr-hoehe", "main")

l.driveHeight()

d("angekommen, gib mir tokens :3", "main")

time.sleep(2)
l.tokenHeight()

d("los leg n token drunter", "main")

time.sleep(5)

if l.grabToken():
    d("omnomnom token", "main")
else:
    d("irgendwas geht da nicht du sepp..", "main")

time.sleep(5)

d("ganz rauf", "main")

l.top()

d("oben", "main")

time.sleep(5)

d("und tschuess token...", "main")

l.releaseToken()

d("token is weg, ab nach unten", "main")

time.sleep(2)

l.bottom()

d("uunnd unten", "Main")

time.sleep(1)

d("omg es geht alles", "main")