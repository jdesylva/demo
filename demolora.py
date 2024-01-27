#!/usr/bin/python3
import time, csv, json
import socket
import paho.mqtt.client as mqtt
from queue import Queue

import supportAppDemo as sad
import appDemo as demo

lafin = False
    
#JDS
# 20240125 - Permettre la communication dans le thread principal avec le module queue
#
sad.set_queue()
#supportAppDemo.qGui =Queue(0)

########################################################
# Référence : https://linuxembedded.fr/2023/06/realiser-une-sonnette-connectee-lora-avec-chirpstack#III.5

# Données pour se connecter à l'interface MQTT de ChirpStack
NOM         = "demolora20240123"
BROKER      = "192.168.50.200"
PORT        = 1883
KEEPALIVE   = 1000
FPORT       = 1
# AppEUI de l'application à laquelle on se relie.
APPLICATION = "b750d774-16b6-4fe8-8eb0-21ea91ff3481"

# Informations sur nos objets
EUI_CLIENT_RFM95   = "212781276c01f3f0"
EUI_CLIENT_LHT65   = "a840411261881bc6"

# Données pour communiquer avec l'interface MQTT
TOPIC_CLIENT_RFM95   = f"application/{APPLICATION}/device/{EUI_CLIENT_RFM95}/event/up"
#TOPIC_CLIENT_RFM95   = "bidon/#"
TOPIC_CLIENT_LHT65   = f"application/{APPLICATION}/device/{EUI_CLIENT_LHT65}/event/up"

#TOPIC_CLIENTS   = "application/{APPLICATION}/#"
print(TOPIC_CLIENT_RFM95)
print(TOPIC_CLIENT_LHT65)

# Enregistre notre script comme client MQTT, càd comme pouvant interagir avec l'interface MQTT.
my_client = mqtt.Client(NOM)

### Fonctions de gestion de l'interface MQTT
def on_connect_cb(client, userdata, flags, return_code):
    """
        Fonction appelée lors de la connexion a l'interface MQTT.
    """
    del client, userdata, flags
    if return_code == 0:
        print("Connexion établie")
    else:
        print("Échec de connexion")
        sys.exit(-1)
        
def on_disconnect_cb(client, userdata, return_code):
    """
        Fonction appelée lors de la déconnexion a l'interface MQTT.
    """
    del client, userdata
    if return_code :
        print("Erreur de connexion, connexion perdue")
    else:
        print("Déconnexion")
    
        
def connect(client):
    """
        Fonction chargée de la connexion à l'interface MQTT.
    """
    client.loop_start()
    client.connect(BROKER, PORT, KEEPALIVE)
    # Attends que la connexion soit établie
    while not client.is_connected():
        time.sleep(.1)
        
def disconnect(client):
    """
        Fonction chargée de la déconnexion à l'interface MQTT.
    """
    client.disconnect()
    client.loop_stop()

TYPE_TEMPERATURE_EXT = 0
TYPE_HUMIDITE_EXT = 1

def on_message_cb(client, userdata, message):
    """
        Fonction appelée lorsque un message est reçu.
    """
    global  application
    
    del client, userdata
    # On prend le thème dans le paquet contenant le message.
    theme = message.topic
    # On prend le message dans le paquet le contenant.
    message = message.payload
    # On décode le message UTF8.
    message_decode = message.decode("utf-8")
    # On décode le message au format JSON.
    message_json = json.loads(message_decode)
    # On conserve le dernier message dans la variable globale.
    sad.message_recu = message_json

    try :  # On décode le message du LHT65N
        objet_code = message_json["object"]
        print("objet: ")
        print(objet_code)
        print("TempC_SHT: ")
        print(objet_code["TempC_SHT"])
        print("Hum_SHT: ")
        print(objet_code["Hum_SHT"])
        sad.qGui.put("{\"TempC_SHT\":" + objet_code["TempC_SHT"] + "}")
        sad.qGui.put("{\"Hum_SHT\":" + objet_code["Hum_SHT"] + "}")

        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("%Y%m%d", named_tuple)

        filename = "rslts" + time_string + ".csv"

        with open(filename, 'a', newline='') as csvwritefile:
            f_resultats = csv.writer(csvwritefile, delimiter=';',
                                          quotechar='', quoting=csv.QUOTE_NONE)

            #if 0 == os.stat(filename).st_size:
            #    f_resultats.writerow(['Time','TempC_SHT','Hum_SHT','Alarme'])

            time_string = time.strftime("%H:%M:%S", named_tuple)

            f_resultats.writerow([time_string, objet_code["TempC_SHT"], objet_code["Hum_SHT"], 'Alarme'])

    except Exception as excpt:
        print("Erreur de décodage des données!")
        print("Erreur : ", excpt)
        
# Enregistrer les fonctions à appelés automatiquement lors de la connexion, déconnexion et la réception d'un message
my_client.on_connect = on_connect_cb
my_client.on_disconnect = on_disconnect_cb
my_client.on_message = on_message_cb

# Relier notre client à l'interface MQTT de notre serveur ChirpStack
connect(my_client)

my_client.subscribe(TOPIC_CLIENT_RFM95)
my_client.subscribe(TOPIC_CLIENT_LHT65)

# Créer et démarrer l'application graphique
application = demo.appDemo("1190x750+225+150")
application.run()

