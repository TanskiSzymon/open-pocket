# Related work and what we take from it

Reviewed 2026-10-13.

## 1. Pocket AI recorder teardown (amitk.io)

https://www.amitk.io/teardown-pocket-ai-recorder/

What is inside the original:

| part | role | note |
|---|---|---|
| Telink-marked SoC (exact model unknown) | BLE and control | not an ESP32 |
| Lyncic LX DBP805 60810 | audio acquisition / codec | |
| Kingston EMMC128-TY29 | eMMC storage | vendor says 64 GB, unverified |
| Winbond 25Q64JV | 8 MiB NOR flash, firmware | |
| RGBW SMD LED | status | |
| battery 3.8 V, 840 mAh, 3.192 Wh, cell code **265448** | | **2.6 mm thick**, 54 × 48 mm, fills most of the enclosure |
| PCB ~55 × 30 mm | | test pads TX, RX, GND, USB DP/DN, EN, 3.3 V, GPIO4/19/20/21/22 |

USB-C only charges in normal use; mass storage is enabled by an app command.
No hardware for on-device AI: the recorder is a front end for the phone and
the cloud, exactly like our v0 design assumes.

Takeaways:
- Thinness comes from a 2.6 mm pouch cell and a bare PCB, not from exotic
  parts. Our "Slim" and custom-PCB variants should start from a 2.6–3 mm
  cell (~800 mAh), not from 603450.
- Mics, antenna, magnets and the enclosure were not documented; nothing to
  copy there.

## 2. pocket-libre (shahcolate/pocket-libre)

https://github.com/shahcolate/pocket-libre — Python, MIT, 62 commits,
34 stars, tests and CI. Replaces the vendor app: downloads recordings over
BLE or Wi-Fi, transcribes locally with Whisper, diarizes with pyannote,
optional summaries with the user's own Anthropic key. Its `PROTOCOL.md` is a
complete reverse-engineered description of the device protocol (firmware
1.3.3 / 1.7 / 1.8):

- BLE GATT, ASCII frames: client `APP&<CMD>`, device `MCU&<REPLY>`
  (`APP&BAT` → `MCU&BAT&58`). Command service `001120A0`, commands written
  to `001120A2` / `001120A3`, audio notifications on `001120A1`, replies on
  `001120A3`. One BLE connection at a time. Advertised services `5536`, `2222`.
- Session key: `APP&SK&<16 chars>` → `MCU&SK&OK|ERR`. After a hardware reset
  the device accepts the first key it sees. No encryption, no BLE pairing.
- Commands: `BAT`, `FW`, `WF`, `SPACE`, `STE`, `T&YYYYMMDDHHmmss`, `MAC`,
  `LIST_DIRS`, `LIST&<date>`, `U&<date>&<name>` (download), `D&<date>&<name>`
  (delete), `USB&0|1` (mass storage), `WIFIO`/`WIFI`/`WIFIS`/`WIFIC`/`WPING`
  (AP transfer), unsolicited `STA&<name>`, `STO`, `REC&CON|CALL`.
- BLE download: raw file in 244-byte notifications, `MCU&U&<size>` first,
  `MCU&OFF` at the end, 26–67 KB/s, no checksum.
- Wi-Fi: device raises a hidden WPA2 AP `PKT01_GREY_XXXXXXXX`, password =
  first 8 characters of the session key, device 192.168.200.1, DHCP for
  .2, TCP port 8475, raw bytes + 10-byte end marker, 1–2 transfers per AP
  session.
- Audio: **MP3, 16 kHz, mono, 32 kbps CBR**, 144-byte frames starting
  `FF F3 48 C4`, 4000 bytes per second. Names `YYYYMMDDHHmmss` (UTC start).

Takeaways (adopted, see `design-spec.md` and `firmware-spec.md`):
- **OpenPocket firmware speaks this protocol.** Then pocket-libre is our
  desktop client on day one and the "laptop receiver" we had out of scope is
  already written, tested and maintained by someone else.
- The original records **mono**. Two mics are for noise reduction, not
  stereo. We keep two mics (55 mm baseline) and produce mono.
- 32 kbps MP3 is 14 MB per hour: a 32 GB card holds months. Transfer time
  over BLE is ~1–2 min per hour of audio, over Wi-Fi seconds.
- We can be better than the original where it is weak: BLE LE Secure
  Connections pairing and an encrypted link as an opt-in extension, while
  the plain protocol stays available for compatibility.

## 3. heypocket-own-pipeline (Cyvid7-Darus10)

https://github.com/Cyvid7-Darus10/heypocket-own-pipeline — documentation
only, one commit, no code. Confirms that USB mass storage exposes a `RECORD`
folder of plain MP3 files. Nothing else to take.
