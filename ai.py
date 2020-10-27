import copy
import random
import numpy as np

from game import Game, states

HIT = 0
STAND = 1
DISCOUNT = 0.95 #This is the gamma value for all value calculations

class Agent:
    def __init__(self):

        # For MC values
        self.MC_values = {} # Dictionary: Store the MC value of each state
        self.S_MC = {}      # Dictionary: Store the sum of returns in each state
        self.N_MC = {}      # Dictionary: Store the number of samples of each state
        # MC_values should be equal to S_MC divided by N_MC on each state (important for passing tests)

        # For TD values
        self.TD_values = {}  # Dictionary storing the TD value of each state
        self.N_TD = {}       # Dictionary: Store the number of samples of each state

        # For Q-learning values
        self.Q_values = {}   # Dictionary storing the Q-Learning value of each state and action
        self.N_Q = {}        # Dictionary: Store the number of samples of each state

        self.counter = 0

        # Initialization of the values
        for s in states:
            self.MC_values[s] = 0
            self.S_MC[s] = 0
            self.N_MC[s] = 0
            self.TD_values[s] = 0
            self.N_TD[s] = 0
            self.Q_values[s] = [0,0] # First element is the Q value of "Hit", second element is the Q value of "Stand"
            self.N_Q[s] = 0
        self.simulator = Game()

    # This is the policy for MC and TD learning.
    @staticmethod
    def default_policy(state):
        user_sum = state[0]
        user_A_active = state[1]
        actual_user_sum = user_sum + user_A_active * 10
        if actual_user_sum < 14:
            return 0
        else:
            return 1

    # This is the fixed learning rate for TD and Q learning.
    @staticmethod
    def alpha(n):
        return 10.0/(9 + n)

    def rewards_to_go(self, state, list):
        reward = 0
        isBreak = False
        for i in list:
            if i == state:
                isBreak = True
            if isBreak:
                reward += np.power(DISCOUNT, self.counter) * i[1]
                self.counter += 1
        return reward
    
    def MC_run(self, num_simulation, tester=False):
        # Perform num_simulation rounds of simulations in each cycle of the overall game loop
        for simulation in range(num_simulation):
            if tester:
                self.tester_print(simulation, num_simulation, "MC")
            self.simulator.reset()  # Restart the simulator

            episode = self.simulator.simulate_sequence(self.default_policy)
            for s in episode:
                self.counter = 0
                self.S_MC[s[0]] += self.rewards_to_go(s, episode)
                self.N_MC[s[0]] += 1
                self.MC_values[s[0]] = self.S_MC[s[0]] / self.N_MC[s[0]]

    def TD_run(self, num_simulation, tester=False):
        #Perform num_simulation rounds of simulations in each cycle of the overall game loop
        for simulation in range(num_simulation):
            # Do not modify the following three lines
            if tester:
                self.tester_print(simulation, num_simulation, "TD")
            self.simulator.reset()

            s = self.simulator.state
            reward = self.simulator.check_reward()

            while s is not None:
                self.N_TD[s] += 1
                next_s, hold = self.simulator.simulate_one_step(self.default_policy(s))
                if next_s == None:
                    self.TD_values[next_s] = 0
                self.TD_values[s] += self.alpha(self.N_TD[s])*(reward
                                                               + DISCOUNT*self.TD_values[next_s] - self.TD_values[s])
                reward = hold
                s = next_s

    def Q_run(self, num_simulation, tester=False):
        #Perform num_simulation rounds of simulations in each cycle of the overall game loop
        for simulation in range(num_simulation):
            if tester:
                self.tester_print(simulation, num_simulation, "Q")
            self.simulator.reset()

            s = self.simulator.state
            reward = self.simulator.check_reward()
            while s is not None:
                self.N_Q[s] += 1
                a = self.pick_action(s, 0.4)
                next_s, hold = self.simulator.simulate_one_step(a)
                if next_s == None:
                    self.Q_values[next_s] = [0, 0]
                self.Q_values[s][a] += self.alpha(self.N_Q[s])*(reward
                                                                + DISCOUNT*max(self.Q_values[next_s][0], self.Q_values[next_s][1]) - self.Q_values[s][a])
                reward = hold
                s = next_s

    def pick_action(self, s, epsilon):
        if random.random() < epsilon:
            return random.randint(0, 1)
        else:
            return np.argmax(self.Q_values[s])

    def autoplay_decision(self, state):
        hitQ, standQ = self.Q_values[state][HIT], self.Q_values[state][STAND]
        if hitQ > standQ:
            return HIT
        if standQ > hitQ:
            return STAND
        return HIT #Before Q-learning takes effect, just always HIT

    def save(self, filename):
        with open(filename, "w") as file:
            for table in [self.MC_values, self.TD_values, self.Q_values, self.S_MC, self.N_MC, self.N_TD, self.N_Q]:
                for key in table:
                    key_str = str(key).replace(" ", "")
                    entry_str = str(table[key]).replace(" ", "")
                    file.write(f"{key_str} {entry_str}\n")
                file.write("\n")

    def load(self, filename):
        with open(filename) as file:
            text = file.read()
            MC_values_text, TD_values_text, Q_values_text, S_MC_text, N_MC_text, NTD_text, NQ_text, _  = text.split("\n\n")
            
            def extract_key(key_str):
                return tuple([int(x) for x in key_str[1:-1].split(",")])
            
            for table, text in zip(
                [self.MC_values, self.TD_values, self.Q_values, self.S_MC, self.N_MC, self.N_TD, self.N_Q], 
                [MC_values_text, TD_values_text, Q_values_text, S_MC_text, N_MC_text, NTD_text, NQ_text]
            ):
                for line in text.split("\n"):
                    key_str, entry_str = line.split(" ")
                    key = extract_key(key_str)
                    table[key] = eval(entry_str)

    @staticmethod
    def tester_print(i, n, name):
        print(f"\r  {name} {i + 1}/{n}", end="")
        if i == n - 1:
            print()