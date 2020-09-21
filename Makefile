install:
	cp dbus/org.fanatec.CSLElite.conf /etc/dbus-1/system.d/
	cp dbus/org.fanatec.CSLElite.service /usr/share/dbus-1/system-services/
	cp dbus/fanatec-input.py /usr/bin/
	# cp org.fanatec.policy /usr/share/polkit-1/actions/

uninstall:
	rm /etc/dbus-1/system.d/org.fanatec.CSLElite.conf
	rm /usr/share/dbus-1/system-services/org.fanatec.CSLElite.service
	rm /usr/bin/fanatec-input.py
	# rm /usr/share/polkit-1/actions/org.fanatec.policy
