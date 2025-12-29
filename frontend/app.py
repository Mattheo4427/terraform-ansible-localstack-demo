from flask import Flask, render_template
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", backend_url=os.getenv("BACKEND_URL"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)