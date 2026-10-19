# Vendor models (not included)

The CAD script checks the enclosure against the real vendor STEP models of the
XIAO and the mic breakout. They are not redistributed here; download them and
put them at these paths:

| Path | Where to get it |
|---|---|
| `seeed/seeed-studio-xiao-esp32s3-3d_model/XIAO-ESP32S3 v2.step` | Seeed Studio wiki, XIAO ESP32S3 page → Resources → "3D model" (zip) |
| `adafruit/adafruit-6049-i2s-mic.step` | [adafruit/Adafruit_CAD_Parts](https://github.com/adafruit/Adafruit_CAD_Parts), the I2S MEMS mic breakout folder |

Without them `openpocket_cad.py` still builds and exports every part and runs
the fit check against simplified envelopes; it only skips the vendor-model
clash check and `openpocket-assembly.step`.
