#!/usr/bin/python3

import supportAppDemo as sad
import appDemo as demo
import mqttclient

#JDS
# 20240125 - Permettre la communication dans le thread principal avec le module queue
#
sad.set_queue()

# Relier notre client à l'interface MQTT de notre serveur ChirpStack
mqtt_client = mqttclient.mqttclient("demolora1.json")
mqtt_client.connect()

# Créer et démarrer l'application graphique
application = demo.appDemo("1190x750+225+150")
application.run()

mqtt_client.disconnect()
