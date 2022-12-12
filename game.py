from oop_cards import Deck, Player
import json


class BlackJack:
    def __init__(self, value_map, player_name):
        self.deck = Deck()
        self.dealer = Player('Dealer', value_map)
        self.player = Player(player_name, value_map)
        self.winner = None  # player / dealer

    def first_deal(self):
        # first deal of the game, player get 2 visible cards, dealer 1 visible, hidden.
        for _ in range(2):
            self.dealer.get_card(self.deck.deal_card())
            self.player.get_card(self.deck.deal_card())

        # hide dealers first card
        self.dealer.cards[0].visible = False
        self.player.sum_score()
        self.dealer.sum_score()

    def deal(self):
        # player get card, dealer get card if below 17 points
        if self.dealer.score < 17:
            card = self.deck.deal_card()
            if card:  # check if deck is not empty
                self.dealer.get_card(card)

        card = self.deck.deal_card()
        if card:
            self.player.get_card(card)

    def hit(self):
        # dealing a card to both player and dealer, checking for busts
        self.deal()
        self.player.sum_score()
        self.dealer.sum_score()
        self.check_bust()

    def stand(self):
        # reveal dealer hidden card and compare scores, checking winner if not bust
        self.dealer.cards[0].visible = True
        self.player.sum_score()
        self.dealer.sum_score()
        if not self.check_bust():
            self.check_winner()

    def check_bust(self):
        # if dealer pass 21 and player not = player wins
        if self.dealer.score > 21 and self.player.score <= 21:
            self.winner = "Player"
            return True
        # if player pass 21 dealer wins
        if self.player.score > 21:
            self.winner = "Dealer"

    def check_winner(self):
        # comparing player and dealer scores and declaring a winner or tie
        if not self.winner:
            if self.player.score > self.dealer.score:
                self.winner = "Player"
            elif self.player.score < self.dealer.score:
                self.winner = "Dealer"
            else:
                self.winner = "Tie"


def load_value_map(filename):
    # loading cards value map
    with open(filename, 'r') as json_file:
        return json.load(json_file)
