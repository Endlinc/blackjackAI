# NOTE: do not modify this file
from ai import Agent
from game import states

import random

ALG_MC = 1
ALG_TD = 2
ALG_QL = 3

ALG_TXT = {
    ALG_MC: "MC",
    ALG_TD: "TD",
    ALG_QL: "Q—Learning"
}

def ai_learn(ai, algorithm, num_eps, print_tester=False):
    if algorithm == ALG_MC:
        ai.MC_run(num_eps, print_tester)
    elif algorithm == ALG_TD:
        ai.TD_run(num_eps, print_tester)
    elif algorithm == ALG_QL:
        ai.Q_run(num_eps, print_tester)

def ai_compare(ai_base, ai, algorithm, tolerance, max_diffs=0):
    diff = 0

    for state in states:
        if algorithm == ALG_MC and abs(ai.MC_values[state] - ai_base.MC_values[state]) > tolerance:
            diff += 1
        elif algorithm == ALG_TD and abs(ai.TD_values[state] - ai_base.TD_values[state]) > tolerance:
            diff += 1
        elif algorithm == ALG_QL:
            if abs(ai.Q_values[state][0] - ai_base.Q_values[state][0]) > tolerance:
                diff += 1
            if abs(ai.Q_values[state][1] - ai_base.Q_values[state][1]) > tolerance:
                diff += 1

    if diff <= max_diffs:
        print("++++ PASSED {} with {} wrong values".format(ALG_TXT[algorithm], diff))
    else:
        print("---- FAILED {} with {} wrong values".format(ALG_TXT[algorithm], diff))

base = Agent()


def test_three_steps(algorithm):

    if algorithm == ALG_QL:
        print("This test doesn't apply to Q values.")
        return

    tolerance = 0.001
    max_diffs = 0
    ai = Agent()

    for step in range(0, 3):
        base.load(f"test_state_{step + 1}")
        print(f"Update update #{step + 1}:")
        
        if algorithm == 0 or algorithm == ALG_MC:
            random.seed(step)
            ai_learn(ai, ALG_MC, 1)
            ai_compare(base, ai, ALG_MC, tolerance, max_diffs)
        
        if algorithm == 0 or algorithm == ALG_TD:
            random.seed(step)
            ai_learn(ai, ALG_TD, 1)
            ai_compare(base, ai, ALG_TD, tolerance, max_diffs)
        
        print()

def test_divergence(algorithm):
    ai = Agent()
    base.load("test_convergence")
    ai.load("test_convergence")

    episodes = int(1e3)
    tolerance = 0.15
    max_diffs = {
        ALG_MC: 5,
        ALG_TD: 10,
        ALG_QL: 5,
    }

    if algorithm == 0 or algorithm == ALG_MC:
        ai_learn(ai, ALG_MC, episodes, print_tester=True)
        ai_compare(base, ai, ALG_MC, tolerance, max_diffs[ALG_MC])
    
    if algorithm == 0 or algorithm == ALG_TD:
        ai_learn(ai, ALG_TD, episodes, print_tester=True)
        ai_compare(base, ai, ALG_TD, tolerance, max_diffs[ALG_TD])
    
    if algorithm == 0 or algorithm == ALG_QL:
        ai_learn(ai, ALG_QL, episodes, print_tester=True)
        ai_compare(base, ai, ALG_QL, tolerance, max_diffs[ALG_QL])
        
    print()

def test_convergence(algorithm):
    ai = Agent()
    base.load("test_convergence")

    episodes = int(1e6)
    tolerance = 0.25
    max_diffs = {
        ALG_MC: 5,
        ALG_TD: 20,
        ALG_QL: 20,
    }

    if algorithm == 0 or algorithm == ALG_MC:
        ai_learn(ai, ALG_MC, episodes, print_tester=True)
        ai_compare(base, ai, ALG_MC, tolerance, max_diffs[ALG_MC])
    
    if algorithm == 0 or algorithm == ALG_TD:
        ai_learn(ai, ALG_TD, episodes, print_tester=True)
        ai_compare(base, ai, ALG_TD, tolerance, max_diffs[ALG_TD])
    
    if algorithm == 0 or algorithm == ALG_QL:
        ai_learn(ai, ALG_QL, episodes, print_tester=True)
        ai_compare(base, ai, ALG_QL, tolerance, max_diffs[ALG_QL])
        
    print()


