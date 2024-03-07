#!/usr/bin/python3
import time, sys
import json, csv
'''
Ces script sert d'exemple d'utilisation du fichier json "demolora.json"
Il peut aussi servir à vérifier la syntaxe de ce fichier json.
Afin de valider le fichie json, on doit placer le fichier à valider dans 
le même répertoire et l'exécuter. 

JDS : 18 février 2024
'''

with open("demolora1.json", 'r') as file:
    parametres = json.load(file)
    
print(parametres)

adresseIP = parametres['adresse_serveur_mqtt']
port = parametres['port_tcp_serveur_mqtt']

print(f"adresseIP = {adresseIP}")
print(f"port = {port}")

listeClients = parametres['eui_clients']
print(f"liste des clients :\n\n{listeClients}\n\n")

i, j = 0, 0

print("============================")
for client in listeClients :
    monClientEuid = client["euid"]
    print(f"Euid client[{i}] = ", monClientEuid)
    j=0
    for donnee in client["peripheriques"]:
        monClientGuiIndex = donnee["gui_index"]
        print(f"GuiIndex client[{i}] donnee[{j}] = ", monClientGuiIndex)
        monClientLabel = donnee["label"]
        print(f"Label client[{i}] donnee[{j}] = ", monClientLabel)
        monClientDestEmail = donnee["dest_email"]
        print(f"Label client[{i}] donnee[{j}] = ", monClientDestEmail)
        j +=1
        #print("....................")
    #print(f'Client #{i} euid = ', f'{monClient[0]["euid"]}')
    #print(f'Client #{i} gui_index = ', f'{client[1][0]["gui_index"]}')
    #print(f'Client #{i} label = {client[1][0]["label"]}')
    i += 1
    print("....................")
print("============================")
