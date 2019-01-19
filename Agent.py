# Running with tensorflow==1.5
import tensorflow as tf
import pandas as pd
import numpy as np

LSTM = tf.keras.layers.LSTM

class Agent(object):

    def __init__(
            self,
            session,
            seq_size,
            n_features,
            a_size=3,
            hidden_size=32,
            stacks=1,
            gamma=0.9,
            learning_rate={ 'actor':0.0001, 'critic':0.001 }
            ):

        self.sess = session

        sequence_length = tf.placeholder(tf.float32, shape=[seq_size])

        self.state = tf.placeholder(shape=[None,seq_size,n_features], dtype=tf.float32, name='state')
        self.reward = tf.placeholder(shape=None, dtype=tf.float32)
        self.value_ = tf.placeholder(shape=[1,1], dtype=tf.float32)
        self.action = tf.placeholder(shape=None, dtype=tf.int32, name='action')
        self.actor_td = tf.placeholder(shape=None,dtype=tf.float32, name='td_error')


        with tf.variable_scope('NN'):
            lstm_0 = LSTM(units=hidden_size,return_sequences=False).apply(self.state)

            self.action_prob = tf.layers.dense(
                inputs=lstm_0,
                units=a_size,
                activation=tf.nn.softmax,
                name='distribution_over_actions'
            )

            self.value = tf.layers.dense(
                inputs=lstm_0,
                units=1,
                activation=None,
                name='value'
            )

        # Temporal-difference error:
        self.td_error = self.reward + gamma * self.value_ - self.value

        # Critic optimization:
        self.critic_loss = tf.square(self.td_error)
        self.critic_opt = tf.train.RMSPropOptimizer(learning_rate['critic']).minimize(self.critic_loss)

        # Actor optimization:
        log_prob = tf.log(self.action_prob[0, self.action])
        self.actor_loss = tf.reduce_mean(log_prob * self.actor_td)
        self.actor_opt = tf.train.RMSPropOptimizer(learning_rate['actor']).minimize(-self.actor_loss)



    def critic_learn(self, state, reward, state_):
        value_ = self.sess.run(self.value, { self.state:state_ })
        feed_dict = { self.state: state, self.value_:value_, self.reward:reward }
        td_error, _ = self.sess.run([self.td_error, self.critic_opt], feed_dict) 

        return td_error



    def actor_learn(self,state,action,td_error):
        feed_dict = { self.state:state, self.action:action, self.actor_td:td_error }
        self.sess.run([self.actor_opt,self.actor_loss],feed_dict)



    def act(self,s,explore=True):

        a_dist = self.sess.run(self.action_prob, feed_dict={ self.state:[s] })

        if explore:
            a = np.random.choice(a_dist[0], p=a_dist[0])
        else:
            a = np.max(a_dist[0])

        a = np.argmax(a_dist == a)

        return a

