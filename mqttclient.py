#!/usr/bin/python3
import time, sys, csv, json
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
    eui_client = list()

    def __init__(self, confFile="demolora.json"):
        """
        Fonction appelée lors de la contruction de l'objet mqttclient. On utilise le 
        fichier "demolora.json" pour configurer les capteurs affichés dans 
        l'interface utilisateur de l'application.
        """

        # On lit le fichier json de configuration
        try:
            with open(confFile, 'r') as file:
                # On récupère le contenu du fichier dans l'objet JSON "parametres"
                self.parametres = json.load(file)
                #print(str(self.parametres))

            self.nom = self.parametres['nom_client_mqtt']
            print(self.nom)
            self.adresse_serveur_mqtt = self.parametres['adresse_serveur_mqtt']
            print(self.adresse_serveur_mqtt)
            self.port = self.parametres['port_tcp_serveur_mqtt']
            print(self.port)
            self.keepalive = self.parametres['keepalive']
            print(self.keepalive)
        
            # AppEUI de l'application à laquelle on se relie.
            self.appeui = self.parametres['appeui']

            # Informations sur nos objets
            for client in self.parametres['eui_clients'] :
                client['topic']=f"application/{self.appeui}/device/{client['eui']}/event/up"
                print("==>" + str(client))
                self.eui_client.append(client)
                
            print("Liste ==>" + str(self.eui_client))
            
        except Exception as excpt:
            print("Erreur lors de la lecture du fichier de configuration \"" + confFile)
            print("Fin prématurée du programme.")
            print("Erreur : ", excpt)

            sys.exit()
            
        # Enregistre notre script comme client MQTT, càd comme pouvant interagir avec l'interface MQTT.
        self.my_client = mqtt.Client(self.nom)

        # Enregistrer les fonctions à appeler automatiquement lors de la connexion, déconnexion et la réception d'un message
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
            self.adresse_serveur_mqtt = adresse
        elif self.parametres['adresse_serveur_mqtt'] != "" :
            self.adresse_serveur_mqtt = self.parametres['adresse_serveur_mqtt']
        else :
            print("Erreur! Vous devez fournir l'adresse du serveur MQTT soit sur la ligne de commande, soit dans le fichier \"demolora.json\"")
            sys.exit(0)
        
        if 0 != port:
            self.port = port
            
        print("adresse : " + self.adresse_serveur_mqtt + "; port : " + str(self.port) + "; keepalive : " + str(self.keepalive))
        self.my_client.loop_start()
        self.my_client.connect(self.adresse_serveur_mqtt, self.port, self.keepalive)
        # Attends que la connexion soit établie
        while not self.my_client.is_connected():
            time.sleep(.1)
            
        for client in self.parametres['eui_clients'] :
            print("Thème ==>" + str(client['topic']))
            self.my_client.subscribe(client['topic'])
        
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
        print("Message MQTT Recu ! ! !")
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

        try :  # On décode le message 
            objet_code = message_json["object"]
            deviceInfo = message_json["deviceInfo"]
            
            print("objet: ")
            print(objet_code)
            print("deviceInfo: ")
            print(deviceInfo)

            print("BatV: ")
            print(str(objet_code["BatV"] * 100))
            
            print("data_0: ")
            print(objet_code["data_0"])
            print("data_1: ")
            print(objet_code["data_1"])
            print("devEUI: ")
            print(deviceInfo["devEui"])
            strData = "{\"devEui\":\"" + deviceInfo["devEui"] + "\", \"BatV\":\"" + str(int(objet_code["BatV"] * 100)) + "\", \"data_0\":" + objet_code["data_0"] + ", \"data_1\":" + objet_code["data_1"] + "}"
            sad.qGui.put(strData)

            named_tuple = time.localtime() # get struct_time
            time_string = time.strftime("%Y%m%d", named_tuple)

            filename = "rslts" + time_string + ".csv"

            with open(filename, 'a', newline='') as csvwritefile:
                f_resultats = csv.writer(csvwritefile, delimiter=';',
                                          quotechar='', quoting=csv.QUOTE_NONE)

                time_string = time.strftime("%H:%M:%S", named_tuple)

                if "a840411261881bc6" == deviceInfo["devEui"] : 
                    f_resultats.writerow([time_string, objet_code["data_0"], objet_code["data_1"], "", "", 'Alarme'])
                elif "df625857c791302f" == deviceInfo["devEui"] : 
                    f_resultats.writerow([time_string,"", "", objet_code["data_0"], objet_code["data_1"], 'Alarme'])
                    
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
    
