#!/usr/bin/env python
import numpy as np
import csv,sys, pickle,os
#from matplotlib import pyplot
import pandas as pd
import random
from os import path
import statistics
# Importing the dataset
#dataset = pd.read_csv('Ads_Optimisation.csv')
#dataset = []
dataset_full = []
#node1 = [0.47,0.49,0.53]
#node2 = [0.45,0.47,0.51]
#node3 = [0.97,0.99,1.33]
#node4 = [0.97,0.99,1.33]

#print(dataset)
# Implementing Random Selection

#print(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
N = int(sys.argv[1])
n = int(sys.argv[2]) - 1
d = 4
#dlist = list(range(0,4))
#select_ad = np.zeros(d)
#count_select_ad = np.zeros(d)
#a = 4
ads_selected = []
std_list = [0]*d
update_list = []
core =[8,8,4,4]
#total_reward = 0
#round_reward = []

#If there is q-table load it, do not need to create a new one
#with open("multiarms-qtable.pkl",'rb') as f:
#    Q = pickle.load(f)

# 1. Load Environment and Q-table structure
#env = gym.make('FrozenLake8x8-v0')

dir_save = 'result_load'
if not path.exists(dir_save):
  os.mkdir(dir_save)

save_folder = './result_load/' 
path_name = save_folder + "load-multiarms-qtable.pkl"
count_selectnpy = save_folder + "load-count_select.npy"
load_accumulatenpy = save_folder + "load_accumulate.npy"
ad_selectnpy = save_folder + "load-ad_select.npy"
count_select = save_folder + "load-count_select"
load_accumulate = save_folder + "load_accumulate"
ad_select = save_folder + "load-ad_select"
ddlist = save_folder + "load-ddlist.txt"
r_reward = save_folder + "load-round_reward.txt"
r_nor_reward = save_folder + "load-round_nor_reward.txt"
r_max_reward = save_folder + "load-round_max_reward.txt"
t_reward = save_folder + "load-total_reward.txt"
t_max_reward = save_folder + "load-total_max_reward.txt"
r_reward_list = save_folder + "load-round_reward_list.txt"
r_nor_reward_list = save_folder + "load-round_nor_reward_list.txt"
r_max_reward_list = save_folder + "load-round_max_reward_list.txt"
result_reward = save_folder + "load-result_reward.csv"
result_reward_round = save_folder + "load-result_reward_round.csv"
result_nor_reward = save_folder + "load-result_nor_reward.csv"
result_nor_reward_round = save_folder + "load-result_nor_reward_round.csv"
result_max_reward = save_folder + "load-result_max_reward.csv"
result_max_reward_round = save_folder + "load-result_max_reward_round.csv"
result_reward_total = save_folder + "load-result_reward_total.csv"
result_max_reward_total = save_folder + "load-result_max_reward_total.csv"
result_node_select = save_folder + "load-result_node_select.csv"
result_min_node_select = save_folder + "load-result_min_node_select.csv"
result_t_total = save_folder + "load-result_std.csv"
result_min_t_total = save_folder + "load-result_min_std.csv"
node_select = save_folder + "load_node_select.txt"

if path.exists(path_name):
  with open(path_name,'rb') as f:
    Q = pickle.load(f)
else:
  Q = np.zeros([N,d])

if path.exists(t_reward):
  with open(t_reward,'rb') as ft:
    total_reward = pickle.load(ft)
else:
  total_reward = 0
if path.exists(t_max_reward):
  with open(t_max_reward,'rb') as ftx:
    total_max_reward = pickle.load(ftx)
else:
  total_max_reward = 0
if path.exists(r_reward_list):
  with open(r_reward_list,'rb') as fl:
    round_reward = pickle.load(fl)
else:
  round_reward = []
if path.exists(r_nor_reward_list):
  with open(r_nor_reward_list,'rb') as fln:
    round_nor_reward = pickle.load(fln)
else:
  round_nor_reward = []
if path.exists(r_max_reward_list):
  with open(r_max_reward_list,'rb') as flx:
    round_max_reward = pickle.load(flx)
else:
  round_max_reward = []

'''
if path.exists(count_selectnpy):
  count_select_ad = np.load(count_selectnpy)
else:
  count_select_ad = np.zeros(d)

#if path.exists(ad_selectnpy):
#  select_ad = np.load(ad_selectnpy)
#else:
#  select_ad = np.zeros(d)

if path.exists(ddlist):
  with open(ddlist,'rb') as fa:
    dlist = pickle.load(fa)
else:
  dlist = list(range(0,d))
'''
if sys.argv[2] == '1':
  dlist = list(range(0,d))
  count_select_ad = np.zeros(d)
  load_accumulate_ad = np.zeros(d)
  round_rew = 0
  round_nor_rew = 0
  round_max_rew = 0
else:
  if path.exists(count_selectnpy):
    count_select_ad = np.load(count_selectnpy)
  else:
    count_select_ad = np.zeros(d)
  if path.exists(load_accumulatenpy):
    load_accumulate_ad = np.load(load_accumulatenpy)
  else:
    load_accumulate_ad = np.zeros(d)
  if path.exists(ddlist):
    with open(ddlist,'rb') as fa:
      dlist = pickle.load(fa)
  else:
    dlist = list(range(0,d))
  if path.exists(r_reward):
    with open(r_reward,'rb') as fr:
      round_rew = pickle.load(fr)
  else:
    round_rew = 0
  if path.exists(r_nor_reward):
    with open(r_nor_reward,'rb') as frn:
      round_nor_rew = pickle.load(frn)
  else:
    round_nor_rew = 0
  if path.exists(r_max_reward):
    with open(r_max_reward,'rb') as frx:
      round_max_rew = pickle.load(frx)
  else:
    round_max_rew = 0

#print('dlist: ', dlist, ' count select: ', count_select_ad, ' Q: ', Q)
# env.obeservation.n, env.action_space.n gives number of states and action in env loaded
# 2. Parameters of Q-leanring
beta = 0.1 #628
gma = 0.9
eta = 0.3
eta_max = 0.3
max_av = 1100
sum_av = 2700 #700 + 900 + 1100
vm_load = float(sys.argv[4])
#power = accept_delay/sum_av
#epis = 100
#eps = 0.5
#decay = 0.9




##for i in range(epis):
#round_rew = 0
#eps *= decay
j = 0
l = 0
m = 0
#count_select_ad = np.zeros(d)
#select_ad = np.zeros(d)
#dlist = list(range(0,d))
##  print('Round: ',i)


#for n in range(0, N):
dataset = []
#accept_delay = float(sys.argv[4])
#dataset = np.zeros(d)
#b = random.randrange(d)
#dataset[b] = 1
#dataset = {'node1':node1[int(select_ad[0])],'node2':node2[int(select_ad[1])],'node3':node3[int(select_ad[2])],'node4':node4[int(select_ad[3])]}
##dataset_full = [node1[int(select_ad[0])],node2[int(select_ad[1])],node3[int(select_ad[2])],node4[int(select_ad[3])]]
dataset_full = [float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7]),float(sys.argv[8])]
for j in dlist:
  dataset.append(dataset_full[j])

'''
if np.random.random() < float(sys.argv[3]) or np.sum(Q[n,:]) == 0 or len(dlist) == 1: # this is not need if load q table from file
  #ad = random.randrange(d) 
  ad = random.choice(dlist)
  #print('random: ',ad)
  l += 1
else: 
  ad_value = np.max(Q[n,dlist])# + np.random.randn(1,len(dlist))*(1./(n+1)))
  ad_arr = np.where(Q[n,:] == ad_value)
  ad = random.choice(ad_arr[0])
  #ad = np.argmax(Q[n,dlist] + np.random.randn(1,len(dlist))*(1./(n+1)))
  #ad = np.argmax(Q[n,:] + np.random.randn(1,d)*(1./(n+1)))
  #print(Q[n,dlist])
  #print('Q-learning: ',ad_value, '-', ad)
  m += 1

if len(sys.argv) > 9:
  ad = int(sys.argv[9])
  #print(ad)
'''

ad = dataset_full.index(min(dataset))
print('dlist: ', dlist, ' node select: ', ad+1, ' dataset select: ', dataset_full[ad], ' dataset: ', dataset)
ads_selected.append(ad)

'''
average_load = (float(sys.argv[4])*d/sum(core) + float(sys.argv[5]) + float(sys.argv[6]) + float(sys.argv[7]) + float(sys.argv[8]))/d
#print('average_load: ', average_load)

update_list = dataset_full 
for p in range(0, d):
	update_list[p] += float(sys.argv[4])/core[p]
	std_list[p] = statistics.stdev(update_list)
	#print(p)
	#print('dataset_full: ', dataset_full)
	#print('update_list: ', update_list)
	update_list[p] -= float(sys.argv[4])/core[p]
	#print('dataset_full after: ', dataset_full)
	#print('update_list after: ', update_list)

#for j in dlist:
#  dataset.append(update_list[j])
#print('dlist: ', dlist, ' node select: ', ad+1, ' dataset select: ', update_list[ad], ' dataset: ', dataset)
#print('std_list: ', std_list)
#load_accumulate_ad[ad] += float(sys.argv[4])
if std_list[ad] <= average_load:
  reward = 1 - std_list[ad]/average_load
else:
  reward = max((statistics.mean(std_list)-std_list[ad])/statistics.mean(std_list),0)

if min(std_list) <= average_load:
  max_reward = 1 - min(std_list)/average_load
else:
  max_reward = max((statistics.mean(std_list)-min(std_list))/statistics.mean(std_list),0)

nor_reward = reward/max_reward
print('reward')
print(reward)
print('nor reward')
print(nor_reward)
print('max reward')
print(max_reward)


if dataset_full[ad] <= min(dataset):
   #print(dataset[ad])
   reward = 1
else:
   reward = 0


#Update Q-Table with new knowledge  
#Q[n,ad] = Q[n,ad] + beta*(reward + gma*np.max(Q[n,dlist]) - Q[n,ad]) 

#normalized reward & q table
if len(sys.argv) > 9:
  Q[n,ad] = Q[n,ad] + beta*(nor_reward + gma*np.max(Q[n,dlist]) - Q[n,ad])
else:
  Q[n,ad] = Q[n,ad] + beta*(reward + gma*np.max(Q[n,dlist]) - Q[n,ad]) 
'''
  
count_select_ad[ad] += 1

if 4 == count_select_ad[0]:
    dlist.remove(0)
    count_select_ad[0] += 1

if 4 == count_select_ad[1]:
    dlist.remove(1)
    count_select_ad[1] += 1

if 2 == count_select_ad[2]:
    #select_ad[2] = 2
    dlist.remove(2)
    count_select_ad[2] += 1

if 2 == count_select_ad[3]:
    #select_ad[3] = 2
    dlist.remove(3)
    count_select_ad[3] += 1

''' 
#reward = dataset[ad]
#reward = dataset.values[n, ad]
total_reward = total_reward + reward
round_rew = round_rew + reward
round_nor_rew = round_nor_rew + nor_reward
total_max_reward = total_max_reward + max_reward
round_max_rew = round_max_rew + max_reward
#print(dataset)
#print(ad)
#print(dlist)
if sys.argv[1] == sys.argv[2]:
  round_reward.append(round_rew)
  round_nor_reward.append(round_nor_rew)
  round_max_reward.append(round_max_rew)

#ad = random.randrange(d)
#ads_selected.append(ad)

# save q-table to file
with open(path_name,'wb') as f:
    pickle.dump(Q,f)
'''

np.save(count_select,count_select_ad)
#print(count_select_ad)
#np.save(load_accumulate,load_accumulate_ad)
#np.save(ad_select,select_ad)
with open(ddlist,'wb') as fa:
    pickle.dump(dlist,fa)

'''
with open(t_reward,'wb') as ft:
    pickle.dump(total_reward,ft)
with open(r_reward,'wb') as fr:
    pickle.dump(round_rew,fr)
with open(r_reward_list,'wb') as fl:
    pickle.dump(round_reward,fl)
with open(r_nor_reward,'wb') as frn:
    pickle.dump(round_nor_rew,frn)
with open(r_nor_reward_list,'wb') as fln:
    pickle.dump(round_nor_reward,fln)
with open(t_max_reward,'wb') as ftx:
    pickle.dump(total_max_reward,ftx)
with open(r_max_reward,'wb') as frx:
    pickle.dump(round_max_rew,frx)
with open(r_max_reward_list,'wb') as flx:
    pickle.dump(round_max_reward,flx)

tcap1 = open(result_reward,'a')
tcap2 = open(result_reward_round,'a')
tcap3 = open(result_reward_total,'w')
'''
tcap4 = open(result_node_select,'a')
tcap5 = open(result_t_total,'a')
tcap6 = open(node_select,'w')
'''
tcap7 = open(result_max_reward,'a')
tcap8 = open(result_max_reward_round,'a')
tcap9 = open(result_max_reward_total,'w')
#tcap10 = open(result_min_node_select,'a')
'''
tcap11 = open(result_min_t_total,'a')
'''
tcap21 = open(result_nor_reward,'a')
tcap22 = open(result_nor_reward_round,'a')

tcap1.write(str(reward))
tcap21.write(str(nor_reward))
tcap7.write(str(max_reward))
#tcap1.write(',')
#tcap2.write(str(round_rew))
#tcap2.write(',')
tcap3.write(str(total_reward))
tcap9.write(str(total_max_reward))
'''
tcap4.write(str(ad+1))
#tcap4.write(',')
tcap5.write(str(std_list[ad]))
tcap11.write(str(min(std_list)))
tcap6.write(str(ad+1))
#tcap5.write(',')
if sys.argv[1] == sys.argv[2]:
  '''
  tcap1.write('\n')
  tcap2.write(str(round_rew))
  tcap2.write('\n')
  tcap21.write('\n')
  tcap22.write(str(round_nor_rew))
  tcap22.write('\n')
  '''
  tcap4.write('\n')
  tcap5.write('\n')
  '''
  tcap7.write('\n')
  tcap8.write(str(round_max_rew))
  tcap8.write('\n')
  '''
  tcap11.write('\n')
  
else:
  '''
  tcap1.write(',')
  tcap21.write(',')
  '''
  tcap4.write(',')
  tcap5.write(',')
  '''
  tcap7.write(',')
  '''
  tcap11.write(',')
  
tcap4.close()
tcap5.close()
tcap6.close()
tcap11.close()

'''
tcap1.close()
tcap2.close()
tcap3.close()
tcap4.close()
tcap5.close()
tcap6.close()
tcap7.close()
tcap8.close()
tcap9.close()
tcap11.close()
tcap21.close()
tcap22.close()

#print('total reward')
#print(total_reward)
print('round reward')
print(round_rew)
print('round nor reward')
print(round_nor_rew)
print('round max reward')
print(round_max_rew)
#print('round reward list')
#print(round_reward)
#print('Q table')
#print(Q)
#print('Select')
#print(ads_selected)
'''
