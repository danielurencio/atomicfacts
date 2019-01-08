import pandas as pd
import numpy as np
import tensorflow as tf
from MarketEnv import MarketEnv
from Agent import Agent
from pymongo import MongoClient

mongo_store = True
db = MongoClient('mongodb://localhost:27017').ac.test

df = pd.read_csv('fx_daily_EUR_USD.csv',parse_dates=['timestamp'],index_col='timestamp')
df.sort_index(inplace=True)
df['position'] = 0

seq_size = 22

env = MarketEnv(df,seq_size)

sess = tf.Session()
agent = Agent(sess,seq_size,5)
sess.run(tf.global_variables_initializer())

i = 0
reward_history = []
print('Sequence size: ' + str(seq_size))


while True:
    running_reward = 0
    s = env.reset()

    while True:
        a = agent.act(s)
        s_, r, done = env.step(a)
        
        td_error = agent.critic_learn(np.array([s]),r,np.array([s_]))
        agent.actor_learn(np.array([s]),a,td_error)

        s = s_
        running_reward += r

        if done:
            reward_history.append(running_reward)
            break


    if i % 100 == 0 and i > 0:
        reward_history = reward_history[-100:]
        last_100_episodes_mean = np.mean(reward_history)
        
        if mongo_store:
            db.insert({ 'iteration':i, 'mean_reward':last_100_episodes_mean })

        print(last_100_episodes_mean)

    i += 1
