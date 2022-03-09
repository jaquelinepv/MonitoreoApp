from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return 'Ok'

if __name__ == "__main__":
    app.run()

