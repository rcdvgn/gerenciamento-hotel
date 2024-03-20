from xmlrpc.server import SimpleXMLRPCServer

import uuid
import random

db = {
    "reservas": {},
    "quartos": [
        101, 102, 103, 104, 105, 106, 
        201, 202, 203, 204, 205, 206,
        301, 302, 303, 304, 305, 306, 
        401, 402, 403, 404, 405, 406
    ],
    "usuarios": {
        "1": {
            "nome": "admin",
            "email": "admin@admin.com",
            "senha": "admin",
            "admin": True,
            "reservas": []
        }
    }
}

def get_reservas(reservas, user_id):
    if not reservas and db['usuarios'][user_id]['admin']:
        return list(db['reservas'].values())
    else:
        return [{'id': id, **db['reservas'][id]} for id in reservas if id in db['reservas']]

def criar_reserva(name, date, duration, user_id):
    id_reserva = str(uuid.uuid4()).replace('-', '')

    reserva = {
        "quarto": random.choice(db['quartos']),
        "nome": name,
        "data": date,
        "duracao": duration
    }
    
    db['reservas'][id_reserva] = reserva
    db['usuarios'][user_id]['reservas'].append(id_reserva)

    return 1, id_reserva

def reserva(id, user_id):
    if id in db['reservas']:
        if db['usuarios'][user_id]['admin'] or id in db['usuarios'][user_id]['reservas']:
            return 1, {'id': id, **db['reservas'][id]}
        else:
            return 0, "Acesso restrito"
    else:
        return 0, "Reserva inexistente"

def excluir_reserva(id, user_id):
    if db['usuarios'][user_id]['admin'] == True:
        if id in db['reservas']:
            del db['reservas'][id]
            for user in db["usuarios"]:
                if id in user['reservas']:
                    user["reservas"].remove(id)
                    return 1, user
                    break
            return 0, "Reserva nao encontrada"
    else:
        if id in db["usuarios"][user_id]["reservas"]:
            db["usuarios"][user_id]["reservas"].remove(id)
            del db['reservas'][id]
            return 1, db["usuarios"][user_id]
        return 0, "Reserva nao encontrada"

    


def register(name, email, password):
    for user in db['usuarios'].values():
        if email == user['email']:
            return 0, "Usuario ja existente"
    
    user = {
        "nome": name,
        "email": email,
        "senha": password,
        "admin": False,
        "reservas": []
    }

    uid = str(uuid.uuid4()).replace('-', '')

    db['usuarios'][uid] = user

    return 1, [user, uid]

def login(email, password):
    for user_id, user in db['usuarios'].items():
        if email == user['email'] and password == user['senha']:
            return 1, [user, user_id]
        
    return 0, "Nenhum usuario encontrado"
    
def main():
    servidor = SimpleXMLRPCServer(("localhost", 8000))

    servidor.register_function(register, "register")
    servidor.register_function(login, "login")
    servidor.register_function(criar_reserva, "criar_reserva")
    servidor.register_function(reserva, "reserva")
    servidor.register_function(get_reservas, "get_reservas")
    servidor.register_function(excluir_reserva, "excluir_reserva")
    
    print("Servidor iniciado...")
    servidor.serve_forever()

if __name__ == "__main__":
    main()
