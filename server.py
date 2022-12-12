from flask import Flask, request, jsonify
from game import BlackJack, load_value_map
import sqlite3

connection = sqlite3.connect('users.db', check_same_thread=False)
cursor = connection.cursor()


def create_table():
    # creating the users database
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id integer PRIMARY KEY,
                        username text unique not null,
                        password text not null,
                        chips integer default '1000' not null)""")


def current_chips(user_name):
    # returning the current chips of a user from the database
    cursor.execute("""SELECT chips FROM users WHERE username=?""", (user_name,))
    user_chips = cursor.fetchone()
    return user_chips[0]


def update_chips(amount, user_name):
    # updating a user chips in the database
    cursor.execute("""UPDATE users SET chips=? WHERE username=?""",
                   (amount, user_name))
    connection.commit()


app = Flask(__name__)

players = {}  # user_name


def make_data_to_return(dealer, player, winner):
    # dictionary with all the details of the game that will move from player to server
    data_to_send = {
        'dealer': dealer.score,
        'dealer_cards': [str(card) for card in dealer.cards],
        'player': player.score,
        'player_cards': [str(card) for card in player.cards],
        'winner': winner,
        'chips': player.chips,
        'bet': player.bet}
    return data_to_send


@app.route('/signup', methods=['POST'])
# a route to create new users in the db
def server_add_new_user():
    user_data = request.json
    username = user_data['username']
    password = user_data['password']
    try:
        cursor.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, password))
        connection.commit()
        return jsonify(True)
    except sqlite3.IntegrityError:
        return jsonify(False)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_details = request.json

    # lookup user in the db
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (login_details['username'], login_details['password']))

    user = cursor.fetchone()  # if user is not none -> user is in the db and passwords match
    if user:
        return jsonify(True)
    return jsonify(False)


@app.route('/new_game/<user_name>')
def new_game(user_name):
    # starting a new game with a first deal
    bj_game = players.get(user_name)
    bj_game.first_deal()
    data = make_data_to_return(bj_game.dealer, bj_game.player, bj_game.winner)
    players[user_name] = bj_game
    return jsonify(data)


@app.route('/hit/<user_name>')
def hit(user_name):
    # using function hit, If player won he receives his bet * 2
    # updating chips in database
    bj_game = players.get(user_name)
    bj_game.hit()
    if bj_game.winner == "Player":
        bj_game.player.chips += bj_game.player.bet * 2
        update_chips(bj_game.player.chips, user_name)
    players[user_name] = bj_game
    data = make_data_to_return(bj_game.dealer, bj_game.player, bj_game.winner)
    return jsonify(data)


@app.route('/stand/<user_name>')
def stand(user_name):
    # using function stand, Player won = receives his bet * 2, Tie = returning the bet
    # updating chips in database
    bj_game = players.get(user_name)
    bj_game.stand()
    if bj_game.winner == "Player":
        bj_game.player.chips += bj_game.player.bet * 2
        update_chips(bj_game.player.chips, user_name)
    elif bj_game.winner == "Tie":
        bj_game.player.chips += bj_game.player.bet
        update_chips(bj_game.player.chips, user_name)
    players[user_name] = bj_game
    data = make_data_to_return(bj_game.dealer, bj_game.player, bj_game.winner)
    return jsonify(data)


@app.route('/place_bet/<user_name>/<int:amount>', methods=['POST'])
def place_bet(user_name, amount):
    # placing a bet and updating current chips in database
    value_map = load_value_map("value_map.json")
    bj_game = BlackJack(value_map, user_name)
    bj_game.player.chips = current_chips(user_name)
    if amount <= bj_game.player.chips:
        bj_game.player.chips -= amount
        update_chips(bj_game.player.chips, user_name)
        bj_game.player.bet = amount

        players[user_name] = bj_game
        return jsonify(True)
    return jsonify(False)


@app.route('/out_of_chips/<user_name>')
def out_of_chips(user_name):
    # checking if a user is out of chips
    if current_chips(user_name) == 0:
        update_chips(1000, user_name)
        return jsonify(True)
    return jsonify(False)


@app.route('/the_rules')
def the_rules():
    # returning a file with the rules of the game
    with open("BlackJack rules", "r") as file:
        data = file.read()
        return data


@app.route('/chips_owned/<user_name>')
def chips_owned(user_name):
    # returning current chips
    return jsonify(current_chips(user_name))


if __name__ == '__main__':
    create_table()
    # debug = True -> every time I change the code, server will restart
    app.run()
