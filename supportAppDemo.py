# Module permettant l'utilidation de la file de transfert des messages GUI entre les modules Python.

import queue

qGui = None
debug = False

def set_queue():
    global qGui
    qGui = queue.Queue(0)


def getColNames(params):
    '''
    Cette fonction retourne la liste des noms de colonnes utilisés dans le fichiers csv 
    contenant les mesures des périphériques configurés. Les entêtes sont construites en
    concaténant le deui du périphérique avec le type de la mesure défini dans le fichier
    de configuration JSON.
    '''

    colNames = []

    colNames.append("Heure")
    for client in params['eui_clients']:
        for peripherique in params['peri_clients'][client]:
            nom = client + peripherique['type']
            colNames.append(nom)
    colNames.append("RSSI")
    colNames.append("SNR")
                
    return colNames
