#!/bin/bash

sudo cp insys.service /etc/systemd/system
sudo chmod +x /etc/systemd/system/insys.service
sudo systemctl enable insys
sudo systemctl daemon-reload
sudo systemctl start insys
sudo systemctl status insys