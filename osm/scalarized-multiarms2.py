#!/usr/bin/env python
import numpy as np
import csv,sys, pickle
#from matplotlib import pyplot
import pandas as pd
import random, os
from os import path
# Importing the dataset
#dataset = pd.read_csv('Ads_Optimisation.csv')
#dataset = []
#dataset_full = []
#node1 = [0.47,0.49,0.53]
#node2 = [0.45,0.47,0.51]
#node3 = [0.97,0.99,1.33]
#node4 = [0.97,0.99,1.33]

#print(dataset)
# Implementing Random Selection

#print(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
N = int(sys.argv[1])
n = int(sys.argv[2]) - 1
weight_time = float(sys.argv[4])
weight_load = float(sys.argv[5])
ttotal1 = float(sys.argv[6])
ttotal2 = float(sys.argv[7])
ttotal3 = float(sys.argv[8])
ttotal4 = float(sys.argv[9])
ttotal_ave = float(sys.argv[10])
load1 = float(sys.argv[11])
load2 = float(sys.argv[12])
load3 = float(sys.argv[13])
load4 = float(sys.argv[14])
load_ave = float(sys.argv[15])
d = 4
#dlist = list(range(0,4))
#select_ad = np.zeros(d)
#count_select_ad = np.zeros(d)
#a = 4
ads_selected = []
#total_reward = 0
#round_reward = []

#If there is q-table load it, do not need to create a new one
#with open("multiarms-qtable.pkl",'rb') as f:
#    Q = pickle.load(f)

# 1. Load Environment and Q-table structure
#env = gym.make('FrozenLake8x8-v0')
dir_save = 'result_scalarized'
if not path.exists(dir_save):
  os.mkdir(dir_save)

save_folder = './result_scalarized/' 
save_folder_ttotal = './result_ttotal/' 
save_folder_load = './result_load/' 

path_name_q_scala = save_folder + "scala-multiarms-qtable.pkl"
path_name_q_ttotal = save_folder_ttotal + "multiarms-qtable.pkl"
path_name_q_load = save_folder_load + "load-multiarms-qtable.pkl"

count_selectnpy = save_folder + "scala-count_select.npy"
ad_selectnpy = save_folder + "scala-ad_select.npy"
count_select = save_folder + "scala-count_select"
ad_select = save_folder + "scala-ad_select"
ddlist = save_folder + "scala-ddlist.txt"
#r_reward = save_folder + "round_reward.txt"
#r_nor_reward = save_folder + "round_nor_reward.txt"
#r_max_reward = save_folder + "round_max_reward.txt"
#t_reward = save_folder + "total_reward.txt"
#t_max_reward = save_folder + "total_max_reward.txt"
#r_reward_list = save_folder + "round_reward_list.txt"
#r_nor_reward_list = save_folder + "round_nor_reward_list.txt"
#r_max_reward_list = save_folder + "round_max_reward_list.txt"
#result_reward = save_folder + "result_reward.csv"
#result_reward_round = save_folder + "result_reward_round.csv"
#result_nor_reward = save_folder + "result_nor_reward.csv"
#result_nor_reward_round = save_folder + "result_nor_reward_round.csv"
#result_max_reward = save_folder + "result_max_reward.csv"
#result_max_reward_round = save_folder + "result_max_reward_round.csv"
#result_reward_total = save_folder + "result_reward_total.csv"
#result_max_reward_total = save_folder + "result_max_reward_total.csv"
result_node_select = save_folder + "scala-result_node_select.csv"
#result_min_node_select = save_folder + "result_min_node_select.csv"
result_t_total = save_folder + "result_t_total.csv"
result_load = save_folder + "result_load.csv"
result_t_total_load = save_folder + "result_t_total_load.csv"
#result_min_t_total = save_folder + "result_min_t_total.csv"
node_select = save_folder + "scala-node_select.txt"

beta = 0.1 #628
gma = 0.9
eta = 0.3
eta_max = 0.3
'''
#load q T total
if path.exists(path_name_q_ttotal):
  with open(path_name_q_ttotal,'rb') as ft:
    Qt = pickle.load(ft)
else:
  Qt = np.zeros([N,d])

#load q load
if path.exists(path_name_q_load):
  with open(path_name_q_load,'rb') as fl:
    Ql = pickle.load(fl)
else:
  Ql = np.zeros([N,d])

#load q scala
if path.exists(path_name_q_scala):
  with open(path_name_q_scala,'rb') as fs:
    Q = pickle.load(fs)
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

if sys.argv[2] == '1':
  dlist = list(range(0,d))
  count_select_ad = np.zeros(d)
  #round_rew = 0
  #round_nor_rew = 0
  #round_max_rew = 0
else:
  if path.exists(count_selectnpy):
    count_select_ad = np.load(count_selectnpy)
  else:
    count_select_ad = np.zeros(d)
  if path.exists(ddlist):
    with open(ddlist,'rb') as fa:
      dlist = pickle.load(fa)
  else:
    dlist = list(range(0,d))
  '''
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
  '''

#print('dlist: ', dlist, ' count select: ', count_select_ad, ' Q: ', Q)
# env.obeservation.n, env.action_space.n gives number of states and action in env loaded
# 2. Parameters of Q-leanring
'''
beta = 0.1 #628
gma = 0.9
eta = 0.3
eta_max = 0.3
#max_av = 1100
#sum_av = 2700 #700 + 900 + 1100
#accept_delay = float(sys.argv[4])
#power = accept_delay/sum_av
#epis = 100
#eps = 0.5
#decay = 0.9
'''
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

dataset_full_t = [(ttotal1-ttotal_ave)/ttotal_ave,(ttotal2-ttotal_ave)/ttotal_ave,(ttotal3-ttotal_ave)/ttotal_ave,(ttotal4-ttotal_ave)/ttotal_ave]
dataset_full_l = [(load1-load_ave)/load_ave,(load2-load_ave)/load_ave,(load3-load_ave)/load_ave,(load4-load_ave)/load_ave]
dataset_full_tl = [(weight_time * x) + (weight_load * y) for x, y in zip(dataset_full_t,dataset_full_l)]

for j in dlist:
  dataset.append(dataset_full_tl[j])

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
'''

#if len(sys.argv) > 9:
#  ad = int(sys.argv[9])
ad = dataset_full_tl.index(min(dataset))
print('scale dlist: ', dlist, ' scala node select: ', ad+1)
#print('dlist: ', dlist, ' node select: ', ad+1, ' dataset select: ', dataset_full[ad], ' dataset: ', dataset)
ads_selected.append(ad)

'''
#if dataset[ad] <= min(dataset):
if dataset_full[ad] <= accept_delay:
  reward = ((eta_max - eta)/eta_max) + (1/dataset_full[ad]**power)
  #reward = 1/dataset_full[ad]**power
  #reward = eta + (accept_delay - dataset_full[ad])/(accept_delay**2)
else:
  reward = min(1/dataset_full[ad]**power,1/(dataset_full[ad]-accept_delay))
  #reward = min(0,1/dataset_full[ad]**power)
  #reward = max(0,eta + (accept_delay - dataset_full[ad])/(accept_delay**2))

if min(dataset) <= accept_delay:
  max_reward = ((eta_max - eta)/eta_max) + (1/min(dataset)**power)
else:
  max_reward = min(1/min(dataset)**power,1/(min(dataset)-accept_delay))

nor_reward = reward/max_reward


reward = (weight_time * Qt[n,ad]) + (weight_load * Ql[n,ad])
print('scala-reward')
print(reward)
#print('nor reward')
#print(nor_reward)
#print('max reward')
#print(max_reward)


if dataset_full[ad] <= min(dataset):
   #print(dataset[ad])
   reward = 1
else:
   reward = 0


#Update Q-Table with new knowledge  
Q[n,ad] = Q[n,ad] + beta*(reward + gma*np.max(Q[n,dlist]) - Q[n,ad]) 

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
with open(path_name_q_scala,'wb') as f:
    pickle.dump(Q,f)
'''
np.save(count_select,count_select_ad)
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
tcap21 = open(result_nor_reward,'a')
tcap22 = open(result_nor_reward_round,'a')
tcap3 = open(result_reward_total,'w')
'''
tcap4 = open(result_node_select,'a')
tcap5 = open(result_t_total,'a')
tcap51 = open(result_load,'a')
tcap52 = open(result_t_total_load,'a')
tcap6 = open(node_select,'w')

'''
tcap7 = open(result_max_reward,'a')
tcap8 = open(result_max_reward_round,'a')
tcap9 = open(result_max_reward_total,'w')
#tcap10 = open(result_min_node_select,'a')
tcap11 = open(result_min_t_total,'a')


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
tcap5.write(str(dataset_full_t[ad]))
tcap51.write(str(dataset_full_l[ad]))
tcap52.write(str(dataset_full_tl[ad]))
'''
tcap11.write(str(min(dataset)))
'''
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
  tcap51.write('\n')
  tcap52.write('\n')
  '''
  tcap7.write('\n')
  tcap8.write(str(round_max_rew))
  tcap8.write('\n')
  tcap11.write('\n')
  '''
else:
  '''
  tcap1.write(',')
  tcap21.write(',')
  '''
  tcap4.write(',')
  tcap5.write(',')
  tcap51.write(',')  
  tcap52.write(',')
  '''
  tcap7.write(',')
  tcap11.write(',')
  '''
'''
tcap1.close()
tcap2.close()
tcap3.close()
'''
tcap4.close()
tcap5.close()
tcap51.close()
tcap52.close()
tcap6.close()
'''
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
#print('Qt table')
#print(Qt)
#print('Ql table')
#print(Ql)
#print('Select')
#print(ads_selected)
'''


