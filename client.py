import hashlib

import requests

base_url = 'http://127.0.0.1:5000/'


def sign_up(username, password):
    # signing a new account to blackjack
    if username and password:
        password = hashlib.sha256(password.encode()).hexdigest()
        url = base_url + 'signup'
        response = requests.post(url, json={"username": username, "password": password})
        return response.json()
    else:
        return False


def log_in(username, password):
    # loging into an existing account
    password = hashlib.sha256(password.encode()).hexdigest()
    url = base_url + 'login'
    response = requests.post(url, json={"username": username, "password": password})
    return response.json()


def place_bet(username, amount):
    # placing bet using
    url = base_url + f'place_bet/{username}/{amount}'
    response = requests.post(url)
    return response.json()


def print_game_details(details, username):
    # printing the hand of the player and dealer
    print(f"\n#{username} hand# - Current chips: " + str(details.get("chips")))
    for card in details.get("player_cards"):
        print(card)
    print(f"Score:" + str(details.get("player")))
    print(f"--------------       Bet: " + str(details.get("bet")))
    print("#Dealer's hand#")
    for card in details.get("dealer_cards"):
        print(card)
    print(f"Score:" + str(details.get("dealer")))


def new_game(username):
    # connecting to new_game url of the server
    url = base_url + f'new_game/{username}'
    response = requests.get(url)
    details = response.json()
    print_game_details(details, username)


def hit(username):
    # connecting to hit url of the server, and printing results
    url = base_url + f'hit/{username}'
    response = requests.get(url)
    details = response.json()
    print_game_details(details, username)
    if details.get('winner') == "Dealer":
        print("\nDealer WINS!")
        return True
    elif details.get('winner') == "Player":
        reward = details.get("bet") * 2
        print(f"\n{username} WINS!\n"
              f"Earned " + str(reward) + " chips")
        return True


def stand(username):
    # connecting to stand url of the server, and printing results
    url = base_url + f'stand/{username}'
    response = requests.get(url)
    details = response.json()
    print_game_details(details, username)
    if details.get('winner') == "Dealer":
        print("\nDealer WINS!")
    elif details.get('winner') == "Player":
        reward = details.get("bet") * 2
        print(f"\n{username} WINS!\n"
              f"Earned {str(reward)} chips")
    else:
        print("It's a Tie!!!\n"
              "You earn your bet back")


def chips_owned(username):
    # connecting to chips_owned url of the server
    url = base_url + 'chips_owned/'
    response = requests.get(url + username)
    return response.json()


def out_of_chips(username):
    # connecting to out_of_chips url of the server
    url = base_url + 'out_of_chips/'
    response = requests.get(url + username)
    print(response.text)


def the_rules():
    # connecting to the_rules url of the server
    url = base_url + 'the_rules'
    response = requests.get(url)
    print(response.text)


def game_menu(username):
    # blackjack main menu
    while True:
        menu_input = input(f"\n♡ ♢ ♧ ♤ Welcome {username} to BlackJack ♡ ♢ ♧ ♤\n"
                           f"1. Start a new game            Chips: {chips_owned(username)}\n"
                           f"2. Refill chips\n"
                           f"3. How to play\n"
                           f"0. Exit-Game\n"
                           f">>> ")

        if menu_input == "1":
            # starting the game
            bet_input = input("\nPlace your bet:       Type 'All' to all-in\n"
                              ">>> ")
            if bet_input.isnumeric():
                if place_bet(username, bet_input):
                    print("Bet placed")
                    new_game(username)
                else:
                    print("You don't own enough chips")
                    continue
            # option to all-in
            elif bet_input.lower() == "all":
                if place_bet(username, chips_owned(username)):
                    print("Bet placed")
                    new_game(username)
            else:
                print("invalid input")
                continue
            # hit or stand after the game started
            while True:
                game_input = input("\n1. Hit\n"
                                   "2. Stand\n"
                                   ">>> ")
                if game_input == "1":
                    if hit(username):
                        break

                elif game_input == "2":
                    stand(username)
                    break

        elif menu_input == "2":
            # refilling chips to 1000 when a player reach 0 chips
            out_of_chips(username)

        elif menu_input == "3":
            # printing the rules of the game
            the_rules()

        elif menu_input == "0":
            # exiting the game
            print("Hope you had fun :3\n"
                  "Gamble responsibly")
            break


# log-in menu
while True:
    user_input = input("\n♡ ♢ ♧ ♤ Welcome to BlackJack ♡ ♢ ♧ ♤\n"
                       "1. Login\n"
                       "2. Sign-Up\n"
                       "0. Exit\n"
                       ">>> ")
    if user_input == "1":
        # log-in option
        log_in_username = input("\nUsername: ")
        log_in_password = input("Password: ")
        if log_in(log_in_username, log_in_password):
            print("\nLoading game...")
            game_menu(log_in_username)
            break
        else:
            print("\nWrong username or password")

    elif user_input == "2":
        # sign-up option
        print("\nLet's create an account :3")
        sign_up_username = input("Username: ")
        sign_up_password = input("Password: ")
        print(sign_up(sign_up_username, sign_up_password))

    elif user_input == "0":
        # close the game
        print("Goodbye")
        break
