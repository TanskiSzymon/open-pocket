# OpenPocket firmware specification (v0, not yet implemented)

Status: specification only. Szymon's decision: no firmware code until the
first unit is built. This document fixes what the firmware must do so the
hardware and BOM are final.

## Goal

Be a drop-in device for **pocket-libre** (https://github.com/shahcolate/pocket-libre):
implement the Pocket BLE / Wi-Fi / USB protocol as documented in its
`PROTOCOL.md` (firmware 1.8 behaviour), so an OpenPocket shows up in
pocket-libre as a Pocket and `sync`, `watch`, `wifi-transfer` and `delete`
work unchanged. Everything beyond that is an extension, never a deviation.

## Platform

- Seeed XIAO ESP32S3 (plain), ESP-IDF 5.x (not Arduino: we need NimBLE,
  TinyUSB MSC, SPI SD and the audio codec library together).
- Console: `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG` (or none), never UART0.
  GPIO43 (U0TXD) drives the NeoPixel and GPIO44 (U0RXD) the motor driver.
  The ROM bootloader still prints its log on U0TXD at every boot and
  deep-sleep wake, so the NeoPixel receives garbage and may flash or latch a
  random colour until the firmware writes it. Accept that flash, or burn
  `CONFIG_BOOT_ROM_LOG_ALWAYS_OFF` (eFuse, one-time) once the firmware is
  stable. Write the pixel off as the first thing after boot.
- Storage: microSD on the SparkFun breakout over SPI (CS D5/GPIO6, SCK
  D8/GPIO7, MISO D9/GPIO8, MOSI D10/GPIO9), FAT32. 10 kΩ pull-ups on CS, DO,
  DAT1 and DAT2 and 10 µF + 100 nF are fitted at the breakout. SPI clock:
  start at 10–20 MHz (80 mm of unshielded wire), raise only if the unit-1
  tests pass. 4 KB/s of MP3 is far below SPI SD throughput even at 10 MHz.
  Directory layout identical to the original:
  `RECORD/YYYYMMDD/YYYYMMDDHHmmss.mp3`.
- Audio in: two SPH0645 on one I2S bus (BCLK GPIO2, LRCL GPIO3, DOUT GPIO4),
  left = mic 1 (SEL→GND), right = mic 2 (SEL→3V3). Each mic drives DOUT
  only in its WS half and is high-Z otherwise (100 kΩ pull-down at the XIAO).
  - Capture at **32 kHz**: BCLK 2.048 MHz, 64 BCLK per frame (WS = BCLK / 64),
    32-bit slots, stereo, Philips I2S. The SPH0645 datasheet range is
    2.048–4.096 MHz; 16 kHz capture (1.024 MHz) is out of spec and close to
    the mic's 900 kHz sleep threshold.
  - Low-pass and decimate ×2 to 16 kHz before mixing and encoding.
  - SPH0645 timing quirk: the mic changes DATA on the BCLK rising edge and
    the ESP32 samples on the rising edge, which gives a one-bit shift or
    random bit errors. Sample on the falling edge (I2S RX timing setting) and
    verify the alignment on unit 1 with a 1 kHz tone (logic analyser or the
    captured waveform: no doubled amplitude, no noise floor jumps).
  - Each sample is 18 significant bits, MSB-first from bit 31 of the slot
    (the mic drives 24 bits, then floats). Take the top 18 bits and
    sign-extend: `s = ((int32_t)raw) >> 14`.
- Audio out to file: MP3 16 kHz mono 32 kbps CBR via `esp_audio_codec`
  (Espressif MP3 encoder), 144-byte frames, matching the original stream
  byte-for-byte in format so pocket-libre's size accounting
  (4000 bytes/s) holds. The 32 kHz capture is internal only; files and the
  protocol are unchanged.
- Mono from two mics, v0: average of the two channels after per-channel DC
  removal and gain match. Later: delay-and-sum or a simple two-mic noise
  reducer; the 25.5 mm baseline is kept for that.

## Controls and indication

- Side button (D4 / GPIO5, active low, internal pull-up; GPIO5 is an RTC
  GPIO, so it also wakes the chip from deep sleep via ext0 with
  `rtc_gpio_pullup_en`, see Power):
  - short press: start / stop recording (`MCU&STA&<name>` / `MCU&STO` to a
    connected client).
  - hold 3 s while idle: toggle BLE advertising on/off (airplane mode).
  - hold 10 s: hardware-style reset of the session key (same as the original
    after a reset: next `APP&SK` is accepted and stored).
- NeoPixel (D6 / GPIO43), one pixel, dimmed: breathing white idle with a
  client connected, solid red recording, blue blink BLE transfer, cyan blink
  Wi-Fi AP up, red double blink SD error. No charging / full states: the
  XIAO routes neither its charger status nor VBUS to a GPIO (the XIAO's own
  charge LED shows charging). Route CHRG/STDBY and VBUS sense to GPIOs on
  the custom PCB. The pixel runs from 3.3 V although it is rated 5 V (3.5 V
  min): colours are dimmer, check on unit 1.
- Haptic (D7 / GPIO44, optional, active high through the NPN driver; the
  10 kΩ base-emitter resistor keeps it off while the pin floats at boot):
  - record start: one pulse → wait ~250 ms for the motor to spin down →
    start I2S capture;
  - record stop: stop capture → close the file → two pulses;
  - never vibrate while capture or BLE live audio is running, and never
    during the Wi-Fi AP (3V3 / battery peak current).
  The motor and both mics sit on the same aluminium lid, so any vibration
  during capture lands in the recording. (Credit: a speech engineer's
  comment on the first design.)
- Battery: VBAT divider on D0 / GPIO1 (2 × 220 kΩ, 100 nF from D0 to GND
  so the 110 kΩ source does not upset the SAR sample), ADC1 channel 0 with
  `ADC_ATTEN_DB_12` (4.2 V / 2 = 2.1 V is above the 6 dB range) and the
  curve-fitting calibration scheme, 10-sample average, reported by `APP&BAT`
  as percent from a LiPo discharge table.

## Protocol (must match pocket-libre `PROTOCOL.md`)

- Device name `PKT01_GREY_<8 hex of MAC>` by default so pocket-libre's
  scanner finds it; configurable to `OPENPOCKET_<...>` once pocket-libre
  accepts a name pattern.
- GATT: command service `001120A0` with `001120A2` (write, commands),
  `001120A3` (write + notify, commands and replies), `001120A1` (notify,
  audio). Advertise `5536` and `2222` as the original does. One connection
  at a time. MTU 247 so audio notifications are 244 bytes.
- Frames: `APP&…` in, `MCU&…` out, ASCII, `&` separated, no terminator.
- Session key: `APP&SK&<16>` → `MCU&SK&OK` / `MCU&SK&ERR` then disconnect,
  as the original. Key stored in NVS. First key after a key reset is adopted.
- Implemented commands: `BAT`, `FW` (reports `1.8`-compatible string plus
  `-op0`), `WF`, `SPACE` (MB free/total from FATFS), `STE`, `T&…` (sets RTC,
  UTC), `MAC`, `LIST_DIRS`, `LIST&<date>`, `U&<date>&<name>`, `U&WIFI`,
  `D&<date>&<name>`, `USB&0|1`, `GET&USB`, `WIFIO`, `WIFI`, `WIFIS`,
  `WIFIC`, `WPING`. Unknown commands: ignored (the original replies nothing).
- BLE download: `MCU&U&<size>` → raw bytes in 244-byte notifications →
  `MCU&OFF`. Live audio during recording on `001120A1` for subscribed
  clients.
- Wi-Fi transfer: on `APP&WIFIO` start a hidden WPA2 AP, SSID = device name,
  password = first 8 chars of the session key, IP 192.168.200.1/24, DHCP
  lease for .2, TCP server on 8475; `WIFIS` codes 0/3/2/1 as the original;
  after `APP&U&<date>&<name>` + `APP&U&WIFI` send the file and the 10-byte
  end marker on the open socket; two transfer connections per AP session;
  `APP&WIFIC` tears it down. `WPING` keeps the AP alive; no ping for 30 s
  closes it.
- USB: `APP&USB&1` enables TinyUSB mass storage of the SD card (read-only
  while recording), `APP&USB&0` disables it. USB otherwise enumerates as
  CDC for logs (the original enumerates as nothing; pocket-libre does not
  care).
- Time: if no `APP&T` has been received since boot, recordings are named
  with the RTC anyway; the RTC is kept by the ESP32-S3 while sleeping.

## Extensions (opt-in, off by default, never break the plain protocol)

- BLE LE Secure Connections pairing + encrypted link when the client
  supports it (`APP&SEC&1` from an extended client).
- `APP&REC&1|0` to start/stop recording remotely.
- Stereo WAV recording mode `APP&FMT&WAV` for tests.
- OTA over the Wi-Fi AP (`APP&OTA`): HTTP server on 192.168.200.1:80.

## Power

- Recording: ESP32-S3 at 80 MHz with Wi-Fi/BLE modem-sleep, I2S + MP3
  encoding + SD writes ≈ 35–50 mA → 500 mAh ≈ 10–12 h.
- Idle, BLE advertising, light sleep between events: ≈ 2–4 mA → 5+ days.
- Deep sleep after 3 days idle; the button wakes it (ext0 on GPIO5, level
  low, `rtc_gpio_pullup_en(GPIO_NUM_5)` so the pull-up survives deep sleep).
- Low battery: if the VBAT divider is fitted, go to deep sleep below
  ~3.4 V so the cell's protection circuit is never the cutoff.
- Deep-sleep floor is set by loads that cannot be switched off on 3V3
  (NeoPixel quiescent current, SD card idle, mics, divider), probably
  ~1 mA against 14 µA for the XIAO alone. Measure it on unit 1 and write the
  number here. A load switch for SD + LED is on the custom PCB list.
- Keep the brownout detector on. Worst-case 3V3 load (Wi-Fi TX + SD write +
  LED) is close to the XIAO regulator's 700 mA; the motor runs from BAT+.
- Charging through the XIAO at 100 mA (~5 h).

## Recovery and flashing

The XIAO BOOT/RESET buttons are inside a screwed metal box, and with TinyUSB
MSC/CDC active the USB-Serial-JTAG auto-reset is gone. Therefore:

- a button gesture while USB is connected (e.g. hold 20 s, beyond the 10 s
  key reset; final choice at implementation) or a CDC 1200-baud touch makes
  the firmware reboot into ROM download mode (forced download boot);
- whenever MSC is off, USB enumerates as USB-Serial-JTAG so `esptool` works
  without opening the box.

## Test plan for unit 1

1. `pocket-libre setup` finds the device, `pair` stores a key, `status`
   shows FW and battery.
2. Record 60 s by button; file appears under `RECORD/`; `sync` downloads it
   over BLE; Whisper transcribes it.
3. `wifi-transfer` of a 10-minute file completes in < 30 s.
4. `APP&USB&1` mounts the card on the laptop.
5. 1 h recording: file size 14.4 MB ± 1 %, no dropouts, battery drop < 6 %.
6. 1 kHz tone at 30 cm: both channels clean, correct L/R, no one-bit
   shift (check the falling-edge sampling and the 18-bit sign extension).
7. The motor stays still through power-up, reset and deep-sleep wake; no
   motor noise in a recording started and stopped by button.
8. Deep sleep: the button wakes the device; sleep current measured.
9. Wi-Fi RSSI at 1 m and 5 m with the lid off, with the aluminium lid and
   RF window, and with a printed lid (go/no-go for the window size).
