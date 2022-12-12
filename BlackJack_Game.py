from tkinter import Tk, Button, PhotoImage, Canvas, messagebox, Entry
import hashlib
import requests

base_url = 'http://127.0.0.1:5000/'


class Gui:
    def __init__(self):
        self.win_size = 900

        self.dealer_start_x = 120
        self.dealer_start_y = 200
        self.player_start_x = self.dealer_start_x
        self.player_start_y = self.win_size - self.dealer_start_y
        self.player_images = []
        self.dealer_images = []

        self.win = Tk()
        self.win.geometry(f'{self.win_size}x{self.win_size}')
        self.win.resizable(False, False)
        self.win.title('BlackJack by Ofek Elbaz')

        self.main_menu()

    def exit_game(self):
        # closing the game
        self.win.destroy()

    def refill_chips(self, username):
        url = base_url + 'out_of_chips/'
        response = requests.get(url + username)
        if response.json():
            messagebox.showinfo("", "Refilled chips back to 1000")
            self.canvas.itemconfig(chips_txt, text=f"Chips: {self.chips_owned(player_username)}",
                                   font=('comic sans ms', 35, 'bold'))
        else:
            messagebox.showinfo("", "You can only refill when out of chips")

    def hit(self, username):
        # connect ot server and deal a card for the player and dealer
        url = base_url + f'hit/{username}'
        # return stats of the game
        response = requests.get(url)
        details = response.json()

        # display player cards
        self.put_cards_on_screen(details.get("player_cards"), self.player_start_x, self.player_start_y, "player")
        # display dealer cards
        self.put_cards_on_screen(details.get("dealer_cards"), self.dealer_start_x, self.dealer_start_y, "dealer")

        # updating player score
        self.canvas.itemconfig(player_score, text=f"{player_username} score:" + str(details.get("player")),
                               font=('comic sans ms', 28, 'bold'))
        # updating dealer score
        self.canvas.itemconfig(dealer_score, text="Dealer score:" + str(details.get("dealer")),
                               font=('comic sans ms', 28, 'bold'))

        # if dealer wins show 'dealer wins' msg
        if details.get('winner') == "Dealer":
            messagebox.showinfo("", "\nDealer WINS!")
            self.game_menu(username)

        # if player wins show 'player wins' msg
        elif details.get('winner') == "Player":
            reward = details.get("bet") * 2
            messagebox.showinfo(f"", f"{username} WINS!\n"
                                     f"Earned " + str(reward) + " chips")
            self.game_menu(username)

    def stand(self, username):
        # connect to server, show hidden card and compare scores
        url = base_url + f'stand/{username}'
        # return stats of the game
        response = requests.get(url)
        details = response.json()

        # reveal the hidden card
        dealer = details.get("dealer_cards")
        self.card = PhotoImage(file=f'images/{dealer[0]}.gif')
        self.dealer_images.append(self.card)
        self.canvas.create_image(self.dealer_start_x, self.dealer_start_y, image=self.card)

        # updating player score
        self.canvas.itemconfig(chips_txt, text=f"{player_username} score:" + str(details.get("player")),
                               font=('comic sans ms', 28, 'bold'))
        # updating dealer score
        self.canvas.itemconfig(dealer_score, text="Dealer score:" + str(details.get("dealer")),
                               font=('comic sans ms', 28, 'bold'))

        # if dealer wins show 'dealer wins' msg
        if details.get('winner') == "Dealer":
            messagebox.showinfo("", "\nDealer WINS!")
            self.game_menu(username)

        # if player wins show 'player wins' msg
        elif details.get('winner') == "Player":
            reward = details.get("bet") * 2
            messagebox.showinfo("", f"{username} WINS!\n"
                                    f"Earned {str(reward)} chips")
            self.game_menu(username)

        # if it's a tie show 'It's a Tie!!!' msg
        else:
            messagebox.showinfo("", "It's a Tie!!!\n"
                                    "You earn your bet back")
            self.game_menu(username)

    def put_cards_on_screen(self, list, x, y, hand):
        # choose one of the hands to take cards from
        if hand == "player":
            for card in list:
                self.card = PhotoImage(file=f'images/{card}.gif')
                self.player_images.append(self.card)  # append image to player list for reference
                self.canvas.create_image(x, y, image=self.card)
                x += 130
        else:
            for card in list:
                self.card = PhotoImage(file=f'images/{card}.gif')
                self.dealer_images.append(self.card)  # append image to dealer list for reference
                self.canvas.create_image(x, y, image=self.card)
                x += 130

    def new_game(self, username):
        # connecting to new_game url of the server
        url = base_url + f'new_game/{username}'
        response = requests.get(url)
        details = response.json()

        # get rid of non-relevant widgets
        self.canvas.delete(bet_txt)
        bet_entry.destroy()
        place_bet_button.destroy()
        all_in_button.destroy()
        self.canvas.delete(chips_amount_txt)

        # changing background
        self.in_game_bg = PhotoImage(file='images/in game bg.png')
        self.canvas.create_image(self.win_size // 2, self.win_size // 2, image=self.in_game_bg)

        # display player cards
        self.put_cards_on_screen(details.get("player_cards"), self.player_start_x, self.player_start_y, "player")
        # display dealer cards
        self.put_cards_on_screen(details.get("dealer_cards"), self.dealer_start_x, self.dealer_start_y, "dealer")

        # player score txt
        global player_score
        player_score = self.canvas.create_text(180, 860, text=f"{player_username} score:" + str(details.get("player")),
                                               font=('comic sans ms', 28, 'bold'), fill="white")

        # player current chips txt - updated after placing bet
        current_chips = self.canvas.create_text(740, 860, text=f"Current Chips:{self.chips_owned(player_username)}",
                                                font=('comic sans ms', 20, 'bold'), fill="white")

        # player bet amount txt
        bet_amount = self.canvas.create_text(550, 540, text=f"Bet:" + str(details.get("bet")),
                                             font=('comic sans ms', 28, 'bold'), fill="white")

        # dealer score txt
        global dealer_score
        dealer_score = self.canvas.create_text(160, 40, text="Dealer score:" + str(details.get("dealer")),
                                               font=('comic sans ms', 28, 'bold'), fill="white")

        # hit button
        hit_button = Button(self.win, text="Hit", command=lambda: self.hit(username),
                            font=('comic sans ms', 25, 'bold'),
                            width=5)
        self.canvas.create_window(700, 440, window=hit_button)

        # stand button
        stand_button = Button(self.win, text="Stand", command=lambda: self.stand(username),
                              font=('comic sans ms', 25, 'bold'),
                              width=8)
        self.canvas.create_window(540, 440, window=stand_button)

    def place_bet(self, username, amount):
        # connect to server url to place bet
        if amount == "":
            messagebox.showinfo("", "Blank not allowed")
        elif amount.isnumeric():
            url = base_url + f'place_bet/{username}/{amount}'
            response = requests.post(url)
            if response.json():
                self.new_game(username)
            else:
                messagebox.showinfo("", "Don't own enough chips")
        else:
            messagebox.showinfo("", "Numbers only")

    def all_in(self, username):
        # used as command in button All-In to use all the chips
        self.place_bet(username, str(self.chips_owned(username)))

    def chips_owned(self, username):
        # connecting to chips_owned url of the server
        url = base_url + 'chips_owned/'
        response = requests.get(url + username)
        return response.json()

    def main_menu(self):
        # setting the background
        self.bg = PhotoImage(file='images/game menu bg.png')
        self.canvas = Canvas(self.win, bd=0, highlightthickness=0)

        # put image on canvas
        self.canvas.create_image(self.win_size // 2, self.win_size // 2, image=self.bg)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # welcome text
        global welcome_text
        welcome_text = self.canvas.create_text(450, 100, text="♧ ♤ ♢ ♡ Welcome to BlackJack ♡ ♢ ♤ ♧",
                                               font=('comic sans ms', 30, 'bold'), fill="white")

        # login button
        global login_option
        login_option = Button(self.win, text="Login", command=self.log_in_menu, font=('comic sans ms', 30, 'bold'),
                              width=15)
        self.canvas.create_window(440, 200, window=login_option)

        # sign-up button
        global sign_in_option
        sign_in_option = Button(self.win, text="Sign-up", command=self.sign_up_menu, font=('comic sans ms', 30, 'bold'),
                                width=15)
        self.canvas.create_window(440, 310, window=sign_in_option)

        # exit Button
        global exit_button
        exit_button = Button(self.win, text="Exit", command=self.exit_game, font=('comic sans ms', 28, 'bold'),
                             width=15)
        self.canvas.create_window(440, 750, window=exit_button)

    def sign_up_menu(self):
        # loging into an existing account
        # get rid of non-relevant widgets
        self.canvas.delete(welcome_text)
        login_option.destroy()
        sign_in_option.destroy()
        exit_button.destroy()

        # add username and password text
        self.canvas.create_text(250, 205, text="Username", font=('comic sans ms', 40, 'bold'), fill="white")
        self.canvas.create_text(250, 310, text="Password", font=('comic sans ms', 40, 'bold'), fill="white")

        # define entry boxes
        un_entry = Entry(self.win, font=('comic sans ms', 28, 'bold'), width=14, bd=0)
        pw_entry = Entry(self.win, font=('comic sans ms', 28, 'bold'), width=14, bd=0)
        # change pw text to stars
        pw_entry.config(show="*")

        # add entry boxes to the canvas
        self.canvas.create_window(400, 190, anchor="nw", window=un_entry)
        self.canvas.create_window(400, 290, anchor="nw", window=pw_entry)

        # add sign up button
        sign_up_button = Button(self.win, text="Sign-up", command=lambda: self.sign_up(un_entry.get(), pw_entry.get()),
                                font=('comic sans ms', 28, 'bold'), width=10)
        self.canvas.create_window(340, 390, anchor="nw", window=sign_up_button)

        # add Go Back button
        back_button = Button(self.win, text="Go Back", command=self.main_menu, font=('comic sans ms', 20, 'bold'),
                             width=10)
        self.canvas.create_window(790, 850, window=back_button)

    def log_in_menu(self):
        # loging into an existing account
        # get rid of non-relevant widgets
        self.canvas.delete(welcome_text)
        login_option.destroy()
        sign_in_option.destroy()
        exit_button.destroy()

        # add username and password text
        self.canvas.create_text(250, 205, text="Username", font=('comic sans ms', 40, 'bold'), fill="white")
        self.canvas.create_text(250, 310, text="Password", font=('comic sans ms', 40, 'bold'), fill="white")

        # define entry boxes
        un_entry = Entry(self.win, font=('comic sans ms', 28, 'bold'), width=14, bd=0)
        pw_entry = Entry(self.win, font=('comic sans ms', 28, 'bold'), width=14, bd=0)
        # change pw text to stars
        pw_entry.config(show="*")

        # add entry boxes to the canvas
        self.canvas.create_window(400, 190, anchor="nw", window=un_entry)
        self.canvas.create_window(400, 290, anchor="nw", window=pw_entry)

        # add login button
        login_button = Button(self.win, text="Login", command=lambda: self.log_in(un_entry.get(), pw_entry.get()),
                              font=('comic sans ms', 28, 'bold'), width=10)
        self.canvas.create_window(340, 390, anchor="nw", window=login_button)

        # add Go Back button
        back_button = Button(self.win, text="Go Back", command=self.main_menu, font=('comic sans ms', 20, 'bold'),
                             width=10)
        self.canvas.create_window(790, 850, window=back_button)

    def rules_menu(self, username):
        # get rid of non-relevant widgets
        self.canvas.delete(player_txt)
        self.canvas.delete(chips_txt)
        new_game_button.destroy()
        rules_button.destroy()
        game_exit_button.destroy()
        refill_chips_button.destroy()

        # returning all the written rules from a file
        url = base_url + 'the_rules'
        response = requests.get(url)

        # text of the rules
        self.canvas.create_text(450, 420, text=str(response.text),
                                font=('comic sans ms', 14, 'bold'), fill="white")
        # add Go Back button
        back_button = Button(self.win, text="Go Back", command=lambda: self.game_menu(username),
                             font=('comic sans ms', 20, 'bold'),
                             width=10)
        self.canvas.create_window(790, 850, window=back_button)

    def game_menu(self, username):
        # putting a new canvas above to hide non-related widgets
        self.game_menu_bg = PhotoImage(file='images/game menu bg.png')
        self.canvas = Canvas(self.win, bd=0, highlightthickness=0)
        # put image on canvas
        self.canvas.create_image(self.win_size // 2, self.win_size // 2, image=self.game_menu_bg)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # blackjack text
        global game_menu_txt
        game_menu_txt = self.canvas.create_text(440, 80, text="BlackJack",
                                                font=('comic sans ms', 60, 'bold'), fill="white")

        # player text
        global player_txt
        player_txt = self.canvas.create_text(660, 500, text=f"{player_username}",
                                             font=('comic sans ms', 36, 'bold'), fill="white")

        # chips text
        global chips_txt
        chips_txt = self.canvas.create_text(180, 510, text=f"Chips: {self.chips_owned(player_username)}",
                                            font=('comic sans ms', 36, 'bold'), fill="white")

        # refill chips
        global refill_chips_button
        refill_chips_button = Button(self.win, text="Refill chips", command=lambda: self.refill_chips(username),
                                     font=('comic sans ms', 28, 'bold'),
                                     width=15)
        self.canvas.create_window(440, 420, window=refill_chips_button)

        # new Game Button
        global new_game_button
        new_game_button = Button(self.win, text="New Game", command=lambda: self.bet_menu(username),
                                 font=('comic sans ms', 28, 'bold'),
                                 width=15)
        self.canvas.create_window(440, 200, window=new_game_button)

        # rules Button
        global rules_button
        rules_button = Button(self.win, text="Rules", command=lambda: self.rules_menu(username),
                              font=('comic sans ms', 28, 'bold'),
                              width=15)
        self.canvas.create_window(440, 310, window=rules_button)

        # exit Button
        global game_exit_button
        game_exit_button = Button(self.win, text="Exit", command=self.exit_game, font=('comic sans ms', 28, 'bold'),
                                  width=15)
        self.canvas.create_window(440, 750, window=game_exit_button)

    def bet_menu(self, username):
        # get rid of non-relevant widgets
        self.canvas.delete(game_menu_txt)
        self.canvas.delete(player_txt)
        self.canvas.delete(chips_txt)
        new_game_button.destroy()
        rules_button.destroy()
        game_exit_button.destroy()
        refill_chips_button.destroy()

        # place bet text
        global bet_txt
        bet_txt = self.canvas.create_text(450, 405, text="Place your bet", font=('comic sans ms', 40, 'bold'),
                                          fill="white")

        # chips amount txt
        global chips_amount_txt
        chips_amount_txt = self.canvas.create_text(440, 860, text=f"Current Chips: {self.chips_owned(player_username)}",
                                                   font=('comic sans ms', 35, 'bold'), fill="white")

        # bet entry box
        global bet_entry
        bet_entry = Entry(self.win, font=('comic sans ms', 28, 'bold'), width=8, bd=0)

        # add entry box to canvas
        self.canvas.create_window(450, 490, anchor="center", window=bet_entry)

        # place bet button
        global place_bet_button
        place_bet_button = Button(self.win, text="Place Bet",
                                  command=lambda: self.place_bet(player_username, bet_entry.get()),
                                  font=('comic sans ms', 20, 'bold'), width=10)
        self.canvas.create_window(450, 580, window=place_bet_button)

        # all in button
        global all_in_button
        all_in_button = Button(self.win, text="All in", command=lambda: self.all_in(username),
                               font=('comic sans ms', 20, 'bold'),
                               width=5)
        self.canvas.create_window(750, 490, window=all_in_button)

    def log_in(self, username, password):
        # loging into an existing account
        password = hashlib.sha256(password.encode()).hexdigest()
        url = base_url + 'login'
        response = requests.post(url, json={"username": username, "password": password})
        if response.json():
            global player_username
            player_username = username
            self.game_menu(username)
        else:
            messagebox.showinfo("Error", "Incorrect Username Or Password")

    def sign_up(self, username, password):
        # signing a new account to blackjack
        if username and password:  # if a user not exist
            password = hashlib.sha256(password.encode()).hexdigest()
            url = base_url + 'signup'
            response = requests.post(url, json={"username": username, "password": password})
            if response.json():
                messagebox.showinfo("", "User created")
                self.main_menu()
            # if username in already taken
            else:
                messagebox.showinfo("Error", "Username Already Taken")
        elif username == "" or password == "":
            messagebox.showinfo("Error", "Blank Not Allowed")


gui = Gui()
gui.win.mainloop()
