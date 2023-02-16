import pyb

aye = pyb.I2C (1, pyb.I2C.CONTROLLER)
x = pyb.I2C.scan (aye)

print(float(x))