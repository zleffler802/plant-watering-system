import smbus2, sys, time

I2C_ADDR = 0x27
bus = smbus2.SMBus(1)

# PCF8574 bit masks (no registers — write_byte directly)
RS = 0x01
# RW = 0x02  (tied low, not used)
EN = 0x04
BL = 0x08  # backlight
D4 = 0x10; D5 = 0x20; D6 = 0x40; D7 = 0x80

def write_byte(v):
    bus.write_byte(I2C_ADDR, v)

def pulse(v):
    # Backlight always on; strobe EN high then low
    write_byte(v | BL)
    write_byte(v | BL | EN)
    write_byte(v | BL)

def nibble(byte_, rs):
    v = 0
    if rs:           v |= RS
    if byte_ & 0x10: v |= D4
    if byte_ & 0x20: v |= D5
    if byte_ & 0x40: v |= D6
    if byte_ & 0x80: v |= D7
    return v

def send_byte(byte_, rs):
    # Send high nibble then low nibble
    pulse(nibble(byte_,      rs))
    pulse(nibble(byte_ << 4, rs))

def cmd(c):  send_byte(c, False)
def char(c): send_byte(ord(c), True)

def write_line(text, row):
    offsets = [0x00, 0x40]
    cmd(0x80 | offsets[row])
    for ch in text[:16].ljust(16):
        char(ch)

# HD44780 4-bit init sequence
time.sleep(0.05)
for _ in range(3):
    pulse(D4 | D5)          # 0x30 in 8-bit mode
pulse(D5)                   # switch to 4-bit (0x20)
time.sleep(0.005)
cmd(0x28)                   # 2 lines, 5x8 font
cmd(0x08)                   # display off
cmd(0x01)                   # clear display
time.sleep(0.002)
cmd(0x06)                   # entry mode: increment, no shift
cmd(0x0C)                   # display on, cursor off, blink off

# Parse args: python3 lcd_write.py "line1" "line2"
args = sys.argv[1:]
line1 = args[0] if len(args) > 0 else "Hello World!"
line2 = args[1] if len(args) > 1 else "ELT-2720"

write_line(line1, 0)
write_line(line2, 1)
print("OK", flush=True)
