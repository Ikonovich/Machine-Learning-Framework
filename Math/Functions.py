import random

import numpy as np
# We are using Numba to improve the performance of some mathematical functions
from numba import jit, float32, int32, int64


# This file contains activation functions and their derivatives, learning rate functions, and general helper
# functions.

########### BEGIN LEARNING RATE FUNCTIONS #########

# Function for a static learning rate, used for convenience
def constant_learning_rate(network):
    return network.lrn_rate_modifier

# Learn rate decreases linearly as batch accuracy decreases.
def inv_batch_accuracy_lrn_rate(network):
    return (1 - network.last_batch_accuracy) * network.lrn_rate_modifier


LEARNING_FUNCTION_MAP = {
    "constant": constant_learning_rate,
    "inverse_batch_accuracy": inv_batch_accuracy_lrn_rate
}

########### END LEARNING RATE FUNCTIONS #########

########### BEGIN ACTIVATION FUNCTIONS ##########


### Calculate tanh of x
def tanh(x):
    x = np.round(x, 5)
    return np.divide((np.exp(2 * x) - 1.0), (np.exp(2 * x) + 1.0))


### Calculate derivative of tanh of x
def tanh_prime(x):
    x = np.round(x, 5)
    return 1.0 - np.square(x)


### Calculate sigmoid of x
def sigmoid(x):
    return np.piecewise(x, [x > 0],
                        [lambda i: 1 / (1 + np.exp(-i)),
                         lambda i: np.exp(i) / (1 + np.exp(i))])


### Calculate sigmoid of x, different method
@jit(float32[:](float32[:]), forceobj=True)
def sigmoid_two(x):
    result = []
    for num in x:
        if num >= 0:
            result.append(1. / (1. + np.exp(-num)))
        else:
            result.append(np.exp(num) / (1. + np.exp(num)))
    return result


### Calculate derivative of sigmoid of x
@jit(float32[:](float32[:]), forceobj=True)
def sigmoid_prime(x):
    sig = sigmoid(x)
    return sig * (1.0 - sig)


### Calculate relu
@jit(float32[:](float32[:]))
def relu(x):
    return np.maximum(x, 0)


### Calculate derivative of relu
@jit(float32[:](float32[:]))
def relu_prime(x):
    output = np.zeros(shape=(x.size,))
    for i, xi in enumerate(x):
        if xi > 0:
            output[i] = 1
    return output.reshape(output.size, 1)


# calculate leaky relu
@jit
def leaky_relu(x):
    results = []
    for num in x:
        if num > 0:
            results.append(num)
        else:
            results.append(0.01 * num)
    return results


### Calculate derivative of leaky relu
@jit(nopython=True)
def leaky_relu_prime(x):
    output = []
    output = np.zeros(shape=(x.size,))
    for i, xi in enumerate(x):
        if xi > 0:
            output[i] = 1
        else:
            output[i] = 0.01
    return output.reshape(output.size, 1)

@jit(nopython=True, parallel=True)
def softmax(x):
    output = np.exp(x - x.max())
    return output / np.sum(output)

@jit
def softmax_prime(x):
    # Reshape the 1-d softmax to 2-d so that np.dot will do the matrix multiplication
    s = x.reshape(-1, 1)
    return np.diagflat(s) - np.dot(s, s.T)


# Map activations to functions
ACTIVATION_FUNCTION_MAP = {
    "leaky_relu": (leaky_relu, leaky_relu_prime),
    "relu": (relu, relu_prime),
    "sigmoid": (sigmoid_two, sigmoid_prime),
    "tanh": (tanh, tanh_prime),
    "softmax": (softmax, softmax_prime)
}
