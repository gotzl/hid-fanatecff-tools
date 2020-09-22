This project helps to access the sysfs functions of the [hid-fanatecff](https://github.com/gotzl/hid-fanatecff) driver and aims to connect games with the (extended) features of the CSL Elite Wheel. It is *not* needed for force-feedback to work.

## DBus service
To give unpriviledged users access to the extended features of the wheel, a DBus service is installed which accesses the drivers sysfs.
The following calls are currently implemented:
* write display value
* write LED staus
* write load cell value

## Communication with games
In Windows, games access the extended features of the wheel via the `Fanatec SDK`. Atm, it is unclear to me how to extract the calls of the SDK and how to propagate them through wine, or how to find out how the SDK detects and communicates with the wheel in first place.

To get some blinking lights on the wheel anyways a possibility is to utilize the telemetry data that some games expose. This is what the `fanatec_led_server.py` is for. It communicates via DBus with the driver and starts clients/servers that connect to the telemetry data of some games. Currently, only `Assetto Corsa` and `F1 2020` are supported.