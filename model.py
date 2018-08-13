#
# Copyright :kissing_heart: :brain: Team. All Rights Reserved.
#

from __future__ import print_function

import sys
import tensorflow as tf
import numpy as np
from tensorflow.python.client import device_lib

# device_lib.list_local_devices()

# TODO: Better command line option parsing?
device_name = sys.argv[0]
if device_name == "gpu":
    device_name = "/gpu:0"
else:
    device_name = "/cpu:0"

# Parameters
num_epochs = 80
learning_rate = 1e-3
batch_size = 64

# TODO: Implements adapter for event columns so that event records can be passed to the network
event_dim = 512
embedding_dim = 128 # input column dimension
encoder_net_hidden_layers = [512, 512, 256] # hidden layer dimensions for base network
latent_dim = 20 # latent variable dimension

# The number of possible answers for each query
answer_dim = [10, 20, 30]

# Placeholders
events = tf.placeholder(tf.float32, shape=[None, event_dim])
answer_0 = tf.placeholder(tf.int64, [None])
answer_1 = tf.placeholder(tf.int64, [None])
answer_2 = tf.placeholder(tf.int64, [None])

def event_adapter(batch_size):
    """
    Adapter for event records.

    Arguments
      batch_size: batch size

    Returns
      event_records: event records to be returned
      query_answers: answers to query
    """

    # TODO: Replace mock data with real data
    event_records = np.random.uniform(0, 1, (batch_size, event_dim))

    query_answers = []
    query_answers.append(np.random.randint(0, answer_dim[0], batch_size))
    query_answers.append(np.random.randint(0, answer_dim[1], batch_size))
    query_answers.append(np.random.randint(0, answer_dim[2], batch_size))

    return event_records, query_answers

def encoder_net(events_embedded):
    """
    Encoder network model for event.

    Arguments
      events: Event tensors

    Returns
      latent_variabes: Latent variables as an output of the encoder network
    """
    # Hidden layers
    h1 = tf.layers.dense(
        inputs=events_embedded,
        units=encoder_net_hidden_layers[0],
        activation=tf.nn.relu
    )

    h2 = tf.layers.dense(
        inputs=h1,
        units=encoder_net_hidden_layers[1],
        activation=tf.nn.relu
    )

    h3 = tf.layers.dense(
        inputs=h2,
        units=encoder_net_hidden_layers[2],
        activation=tf.nn.relu
    )

    # output layer
    latent_variables = tf.layers.dense(
        inputs=h3, units=latent_dim, activation=None
    )

    return latent_variables


def query_net(latent_variables, hidden_layers, output_dim):
    """
    Query network that takes latent variables and outputs answers for the specified query.

    Arguments
      latent_variables: Latent variables; output of encoder network
      hidden_layers: :ist of two integers; dimensions  for hidden layers
      output_dim: Query specific output dimension

    Returns
      logits: Output logits
    """
    h1 = tf.layers.dense(
        inputs=latent_variables,
        units=hidden_layers[0],
        activation=tf.nn.relu
    )

    h2 = tf.layers.dense(
        inputs=h1,
        units=hidden_layers[1],
        activation=tf.nn.relu
    )

    logits = tf.layers.dense(
        inputs=h2,
        units=output_dim,
        activation=None
    )

    return logits


# Declare model
embeddings = tf.Variable(tf.random_uniform([event_dim, embedding_dim], -1.0, 1.0))
events_embedded = tf.matmul(events, embeddings)
latent = encoder_net(events_embedded)
logits_0 = query_net(latent, [64, 64], answer_dim[0])
logits_1 = query_net(latent, [64, 64], answer_dim[1])
logits_2 = query_net(latent, [64, 64], answer_dim[2])

# Declare loss
loss_0 = tf.losses.hinge_loss(tf.one_hot(answer_0, answer_dim[0]), logits=logits_0)
loss_1 = tf.losses.hinge_loss(tf.one_hot(answer_0, answer_dim[1]), logits=logits_1)
loss_2 = tf.losses.hinge_loss(tf.one_hot(answer_0, answer_dim[2]), logits=logits_2)
model_loss = loss_0 + loss_1 + loss_2

# Declare Optimizer
solver = tf.train.AdamOptimizer(learning_rate).minimize(model_loss)

with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as sess:
    with tf.device(device_name):
        sess.run(tf.global_variables_initializer())

        for epoch in range(num_epochs):
            events_records, query_answers = event_adapter(batch_size)

            feed_dict = {
                events: events_records,
                answer_0: query_answers[0],
                answer_1: query_answers[1],
                answer_2: query_answers[2],
            }

            _, loss = sess.run([solver, model_loss], feed_dict)

            if epoch % 5 == 0:
                print("Epoch: {}, Loss: {:.4}".format(epoch, loss))

