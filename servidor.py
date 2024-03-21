from xmlrpc.server import SimpleXMLRPCServer

import uuid
import random

db = {
    "usuarios": {
        "0": {
            "nome": "admin",
            "email": "admin@admin.com",
            "senha": "admin",
            "admin": True,
            "reservas": []
        }
    },
    "hoteis": {
        "Ibis_Budget":{
            "reservas": {},
            "quartos": {
                '101': "ocupado", '102': "livre", '103': "livre", '104': "ocupado", '105': "livre", '106': "livre", 
                '201': "ocupado", '202': "ocupado", '203': "livre", '204': "ocupado", '205': "ocupado", '206': "livre"
            }
        },
        "Ibis_Styles":{
            "reservas": {},
            "quartos": {
                '101': "livre", '102': "livre", '103': "livre", '104': "ocupado", '105': "ocupado", '106': "ocupado", 
                '201': "livre", '202': "ocupado", '203': "livre", '204': "livre", '205': "ocupado", '206': "livre"
            }
        },
        "Ibis_Premium":{
            "reservas": {},
            "quartos": {
                '101': "ocupado", '102': "ocupado", '103': "livre", '104': "livre", '105': "livre", '106': "livre", 
                '201': "ocupado", '202': "livre", '203': "ocupado", '204': "livre", '205': "ocupado", '206': "livre"
            }
        }
    }
}

def get_all_reservas():
    all_reservas = {}
    for hotel in db["hoteis"].values():
        for hotel_reservas_id, hotel_reserva in hotel['reservas'].items():
            all_reservas[hotel_reservas_id] = {'id': hotel_reservas_id, **hotel_reserva}

    return all_reservas

def get_reservas(reservas, user_id):
    all_reservas = get_all_reservas()

    if db['usuarios'][user_id]['admin']:
        return list(all_reservas.values())
    else:
        return [reserva for reserva in all_reservas.values() if reserva['id'] in reservas]
    
def quartos_livres(hotel):
    return [num_quarto for num_quarto, status in db['hoteis'][hotel]['quartos'].items() if status != "ocupado"]

def criar_reserva(name, date, duration, id, room, hotel, user_id):
    id_reserva = str(uuid.uuid4()).replace('-', '') if not id else id

    quarto = random.choice(quartos_livres(hotel)) if not room else room
    
    db['hoteis'][hotel]['quartos'][quarto] = "ocupado"

    reserva = {
        "quarto": quarto,
        "nome": name,
        "data": date,
        "duracao": duration,
        "hotel": hotel
    }
    
    db['hoteis'][hotel]['reservas'][id_reserva] = reserva
    db["usuarios"][user_id]['reservas'].append(id_reserva)

    return 1, id_reserva

def reserva(id, user_id):
    all_reservas = get_all_reservas()
    if id in all_reservas:
        if db['usuarios'][user_id]['admin'] or id in db['usuarios'][user_id]['reservas']:
            return 1, all_reservas[id]
        else:
            return 0, "Acesso restrito"
    else:
        return 0, "Reserva inexistente"

def excluir_reserva(id, user_id):
    all_reservas = get_all_reservas()
    
    if db['usuarios'][user_id]['admin'] == True:
        if id in all_reservas:
            del db['hoteis'][all_reservas[id]['hotel']]['reservas'][id]
            for user in db["usuarios"]:
                if id in user['reservas']:
                    user["reservas"].remove(id)
                    db['hoteis'][all_reservas[id]['hotel']]['quartos'][all_reservas[id]['quarto']] = "livre"
                    return 1, user
                    
            
            return 0, "Reserva nao encontrada"
    else:
        if id in db["usuarios"][user_id]["reservas"]:
            db["usuarios"][user_id]["reservas"].remove(id)
            del db['hoteis'][all_reservas[id]['hotel']]['reservas'][id]
            db['hoteis'][all_reservas[id]['hotel']]['quartos'][all_reservas[id]['quarto']] = "livre"
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

def get_quartos(hotel):
    return db["hoteis"][hotel]["quartos"]
    
def get_all_hoteis():
    return list(db['hoteis'].keys())

def adicionar_hotel(hotel_name):
    if hotel_name in db['hoteis']:
        return 0, "Hotel ja existente"
    else:
        new_hotel = hotel_name.replace(" ", "_")
        db['hoteis'][new_hotel] = {"reservas": {}, "quartos": {}}
        return 1, new_hotel

def adicionar_quarto(num_quarto, hotel):
    if num_quarto in db['hoteis'][hotel]['quartos']:
        return 0, "Quarto ja existente"
    else:
        db['hoteis'][hotel]['quartos'][num_quarto] = "livre"
        return 1, hotel

def excluir_hotel(hotel, user_id):
    if hotel in db['hoteis']:
        all_reservas = get_all_reservas()
        for reserva_id, reserva in all_reservas.items():
            if reserva["hotel"] == hotel:
                for usuario_id in db["usuarios"].keys():
                    if reserva_id in db["usuarios"][usuario_id]["reservas"]:
                        db["usuarios"][usuario_id]["reservas"].remove(reserva_id)
                del db["hoteis"][hotel]["reservas"][reserva_id]
    
        return 1, db['usuarios'][user_id]
    else:
        return 0, "Erro ao excluir hotel"

def excluir_quarto(hotel, quarto, user_id):
    if quarto in db["hoteis"][hotel]["quartos"]:
            del db["hoteis"][hotel]["quartos"][quarto]

            all_reservas = get_all_reservas()
            for reserva_id, reserva in all_reservas.items():
                if reserva['hotel'] == hotel and reserva['quarto'] == quarto:
                    for usuario_id in db["usuarios"].keys():
                        if reserva_id in db["usuarios"][usuario_id]["reservas"]:
                            db["usuarios"][usuario_id]["reservas"].remove(reserva_id)
                    del db["hoteis"][hotel]["reservas"][reserva_id]
            
            return 1, db['usuarios'][user_id]
    else:
        return 0, "Quarto inexistente"

def main():
    servidor = SimpleXMLRPCServer(("localhost", 8000))

    servidor.register_function(register, "register")
    servidor.register_function(login, "login")
    servidor.register_function(criar_reserva, "criar_reserva")
    servidor.register_function(reserva, "reserva")
    servidor.register_function(get_reservas, "get_reservas")
    servidor.register_function(excluir_reserva, "excluir_reserva")
    servidor.register_function(get_all_hoteis, "get_all_hoteis")
    servidor.register_function(get_quartos, "get_quartos")
    servidor.register_function(adicionar_hotel, "adicionar_hotel")
    servidor.register_function(adicionar_quarto, "adicionar_quarto")
    servidor.register_function(excluir_quarto, "excluir_quarto")
    servidor.register_function(excluir_hotel, "excluir_hotel")
    
    print("Servidor iniciado...")
    servidor.serve_forever()

if __name__ == "__main__":
    main()
