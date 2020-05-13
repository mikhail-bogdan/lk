from flask import Flask


from config import CFG


app = Flask(__name__, static_folder='static')
