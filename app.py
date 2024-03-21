from flask import Flask, render_template, request, session, redirect, url_for
from datetime import timedelta

import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")


app = Flask(__name__)


app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.secret_key = 'SECRETE_KEY'

# @app.before_request
# def make_session_permanent():
#     session.permanent = True

@app.route('/lost_connection')
def lost_connection():
    return render_template('lost_connection.html')

@app.route('/')
def index():
    if 'user' in session:
        try:
            reservas = proxy.get_reservas(session['user']['reservas'], session['user_id']) 
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))
        
        return render_template('index.html', reservas=reservas, user=session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        try:
            status, response = proxy.register(name, email, password)
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))
            
        if status == 1:
            session['user'] = response[0]
            session['user_id'] = response[1]

            return redirect(url_for('index'))
        else:
            return f"<h1>{response}</h1>"
    else:
        if 'user' in session:
            return redirect(url_for("index"))
        else:
            return render_template('register.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            status, response = proxy.login(email, password)
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))

        if status == 1:
            session['user'] = response[0]
            session['user_id'] = response[1]

            return redirect(url_for("index"))
        else:
            return f"<h1>{response}</h1>" 
        
    else:
        if 'user' in session:
            return redirect(url_for("index"))
        else:
            return render_template('login.html')
        

@app.route('/criar-reserva', methods=['POST', 'GET'])
@app.route('/criar-reserva/<edit_id>', methods=['POST', 'GET'])
def criar_reserva(edit_id=""):
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        duration = request.form['duration']
        hotel = request.form['hotel']

        id = "" if not request.form['id'] else request.form['id']
        room = "" if not request.form['room'] else request.form['room']

        try:
            status, response = proxy.criar_reserva(name, date, duration, id, room, hotel, session['user_id'])
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))

        if status == 1:
            updated_user = session['user'].copy()
            if not response in updated_user['reservas']:
                updated_user['reservas'].append(response)
            session['user'] = updated_user

            return redirect(url_for('reserva', id=response))
        else:
            return f"<h1>{response}</h1>"

    else:
        if 'user' in session:
            if edit_id != "":
                
                try:
                    status, response = proxy.reserva(edit_id, session['user_id'])
                except ConnectionRefusedError:
                    return redirect(url_for("lost_connection"))

                if status == 1:
                    existing_reserva = {
                        "quarto": response["quarto"],
                        "nome": response["nome"],
                        "data": response["data"],
                        "duracao": response["duracao"],
                        "hotel": response["hotel"],
                        "id": response["id"],
                    }
                else:
                    return f"<h2>{response}</h2>"
            else:
                existing_reserva = ""

            try:
                hoteis = proxy.get_all_hoteis()
            except ConnectionRefusedError:
                return redirect(url_for("lost_connection"))
            return render_template('criar_reserva.html', existing_reserva=existing_reserva, hoteis=hoteis, user=session['user'])
            
        else:
            return redirect(url_for("login"))


@app.route('/reserva/<id>', methods=['POST', 'GET'])
def reserva(id):
    if request.method == 'POST':
       pass        
    else:
        if 'user' in session:
            try:
                status, response = proxy.reserva(id, session['user_id'])
            except ConnectionRefusedError:
                return redirect(url_for("lost_connection"))

            if status == 1:
                return render_template('reserva.html', response=response, user=session['user'])
            else:
                return f"<h1>{response}</h1>"
        else:
            return redirect(url_for("login"))

@app.route('/excluir-reserva/<id>')
def excluir_reserva(id):
    if 'user' in session:
        try:
            status, response = proxy.excluir_reserva(id, session['user_id'])
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))

        if status == 1:
            session['user'] = response
            return redirect(url_for('index'))
        else:
            return f"<h1>{response}</h1>"
    else:
        return redirect(url_for("login"))
    
@app.route('/consulta', methods=['POST'])
def consulta():
    if 'user' in session:
        query = request.form["query"]

        return redirect(url_for("reserva", id=query))
    else:
        return redirect(url_for("login"))

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        pass
    else:
        if session['user']['admin'] == True:
            try:
                hoteis = proxy.get_all_hoteis()
            except ConnectionRefusedError:
                return redirect(url_for("lost_connection"))
            
            hoteis_info = []
            for hotel in hoteis:
                try:
                    quartos = proxy.get_quartos(hotel)
                except ConnectionRefusedError:
                    return redirect(url_for("lost_connection"))
                hoteis_info.append({"nome": hotel, "num_quartos": len(quartos.keys())})

            return render_template('admin.html', user=session["user"], hoteis_info=hoteis_info)
        else:
            return "<h1>Acesso restrito</h1>"

@app.route('/quartos/<hotel>', methods=['POST', 'GET'])
def quartos(hotel):
    if request.method == 'POST':
        pass
    else:
        if session['user']['admin'] == True:            
            try:
                quartos = proxy.get_quartos(hotel)
            except ConnectionRefusedError:
                return redirect(url_for("lost_connection"))

            return render_template('quartos.html', user=session["user"], hotel=hotel, quartos=quartos)
        else:
            return "<h1>Acesso restrito</h1>"

@app.route('/adicionar-quarto/<hotel>', methods=['POST', 'GET'])
def adicionar_quarto(hotel):
    if request.method == 'POST':
        num_quarto = request.form['num_quarto']

        try:
            status, response = proxy.adicionar_quarto(num_quarto, hotel)
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))

        if status == 0:
            return f"<h1>{response}</h1>"
        else:
            return redirect(url_for('quartos', hotel=response))
    else:
        if session['user']['admin'] == True:
            return render_template('adicionar_quarto.html', user=session["user"], hotel=hotel)
        else:
            return "<h1>Acesso restrito</h1>"

@app.route('/adicionar-hotel/', methods=['POST', 'GET'])
def adicionar_hotel():
    if request.method == 'POST':
        hotel_name = request.form['hotel_name']

        try:
            status, response = proxy.adicionar_hotel(hotel_name)
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))

        if status == 0:
            return f"<h1>{response}</h1>"
        else:
            return redirect(url_for('quartos', hotel=response))
    else:
        if session['user']['admin'] == True:
            return render_template('adicionar_hotel.html', user=session["user"])
        else:
            return "<h1>Acesso restrito</h1>"

@app.route('/excluir-quarto/<hotel>/<quarto>', methods=['POST', 'GET'])
def excluir_quarto(hotel, quarto):
    if session['user']['admin'] == True:
        try:
            status, response = proxy.excluir_quarto(hotel, quarto, session['user_id'])
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))

        if status == 0:
            return f"<h1>{response}</h1>"
        else:
            session['user'] = response
            return redirect(url_for('admin'))
    else:
        return "<h1>Acesso restrito</h1>"

@app.route('/excluir-hotel/<hotel>')
def excluir_hotel(hotel):
    if session['user']['admin'] == True:
        try:
            status, response = proxy.excluir_hotel(hotel, session['user_id'])
        except ConnectionRefusedError:
            return redirect(url_for("lost_connection"))

        if status == 0:
            return f"<h1>{response}</h1>"
        else:
            session['user'] = response
            return redirect(url_for('admin'))
    else:
        return "<h1>Acesso restrito</h1>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# Rodar a aplicação
if __name__ == '__main__':
    app.run(debug=True)
