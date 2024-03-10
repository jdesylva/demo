#!/usr/bin/python3
#
import time, sys, os, csv, json
import socket
#
import tkinter as tk
from tkinter import ttk, PhotoImage
#
#
confFile="demolora.json"
#
#
class peripheriquesListe:

    parametres = None

    def __init__(self, root, confFile="demolora.json"):
        """
        Fonction appelée lors de la contruction de l'objet peripheriquesListe. On utilise le 
        fichier "demolora.json" pour configurer les capteurs affichés dans 
        la liste.
        """

        # On lit le fichier json de configuration
        try:
            with open(confFile, 'r') as file:
                # On récupère le contenu du fichier dans l'objet JSON "parametres"
                self.parametres = json.load(file)
                #print(str(self.parametres))

        except Exception as excpt:
            print("Erreur lors de la lecture du fichier de configuration \"" + confFile)
            print("Fin prématurée du programme.")
            print("Erreur : ", excpt)
            sys.exit()

        self.entete_capteurs = ["Alarme", "Capteur", " ", "Min", "Max", "Lim.-", "Lim.+"]

        self.tree = ttk.Treeview(root, columns=self.entete_capteurs, show="headings", height=10)
        self.tree.column("# 0", anchor=tk.W, width=75)
        self.tree.heading("# 0", text="Alarme")
        self.tree.column("# 1", anchor=tk.W, width=300)
        self.tree.heading("# 1", text="Capteur")
        self.tree.column("# 2", anchor=tk.W, width=100)
        self.tree.heading("# 2", text="Valeur")
        self.tree.column("# 3", anchor=tk.W, width=100)
        self.tree.heading("# 3", text="Min.")
        self.tree.column("# 4", anchor=tk.W, width=100)
        self.tree.heading("# 4", text="Max.")
        self.tree.column("# 5", anchor=tk.W, width=100)
        self.tree.heading("# 5", text="Limite -")
        self.tree.column("# 6", anchor=tk.W, width=100)
        self.tree.heading("# 6", text="Limite +")
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Préparer les données
        donnees = []
        for n in range(0, len(self.parametres["eui_clients"])):
            mesPeripheriques = self.parametres["eui_clients"][n]["peripheriques"]
            for p in range (0, len(mesPeripheriques)):
                monPeripherique = mesPeripheriques[p]
                donnees.append((monPeripherique["label"], '- - -', '- - -', '- - -', '0', '100'))

        # Insérer les données dans le widget
        almVerte = tk.PhotoImage(file="almVerte.png")
        almRouge = tk.PhotoImage(file="almRouge.png")

        i = 0
        capteursID=[]

        for capteur in donnees:
            capteursID.append(self.tree.insert('', 'end', text='', image=almVerte, tags=('cptr'+ str(i)), values=capteur))
            i+=1
    
    
        self.tree.tag_configure('flashtag', background='red')
        self.tree['show'] = 'tree headings'
        self.tree.pack(fill="x")
        #self.tree.pack(side="left")
        self.tree.selection_set(capteursID[0])
        self.tree.focus(capteursID[0])
        #self.tree.grid(row=0, column=0, sticky='nsew')
        #root.pack(expand=True)

        
    def maj(self, ligne, colonne, valeur):

        row_id = self.tree.get_children()[ligne] 
        self.tree.set(row_id, column=colonne, value=str(valeur))

