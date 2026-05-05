# Automated Desk Plant Watering System

**Zack Leffler | ELT2720 | Vermont State University**

An automated watering system for a desk plant. A Raspberry Pi 3A+ running Node-RED monitors soil moisture and automatically activates a pump when the soil is dry. Safety interlocks prevent watering if the reservoir is empty or a spill is detected. A 16×2 LCD and web dashboard display live system status.

---

## Features

- Automatic watering when soil moisture drops below 40%
- Ultrasonic water level monitoring with low-water lockout
- Spill detection with immediate pump shutoff
- Manual override button (respects safety interlocks)
- 16×2 LCD with contextual status display
- FlowFuse Dashboard 2.0 web UI with live gauges

---

## Hardware

| Component | Part | Notes |
|---|---|---|
| Controller | Raspberry Pi 3A+ | Running Node-RED |
| PCB | Custom HAT (JLCPCB) | Self-soldered |
| Soil sensor | Adafruit STEMMA ADA4026 | I2C @ 0x36 |
| Water level | RCWL-1601 ultrasonic | GPIO TRIG/ECHO |
| Spill sensor | Adafruit ADA4965 | GPIO input |
| LCD | Adafruit 16×2 ADA1447 + ADA292 backpack | I2C @ 0x27 |
| Pump | DaToo 3W 5V submersible | MOSFET-switched |
| MOSFET | AO3400A SOT-23 N-channel | Pump gate driver |
| Diode | 1N4001 | Flyback protection |
| Reservoir | Cambro RFS6PP190 6-qt round | Radius 12.6 cm |

---

## GPIO Pin Assignments

| Signal | GPIO | Pin |
|---|---|---|
| Spill sensor input | GPIO17 | 11 |
| Status LED output | GPIO23 | 16 |
| Manual button input | GPIO25 | 22 |
| I2C SDA | GPIO2 | 3 |
| I2C SCL | GPIO3 | 5 |
| Ultrasonic TRIG | GPIO5 | 29 |
| Ultrasonic ECHO | GPIO6 | 31 |
| Pump MOSFET gate | GPIO12 | 32 |

---

## Software Architecture

Platform: **Node-RED** on Raspberry Pi OS Lite  
Dashboard: **FlowFuse Dashboard 2.0** at `http://<pi-ip>:1880/dashboard`  
Sensor I/O: Python scripts called via Node-RED exec nodes

### Node-RED Tabs

**1. Plant Watering System** — main logic
- Polls sensors every 30 minutes (and on startup)
- Soil: `soil_read.py` → scaled 200–2000 raw to 0–100%
- Water level: `distance_read.py` → distance converted to %
- Spill: GPIO17, stored to global context
- Safety gate blocks pump if any interlock fails
- Pump cycle: 5 s ON then OFF, re-entry guard prevents overlap

**2. Dashboard** — display only
- Soil moisture gauge and tank level gauge
- Status text: Pump, Spill, Water Level, Last Watered
- Receives raw values from main tab; all formatting done here

**3. LCD**
- Triggered on any sensor update, debounced to 1 msg/2 s
- Contextual display:

| State | Line 1 | Line 2 |
|---|---|---|
| Normal | `Soil: XX%` | `Tank: XX%` |
| Watering | `Watering...` | `Tank: XX%` |
| Low water | `Refill Tank!` | `Tank: XX%` |
| Spill | `SPILL DETECTED!` | `Pump OFF` |

---

## Safety Logic

Three conditions must all pass before the pump will run:

1. **Spill check** — `spill_detected` must be `false`
2. **Low water check** — water level must be ≥ 10%
3. **Soil check** — soil moisture must be < 40%

All three are stored in Node-RED global context. On startup, all values are `undefined`, causing the safety gate to block watering until valid sensor readings arrive — intentional fail-safe behavior.

Manual override bypasses the soil check only. Spill and low-water locks are always enforced.

---

## Python Scripts

### `soil_read.py`
Reads the Adafruit Seesaw sensor via `adafruit_seesaw`. Prints raw moisture value (200 = dry, 2000 = wet) to stdout. Node-RED scales this to 0–100%.

### `distance_read.py`
Reads the RCWL-1601 via GPIO TRIG/ECHO. Takes a 10-pulse median using `time.perf_counter()` for nanosecond timing resolution. Prints distance in cm to stdout.

### `lcd_write.py`
Drives the ADA1447 LCD via PCF8574 I2C backpack using raw `smbus2`. Accepts two command-line arguments.

```bash
python3 lcd_write.py "Soil: 42%" "Tank: 78%"
```

---

## Setup

### Dependencies

```bash
pip install smbus2 adafruit-circuitpython-seesaw
```

### Node-RED packages (install in `~/.node-red`)

```bash
npm install @flowfuse/node-red-dashboard
npm install node-red-node-pi-gpio
```

### Deploy flows

1. Copy Python scripts to `/home/<user>/`
2. Import `flows-28.json` into Node-RED
3. Deploy and verify sensor readings in the debug sidebar

---

## Known Issues

- **LCD contrast** — LCD is powered at 3.3V; a 1 kΩ resistor from V0 to GND compensates. Next board revision should run at 5V with I2C level shifting.
- **I2C pull-ups** — HAT resistors R5/R6 are DNP; Pi internal pull-ups and the backpack are sufficient.
- **Soil sensor wiring** — JST pinout (GND, VIN, SDA, SCL) does not match HAT J3 (3.3V, GND, SCL, SDA). Crossover cable required on all 4 pins.
- **Ultrasonic blind zone** — RCWL-1601 has a ~0-2.5 cm blind zone. Reduces available tank space.
