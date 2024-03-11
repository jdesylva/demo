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

        except Exception as excpt:
            print("Erreur lors de la lecture du fichier de configuration \"" + confFile)
            print("Fin prématurée du programme.")
            print("Erreur : ", excpt)
            sys.exit()

        self.entete_capteurs = ["Capteur", "Valeur", "Min", "Max", "Lim.-", "Lim.+"]

        style_entete = ttk.Style()
        style_entete.configure("Treeview.Heading", font=(None, 20))

        style_tree = ttk.Style()
        style_tree.configure("Treeview", font=(None, 16), rowheight=30)

        self.tree = ttk.Treeview(root, columns=self.entete_capteurs, show="tree headings", height=10)
        self.tree.column("# 0", anchor=tk.W, width=30)
        self.tree.heading("# 0", text="")
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
        for client in self.parametres["eui_clients"]:
            mesPeripheriques = self.parametres["peri_clients"][client]
            for p in range (0, len(mesPeripheriques)):
                monPeripherique = mesPeripheriques[p]
                donnees.append((monPeripherique['label'], '- - -', '- - -', '- - -', '0', '100'))
        # Insérer les données dans le widget
        self.almVerte = tk.PhotoImage(file="almVerte.png")
        self.almRouge = tk.PhotoImage(file="almRouge.png")

        i = 0
        self.capteursID=[]
        
        for capteur in donnees:
            print(f"capteur ==> {capteur}")
            self.capteursID.append(self.tree.insert('', tk.END, text='', tags=('cptr'+ str(i)), values=capteur, image=self.almVerte))
            i+=1
    
        self.tree.bind("<Double-1>", self.itemEvent)
        self.tree.tag_configure('cptr2', background='pink')
        self.tree.place(relx=0.05, rely=0.35, relheight=0.32, relwidth=0.877)
        self.tree['show'] = 'tree headings'
        self.tree.selection_set(self.capteursID[0])
        self.tree.focus(self.capteursID[0])

    def itemEvent(self, event):
        itemSelect = self.tree.selection()[0] # now you got the item on that tree
        print (f"you clicked on item '{itemSelect}'; tag == ", self.tree.item(itemSelect,"tags"))
        curItem = self.tree.focus()
        print(f"Current item selected == {self.tree.item(curItem)}")
        self.tree.item(itemSelect, image = self.almRouge)
        self.tree.tag_configure(self.tree.item(itemSelect,"tags"), background='pink')
        
    def maj(self, ligne, colonne, valeur):

        row_id = self.tree.get_children()[ligne]
        self.tree.set(row_id, column=colonne, value=str(valeur))


