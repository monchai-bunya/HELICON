#!/usr/bin/python
import numpy as np
import gym, random
from gym import spaces
from gym.utils import seeding
from random import randint
import pickle
from tools import get_config

global np_random, seed, ranges, bounds, action_space, observation_space, number, guess_count, guess_max, observation, reward1_count, reward5_count
def __init__():
        ranges = 1  # Randomly selected number is within +/- this value
        bounds = 10
        action_space = np.arange(0,2,0.01)
        observation_space = spaces.Discrete(4)

        number = round(np.random.uniform(0.8, ranges),2)
        guess_count = 0
        guess_max = 10000
        observation = 0
        reward1_count = 0
        reward5_count = 0
        seed()
        reset(ranges)
        return ranges, bounds, action_space, observation_space, number, guess_count, guess_max, observation, reward1_count, reward5_count 

def seed(seed=None):
        np_random, seed = seeding.np_random(seed)
        #print(np_random, seed)
        return [seed]

def step(action, number, guess_count, guess_max, ranges, reward1_count, reward5_count):
        #assert action_space.contains(action)

        reward = 0
        done = False

        #if (number - ranges * 0.01) < action < (number + ranges * 0.01):
        if (number - 0.05) < action < (number + 0.05):
            reward = 1
            reward1_count += 1
            #done = True

        if action < number:
            observation = 1

        elif action == number:
            observation = 2
            reward = 5
            reward5_count += 1

        elif action > number:
            observation = 3

        guess_count += 1
        if guess_count >= guess_max:
            done = True
        #print(cal_r2(number,action))
        #print(number,action)
        action = action + round(random.uniform(-0.03,0.03), 2)
        return observation, reward, done, {"number": number, "guesses": guess_count}, guess_count, action, number, reward1_count, reward5_count

def reset(ranges):
        #print(np_random, seed)
        number = round(np.random.uniform(0.8, ranges),2)
        guess_count = 0
        observation = 0
        reward1_count = 0
        reward5_count = 0
        return observation, number, guess_count, reward1_count, reward5_count

ranges, bounds, action_space, observation_space, number, guess_count, guess_max, observation, reward1_count, reward5_count = __init__()

# Get configurations for the configure file
config_dic=get_config()

if (float(config_dic['vm_load_sum']) + float(config_dic['pm_load']))/float(config_dic['pm_core']) <= 0.3:
	file_name = 'guess-qtable-m1l.pkl'
elif 0.3 < (float(config_dic['vm_load_sum']) + float(config_dic['pm_load']))/float(config_dic['pm_core']) <= 0.7:
	file_name = 'guess-qtable-m1m.pkl'
else:
	file_name = 'guess-qtable-m1h.pkl'

#If there is q-table load it, do not need to create a new one
#with open("guess-qtable-m1h.pkl",'rb') as f:
with open(file_name,'rb') as f:
    Q = pickle.load(f)

# 1. Load Environment and Q-table structure
#Q = np.zeros([observation_space.n,action_space.size])

# 2. Parameters of Q-leanring
eta = .1 #628
gma = .9

count_ob_in_range = 0
count_ob1 = 0
count_ob2 = 0
count_ob3 = 0
rev_list = [] # rewards per episode calculate
real_list = []
pred_list = []
# 3. Q-learning Algorithm

   # Reset environment
s, number, guess_count, reward1_count, reward5_count = reset(ranges)
rAll = 0
fd1 = open('time_transcode.txt','r')
fd2 = open('time_receive.txt','r')
fd3 = open('time_process.txt','r')
fd4 = open('time_request.txt','r')
fd5 = open('time_total.txt','w')
tm_tr = float(fd1.read().strip())
tm_rc = float(fd2.read().strip())
tm_pr = float(fd3.read().strip())
tm_rq = float(fd4.read().strip())
tm_trt = tm_tr + tm_rc + tm_pr + tm_rq
if tm_trt == 0:
   number = round(np.random.uniform(0.5, ranges),2)
else:
   number = tm_trt

a = np.argmax(Q[s,:] + np.random.randn(1,action_space.size)*(1./(1)))
choice = round(action_space[a],2)

s1, r, d, info, guess_count, pred, real, reward1_count, reward5_count = step(choice, number, guess_count, guess_max, ranges, reward1_count, reward5_count)

#Update Q-Table with new knowledge        
Q[s,a] = Q[s,a] + eta*(r + gma*np.max(Q[s1,:]) - Q[s,a])        
s = s1
fd5.write(str(pred))
fd1.close()
fd2.close()
fd3.close()
fd4.close()
fd5.close()

# save q-table to file
with open("guess-qtable.pkl",'wb') as f:
    pickle.dump(Q,f)

