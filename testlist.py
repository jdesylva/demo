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
if  len(sys.argv) > 1:
    if os.path.isfile(sys.argv[1]):
        confFile=sys.argv[1]
    else:
        print(f"Le fichier {sys.argv[1]} est introuvable!")
        sys.exit()
#
# On lit le fichier json de configuration
try:
    with open(confFile, 'r') as file:
        # On récupère le contenu du fichier dans l'objet JSON "parametres"
        parametres = json.load(file)
        #print(str(self.parametres))
#
except Exception as excpt:
    print("Erreur lors de la lecture du fichier de configuration \"" + confFile)
    print("Fin prématurée du programme.")
    print("Erreur : ", excpt)
    sys.exit()
#
#
root = tk.Tk()
root.title("Exemple de liste Tkinter")

entete_capteurs = ["Alarme", "Capteur", " ", "Min", "Max", "Lim.-", "Lim.+"]

tree = ttk.Treeview(root, columns=entete_capteurs, show="headings", height=5)
tree.column("# 0", anchor=tk.W, width=75)
tree.heading("# 0", text="Alarme")
tree.column("# 1", anchor=tk.W, width=300)
tree.heading("# 1", text="Capteur")
tree.column("# 2", anchor=tk.W, width=100)
tree.heading("# 2", text="Valeur")
tree.column("# 3", anchor=tk.W, width=100)
tree.heading("# 3", text="Min.")
tree.column("# 4", anchor=tk.W, width=100)
tree.heading("# 4", text="Max.")
tree.column("# 5", anchor=tk.W, width=100)
tree.heading("# 5", text="Limite -")
tree.column("# 6", anchor=tk.W, width=100)
tree.heading("# 6", text="Limite +")
vsb = ttk.Scrollbar(orient="vertical", command=tree.yview)
hsb = ttk.Scrollbar(orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
vsb.pack(side="right", fill="y")
hsb.pack(side="bottom", fill="x")

print('len(parametres["eui_clients"]) = ', len(parametres["eui_clients"]))
# Préparer les données
donnees = []
for n in range(0, len(parametres["eui_clients"])):
    mesPeripheriques = parametres["eui_clients"][n]["peripheriques"]
    for p in range (0, len(mesPeripheriques)):
        monPeripherique = mesPeripheriques[p]
        donnees.append((monPeripherique["label"], '- - -', '- - -', '- - -', '0', '100'))
print(donnees)

# Insérer les données dans le widget
almVerte = tk.PhotoImage(file="almVerte.png")
almRouge = tk.PhotoImage(file="almRouge.png")

i = 0
capteursID=[]

for capteur in donnees:
    capteursID.append(tree.insert('', 'end', text='', image=almVerte, tags=('cptr'+ str(i)), values=capteur))
    i+=1
    
print(capteursID)
    
tree.tag_configure('flashtag', background='red')
tree['show'] = 'tree headings'
tree.pack(side="left")
tree.selection_set(capteursID[0])
tree.focus(capteursID[0])

tempe = 25

def task():
    global tree, tempe
    row_id = tree.get_children()[0] 
    tree.set(row_id, column="# 2", value=str(tempe))
    tempe += 1
    root.after(2000, task)  # Reschedule the event after 2 seconds

root.after(2000, task)  # Start the loop

root.mainloop()


