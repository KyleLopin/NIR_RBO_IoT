import os

# restart the mosquitto broker to see if it helps
# connection on startup
os.system("sudo service mosquitto stop")
os.system("xterm -hold -e 'mosquitto -v'")