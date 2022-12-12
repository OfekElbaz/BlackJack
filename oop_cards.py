import random


#  Card (suit, rank, visible=True)
class Card:
    def __init__(self, suit, rank, value=None, visible=True):
        self.suit = suit
        self.rank = rank
        self.value = value
        self.visible = visible  # can be used to ignore when calculating score

    def __str__(self):
        if self.visible:
            return self.rank + " of " + self.suit
        return "hidden"


#  Deck (a list of cards - initializes cards)
class Deck:
    def __init__(self, with_joker=False, ordered=False):
        #  create empty list
        self.cards = []
        self.suits = ('♡', '♢', '♤', '♧')

        if with_joker:
            self.ranks = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "JOKER")
        else:
            self.ranks = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")

        self.create_deck()
        if not ordered:
            self.shuffle_cards()

    def create_deck(self):
        # creating a deck with or without a joker
        for rank in self.ranks:
            for suit in self.suits:
                self.cards.append(Card(suit, rank))

    def shuffle_cards(self):
        # shuffles the cards
        random.shuffle(self.cards)

    def print_cards(self):
        for card_ in self.cards:
            print(card_)

    def deal_card(self):
        if self.cards:  # False if empty, True otherwise
            return self.cards.pop()
        return None


class Player:
    def __init__(self, name, value_map: dict[str, int]):
        self.cards = []
        self.name = name
        self.score = 0  # sum of the visible cards
        self.chips = 0  # money
        self.bet = 0
        self.value_map = value_map

    def set_card_value(self, card):
        # get the value by rank from value_map dictionary
        card_value = self.value_map.get(card.rank)
        card.value = card_value

    def get_card(self, card):
        # take a card (will be from the deck), set its value and add to personal list of cards
        self.set_card_value(card)
        self.cards.append(card)

    def remove_card(self, card):
        if card in self.cards:
            self.cards.pop(self.cards.index(card))

    def sum_score(self):
        # adding up the value of the cards
        self.reset_score()
        for card in self.cards:
            if card.visible:
                if card.value == 11 and self.score > 10:  # handling the ace card
                    card.value = 1
                self.score += card.value

    def reset_score(self):
        # reset the score
        self.score = 0
