# Integrate SENEC Hybrid Home Battery with Charge HQ
Script run on local network with SENEC.Home V3 installed (apparently should also work on most other Senec system but I am not 100%). The output is a JSON payload to be pushed to Charge HQ API to enable solar-aware EV charging using only excess solar power. 

The only changes necessary is to alter the local IP address of the SENEC battery (should be printed on the LCD display of the battery) in config.ini, and to insert the API key which is obtained via Charge HQ (see instruction in link below)

You would need to run this on a standalone server e.g. a Raspberry Pi. 

senec.py based on https://gist.github.com/smashnet/82ad0b9d7f0ba2e5098e6649ba08f88a

More info about Charge HQ Push API at https://chargehq.net/kb/push-api
