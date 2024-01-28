#!/usr/bin/python3
import time, csv, json
import socket
import paho.mqtt.client as mqtt
from queue import Queue

import supportAppDemo as sad
import appDemo as demo
import mqttclient

#JDS
# 20240125 - Permettre la communication dans le thread principal avec le module queue
#
sad.set_queue()
#supportAppDemo.qGui =Queue(0)

# Relier notre client à l'interface MQTT de notre serveur ChirpStack
mqtt_client = mqttclient.mqttclient("demolora.json")
mqtt_client.connect()

# Créer et démarrer l'application graphique
application = demo.appDemo("1190x750+225+150")
application.run()

mqtt_client.disconnect()
