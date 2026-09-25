# ESPHome Geiger Counter with Home Assistant and uRADMonitor

ESPHome firmware for a NodeMCU V3 (ESP8266) connected to a RadiationD v1.1
CAJOE Geiger counter board. The ESP counts pulses locally, exposes measurements
and diagnostics to Home Assistant, and can upload CPM readings directly to
uRADMonitor without requiring Home Assistant or MQTT for the upload path.

This is an independent community project and is not affiliated with
uRADMonitor or ESPHome.

## Features

- Counts active-low Geiger pulses on `D1` / `GPIO5`.
- Publishes CPM, total pulses, and a five-minute CPM average to Home Assistant.
- Uploads uRADMonitor EXP fields `01` (Unix time) and `0B` (CPM).
- Keeps `Off`, `Test`, and `Production` modes strictly separate.
- Stores separate test and production Device IDs in ESP8266 flash.
- Defaults to `Off` on first use and later restores the deliberately selected mode.
- Registers a Device ID only after `Test` or `Production` is deliberately selected.
- Exposes upload results, counters, active Device ID, uptime, Wi-Fi signal,
  free heap, largest heap block, fragmentation, and reset reason.
- Includes a dependency-free Python mock server and a Docker Compose setup.

The implementation uses normal ESPHome YAML packages and lambdas. No custom
C++ component or external ESPHome library is required.

## Hardware and electrical safety

The reference setup uses:

- NodeMCU V3 / ESP8266
- RadiationD v1.1 CAJOE Geiger counter board
- Pulse output connected to `D1` (`GPIO5`)
- A shared ground between both boards

ESP8266 GPIO pins are **not 5 V tolerant**. Some Geiger boards and clones have
different output stages, so measure the pulse output before connecting it. If
the pulse can reach 5 V, use a level shifter or a resistor divider. A commonly
used divider is 10 kΩ from the signal to `D1` and 15 kΩ from `D1` to ground,
which reduces 5 V to approximately 3 V.

Do not connect two independent 5 V supplies to the NodeMCU at the same time
unless the power arrangement explicitly prevents back-feeding.

## Repository layout

| Path | Purpose |
| --- | --- |
| `geiger_node.yaml` | Complete example device configuration |
| `packages/geiger_core.yaml` | Pulse counter and ESP8266 diagnostics |
| `packages/urad_upload.yaml` | Registration, modes, and uploader |
| `secrets.example.yaml` | Safe template for local credentials |
| `mock/urad_mock.py` | Local uRADMonitor-compatible test endpoint |
| `mock/compose.yaml` | Optional Docker Compose deployment |

## Installation

### Option 1: use the complete example

1. Clone or download this repository into your ESPHome configuration directory.
2. Copy `secrets.example.yaml` to `secrets.yaml`.
3. Replace every placeholder in `secrets.yaml`.
4. Confirm `geiger_pin`, board type, and wiring in `geiger_node.yaml`.
5. Validate, compile, and install:

```bash
esphome config geiger_node.yaml
esphome compile geiger_node.yaml
esphome run geiger_node.yaml
```

Keep the directory structure intact because `geiger_node.yaml` includes both
files from `packages/`.

### Option 2: include the packages from GitHub

Add the following to your own device YAML:

```yaml
packages:
  geiger_uradmonitor:
    url: https://github.com/phoenix-blue/esphome-uradmonitor-geiger
    ref: main
    refresh: 1d
    files:
      - packages/geiger_core.yaml
      - packages/urad_upload.yaml
```

Remote ESPHome packages cannot look up secrets from the remote repository.
Define the required substitutions in your local YAML before including them:

```yaml
substitutions:
  geiger_pin: GPIO5
  upload_interval: 60s
  urad_upload_url: https://data.uradmonitor.com/api/v1/upload/exp/
  urad_mock_url: !secret urad_mock_url
  urad_user_id: !secret urad_user_id
  urad_user_hash: !secret urad_user_hash
```

Your local configuration must also provide an SNTP time component with the ID
`sntp_time`, plus `http_request`, `api`, Wi-Fi, and the other platform settings
shown in `geiger_node.yaml`.

See the official [ESPHome packages documentation](https://esphome.io/components/packages/)
for package syntax and merge behavior.

## Secrets and credentials

| Secret | Where to obtain or generate it |
| --- | --- |
| `wifi_ssid`, `wifi_password` | Your local Wi-Fi configuration |
| `api_encryption_key` | Generate with `openssl rand -base64 32` |
| `ota_password` | Choose a unique local OTA password |
| `fallback_ap_password` | Choose a unique fallback access-point password |
| `web_username`, `web_password` | Choose local credentials for the device web UI |
| `urad_mock_url` | Address of the included mock server |
| `urad_user_id`, `urad_user_hash` | API tab in your uRADMonitor account |

Never commit `secrets.yaml`. It is ignored by `.gitignore`. If a real key or
password is ever committed or shared, rotate it; removing it from the latest
file does not remove it from Git history.

## Safe first run

1. Install the firmware while the upload mode remains `Off`.
2. Confirm that CPM changes in Home Assistant when the counter detects pulses.
3. Start the local mock server and set the mode to `Test`.
4. Confirm automatic registration and successful test uploads.
5. Only then select `Production` to register and upload to uRADMonitor.

Test and production Device IDs are stored independently. A Device ID returned
by the mock server is therefore never reused for production.

## Local mock server

Run it directly:

```bash
cd mock
python3 urad_mock.py
```

Or use Docker Compose:

```bash
cd mock
docker compose up --build -d
```

Default endpoints:

- Health: `http://SERVER_IP:8080/health`
- Status and recent requests: `http://SERVER_IP:8080/status`
- Upload: `http://SERVER_IP:8080/api/v1/upload/exp/`

The defaults are intentionally test-only: user ID `test`, hash `test`, and
returned Device ID `13ABC001`. They can be changed with the environment
variables documented at the top of `mock/urad_mock.py`.

The mock validates authentication, registration, monotonically increasing
timestamps, field `01`, and numeric field `0B`. It can also inject delay or
periodic failures for resilience testing.

## uRADMonitor protocol behavior

Production requests use the account credentials in `X-User-id` and
`X-User-hash`, and the assigned sensor identifier in `X-Device-id`. A device
without an assigned ID first registers with reserved Device ID `13000000` and
stores the returned `setid`. Uploads then send:

- `01`: current Unix timestamp
- `0B`: current CPM

Refer to the official
[uRADMonitor open-data upload tutorial](https://www.uradmonitor.com/open-data-upload-tutorial/)
for account setup, headers, registration, and field definitions.

The production endpoint is encoded in the URL path because that form was
confirmed against the live service. The local mock uses the documented request
body form, making both behaviors easy to inspect without sending test data to
the public service.

## Home Assistant entities

The native ESPHome API exposes:

- Radiation CPM, total pulses, and five-minute average
- uRAD upload mode, active Device ID, latest result, and latest response
- Successful and failed upload counters
- Manual upload and test-ID reset buttons
- Uptime and Wi-Fi signal
- Free heap, largest free block, heap fragmentation, and reset reason

No production registration-reset button is exposed. This avoids accidentally
creating a new public device identity from the Home Assistant UI.

## ESP8266 HTTPS note

`verify_ssl: false` is deliberate. ESPHome does not support certificate
verification for `http_request` on ESP8266. The 16,384-byte receive buffer is
also deliberate because modern HTTPS servers can use TLS records of that size.
Both HTTPS and the built-in web server consume scarce ESP8266 memory, which is
why the diagnostic entities are included.

See the official
[ESPHome HTTP Request documentation](https://esphome.io/components/http_request/)
for the current platform limitations and TLS buffer guidance.

## Extending the sensor

A DS18B20 temperature probe can be added through ESPHome's OneWire components.
Supply voltage can also be measured with the ESP8266 ADC, but only through a
properly calculated divider that keeps the board's A0 input within its allowed
range. Validate memory stability before adding either feature.

## License

MIT — see [LICENSE](LICENSE).
