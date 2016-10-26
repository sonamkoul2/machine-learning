import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from collections import defaultdict
import matplotlib.pyplot as plt




class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
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
        
    def chooseAction(self, state):
        epsilon = 0.1
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
        action = self.chooseAction(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.set_value(self.state, action, reward)
        
        """total_reward = []
        total_reward = []
        net_reward_list = []
        
        if reward == 12 and deadline >= 0:
            total_reward.append(reward)
            count = total_reward.count(reward)
            net_reward = sum(total_reward)/count
            net_reward_list.append(net_reward)
        plt.plot(range(len(net_reward_list)), net_reward_list)
        plt.show()"""
            
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)# [debug]
        
        
        
        

    
    
        
        
        

        
        
        
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.00001, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
