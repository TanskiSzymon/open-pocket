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
- Storage: microSD on the SparkFun breakout over SPI (CS D5/GPIO6, SCK
  D8/GPIO7, MISO D9/GPIO8, MOSI D10/GPIO9), FAT32. 4 KB/s of MP3 is far
  below SPI SD throughput. Directory layout identical to the original:
  `RECORD/YYYYMMDD/YYYYMMDDHHmmss.mp3`.
- Audio in: two SPH0645 on one I2S bus (BCLK GPIO2, LRCL GPIO3, DOUT GPIO4),
  32-bit frames, left = mic 1 (SEL→GND), right = mic 2 (SEL→3V3), 16 kHz.
- Audio out to file: MP3 16 kHz mono 32 kbps CBR via `esp_audio_codec`
  (Espressif MP3 encoder), 144-byte frames, matching the original stream
  byte-for-byte in format so pocket-libre's size accounting
  (4000 bytes/s) holds.
- Mono from two mics, v0: average of the two channels after per-channel DC
  removal and gain match. Later: delay-and-sum or a simple two-mic noise
  reducer; the 27 mm baseline is kept for that.

## Controls and indication

- Side button (D7 / GPIO44, active low, internal pull-up):
  - short press: start / stop recording (`MCU&STA&<name>` / `MCU&STO` to a
    connected client).
  - hold 3 s while idle: toggle BLE advertising on/off (airplane mode).
  - hold 10 s: hardware-style reset of the session key (same as the original
    after a reset: next `APP&SK` is accepted and stored).
- NeoPixel (D6 / GPIO43), one pixel, dimmed: breathing white idle with a
  client connected, solid red recording, blue blink BLE transfer, cyan blink
  Wi-Fi AP up, orange charging, green full, red double blink SD error.
- Haptic (D4 / GPIO5, optional): one pulse on record start, two on stop.
- Battery: VBAT divider on D0 / GPIO1 (2 × 220 kΩ), 10-sample average,
  reported by `APP&BAT` as percent from a LiPo discharge table.

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
- Deep sleep after 3 days idle; button wakes.
- Charging through the XIAO at 100 mA (~5 h).

## Test plan for unit 1

1. `pocket-libre setup` finds the device, `pair` stores a key, `status`
   shows FW and battery.
2. Record 60 s by button; file appears under `RECORD/`; `sync` downloads it
   over BLE; Whisper transcribes it.
3. `wifi-transfer` of a 10-minute file completes in < 30 s.
4. `APP&USB&1` mounts the card on the laptop.
5. 1 h recording: file size 14.4 MB ± 1 %, no dropouts, battery drop < 6 %.
