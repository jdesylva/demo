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
    lstTopics = list()
    
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
            self.adresse_serveur_mqtt = self.parametres['adresse_serveur_mqtt']
            self.port = self.parametres['port_tcp_serveur_mqtt']
            self.keepalive = self.parametres['keepalive']
        
            # AppEUI de l'application à laquelle on se relie.
            self.appeui = self.parametres['appeui']

            # Informations sur nos objets
            for client in self.parametres['eui_clients'] :
                self.lstTopics.append(f"application/{self.appeui}/device/{client}/event/up")
                print(f"EUI client ==> {client}")
            
        except Exception as excpt:
            print("Erreur lors de la lecture du fichier de configuration \"" + confFile)
            print("Fin prématurée du programme.")
            print("Erreur : ", excpt)

            sys.exit()
            
        # Enregistre notre script comme client MQTT, càd comme pouvant interagir avec l'interface MQTT.
        # self.my_client = mqtt.Client(self.nom) # Pour paho.mqtt versions < ???
        self.my_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.nom)

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
            
        print("Adresse du serveur : " + self.adresse_serveur_mqtt + "; port : " + str(self.port) + "; keepalive : " + str(self.keepalive))
        try:
            self.my_client.loop_start()
            self.my_client.connect(self.adresse_serveur_mqtt, self.port, self.keepalive)
            # Attends que la connexion soit établie
            i = 0
            while not self.my_client.is_connected() and i < 30 :
                time.sleep(1)
                print(".")
                i += 1

            if not self.my_client.is_connected() :
                print("Erreur : Serveur mqtt inaccessible à l'adresse ", self.adresse_serveur_mqtt )
                sys.exit(-1)
            
        except Exception as e :
            print("Erreur lors de la connexion au serveur mqtt à l'adresse ", self.adresse_serveur_mqtt )
            print(f"Erreur : {e}")
            sys.exit(-1)
        
        print(f"MQTT client relié au serveur à l'adresse {self.adresse_serveur_mqtt} en {i} seconde(s).")
        
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

            strData = "{\"devEui\":\"" + deviceInfo["devEui"] + "\", \"BatV\":\"" + str(int(objet_code["BatV"] * 100)) + "\", \"data_0\":" + objet_code["data_0"] + ", \"data_1\":" + objet_code["data_1"] + "}"
            sad.qGui.put(strData)

            named_tuple = time.localtime() # get struct_time
            time_string = time.strftime("%Y%m%d", named_tuple)
            # On inscrit les données dans le fichier CSV
            
            filename = "rslts" + time_string + ".csv"

            with open(filename, 'a', newline='') as csvwritefile:
                f_resultats = csv.writer(csvwritefile, delimiter=';',
                                          quotechar='', quoting=csv.QUOTE_NONE)

                time_string = time.strftime("%H:%M:%S", named_tuple)

                lstColonnes = sad.getColNames(self.parametres)
                lignesFichier = list()
                lignesFichier.append(time_string)
                
                # Ici on parcours la liste des noms de colonnes.
                for nomColonne in lstColonnes:
                    # et si la colonne appartient au périphérique associé à ce message
                    if nomColonne.startswith(deviceInfo["devEui"]):
                        #print(f"nomColonne : {nomColonne}")
                        #print(f"ObjectCode : {objet_code}")
                        #print(f"deviceInfo : {deviceInfo}")
                        #print("- - - - - - - - - - - - - ")
                        #print(self.parametres['peri_clients'][deviceInfo['devEui']])
                        
                        mType = nomColonne[len(deviceInfo["devEui"]): len(nomColonne)]

                        lignesFichier.append(objet_code[mType])

                    else:
                        lignesFichier.append("")
                        
                        
                f_resultats.writerow(lignesFichier)
                #print(lignesFichier)

        except Exception as excpt:
            print("Erreur de décodage des données!")
            print("Erreur : ", excpt)
        

    def on_connect_cb(self, client, userdata, flags, return_code):
        """
        Fonction appelée lors de la connexion à l'interface MQTT.
        """
        del client, userdata, flags
        if return_code == 0:
            print("Connexion établie")
            for topic in self.lstTopics :
                print("Thème ==>" + str(topic))
                self.my_client.subscribe(topic)
        else:
            print("Échec de connexion")
            sys.exit(-1)
        
