import socket
import time, sys
import json, csv
import pandas as pd

try:
    import Tkinter as tk
    print("import Tkinter as tk")
except ImportError:
    import tkinter as tk
    import tkinter.messagebox as messagebox
    print("import tkinter as tk")

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import supportAppDemo as sad
    
class appDemo:

    root = None
    lafin = False
    sad.message_recu = None
    photo=None
    almRouge=None
    almVert=None
    
    def __init__(self, geo="1000x700+225+150"):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

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
            #self.photo = tk.PhotoImage(file="cl-logo_joliette_33.png")
            self.photo = tk.PhotoImage(file="logodemo_t.png")


            # Load the custom icon image
            icon_image = tk.PhotoImage(file="iconeDemo.png")

            # Set the custom icon for the window titlebar
            self.root.iconphoto(False, icon_image)

        except Exception as excpt:
            
            print("Fichiers des images manquants!")
            print("Erreur : ", excpt)
            sys.exit()

        #self.Header = tk.Label(self.root, image=self.photo, width=1145, height=335)
        self.Header = tk.Label(self.root, image=self.photo, width=1184, height=164)
        #self.Header = tk.Label(self.root, image=self.photo, width=572, height=167)
        #self.Header = tk.Label(self.root, image=self.photo, width=382, height=112)
        #self.Header = tk.Label(self.root, text="Test")
        self.Header.place(relx=0.0, rely=0.0)
        self.Header.bind("<Button-1>", self.buttonLogoClick)
        #self.Header.place(relx=0.05, rely=0.05, relheight=0.2, relwidth=0.95)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.TextDebug = tk.Text(self.root)
        self.TextDebug.place(relx=0.05, rely=0.744, relheight=0.111, relwidth=0.877)
        self.TextDebug.configure(background="lightgrey")
        self.TextDebug.configure(font="TkTextFont")
        self.TextDebug.configure(selectbackground="#c4c4c4")
        self.TextDebug.configure(wrap="word")
        self.TextDebug.insert(tk.END, str(self.root))
        self.TextDebug.insert(tk.END, "\n")

        self.Label1 = tk.Label(self.root)
        self.Label1.place(relx=0.0, rely=0.65, height=21, width=200)
        self.Label1.configure(text="- - - - - ")
#        self.Label1.configure(text="Mon adresse : " + self.IP)
#        self.Label1.configure(justify='left')
        self.Label1.configure(justify='left')
        self.Label1.configure(font=("Courrier New", 20))
        self.Label1.bind("<Button-1>", self.Label1Click) #JDS
        print("1-")

        self.lblTemperature = tk.Label(self.root, anchor="w")
        self.lblTemperature.place(relx=0.05, rely=0.30, height=23, width=400)
        self.lblTemperature.configure(text="Données actuelles")
        self.lblTemperature.configure(justify='left')
        self.lblTemperature.configure(font=("Courrier New", 20, "bold"))

        self.lblMinimum = tk.Label(self.root, anchor="w")
        self.lblMinimum.place(relx=0.42, rely=0.30, height=23, width=200)
        self.lblMinimum.configure(text="Min.")
        self.lblMinimum.configure(justify='left')
        self.lblMinimum.configure(font=("Courrier New", 20, "bold"))

        self.lblMaximum = tk.Label(self.root, anchor="w")
        self.lblMaximum.place(relx=0.52, rely=0.30, height=23, width=200)
        self.lblMaximum.configure(text="Max.")
        self.lblMaximum.configure(justify='left')
        self.lblMaximum.configure(font=("Courrier New", 20, "bold"))

        self.lblLimitMinimum = tk.Label(self.root, anchor="w")
        self.lblLimitMinimum.place(relx=0.62, rely=0.30, height=23, width=200)
        self.lblLimitMinimum.configure(text="Limite -")
        self.lblLimitMinimum.configure(justify='left')
        self.lblLimitMinimum.configure(font=("Courrier New", 20, "bold"))

        self.lblLimitMaximum = tk.Label(self.root, anchor="w")
        self.lblLimitMaximum.place(relx=0.73, rely=0.30, height=23, width=200)
        self.lblLimitMaximum.configure(text="Limite +")
        self.lblLimitMaximum.configure(justify='left')
        self.lblLimitMaximum.configure(font=("Courrier New", 20, "bold"))

        self.lblAlarme = tk.Label(self.root, anchor="w")
        self.lblAlarme.place(relx=0.86, rely=0.30, height=23, width=200)
        self.lblAlarme.configure(text="Alarme")
        self.lblAlarme.configure(justify='left')
        self.lblAlarme.configure(font=("Courrier New", 20, "bold"))


        self.lblHumInterne = tk.Label(self.root,anchor="w")
        self.lblHumInterne.place(relx=0.05, rely=0.4, height=23, width=320)
        self.lblHumInterne.configure(text="Humidité Intérieure : ")
        self.lblHumInterne.configure(justify=tk.LEFT)
        self.lblHumInterne.configure(font=("Courrier New", 20))
        print("2-")

        self.lblHumInterneVal = tk.Label(self.root, anchor="w")
        self.lblHumInterneVal.place(relx=0.34, rely=0.4, height=23, width=200)
        self.lblHumInterneVal.configure(text="---")
        self.lblHumInterneVal.configure(justify='left')
        self.lblHumInterneVal.configure(font=("Courrier New", 20))
        print("3-")

        self.lblHumInterneAlm = tk.Label(self.root, image=self.almVerte, width=20, height=20)
        self.lblHumInterneAlm.place(relx=0.91, rely=0.40)

        
        self.lblTempInterne = tk.Label(self.root, anchor="w")
        self.lblTempInterne.place(relx=0.05, rely=0.35, height=23, width=340)
        self.lblTempInterne.configure(text="Température Intérieure : ")
        self.lblTempInterne.configure(justify='left')
        self.lblTempInterne.configure(font=("Courrier New", 20))
#        self.lblTempInterne.bind("<Button-1>", self.Label1Click) #JDS
        print("4-")

        self.lblTempInterneVal = tk.Label(self.root, anchor="w")
        self.lblTempInterneVal.place(relx=0.34, rely=0.35, height=23, width=200)
        self.lblTempInterneVal.configure(text="---")
        self.lblTempInterneVal.configure(justify='left')
        self.lblTempInterneVal.configure(font=("Courrier New", 20))
        self.lblTempInterneMin = tk.Label(self.root, anchor="w")
        self.lblTempInterneMin.place(relx=0.42, rely=0.35, height=23, width=200)
        self.lblTempInterneMin.configure(text="---")
        self.lblTempInterneMin.configure(justify='left')
        self.lblTempInterneMin.configure(font=("Courrier New", 20))

        self.lblTempInterneMax = tk.Label(self.root, anchor="w")
        self.lblTempInterneMax.place(relx=0.52, rely=0.35, height=23, width=200)
        self.lblTempInterneMax.configure(text="---")
        self.lblTempInterneMax.configure(justify='left')
        self.lblTempInterneMax.configure(font=("Courrier New", 20))
        print("5-")

        self.lblTempInterneAlm = tk.Label(self.root, image=self.almVerte, width=20, height=20)
        self.lblTempInterneAlm.place(relx=0.91, rely=0.35)
        
        self.lblHumExterne = tk.Label(self.root,anchor="w")
        self.lblHumExterne.place(relx=0.05, rely=0.5, height=23, width=310)
        self.lblHumExterne.configure(text="Humidité Extérieure : ")
        self.lblHumExterne.configure(justify=tk.LEFT)
        self.lblHumExterne.configure(font=("Courrier New", 20))
        print("6-")

        self.lblHumExterneVal = tk.Label(self.root, anchor="w")
        self.lblHumExterneVal.place(relx=0.34, rely=0.5, height=23, width=200)
        self.lblHumExterneVal.configure(text="---")
        self.lblHumExterneVal.configure(justify='left')
        self.lblHumExterneVal.configure(font=("Courrier New", 20))
        print("7-")

        self.lblHumExterneAlm = tk.Label(self.root, image=self.almRouge, width=20, height=20)
        self.lblHumExterneAlm.place(relx=0.91, rely=0.5)
        
        self.lblTempExterne = tk.Label(self.root, anchor="w")
        self.lblTempExterne.place(relx=0.05, rely=0.45, height=23, width=340)
        self.lblTempExterne.configure(text="Température Extérieure : ")
        self.lblTempExterne.configure(justify='left')
        self.lblTempExterne.configure(font=("Courrier New", 20))
#        self.lblTempExterne.bind("<Button-1>", self.Label1Click) #JDS
        print("8-")

        self.lblTempExterneVal = tk.Label(self.root, anchor="w")
        self.lblTempExterneVal.place(relx=0.34, rely=0.45, height=23, width=200)
        self.lblTempExterneVal.configure(text="---")
        self.lblTempExterneVal.configure(justify='left')
        self.lblTempExterneVal.configure(font=("Courrier New", 20))
#        self.lblTempExterne.bind("<Button-1>", self.Label1Click) #JDS


        self.lblTempExterneAlm = tk.Label(self.root, image=self.almRouge, width=20, height=20)
        self.lblTempExterneAlm.place(relx=0.91, rely=0.45)

        print("9-")

        

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            self.IP = s.getsockname()[0]
        except:
            self.IP='127.0.0.1'
        finally:
            s.close()

        self.ButtonTerminate = tk.Button(self.root)
        self.ButtonTerminate.place(relx=0.80, rely=0.90, height=62, width=150)
        self.ButtonTerminate.bind("<Button-1>", self.buttonLogoClick)
        self.ButtonTerminate.configure(activebackground="#c4c4c4")
        self.ButtonTerminate.configure(activeforeground="black")
        self.ButtonTerminate.configure(text='''Fermer''')
        self.ButtonTerminate.configure(background="#888888")
        self.ButtonTerminate.configure(font=("Courrier New", 20))


    def buttonLogoClick(self, event):

        self.on_closing()
        pass

    def addTemperatureSHT(self, data):

        self.lblTempInterneVal.configure(text=str(data))
        limites = self.findMiniMax("TempC_SHT")
        self.lblTempInterneMin.configure(text=str(limites[0]))
        self.lblTempInterneMax.configure(text=str(limites[1]))

    def addHumiditySHT(self, data):

        self.lblHumInterneVal.configure(text=str(data))

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
                    data_json = json.loads(data)
                    print("data_json = ")
                    print(data_json)
                    
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
            
            
        
