#!/usr/bin/sh
#Installation script for raspbian OS

#Run the following 2 lines in a terminal in this folder to convert and execute the shell script
#sudo chmod u+x ./raspbian_install.sh
#./raspbian_install.sh

pip3 install -r requirements.txt --no-warn-script-location
pip3 uninstall -y numpy
sudo apt install python3-pyqt5 pyqthon3-numpy
