# Module permettant l'utilidation de la file de transfert des messages GUI entre les modules Python.

import queue

def set_queue():
    global qGui
    qGui = queue.Queue(0)




