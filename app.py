import chess
import random
import string
from agent import Game
from flask_cors import CORS
from flask import Flask, jsonify, request

import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
cors = CORS(app)

games = {}


@app.route("/start/<mode>/<diff>", methods=["GET"])
def start_game(mode, diff):
    id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    games[id] = Game(mode, diff)
    return jsonify([id, games[id].board.board2D()])

@app.route("/make_move/<id>", methods=["GET"])
@app.route("/make_move/<id>/<move>", methods=["GET"])
def make_move(id, move=None):
    game = games[id]
    game.play(move)
    return jsonify(game.board.board2D())

@app.route("/possible_moves_from/<id>/<start>", methods=["GET"])
def possible_moves_from(id, start):
    game = games[id]
    return jsonify(game.board.legal_moves_from(start))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)