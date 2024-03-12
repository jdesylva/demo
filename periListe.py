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
    
        self.tree.bind("<Key>", self.itemKeyEvent)
        self.tree.bind("<Button-1>", self.itemMouseEvent)
        self.tree.bind("<Button-3>", self.itemMouseEvent)
        self.tree.bind("<Double-1>", self.editCell)
        self.tree.tag_configure('cptr2', background='pink')
        self.tree.place(relx=0.05, rely=0.35, relheight=0.32, relwidth=0.877)
        self.tree['show'] = 'tree headings'
        self.tree.selection_set(self.capteursID[0])
        self.tree.focus(self.capteursID[0])

    def editCell(self, event):

        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify_column(event.x)
        print(f"item == {item}")
        print(f"column == {column}")

        if item and column:
            values = self.tree.item(item, 'values')
            print(f"values == {values}")
            if values:
                row = values[0]
                text = self.tree.item(item, 'text')
                self.entry = tk.Entry(self.tree, width=8)
                self.entry.insert(0, text)
                print(f"text == {text}")
                print(f"row == {text}")

                self.entry.place(x=event.x, y=event.y, anchor='w')
                self.entry.focus_set()
                self.entry.bind('<FocusOut>', lambda e: self.update_cell(item, self.entry.get(), column))
                self.entry.bind('<Return>', lambda e: self.update_cell(item, self.entry.get(), column))

    def update_cell(self, item, new_text, column):
        print(f"new_text == {new_text}")
        #self.tree.item(item, text=new_text)
        val = self.tree.item(item)
        print(f"val == {val}")
        print(f"column == {column}")
        val_list = val['values']
        print(f"val_list == {val_list}")
        val_list[int(column[1])-1] = new_text
        self.tree.item(item, values=val_list)
        self.tree.update()
        self.entry.destroy()

        #self.tree.unbind('<Double-1>')
        #self.tree.bind('<Double-1>', self.editCell)
    
    def itemKeyEvent(self, event):
        print(f"Event ==> {event}")
        if event.char == '\x1b' :
            itemSelect = self.tree.selection()[0] # now you got the item on that tree
            self.tree.item(itemSelect, image = self.almVerte)
            
    def itemMouseEvent(self, event):
        #print(f"Event ==> {event}")
        itemSelect = self.tree.selection()[0] # now you got the item on that tree
        print(f"itemselect ==> {self.tree.item(itemSelect)}")
        if event.num == 3 :
            itemSelect = self.tree.selection()[0] # now you got the item on that tree
            self.tree.item(itemSelect, image = self.almVerte)
        elif event.num == 1:
            self.tree.item(itemSelect, image = self.almRouge)
            
    '''            
        self.tree.tag_configure(self.tree.item(itemSelect,"tags"), background='pink')
        curItem = self.tree.focus()
        print(f"Current item selected == {self.tree.item(curItem)}")
        self.tree.item(itemSelect, image = self.almRouge)
        self.tree.tag_configure(self.tree.item(itemSelect,"tags"), background='pink')
        print(f"self.getLimit(curItem, \"inf\"){self.getLimit(curItem, 'inf')}")
        print(f"self.getLimit(curItem, \"sup\"){self.getLimit(curItem, 'sup')}")
        print(f"Event ==> {event}")
    '''        
    def changeImage(guiIndex, uneImage):
        row_id = self.tree.get_children()[guiIndex]
        self.tree.item(guiIndex, image = uneImage)
        
    def maj(self, guiIndex, colonne, valeur):

        row_id = self.tree.get_children()[guiIndex]
        self.tree.set(row_id, column=colonne, value=str(valeur))

    def getLimit(self, ligne, unType):
        ''' 
        Cette fonction retourne la limite positive ou négative de l'alarme associée au périphérique.
        Le paramètre "un_iid" contient l'identificateur du périphérique dans la liste 
        Le paramètre "unType" contient soit la valeur "sup" ou la valeur "inf" pour les limites
        supérieure et inférieure respectivement.
        '''

        row_id = self.tree.get_children()[ligne]
        
        lesValeurs = self.tree.item(row_id, "values")
        if unType == "sup":
            return lesValeurs[5]
        elif unType == "inf":
            return lesValeurs[4]
        
