import socket
import time, sys
import json, csv
import pandas as pd

import tkinter as tk
import tkinter.messagebox as messagebox

from tkinter import simpledialog 

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
    
    def __init__(self, geo="1000x700+225+150", confFile="demolora.json"):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

        with open(confFile, 'r') as file:
            parametres = json.load(file)

        self.adresseIP = parametres['adresse_serveur']
        self.port = parametres['port_tcp_serveur']

        print("Veuillez patienter, mise en route du programme en cours")
        self.root = tk.Tk()
        self.root.geometry(geo)
        self.root.resizable(False, False)
        #root.attributes('-fullscreen',True)
        self.root.title("Cégep Joliette Télécom@" + str(socket.gethostname()))
        self.root.wm_attributes('-alpha', 0.85)
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

        self.Header = tk.Label(self.root, image=self.photo, width=1184, height=164)
        self.Header.place(relx=0.0, rely=0.03)
        self.Header.bind("<Button-1>", self.buttonLogoClick)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        heure = time.localtime() # get struct_time
        time_string = time.strftime("%Y%m%d %H:%M", heure)

        self.lblDate = tk.Label(self.root, anchor="w")
        self.lblDate.place(relx=0.05, rely=0.3, height=27, width=225)
        self.lblDate.configure(text=time_string)
        self.lblDate.configure(justify='left')
        self.lblDate.configure(font=("Courrier New", 12))

        self.lblAdresseIP = tk.Label(self.root, anchor="w")
        self.lblAdresseIP.place(relx=0.05, rely=0.95, height=23, width=225)
        self.lblAdresseIP.configure(text="Serveur " + self.adresseIP)
        self.lblAdresseIP.configure(justify='left')
        self.lblAdresseIP.configure(font=("Courrier New", 10, "bold"))
        self.lblAdresseIP.bind("<Button-1>", self.buttonAdresse)

        self.lblPortTCP = tk.Label(self.root, anchor="w")
        self.lblPortTCP.place(relx=0.25, rely=0.95, height=23, width=100)
        self.lblPortTCP.configure(text="Port " + ":" + str(self.port))
        self.lblPortTCP.configure(justify='left')
        self.lblPortTCP.configure(font=("Courrier New", 10, "bold"))
        self.lblPortTCP.bind("<Button-1>", self.buttonPort)

        self.TextDebug = tk.Text(self.root)
        self.TextDebug.place(relx=0.05, rely=0.744, relheight=0.2, relwidth=0.877)
        self.TextDebug.configure(background="lightgrey")
        self.TextDebug.configure(font="TkTextFont")
        self.TextDebug.configure(selectbackground="#c4c4c4")
        self.TextDebug.configure(wrap="word")
        self.TextDebug.insert(tk.END, str(self.root))
        self.TextDebug.insert(tk.END, "\n")

        self.Label1 = tk.Label(self.root)
        self.Label1.place(relx=0.0, rely=0.7, height=21, width=200)
        self.Label1.configure(text="- - - - - ")
        self.Label1.configure(justify='left')
        self.Label1.configure(font=("Courrier New", 20))
        self.Label1.bind("<Button-1>", self.Label1Click) #JDS
        print("1-")

        self.lblTemperature = tk.Label(self.root, anchor="w")
        self.lblTemperature.place(relx=0.05, rely=0.35, height=23, width=400)
        self.lblTemperature.configure(text="Données actuelles")
        self.lblTemperature.configure(justify='left')
        self.lblTemperature.configure(font=("Courrier New", 20, "bold"))

        self.lblMinimum = tk.Label(self.root, anchor="w")
        self.lblMinimum.place(relx=0.42, rely=0.35, height=23, width=200)
        self.lblMinimum.configure(text="Min.")
        self.lblMinimum.configure(justify='left')
        self.lblMinimum.configure(font=("Courrier New", 20, "bold"))

        self.lblMaximum = tk.Label(self.root, anchor="w")
        self.lblMaximum.place(relx=0.52, rely=0.35, height=23, width=200)
        self.lblMaximum.configure(text="Max.")
        self.lblMaximum.configure(justify='left')
        self.lblMaximum.configure(font=("Courrier New", 20, "bold"))

        self.lblLimitMinimum = tk.Label(self.root, anchor="w")
        self.lblLimitMinimum.place(relx=0.62, rely=0.35, height=23, width=200)
        self.lblLimitMinimum.configure(text="Limite -")
        self.lblLimitMinimum.configure(justify='left')
        self.lblLimitMinimum.configure(font=("Courrier New", 20, "bold"))

        self.lblLimitMaximum = tk.Label(self.root, anchor="w")
        self.lblLimitMaximum.place(relx=0.73, rely=0.35, height=23, width=200)
        self.lblLimitMaximum.configure(text="Limite +")
        self.lblLimitMaximum.configure(justify='left')
        self.lblLimitMaximum.configure(font=("Courrier New", 20, "bold"))

        self.lblAlarme = tk.Label(self.root, anchor="w")
        self.lblAlarme.place(relx=0.86, rely=0.35, height=23, width=200)
        self.lblAlarme.configure(text="Alarme")
        self.lblAlarme.configure(justify='left')
        self.lblAlarme.configure(font=("Courrier New", 20, "bold"))


        self.lblHumInterne = tk.Label(self.root,anchor="w")
        self.lblHumInterne.place(relx=0.05, rely=0.45, height=23, width=320)
        self.lblHumInterne.configure(text="Humidité Intérieure : ")
        self.lblHumInterne.configure(justify=tk.LEFT)
        self.lblHumInterne.configure(font=("Courrier New", 20))
        print("2-")

        self.lblHumInterneVal = tk.Label(self.root, anchor="w")
        self.lblHumInterneVal.place(relx=0.34, rely=0.45, height=23, width=200)
        self.lblHumInterneVal.configure(text="---")
        self.lblHumInterneVal.configure(justify='left')
        self.lblHumInterneVal.configure(font=("Courrier New", 20))
        print("3-")

        self.lblHumInterneAlm = tk.Label(self.root, image=self.almVerte, width=20, height=20)
        self.lblHumInterneAlm.place(relx=0.91, rely=0.45)

        self.lblHumInterneMin = tk.Label(self.root, anchor="w")
        self.lblHumInterneMin.place(relx=0.42, rely=0.45, height=23, width=200)
        self.lblHumInterneMin.configure(text="---")
        self.lblHumInterneMin.configure(justify='left')
        self.lblHumInterneMin.configure(font=("Courrier New", 20))

        self.lblHumInterneMax = tk.Label(self.root, anchor="w")
        self.lblHumInterneMax.place(relx=0.52, rely=0.45, height=23, width=200)
        self.lblHumInterneMax.configure(text="---")
        self.lblHumInterneMax.configure(justify='left')
        self.lblHumInterneMax.configure(font=("Courrier New", 20))

        self.txtHumInterneAlmMin = tk.Entry(self.root, bg="lightgrey")
        self.txtHumInterneAlmMin.place(relx=0.62, rely=0.45, height=27, width=80)
        self.txtHumInterneAlmMin.insert(0, "0")
        self.txtHumInterneAlmMin.configure(justify='left')
        self.txtHumInterneAlmMin.configure(font=("Courrier New", 20))

        self.txtHumInterneAlmMax = tk.Entry(self.root, bg="lightgrey")
        self.txtHumInterneAlmMax.place(relx=0.73, rely=0.45, height=27, width=80)
        self.txtHumInterneAlmMax.insert(0, "100")
        self.txtHumInterneAlmMax.configure(justify='left')
        self.txtHumInterneAlmMax.configure(font=("Courrier New", 20))

        self.lblTempInterne = tk.Label(self.root, anchor="w")
        self.lblTempInterne.place(relx=0.05, rely=0.4, height=23, width=340)
        self.lblTempInterne.configure(text="Température Intérieure : ")
        self.lblTempInterne.configure(justify='left')
        self.lblTempInterne.configure(font=("Courrier New", 20))
        print("4-")

        self.lblTempInterneVal = tk.Label(self.root, anchor="w")
        self.lblTempInterneVal.place(relx=0.34, rely=0.4, height=23, width=200)
        self.lblTempInterneVal.configure(text="---")
        self.lblTempInterneVal.configure(justify='left')
        self.lblTempInterneVal.configure(font=("Courrier New", 20))

        self.lblTempInterneMin = tk.Label(self.root, anchor="w")
        self.lblTempInterneMin.place(relx=0.42, rely=0.4, height=23, width=200)
        self.lblTempInterneMin.configure(text="---")
        self.lblTempInterneMin.configure(justify='left')
        self.lblTempInterneMin.configure(font=("Courrier New", 20))

        self.lblTempInterneMax = tk.Label(self.root, anchor="w")
        self.lblTempInterneMax.place(relx=0.52, rely=0.4, height=23, width=200)
        self.lblTempInterneMax.configure(text="---")
        self.lblTempInterneMax.configure(justify='left')
        self.lblTempInterneMax.configure(font=("Courrier New", 20))
        print("5-")

        self.txtTempInterneAlmMin = tk.Entry(self.root, bg="lightgrey")
        self.txtTempInterneAlmMin.place(relx=0.62, rely=0.4, height=27, width=80)
        self.txtTempInterneAlmMin.insert(0, "0")
        self.txtTempInterneAlmMin.configure(justify='left')
        self.txtTempInterneAlmMin.configure(font=("Courrier New", 20))

        self.txtTempInterneAlmMax = tk.Entry(self.root, bg="lightgrey")
        self.txtTempInterneAlmMax.place(relx=0.73, rely=0.4, height=27, width=80)
        self.txtTempInterneAlmMax.insert(0, "100")
        self.txtTempInterneAlmMax.configure(justify='left')
        self.txtTempInterneAlmMax.configure(font=("Courrier New", 20))

        self.lblTempInterneAlm = tk.Label(self.root, image=self.almVerte, width=20, height=20)
        self.lblTempInterneAlm.place(relx=0.91, rely=0.4)
        
        self.lblHumExterne = tk.Label(self.root,anchor="w")
        self.lblHumExterne.place(relx=0.05, rely=0.55, height=23, width=310)
        self.lblHumExterne.configure(text="Humidité Extérieure : ")
        self.lblHumExterne.configure(justify=tk.LEFT)
        self.lblHumExterne.configure(font=("Courrier New", 20))
        print("6-")

        self.lblHumExterneVal = tk.Label(self.root, anchor="w")
        self.lblHumExterneVal.place(relx=0.34, rely=0.55, height=23, width=200)
        self.lblHumExterneVal.configure(text="---")
        self.lblHumExterneVal.configure(justify='left')
        self.lblHumExterneVal.configure(font=("Courrier New", 20))

        self.lblHumExterneMin = tk.Label(self.root, anchor="w")
        self.lblHumExterneMin.place(relx=0.42, rely=0.55, height=23, width=200)
        self.lblHumExterneMin.configure(text="---")
        self.lblHumExterneMin.configure(justify='left')
        self.lblHumExterneMin.configure(font=("Courrier New", 20))

        self.lblHumExterneMax = tk.Label(self.root, anchor="w")
        self.lblHumExterneMax.place(relx=0.52, rely=0.55, height=23, width=200)
        self.lblHumExterneMax.configure(text="---")
        self.lblHumExterneMax.configure(justify='left')
        self.lblHumExterneMax.configure(font=("Courrier New", 20))

        print("7-")

        self.txtTempExterneAlmMin = tk.Entry(self.root, bg="lightgrey")
        self.txtTempExterneAlmMin.place(relx=0.62, rely=0.55, height=27, width=80)
        self.txtTempExterneAlmMin.insert(0, "0")
        self.txtTempExterneAlmMin.configure(justify='left')
        self.txtTempExterneAlmMin.configure(font=("Courrier New", 20))

        self.txtTempExterneAlmMax = tk.Entry(self.root, bg="lightgrey")
        self.txtTempExterneAlmMax.place(relx=0.73, rely=0.55, height=27, width=80)
        self.txtTempExterneAlmMax.insert(0, "100")
        self.txtTempExterneAlmMax.configure(justify='left')
        self.txtTempExterneAlmMax.configure(font=("Courrier New", 20))

        self.lblHumExterneAlm = tk.Label(self.root, image=self.almRouge, width=20, height=20)
        self.lblHumExterneAlm.place(relx=0.91, rely=0.55)
        
        self.lblTempExterne = tk.Label(self.root, anchor="w")
        self.lblTempExterne.place(relx=0.05, rely=0.5, height=23, width=340)
        self.lblTempExterne.configure(text="Température Extérieure : ")
        self.lblTempExterne.configure(justify='left')
        self.lblTempExterne.configure(font=("Courrier New", 20))

        print("8-")

        self.lblTempExterneVal = tk.Label(self.root, anchor="w")
        self.lblTempExterneVal.place(relx=0.34, rely=0.5, height=23, width=200)
        self.lblTempExterneVal.configure(text="---")
        self.lblTempExterneVal.configure(justify='left')
        self.lblTempExterneVal.configure(font=("Courrier New", 20))

        self.lblTempExterneMin = tk.Label(self.root, anchor="w")
        self.lblTempExterneMin.place(relx=0.42, rely=0.5, height=23, width=200)
        self.lblTempExterneMin.configure(text="---")
        self.lblTempExterneMin.configure(justify='left')
        self.lblTempExterneMin.configure(font=("Courrier New", 20))

        self.lblTempExterneMax = tk.Label(self.root, anchor="w")
        self.lblTempExterneMax.place(relx=0.52, rely=0.5, height=23, width=200)
        self.lblTempExterneMax.configure(text="---")
        self.lblTempExterneMax.configure(justify='left')
        self.lblTempExterneMax.configure(font=("Courrier New", 20))

        self.txtTempExterneAlmMin = tk.Entry(self.root, bg="lightgrey")
        self.txtTempExterneAlmMin.place(relx=0.62, rely=0.5, height=27, width=80)
        self.txtTempExterneAlmMin.insert(0, "0")
        self.txtTempExterneAlmMin.configure(justify='left')
        self.txtTempExterneAlmMin.configure(font=("Courrier New", 20))

        self.txtTempExterneAlmMax = tk.Entry(self.root, bg="lightgrey")
        self.txtTempExterneAlmMax.place(relx=0.73, rely=0.5, height=27, width=80)
        self.txtTempExterneAlmMax.insert(0, "100")
        self.txtTempExterneAlmMax.configure(justify='left')
        self.txtTempExterneAlmMax.configure(font=("Courrier New", 20))

        self.lblTempExterneAlm = tk.Label(self.root, image=self.almRouge, width=20, height=20)
        self.lblTempExterneAlm.place(relx=0.91, rely=0.5)

        print("9-")

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            self.IP = s.getsockname()[0]
        except:
            self.IP='127.0.0.1'
        finally:
            s.close()

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
        
    def addTemperatureSHT(self, data):

        self.lblTempInterneVal.configure(text=str(data))
        limites = self.findMiniMax("TempC_SHT")
        self.lblTempInterneMin.configure(text=str(limites[0]))
        self.lblTempInterneMax.configure(text=str(limites[1]))
        self.updateTime()
        
    def addHumiditySHT(self, data):

        self.lblHumInterneVal.configure(text=str(data))
        limites = self.findMiniMax("Hum_SHT")
        self.lblHumInterneMin.configure(text=str(limites[0]))
        self.lblHumInterneMax.configure(text=str(limites[1]))

    def addData(self, type, data):

        if type == 0 :  # Température extérieure
            self.lblTempExterneVal.configure(text=str(data))
        elif type == 1 :  # Humidité extérieure
            self.lblHumExterneVal.configure(text=str(data))
        
    def run(self):

        while not self.lafin:
    
            self.root.update_idletasks()
            self.root.update()
            time.sleep(0.01)
            if sad.message_recu:
                print("Message reçu = " + str(sad.message_recu))
                while(not sad.qGui.empty()):
                    data = sad.qGui.get()
                    print(str(data))
                    data_json = json.loads(data)
                    print("data_json = ")
                    print(data_json)
                    
                    if "devEui" in str(data) :
                        print("" + str(data_json["devEui"]))
                    if "TempC_SHT" in str(data) :
                        self.addTemperatureSHT(data_json["TempC_SHT"])
                    if "Hum_SHT" in str(data) :
                        self.addHumiditySHT(data_json["Hum_SHT"])

                sad.message_recu = None
                    
        self.root.quit()

    
    def on_closing(self):

        if messagebox.askokcancel("Terminé ?", "Est-ce que vous voulez fermer le programme ?"):

            self.lafin = True
            time.sleep(1)
            #root.destroy()
            
    def Label1Click(self, event):

        self.TextDebug.delete("1.0", "end")

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
            
            
    def findMiniMax(self, column):

        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("%Y%m%d", named_tuple)

        filename = "rslts" + time_string + ".csv"
        print(filename)

        try :
            
            df = pd.read_csv(filename, sep=';', names=['time', 'TempC_SHT', 'Hum_SHT', 'Alarme'])
            #print(df)
            #print(df['TempC_SHT'])

            #val_min = df['TempC_SHT'].min()
            #val_max = df['TempC_SHT'].max()
            val_min = df[column].min()
            val_max = df[column].max()

        except Exception as excpt:

            print("Erreur 1 : ")
            print(excpt)
            
            val_min = 0
            val_max = -1

        return [val_min, val_max]
            
            
        
