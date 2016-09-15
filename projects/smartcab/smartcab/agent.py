import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from q_table import QLTable, QLTableUpdater
import pandas as pd
import numpy as np


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.q_table = QLTable(alpha=0.1, gamma=0.1)
        self.q_table_updater = QLTableUpdater(self.q_table)
        self.total_actions = 0.0
        self.total_rewards = 0.0
        
    def set_q_table(self, alpha=0.0, gamma=0.0):
        self.q_table = QLTable(alpha=alpha, gamma=gamma)
        self.q_table_updater = QLTableUpdater(self.q_table)
        

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        
    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = 'light: {}, left: {}. oncoming: {}, next_waypoint: {}'.format(inputs['light'], inputs['left'], inputs['oncoming'], self.next_waypoint)
        
        # TODO: Select action according to your policy
        action = self.q_table.best_action(light=inputs['light'], next_waypoint=self.next_waypoint, left=inputs['left'], oncoming=inputs['oncoming'])

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.q_table_updater.update(light=inputs['light'], next_waypoint=self.next_waypoint, left=inputs['left'], oncoming=inputs['oncoming'], action=action, reward=reward)
        
        self.total_rewards += reward
        self.total_actions += 1.0

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
    
    def __init_q_table(self):
        self.q_table = {}
        
    def __positions(self):
        positions_list = []
        for i in range(6):
            for j in range(8):
                positions_list.append(i+1, j+1)
        return positions_list
        
def simulate(alpha=0.0, gamma=0.0):
    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials
    a.set_q_table(alpha=alpha, gamma=gamma)

    # Now simulate it
    sim = Simulator(e, update_delay=0.01, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line
        
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
        pd.DataFrame({'alpha':alphas, 'gamma':gammas, 'avr_total_actions':avr_total_actions, 'avr_total_rewards':avr_total_rewards})
                 
        

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