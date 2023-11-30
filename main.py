from flask import (
    Flask,
    get_flashed_messages,
    jsonify,
    render_template,
    url_for,
    redirect,
    request,
    session,
    flash,
)
from jwt import JWT, AbstractJWKBase
import mysql.connector
from config import DevConfig
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)

CORS(
    app, resources={r"/*": {"origins": "http://localhost:5173"}}
)  # para que funcione con vue
app.config.from_object(DevConfig)
mail = Mail(app)


mydb = mysql.connector.connect(
    host="localhost", user="kt6delta", password="Ballena12+", database="Registrados"
)

@app.route("/send_email", methods=["POST"])  # envia coreo
def send_email():
    if request.method == "POST":
        email = request.get_json()["email"]
        username = request.get_json()["username"]
        url = request.get_json()["token"]
        name = "Tecnimontacargas Dual"
        msg_title = "!Verificacion de correo electronico!"
        sender = "noreply@app.com"
        msg = Message(msg_title, sender=sender, recipients=[email])
        msg_body = "Haga clcik en el siguiente boton o en el link para terminar la verificacion de correo eletronico"
        data = {
            "app_name": name,
            "user": username,
            "title": msg_title,
            "body": msg_body,
            "url": url,
        }
        msg.html = render_template("email.html", data=data)
        try:
            mail.send(msg)
            return jsonify({"message": "email sent"})  # regresa un token
        except Exception as e:
            print(e)
            return f"the email was not sent {e}"



@app.route("/bienvenido", methods=["GET", "POST"])
def bienvenido():
    datos = session.get("username")
    return jsonify(datos, {"message": "exito, se ejecuto la funcion"})


@app.route("/login", methods=["GET", "POST"])
def login():
    user = request.get_json()
    username = user["username"]
    password = user["password"]
    if request.method == "POST":
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT * FROM user WHERE username = %(username)s", {"username": username}
        )
        data = mycursor.fetchall()
        if data:
            userdata = data[0]
            if userdata:
                passcheck = userdata[3]
            if userdata and check_password_hash(passcheck, password):
                session["username"] = userdata
                return redirect(url_for("bienvenido"))
            else:
                flash("contraseña incorreta", "error")
        else:
            flash("Usuario no existente", "error")
    return jsonify(user, {"message": get_flashed_messages()})

@app.route("/registro", methods=["GET", "POST"])
def registro():
    user = request.get_json()
    if request.method == "GET":  # obtiene info
        mycursor = mydb.cursor()
        if user["dato"] == "username":
            sql = "SELECT username FROM user"
        elif user["dato"] == "email":
            sql = "SELECT email FROM user"
        elif user["dato"] == "password":
            sql = "SELECT password FROM user"
        else:
            sql = "SELECT * FROM user"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        return jsonify(data)
    
    if request.method == "POST":  # envia info
        password = createpassword(user["password"])
        token = createtoken(user["username"])
        mycursor = mydb.cursor()
        sql = "SELECT * FROM user WHERE username = %s"
        val = [user["username"]]
        mycursor.execute(sql, val)
        data = mycursor.fetchall()
        create = True
        if data:
            flash("User existente", "existe_us")
            create = False
        elif not data:
            sql = "SELECT * FROM user WHERE email = %s"
            val = [user["email"]]
            mycursor.execute(sql, val)
            coe = mycursor.fetchall()
            if coe:
                create = False
                flash("Correo existente", "existe_co")
            elif user["password"] == user["confirmpassword"] and create == True:
                mycursor.execute(
                    "INSERT INTO user (username, email, password, verification_code) VALUES (%s, %s, %s, %s)",
                    (user["username"], user["email"], password, token),
                )
                mydb.commit()
                flash("Se creo en la base de datos", "success")
                return redirect(
                    url_for(
                        "send_email",
                        query_args={
                            "email": user["email"],
                            "username": user["username"],
                            "token": token
                        },
                    )
                )
            else:
                flash("Las contraseñas son diferentes", "error")
                return jsonify(user, {"message": get_flashed_messages()})
        return jsonify(user, {"message": get_flashed_messages()})

@app.route("/verificacion", methods=["POST"])
#@jwt_required()
def login2():
    data = request.get_json()
    token = data["token"]
    if request.method == "POST":
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM user WHERE verification_code = %s", (token))
        data = mycursor.fetchall()
        if data:
            flash("correo verificado", "exito")
        else:
            flash("token incorreta", "error")
    return jsonify(data, {"message": get_flashed_messages()})


def createpassword(password):
    return generate_password_hash(password)

jwt_object = JWT()
def createtoken(username):
    AbstractJWKBase.key = app.config['SECRET_KEY']
    token = jwt_object.encode({'username': username}, app.config['SECRET_KEY'])
    print(token)
    #return token

if __name__ == "__main__":
    app.run(debug=True, port=8000)

    # no visible la secret key y los otros datos
    # que al oprimir el link del boton , en la base de datos se cambie el valor de la columna is_verification a 1
