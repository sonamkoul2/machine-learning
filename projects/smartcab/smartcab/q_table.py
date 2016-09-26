# -*- coding: utf-8 -*-
"""
Created on Thu Sep 08 18:25:56 2016

@author: sonam
"""

class QLTable():
    def __init__(self, alpha=1.00, gamma=0.5):
        self._alpha = alpha; self._gamma = gamma; self.__initialize_table()

    def alpha(self):
        return self._alpha

    def gamma(self):
        return self._gamma
        
    def max_q_l(self, light=None, next_waypoint=None, left=None, oncoming=None):
        
        values =[]
        for action in ['forward', 'left', 'right', 'None']:
            values.append(self.get_value(light=light, next_waypoint=next_waypoint, left=left, oncoming=oncoming, action=action))
            return max(values)
    
    def getQ(self, light=None, next_waypoint=next_waypoint, left=left, oncoming=None, action):
        return self.q.get((state, action),0.0)

    def learnQ(self, state, action, reward, newv):
        oldv = self.q.get((state, action), reward)
        self.q[(state, action)] = (1-self.alpha)*oldv + self.alpha * newv

    def chooseAction(self, state):
        q = {self.getQ(state, a) for a in ['forward', 'left', 'right', 'None']}
        maxq = max(q)
        action = self.actions[maxq]
        return action
    def learn(self, state1, action1, reward, state2):
        maxqnew = max([self.getQ(state2, a) for a in ['forward', 'left', 'right', 'None']])
        maxqvec=[]        
        for act in self.valid_actions:
            maxqvec.append(self.getQ(state2,act))
            maxqnew=max(maxqvec)
            self.learnQ(state1, action1, reward, reward + self.gamma*maxqnew)
 


    def get_value(self, light=None, next_waypoint=None, left=None, oncoming=None, action=None):
        
        return self._table[self.__state_action(light=light, left=left, oncoming=oncoming, next_waypoint=next_waypoint, action=action)]

    def set_value(self, light=None, next_waypoint=None, left=None, oncoming=None, action=None, newv=0.0):
        
        self._table[self.__state_action(light=None, next_waypoint=None, left=None, oncoming=None, action=action)] = newv


    def update(self, light=None, next_waypoint=None, left=None, oncoming=None, action=None, reward=0.0):
        
        oldv = self.__value(light=light, next_waypoint=next_waypoint, left=left, oncoming=oncoming, action=action)

        newv = oldv * (1 - self._alpha) + self._alpha * (reward + self._gamma * oldv)

        self.__set_value(light=light, next_waypoint=next_waypoint, left=left, oncoming=oncoming, action=action, newv=newv)
        
    def argMax(self, light=None, next_waypoint=None, left=None, oncoming=None):
        # Returns the key with the highest value
        if len(self.keys()) == 0: return None
        all = self.items()
        values = [X[1] for X in all]
        maxIndex = values.index(max(values))
        return all[maxIndex][0]
        


    def __next_waypoint(self, light, next_waypoint):
        return self._table['light'][light]['next_waypoint'][next_waypoint]

    def __state_action(self, light=None, next_waypoint=None, left=None, oncoming=None, action=None):
        return "{}-{}-{}-{}-{}".format(str(light), str(left), str(oncoming), str(next_waypoint), str(action))

    def __initialize_table(self):
        self._table = {}
        

        for light in ['red', 'green']:
            for left in ['forward', 'left', 'right', 'None']:
                for oncoming in ['forward', 'left', 'right', 'None']:
                    for next_waypoint in ['forward', 'left', 'right', 'None']:
                        for action in ['forward', 'left', 'right', 'None']:
                            self._table[self.__state_action(light=None, next_waypoint=None, left=None, oncoming=None, action=action)] = 0.0
                                
class QLTableUpdater():
    def __init__(self, table, action_value_table):
        self.table = table
        self.action_value_table = action_value_table  
        
    def update(self, light=None, next_waypoint=None, left=None, oncoming=None, action=None, reward=0.0):
        
        light, next_waypoint, left, oncoming = state
        
        oldv = self.table.get_value(light=light, next_waypoint=next_waypoint, oncoming=oncoming, left=left, action=action)
        
        newv = oldv*(1 - self.table._alpha) + self.table._alpha * (reward + self.table._gamma*self.table.max_q_l(light=light, oncoming=oncoming, next_waypoint=next_waypoint, left=left))
        
        self.table.set_value(light=light, left=left, oncoming=oncoming, next_waypoint=next_waypoint, action=action, new=newv)
        


       