import copy
import random

HIT = 0
STAND = 1

ranks = [
    "ace",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "jack",
    "queen",
    "king",
]
suits = [
    "clubs",
    "spades",
    "diamonds",
    "hearts",
]

cards = []
for rank in ranks:
    for suit in suits:
        cards.append((rank, suit))

'''
    State representation: (user_sum, user_has_Ace, dealer_first)
        - user_sum: sum of user's cards' value, where A counts as 1. Possible values are 2 to 20
        - user_has_Ace: whether user has at least one Ace. Possible values are 0 and 1
        - dealer_first: the first card's value of dealer, where A counts as 1. Possible values are 1 to 10
        
        - Special states: 
            - WIN_STATE:    represented as (0,0,0)
            - LOSE_STATE:   represented as (1,1,1)
'''
WIN_STATE = (0,0,0)
LOSE_STATE = (1,0,0)

states = []
states.append(WIN_STATE)
states.append(LOSE_STATE)
for user_sum in range(2,21):
    for user_A_active in range(0,2):
        for dealer_first in range(1,11):
            s = (user_sum, user_A_active, dealer_first)
            states.append(s)

                
def get_amt(card):
    rank, _ = card
    if rank == "ace":
        return 1
    elif rank in ["jack", "queen", "king"]:
        return 10
    # else    
    return int(rank)

class Game:
    def __init__(self):
        self.winNum = 0
        self.loseNum = 0
        self.reset()

    def reset(self):
        # Restart the game
        self.userCard = []
        self.dealCard = []
        self.stand = False
        self.init_cards(self.userCard, self.dealCard)
        
    def init_cards(self, uList, dList):
        # Generates two cards for dealer and user, one at a time for each.
        # Returns if card is Ace and the total amount of the cards per person.
        user_A = 0
        dealer_A = 0

        card_1, card_A = self.__gen_card(uList)
        user_A += card_A
        card_2, card_A = self.__gen_card(dList)
        dealer_A += card_A
        card_3, card_A = self.__gen_card(uList)
        user_A += card_A
        card_4, card_A = self.__gen_card(dList)
        dealer_A += card_A

        # Sum of user's cards
        self.user_sum = get_amt(card_1) + get_amt(card_3)
        # Number of user's Aces
        self.user_A = user_A
        # Sum of dealer's cards (including hidden one)
        self.__dealer_sum = get_amt(card_2) + get_amt(card_4)
        # Number of all dealer's Aces (including hidden one)
        self.__dealer_A = dealer_A
        # The first card of dealer
        self.dealer_first = get_amt(card_2)

        # The state includes only information visible to the player
        self.state = self.make_state()

    def game_over(self):
        return self.stand or self.state == WIN_STATE or self.state == LOSE_STATE

    @staticmethod
    def __gen_card(xList):
        # Generate and remove an card to append to xList.
        # Return the card, and whether the card is an Ace
        cA = 0
        card = random.choice(cards)
        xList.append(card)
        if card[0] == 'ace':
            cA = 1
        return card, cA

    def make_state(self):
        # Calculate actual hands after counting A as 11 as needed
        actual_user_sum, user_A_active = self.calculate_hand(self.user_sum, self.user_A)
        actual_dealer_sum, _ = self.calculate_hand(self.__dealer_sum, self.__dealer_A)

        # If user gets 21, user wins unless dealer also gets 21
        if actual_user_sum == 21:
            if actual_dealer_sum == 21:
                return LOSE_STATE
            return WIN_STATE
        
        # If user busts, user loses
        if actual_user_sum > 21:
            return LOSE_STATE
        
        # If user stands, check results
        if self.stand:
            # User wins if dealer busts or dealer gets smaller results
            if actual_dealer_sum > 21 or actual_user_sum > actual_dealer_sum:
                return WIN_STATE
            return LOSE_STATE

        # Otherwise, return the state representation (see line 36 for explaination)
        return (self.user_sum, user_A_active, self.dealer_first)

    def act_hit(self):
        # Give player a card
        card, cA = self.__gen_card(self.userCard)
        self.user_A += cA
        self.user_sum += get_amt(card)
        
        # Make state based on the updated user cards
        self.state = self.make_state()

    @staticmethod
    def calculate_hand(card_sum, card_A):
        A_active = 0
        if card_A and card_sum + 10 <= 21:
            A_active = 1
        
        actual_sum = card_sum + A_active * 10
        return actual_sum, A_active

    def act_stand(self):
        # H17 rule: if dealer's cards contain A's, there is always one A that's counted as 11
        actual_dealer_sum, _ = self.calculate_hand(self.__dealer_sum, self.__dealer_A)
        actual_user_sum, _ = self.calculate_hand(self.user_sum, self.user_A)

        if actual_dealer_sum != 21:
            # Dealer stops when it reaches 17 or it reaches user's card value
            while actual_dealer_sum < actual_user_sum and actual_dealer_sum < 17:
                card, cA = self.__gen_card(self.dealCard)
                self.__dealer_A += cA
                self.__dealer_sum += get_amt(card)
                actual_dealer_sum, _ = self.calculate_hand(self.__dealer_sum, self.__dealer_A)
        
        # Make state based on the updated cards
        self.stand = True
        self.state = self.make_state()
    
    def update_stats(self):
        if self.state == WIN_STATE:
            self.winNum += 1
        elif self.state == LOSE_STATE:
            self.loseNum += 1
    
    def check_reward(self):
        if not self.game_over():
            return 0
        if self.state == WIN_STATE:
            return 1       
        return -1
    
    def simulate_sequence(self, policy):
        """
        Simulate a sequence based on the passed in policy

        :param policy:  the policy function that gives an action based on user's sum 
        :return:        a sequence of states from the original state to terminal
        """
        episode = []

        while not self.game_over():
            # Add the current state to episode
            episode.append((self.state, self.check_reward()))

            # Pick an action based on policy
            action = policy(self.state)

            # Perform action
            if action == HIT:
                self.act_hit()
            elif action == STAND:
                self.act_stand()
        
        # Add the terminal state
        episode.append((self.state, self.check_reward()))

        return episode

    def simulate_one_step(self, action):
        """
        Simulate one step based on the passed in action

        :param action: the action to take at the current state
        :return: a sequence of states from the original state to terminal
        """

        # If the current state is already terminal, return None
        if self.game_over():
            return None, self.check_reward()
        
        # Perform action based on the parameter
        if action == HIT:
            self.act_hit()
        elif action == STAND:
            self.act_stand()
        
        return self.state, self.check_reward()