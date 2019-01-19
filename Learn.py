import pandas as pd
import numpy as np
import tensorflow as tf
from MarketEnv import MarketEnv
from Agent import Agent
from pymongo import MongoClient

mongo_store = True
test_holdout = True

db = MongoClient('mongodb://localhost:27017').ac.test_2

df = pd.read_csv('fx_daily_EUR_USD.csv',parse_dates=['timestamp'],index_col='timestamp')
df.sort_index(inplace=True)

df['ma_5'] = df.close.rolling(5).mean()
df['ma_22'] = df.close.rolling(22).mean()

df = df[['close','ma_5','ma_22']]
df['position'] = 0
df.dropna(inplace=True)

n_features = len(df.columns)
seq_size = 22

env = MarketEnv(df,seq_size)

if test_holdout:
    env_test = MarketEnv(df,seq_size,foreignScaler=env.scaler)

sess = tf.Session()
agent = Agent(sess, seq_size, n_features, hidden_size=16, a_size=3)
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


        if test_holdout:

            test_reward = 0
            s_test = env_test.reset()
            test_done = False

            while not test_done:
                a_test = agent.act(s_test,explore=False)
                s_test_, r_test, test_done = env_test.step(a_test)

                s_test = s_test_
                test_reward += r_test
       

        if mongo_store:
            doc = { 'iteration':i, 'mean_reward':last_100_episodes_mean }

            if test_holdout:
                doc['test_reward'] = test_reward

            db.insert(doc)

        print('Iteration: ' + str(i))
        print('  Last 100 mean reward: ' + str(round(last_100_episodes_mean,4)))

        if test_holdout:
            print('  Test reward: ' + str(round(test_reward,4)))

        print('\n')

    i += 1
