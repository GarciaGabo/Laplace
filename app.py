from flask import Flask
from routes.laplace import laplace_bp
from routes.inversa import inversa_bp

app = Flask(__name__)

app.register_blueprint(laplace_bp)
app.register_blueprint(inversa_bp)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
#host='0.0.0.0' para abrir el servidor en la misma red
