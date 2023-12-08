This project helps to access the sysfs functions of the [hid-fanatecff](https://github.com/gotzl/hid-fanatecff) driver and aims to connect games with the (extended) features of the CSL Elite Wheel. It is *not* needed for force-feedback to work.


# Usage
Checkout the repository
```
git clone --recurse-submodules https://github.com/gotzl/hid-fanatecff-tools.git 
```

To get some blinking lights on the wheel, the telemetry data that some games expose is to utilized. This is what the `fanatec_led_server.py` is for
```
cd hid-fanatecff-tools/tools
sudo ./fanatec_led_server.py --device 0005 --display speedKmh
```
Use the PID of your fanatec wheel instead of `0005`. Possible values for display are `gear (default), speedKmh`.
Press `CTRL-c` to stop the application.
The command starts a thread per supported game and waits for connection to the respective telemetry data. Currently, only a small number of games is supported and **each game requires some additional setup first**, see below.


## DBus service (!!not working yet!!)
To give unpriviledged users access to the extended features of the wheel, a DBus service is installed which accesses the drivers sysfs.
The following calls are currently implemented:
* write display value
* write LED staus
* write load cell value
* tuning menu


# Communication with games
In Windows, games access the extended features of the wheel via the `Fanatec SDK`. Atm, it is unclear to me how to extract the calls of the SDK and how to propagate them through wine, or how to find out how the SDK detects and communicates with the wheel in first place.

However, many games offer telemetry vie UDP or shared memory, which is used by `fanatec_led_server.py`. See the following how to setup the games to be able to communicate with it.

## AC
AC has a UDP endpoint running per default, nothing todo here :)

Note: AC lacks support for MAX RPMs and a fixed value of 8000 is used.

## ACC
ACC makes use of what's called `named-mapping` in windows. These `named-mappings` have to be bridged to linux. See the `tools/pyacc/README` on how to setup ACC.

## RF2
For RF2, there is a [plugin that creates `named-mappings`](https://github.com/schlegp/rF2SharedMemoryMapPlugin_Wine/blob/master/build) which has to be installed first (it's a fork of [this](https://forum.studio-397.com/index.php?threads/rf2-shared-memory-tools-for-developers.54282/) and creates `named-mappings` directly in `/dev/shm/`). The procedure is the same as for using [TinyPedal](https://github.com/s-victor/TinyPedal) in Linux. (don't forget to activate the plugin in-game after installation)

## F1 2020
F1 2020 sends telemetry via UDP. This has to be activated in-game, for instance in the pause menu there is a 'telemetry' section. The defaults are sufficient.

Note: F1 2020 lacks support for TC-in-action/ABS-in-action.

## WRC
WRC sends telemetry via UDP, [see this for full information](https://answers.ea.com/t5/Guides-Documentation/EA-SPORTS-WRC-How-to-use-User-Datagram-Protocol-UDP-on-PC/m-p/13178407/thread-id/1).
To activate and use wiht hid-fanatecff-tools, place a file called `hid-fanatecff-tools.json` in `.../My Documents/My Games/WRC/telemetry/udp/` with the following contents:
```
{
	"versions":
	{
		"schema": 1,
		"data": 3
	},
	"id": "hid-fanatecff-tools",
	"header":
	{
		"channels": []
	},
	"packets": [
		{
			"id": "session_update",
			"channels": [
				"packet_uid",
				"shiftlights_fraction",
				"shiftlights_rpm_start",
				"shiftlights_rpm_end",
				"shiftlights_rpm_valid",
				"vehicle_gear_index",
				"vehicle_gear_index_neutral",
				"vehicle_gear_index_reverse",
				"vehicle_gear_maximum",
				"vehicle_speed",
				"vehicle_transmission_speed",
				"vehicle_engine_rpm_current",
			]
		}
	]
}
```
and modify the `packets` list in `.../My Documents/My Games/WRC/telemetry/config.json` by adding
```
			{
				"structure": "hid-fanatecff-tools",
				"packet": "session_update",
				"ip": "127.0.0.1",
				"port": 20778,
				"frequencyHz": 30,
				"bEnabled": true
			}
```


# Adding a game
The specifics for each game are located in python files with their implementation of `fanatec_led_server.Client` class. Each file can by run on its own, although the defaults for the `device` may not match your device.
If you want to add a game, easiest would be to follow an existing game that uses the same technique and start from there. Then add it in the main function of `fanatec_led_server.py`. 
