install:
	@echo -e "\n::\033[34m Installing Fanatec tools\033[0m"
	@echo "====================================================="
	@cp -v  dbus/org.fanatec.conf /etc/dbus-1/system.d/
	@cp -v  dbus/org.fanatec.service /usr/share/dbus-1/system-services/
	@cp -v  dbus/fanatec_input.py /usr/bin/
	@cp -v  dbus/fanatec-input.systemd.service /lib/systemd/system/fanatec-input.service
	@ln -sf fanatec-input.service /lib/systemd/system/dbus-org.fanatec.service
	# cp org.fanatec.policy /usr/share/polkit-1/actions/

uninstall:
	@echo -e "\n::\033[34m Uninstalling Fanatec tools\033[0m"
	@echo "====================================================="
	@rm -fv  /etc/dbus-1/system.d/org.fanatec.conf
	@rm -fv  /usr/share/dbus-1/system-services/org.fanatec.service
	@rm -fv  /usr/bin/fanatec-input.py
	@rm -fr  /lib/systemd/system/fanatec-input.service /lib/systemd/system/dbus-org.fanatec.service
	# rm /usr/share/polkit-1/actions/org.fanatec.policy
