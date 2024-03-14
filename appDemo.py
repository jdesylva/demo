import socket
import time, sys
import json, csv
import pandas as pd
import sendemail

import tkinter as tk
import tkinter.messagebox as messagebox

from tkinter import simpledialog 

from periListe import peripheriquesListe as pl
import supportAppDemo as sad
import mqttclient


class appDemo:

    root = None
    lafin = False
    sad.message_recu = None
    photo = None
    almRouge = None
    almVert = None
    mqtt_client = None
    adresseIP = None
    port = None
    labels = list()

    def __init__(self, geo="1000x700+225+150", confFile="demolora.json"):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

        with open(confFile, 'r') as file:
            self.parametres = json.load(file)

        self.adresseIP = self.parametres['adresse_serveur_mqtt']
        self.port = self.parametres['port_tcp_serveur_mqtt']

        self.email_sender = self.parametres['email_sender']
        self.app_password = self.parametres['app_password']
        sad.debug = self.parametres['debug']
        
        print("Veuillez patienter, mise en route du programme en cours")
        self.root = tk.Tk()
        self.root.geometry(geo)
        #self.root.resizable(False, False)
        #self.root.attributes('-fullscreen',True)
        self.root.minsize(1000, 700)
        self.root.title("Cégep Joliette Télécom@" + str(socket.gethostname()))
        self.root.wm_attributes('-alpha', 0.75)
        #self.root.overrideredirect(True)  # Remove window borders
        #self.root.wait_visibility(self.root)

        try :

            self.almRouge = tk.PhotoImage(file="almRouge.png")
            self.almVerte = tk.PhotoImage(file="almVerte.png")
            self.photo = tk.PhotoImage(file="logodemo_t.png")

            # Load the custom icon image
            icon_image = tk.PhotoImage(file="iconeDemo.png")

            # Set the custom icon for the window titlebar
            self.root.iconphoto(False, icon_image)

        except Exception as excpt:
            
            print("Fichiers des images manquants!")
            print("Erreur : ", excpt)
            sys.exit()

        # Relier notre client à l'interface MQTT de notre serveur ChirpStack
        mqtt_client = mqttclient.mqttclient("demolora.json")
        mqtt_client.connect()

        # Get the current screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # get the width and height of the image
        image_width = self.photo.width()
        image_height = self.photo.height()

        self.Header = tk.Label(self.root, image=self.photo, width=image_width, height=image_height)
        self.Header.place(relx=0.5, rely=0.03, anchor=tk.N)

        self.Header.bind("<Button-1>", self.buttonLogoClick)
        self.Header.bind("<Configure>", self.on_window_resize)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        heure = time.localtime() # get struct_time
        time_string = time.strftime("%Y%m%d %H:%M", heure)

        self.lblDate = tk.Label(self.root, anchor="w")                          # Entete
        self.lblDate.place(relx=0.05, rely=0.3, height=27, width=225)
        self.lblDate.configure(text=time_string)
        self.lblDate.configure(justify='left')
        self.lblDate.configure(font=("Courrier New", 12))

        self.lblAdresseIP = tk.Label(self.root, anchor="w")                     # Bas de page
        self.lblAdresseIP.place(relx=0.05, rely=0.95, height=23, width=225)
        self.lblAdresseIP.configure(text="Serveur " + self.adresseIP)
        self.lblAdresseIP.configure(justify='left')
        self.lblAdresseIP.configure(font=("Courrier New", 10, "bold"))
        self.lblAdresseIP.bind("<Button-1>", self.buttonAdresse)

        self.lblPortTCP = tk.Label(self.root, anchor="w")                       # Bas de page
        self.lblPortTCP.place(relx=0.25, rely=0.95, height=23, width=100)
        self.lblPortTCP.configure(text="Port " + ":" + str(self.port))
        self.lblPortTCP.configure(justify='left')
        self.lblPortTCP.configure(font=("Courrier New", 10, "bold"))
        self.lblPortTCP.bind("<Button-1>", self.buttonPort)

        self.TextDebug = tk.Text(self.root)                                     # Bas de page (debug)
        self.TextDebug.place(relx=0.05, rely=0.744, relheight=0.2, relwidth=0.877)
        self.TextDebug.configure(background="lightgrey")
        self.TextDebug.configure(font="TkTextFont")
        self.TextDebug.configure(selectbackground="#c4c4c4")
        self.TextDebug.configure(wrap="word")
        self.TextDebug.insert(tk.END, str(self.root))
        self.TextDebug.insert(tk.END, "\n")

        self.Label1 = tk.Label(self.root)                                       # Bas de page
        self.Label1.place(relx=0.05, rely=0.7, relheight=0.03, relwidth=0.2)
        self.Label1.configure(text="- - - - - ")
        self.Label1.configure(justify='left')
        self.Label1.configure(font=("Courrier New", 20))
        self.Label1.bind("<Button-1>", self.Label1Click) 
        self.labels.append(self.Label1) 

        self.lstPeripheriques = pl(self.root)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            self.IP = s.getsockname()[0]
        except:
            self.IP='127.0.0.1'
        finally:
            s.close()

    def on_configure(self, event):
        if event.width != self.width or event.height != self.height:
            self.width = event.width
            self.height = event.height
            self.resize()

    def resize(self):
        # Your resizing logic here
        print(f"Resizing to {self.width}x{self.height}")

            
    def buttonLogoClick(self, event):

        self.on_closing()

    def buttonAdresse(self, event):

        adresseIP=simpledialog.askstring("Entrée", "Donner l'adresse IP du serveur", parent=self.root)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        IP = ('localhost', 1)

        tmout = s.gettimeout()

        try:
            # On assume que le serveur mqtt devrait répondre rapidement.
            # On fixe le délai d'attente maximum à 1 seconde
            s.settimeout(1.0)
            #
            # On se relie au serveur selon la configuration actuelle
            s.connect((adresseIP, self.port))
            # Si l'adresse entrée ne répond pas, une exception sera générée et le 
            # bloc "try:" va se terminé ici avec une exception.
            # On sauve donc l'adresse dans l'attribut de la classe.
            self.adresseIP = adresseIP
            # On met à jour l'interface utilisateur avec la nouvelle adresse IP.
            self.lblAdresseIP.configure(text="Serveur : " + str(adresseIP))

            # On traite le cas où le progrmme est déjà relié à un serveur
            if None != self.mqtt_client:
                self.mqtt_client.disconnect()
                
            # Relier notre client à l'interface MQTT du serveur ChirpStack.
            # On passe en paramètre le nom du fichier de configuration json.
            self.mqtt_client = mqttclient.mqttclient("demolora.json")

            self.lblPortTCP.configure(text=str(self.port), fg='black')
            # On mémorise la nouvelle adresse (debug)
            IP = adresseIP

        except:
            # On mémorise l'adresse localhost si il y a une exception
            IP = ('127.0.0.1', 1)
            # On indique dans le GUI qu'il y a eu erreur avec le serveur
            self.lblAdresseIP.configure(text="Serveur : Aucun")
        finally:
            s.settimeout(tmout)
            s.close()

        print(IP)

    def buttonPort(self, event):

        port=simpledialog.askinteger("Entrée", "Donner le numéro du port TCP \nutilisé par le serveur", parent=self.root, minvalue=1, maxvalue=65535)

        if port is not None:
            self.lblPortTCP.configure(text=str(port), fg='red')
            self.port = port

        print(self.port)

    def updateTime(self):
        heure = time.localtime() # get struct_time
        time_string = time.strftime("%Y%m%d %H:%M", heure)

        self.lblDate.configure(text=time_string)

    def findGuiIndex(self, DeviceEui, type_de_donnee):
        '''
        Cette fonction retourne l'index du périphérique défini par
        le DeviceEui et le type_de_donnee reçus en paramètres. Cet
        index correspond à la ligne associée au périphérique dans
        la liste du GUI.
        '''
        for client in self.parametres['eui_clients']:
            if client == DeviceEui:
                for capteur in self.parametres['peri_clients'][client]:
                    if capteur["type"] == type_de_donnee:
                        return capteur['gui_index']
                
        return -1 # Indiquer l'erreur
        
    def findDescription(self, DeviceEui, type_de_donnee):
        for sensor in self.parametres['peri_clients'][DeviceEui]:
            if sensor['type'] == type_de_donnee :
                return sensor['label']
        return "client inconnu" # Indiquer l'erreur
    
    def findDestinataire(self, DeviceEui, type_de_donnee):
        for sensor in self.parametres['peri_clients'][DeviceEui]:
            if sensor['type'] == type_de_donnee :
                return sensor['dest_email']
        return "client inconnu" # Indiquer l'erreur
    
    def generateAlarm(self, DeviceEui, donnee, type_de_donnee):

        mGuiIndex = self.findGuiIndex(DeviceEui, type_de_donnee)
        mDescription = self.findDescription(DeviceEui, type_de_donnee)
        mDestinataire = self.findDestinataire(DeviceEui, type_de_donnee)

        if self.lstPeripheriques.alarmes[mGuiIndex] == False:
            self.lstPeripheriques.alarmes[mGuiIndex] = True
            
            sujet = "Alerte DemoLoRa ! ! !"
            msg = f"Le capteur {mDescription} a atteint la valeur {donnee}. Voulez-vous envoyer le courriel d'alarme à {mDestinataire} ?"
            if True == sad.debug:
                print(msg)
            if True == messagebox.askyesno(sujet, msg):
                msg = f"Le capteur {mDescription} a atteint la valeur {donnee}."
                sendemail.send_email(sujet, msg, self.email_sender, mDestinataire, self.app_password)
        
    def addData(self, DeviceEui, donnee, type_de_donnee):
        # Récupérer le numéro de la ligne associée à cette donnee dans la liste
        guiIndex = self.findGuiIndex(DeviceEui, type_de_donnee)
        # Mettre à jour la donnée dans la liste.
        self.lstPeripheriques.maj(guiIndex, "Valeur", str(donnee))
        # Calculer les valeurs maximale et minimale de ce capteur pour la journée présente.
        limites = self.findMinMax(DeviceEui + type_de_donnee)
        # Mettre à jour ces valeurs maximale et minimale dans la liste.
        self.lstPeripheriques.maj(guiIndex, "Min", str(limites[0]))
        self.lstPeripheriques.maj(guiIndex, "Max", str(limites[1]))

        # Vérifier les limites d'alarmes
        if float(donnee) > float(self.lstPeripheriques.getLimit(guiIndex, "sup")) or \
               float(donnee) < float(self.lstPeripheriques.getLimit(guiIndex, "inf")) :
            self.lstPeripheriques.changeImage(guiIndex, self.almRouge)
            self.generateAlarm(DeviceEui, donnee, type_de_donnee)

        # Mettre à jour l'heure de la derniere lecture dans le GUI
        self.updateTime()
            
    def run(self):

        while not self.lafin:
    
            self.root.update_idletasks()
            self.root.update()
            time.sleep(0.01)
            if sad.message_recu:
                if sad.debug:
                    print("Message reçu = " + str(sad.message_recu))
                # Pour tous les messages présents dans la queue
                while(not sad.qGui.empty()):
                    # Récupérer les données sous format JSON
                    data = sad.qGui.get()
                    data_json = json.loads(data)
                    if sad.debug :
                        print(f"data_json ==> {data_json}")

                    # Imprimer le EUI pour dépannage
                    if "devEui" in str(data) and sad.debug :
                        print("*** DEUI *** ==>" + str(data_json["devEui"]))

                    # Ajouter la mesure du capteur dans le gui.
                    devEui = data_json["devEui"]
                    for sensor in self.parametres['peri_clients'][devEui]:
                        mType = sensor['type']
                        self.addData(data_json["devEui"], data_json[mType], mType)

                sad.message_recu = None
                    
        self.root.quit()

    
    def on_closing(self):

        if messagebox.askokcancel("Terminé ?", "Est-ce que vous voulez fermer le programme ?"):

            self.lafin = True
            time.sleep(1)
            #root.destroy()
            #self.mqtt_client.disconnect()
            
    def on_window_resize(self, event):
        width = event.width
        height = event.height
        
    def Label1Click(self, event):

        self.TextDebug.delete("1.0", tk.END)

        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("%Y%m%d", named_tuple)

        filename = "rslts" + time_string + ".csv"

        try :

            with open(filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)

                for row in csv_reader:

                    print(row)
                    
                    self.TextDebug.insert(tk.END, row)
                    self.TextDebug.insert(tk.END, "\n")

        except :

            self.TextDebug.insert(tk.END, "ERREUR : Fichier " + filename + " introuvable.")
            
            
    def findMinMax(self, column):
        '''
        Cette fonction parcours le fichier des résultats de la journée en cours afin de trouver les 
        mesures minimale et maximale obtenues. Le paramètre "column" consiste en la concaténation 
        du deui du périphérique avec le type de la mesure définis dans le fichier de configuration JSON.
        Le résultat est retourné sous forme d'une liste, l'indice "0" de la liste correspond à la valeur 
        minimale et l'indice "1" de la liste correspond à la valeur maximale de la mesure au cours de 
        la journée.
        '''
        
        named_tuple = time.localtime() 
        time_string = time.strftime("%Y%m%d", named_tuple)

        filename = "rslts" + time_string + ".csv"

        lstColNames = sad.getColNames(self.parametres)
        
        try :
            
            df = pd.read_csv(filename, sep=';', names=lstColNames)
            val_min = df[column].min()
            val_max = df[column].max()

        except Exception as excpt:

            print("Erreur findMinMax : ")
            print(excpt)
            
            val_min = 0
            val_max = -1

        return [val_min, val_max]
            
            
        
