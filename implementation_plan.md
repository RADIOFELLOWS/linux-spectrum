# Implementation Plan for Network Discovery CLI

This project aims to extend `linux-spectrum` with the ability to locate supported spectrum analyzers on a given subnet. We will implement a discovery command, manage a list of recognized instruments and update documentation.

## 1. Network Discovery Command

* Create a new CLI command `discover` that scans a user supplied subnet (e.g. `192.168.1.0/24`).
* Iterate over IP addresses in the range and attempt to open a VISA TCP resource `TCPIP::<ip>::INSTR` on port 5025.
* For each successful connection query `*IDN?` to identify the device.
* Store and display found instruments in a table including IP, ID string and whether the device is supported.
* Consider using concurrent requests (e.g. `concurrent.futures.ThreadPoolExecutor`) for faster scanning of large subnets.

## 2. Supported Spectrum Analyzers

* Maintain a dictionary `SUPPORTED_ANALYZERS` mapping model keywords to friendly names.
* Initially include support for **Rohde & Schwarz FSV** (match `Rohde&Schwarz,FSV` in the `*IDN?` response).
* The discovery command should compare each `*IDN?` response against this list and mark recognized devices.

## 3. Error Handling and Timeouts

* Use short connection and query timeouts to avoid hanging on unreachable hosts.
* Catch `pyvisa.VisaIOError` and socket errors; treat them as "no instrument" for that IP.
* Report any unexpected exceptions but continue scanning remaining addresses.

## 4. CLI and Documentation Updates

* Expose the new `discover` command via Typer in `src/cli.py`.
* Update `README.md` with instructions and example usage.
* Correct existing typos (`repsponse` -> `response`) and harden `instrument_context` cleanup (check for `instrument` before closing).
* Decide whether to remove or implement the `linux-spectrum-gui` script; at minimum document current status.

## 5. Future Extensions

* Add more analyzers to `SUPPORTED_ANALYZERS` as needed.
* Provide unit tests for the discovery logic using mocked VISA resources.
* Explore mDNS/LXI discovery (via `zeroconf`) as an optional improvement for automatic detection without knowing the subnet range.

