#!/usr/bin/python3
import time, csv, json
import socket
import paho.mqtt.client as mqtt
import supportAppDemo as sad

#JDS
# 20240125 - Permettre la communication dans le thread principal avec le module queue
#
#sad.set_queue()
#supportAppDemo.qGui =Queue(0)

########################################################
# Référence : https://linuxembedded.fr/2023/06/realiser-une-sonnette-connectee-lora-avec-chirpstack#III.5

class mqttclient:

    parametres = None

    def __init__(self, confFile="demolora.json"):
        """
        Fonction appelée lors de la contruction de l'objet mqttclient.
        """

        # On lit le fichier json de configuration
        try:
            with open(confFile, 'r') as file:
                self.parametres = json.load(file)

            self.nom = self.parametres['nom_client']
            print(self.nom)
            self.adresse = self.parametres['adresse_serveur']
            print(self.adresse)
            self.port = self.parametres['port_tcp_serveur']
            print(self.port)
            self.keepalive = self.parametres['keepalive']
            print(self.keepalive)
        
            # AppEUI de l'application à laquelle on se relie.
            self.appeui = self.parametres['appeui']

            # Informations sur nos objets
            self.eui_client_RFM95   = self.parametres['eui_client_RFM95']
            self.eui_client_LHT65   = self.parametres['eui_client_LHT65']
        
            # Données pour communiquer avec l'interface MQTT
            self.topic_client_RFM95   = f"application/{self.appeui}/device/{self.eui_client_RFM95}/event/up"
            #TOPIC_CLIENT_RFM95   = "bidon/#"
            self.topic_client_LHT65   = f"application/{self.appeui}/device/{self.eui_client_LHT65}/event/up"
            print(self.topic_client_RFM95)
            print(self.topic_client_LHT65)

        except Exception as excpt:
            print("Erreur lors de la lecture du fichier de configuration \"" + confFile)
            print("Fin prématurée du programme.")
            print("Erreur : ", excpt)

            sys.exit()
            
        # Enregistre notre script comme client MQTT, càd comme pouvant interagir avec l'interface MQTT.
        self.my_client = mqtt.Client(self.nom)

        # Enregistrer les fonctions à appelés automatiquement lors de la connexion, déconnexion et la réception d'un message
        self.my_client.on_connect = self.on_connect_cb
        self.my_client.on_disconnect = self.on_disconnect_cb
        self.my_client.on_message = self.on_message_cb

        ### Fonctions de gestion de l'interface MQTT
    def on_disconnect_cb(self, client, userdata, return_code):
        """
        Fonction appelée lors de la déconnexion a l'interface MQTT.
        """
        del client, userdata
        if return_code :
            print("Erreur de connexion, connexion perdue. Erreur : " + str(return_code))
        else:
            print("Déconnexion")
        
    def connect(self, adresse="", port=0):
        """
        Fonction chargée de la connexion à l'interface MQTT.
        """
        if "" != adresse:
            self.adresse = adresse

        if 0 != port:
            self.port = port
            
        print("adresse : " + self.adresse + "; port : " + str(self.port) + "; keepalive : " + str(self.keepalive))
        self.my_client.loop_start()
        self.my_client.connect(self.adresse, self.port, self.keepalive)
        # Attends que la connexion soit établie
        while not self.my_client.is_connected():
            time.sleep(.1)
            
        self.my_client.subscribe(self.topic_client_RFM95)
        self.my_client.subscribe(self.topic_client_LHT65)
        
        print("MQTT client connected.")
        
    def disconnect(self):
        """
        Fonction chargée de la déconnexion à l'interface MQTT.
        """
        self.my_client.disconnect()
        self.my_client.loop_stop()

        #TYPE_TEMPERATURE_EXT = 0
        #TYPE_HUMIDITE_EXT = 1

    def on_message_cb(self, client, userdata, message):
        """
        Fonction appelée lorsque un message est reçu.
        """
        #global  application
        print("Message Recu ! ! !")
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
            deviceInfo = message_json["deviceInfo"]
            
            print("objet: ")
            print(objet_code)
            print("deviceInfo: ")
            print(deviceInfo)
            
            print("TempC_SHT: ")
            print(objet_code["TempC_SHT"])
            print("Hum_SHT: ")
            print(objet_code["Hum_SHT"])
            print("devEUI: ")
            print(deviceInfo["devEui"])
            #sad.qGui.put("{\"TempC_SHT\":" + objet_code["TempC_SHT"] + "}")
            #sad.qGui.put("{\"Hum_SHT\":" + objet_code["Hum_SHT"] + "}")
            #strData = "{\"devEui\":" + objet_code["devEui"] + ", \"devEui\":" + deviceInfo["devEui"] + ", \"Hum_SHT\":" + objet_code["Hum_SHT"] + "}"
            strData = "{\"devEui\":\"" + deviceInfo["devEui"] + "\", \"TempC_SHT\":" + objet_code["TempC_SHT"] + ", \"Hum_SHT\":" + objet_code["Hum_SHT"] + "}"
            #sad.qGui.put("{\"devEui\":" + objet_code["devEui"] + "}")
            #sad.qGui.put("{\"TempC_SHT\":" + objet_code["TempC_SHT"] + "}")
            #sad.qGui.put("{\"Hum_SHT\":" + objet_code["Hum_SHT"] + "}")
            sad.qGui.put(strData)

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
        

    def on_connect_cb(self, client, userdata, flags, return_code):
        """
        Fonction appelée lors de la connexion a l'interface MQTT.
        """
        del client, userdata, flags
        if return_code == 0:
            print("Connexion établie")
        else:
            print("Échec de connexion")
            sys.exit(-1)
        
# Créer et démarrer l'application graphique
#application = demo.appDemo("1190x750+225+150", "192.168.50.200")
#application.run()

if __name__ == '__main__':
    
    sad.set_queue()
        
    mClient = mqttclient("demolora.json")
    mClient.connect()

    while(True):
        time.sleep(0.2)
    
