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

@app.route('/')
def index():
    if 'user' in session:
        reservas = proxy.get_reservas(session['user']['reservas'], session['user_id']) 
        return render_template('index.html', reservas=reservas)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        status, response = proxy.register(name, email, password)
        
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

        status, response = proxy.login(email, password)

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
        

@app.route('/criar-reserva/<id>', methods=['POST', 'GET'])
@app.route('/criar-reserva/<id>', methods=['POST', 'GET'])
def criar_reserva(edit_id=""):
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        duration = request.form['duration']

        status, response = proxy.criar_reserva(name, date, duration, session['user_id'])

        if status == 1:
            updated_user = session['user']
            if not response in updated_user['reservas']:
                updated_user['reservas'].append(response)
                session['user'] = updated_user

            return redirect(url_for('reserva', id=response))
        else:
            return f"<h1>{response}</h1>"

    else:
        if 'user' in session:
            if edit_id != "":
                status, response = proxy.reserva(edit_id, session['user_id'])

                if status == 1:
                    updated_reserva = {
                        "quarto": response["quarto"],
                        "nome": response["nome"],
                        "data": response["data"],
                        "duracao": response["duracao"],
                        "id": response["id"],
                    }
            return render_template('criar_reserva.html', updated_reserva=updated_reserva)
            
        else:
            return redirect(url_for("login"))


@app.route('/reserva/<id>', methods=['POST', 'GET'])
def reserva(id):
    if request.method == 'POST':
       pass        
    else:
        if 'user' in session:
            status, response = proxy.reserva(id, session['user_id'])

            if status == 1:
                return render_template('reserva.html', response=response)
            else:
                return f"<h1>{response}</h1>"
        else:
            return redirect(url_for("login"))

# Rota personalizada
@app.route('/consulta/<id>')
def hello(id):
    return render_template('consulta.html', id=id)

@app.route('/excluir-reserva/<id>')
def excluir_reserva(id):
    if 'user' in session:
        status, response = proxy.excluir_reserva(id, session['user_id'])

        if status == 1:
            session['user'] = response
            return render_template('index.html')
        else:
            return f"<h1>{response}</h1>"
    else:
        return redirect(url_for("login"))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# Rodar a aplicação
if __name__ == '__main__':
    app.run(debug=True)
