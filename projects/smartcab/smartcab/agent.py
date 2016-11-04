import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from collections import defaultdict
import numpy as np
import pandas as pd




class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.total_rewards = 0.0
        self.total_actions = 0.0
        self.n_steps = 9
        # TODO: Initialize any additional variables here
        global QTable
        QTable = defaultdict(int)
        self._initialize_QTable()
        
    def _initialize_QTable(self):
        for state in xrange(96):
            for action in xrange(4):
                 QTable[(state, action)] = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
    def max_Q_value(self, next_state):
        maxQ = 0
        for action in self.env.valid_actions:
            this_value = QTable[(next_state, action)]
            if this_value > maxQ:
                maxQ = this_value
        return maxQ
        
    def set_value(self, state, action, reward):
        alpha = 0.9; gamma = 0.5
        old_value = QTable[(state, action)]
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        self.state = 'light: {}, left: {}. oncoming: {}, next_waypoint: {}'.format(inputs['light'], inputs['left'], inputs['oncoming'], self.next_waypoint)
        new_value = old_value * (1 - alpha) + alpha*reward + alpha*gamma * self.max_Q_value(self.state)
        QTable[(state, action)] = new_value
        
    def epsilon_decay(self, t):
        return 1.0/float(t)
        
    def chooseAction(self, state, epsilon):
        
        q = [QTable[(state, action)] for action in self.env.valid_actions]
        maxQ = max(q)
        
        count = q.count(maxQ)
       
        if count > 1:
            best = [i for i in range(4) if q[i] == maxQ]
            i = random.choice(best)
        else:
            i = q.index(maxQ)
        
        
        best_action = self.env.valid_actions[i]
        
         
        other_action = random.choice(self.env.valid_actions[:i] + self.env.valid_actions[i+1:])
        
        if random.random() <= epsilon:
            return other_action
        else:
            return best_action
            
    
    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = 'light: {}, left: {}. oncoming: {}, next_waypoint: {}'.format(inputs['light'], inputs['left'], inputs['oncoming'], self.next_waypoint)
        
        # TODO: Select action according to your policy
        self.n_steps += 1
        epsilon = self.epsilon_decay(self.n_steps)
        action = self.chooseAction(self.state, epsilon)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.set_value(self.state, action, reward)
        
        self.total_rewards += reward
        self.total_actions += 1.0
                
        print "LearningAgent.update(): deadline = {}, inputs = {}, next_waypoint = {}, action = {}, reward = {}".format(deadline, inputs, self.next_waypoint, action, reward)# [debug]
        
    def __positions(self):
        positions_list = []
        for i in range(6):
            for j in range(8):
                positions_list.append((i+1,j+1))
        return positions_list
        
def simulate(alpha=0.0, gamma=0.0):
    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track
    # Now simulate it
    sim = Simulator(e, update_delay=0.0000001)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
        
    return a

        
def for_two_sets_alpha_gamma_values(first_set={'alpha': 0.9, 'gamma':0.3}, second_set={'alpha':0.9, 'gamma':0.5}):
    alphas = []; gammas = []; rewards_per_action = []
    for a_set in [first_set, second_set]:
        alpha = a_set['alpha']; gamma = a_set['gamma']
        for values in range(15):
            a = simulate(alpha=alpha, gamma=gamma)
            alphas.append(alpha); gammas.append(gamma)
            rewards_per_action.append(float(a.total_actions))
                 
    pd.DataFrame({'alpha':alphas, 'gamma':gammas, 'rewards_per_action':rewards_per_action}).to_csv('fifteen_alpha_gamma_sets.csv')
        
def for_many_alpha_gamma_values():
    values_of_alpha = [0.1, 0.3, 0.5, 0.7, 0.9]
    values_of_gamma = [0.1, 0.3, 0.5, 0.7, 0.9]
          
    alphas = []; gammas = []
          
    avr_total_actions = []; avr_total_rewards = []
         
    for alpha in values_of_alpha:
          for gamma in values_of_gamma:
              episodes_avr_total_actions = []
              episodes_avr_total_rewards = []
              for trial in range(1):
                  a = simulate(alpha=alpha, gamma=gamma)
                  episodes_avr_total_actions.append(a.total_actions)
                  episodes_avr_total_actions.append(a.total_rewards)
                      
              alphas.append(alpha); gammas.append(gamma)
                 
              avr_total_actions.append(np.average(episodes_avr_total_actions))
              avr_total_rewards.append(np.average(episodes_avr_total_rewards))
    pd.DataFrame({'alpha':alphas, 'gamma':gammas, 'avr_total_actions':avr_total_actions, 'avr_total_rewards':avr_total_rewards}).to_csv('alpha_gamma_test.csv')
        
        
        
        
def run():
    """Run the agent for a finite number of trials."""

    if True:
        for_two_sets_alpha_gamma_values(first_set={'alpha': 0.9, 'gamma':0.3}, second_set={'alpha':0.9, 'gamma':0.5})
    elif False:
        for_many_alpha_gamma_values()   
    else:
        simulate(alpha=0.9, gamma=0.3)

if __name__ == '__main__':
    run()
