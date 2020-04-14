from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/", methods=["POST","GET"])


def hello():
    print(request.data)
    return 'Hello there!'

if __name__== '__main__':
    app.run(host='0.0.0.0')
