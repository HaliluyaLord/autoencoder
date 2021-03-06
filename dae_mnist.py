import numpy as np
import matplotlib.pyplot as plt

from keras.models import Model
from keras.layers import (Input, Conv2D, MaxPooling2D, UpSampling2D, LeakyReLU)

# Load data
from keras.datasets import mnist

# input image dimensions
img_rows, img_cols = 28, 28                          
input_shape = (img_rows, img_cols, 1)

# the data, shuffled and split between train and test sets
(x_train, _), (x_test, _) = mnist.load_data()

x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)

x_train = x_train.astype('float32') / 255
x_test = x_test.astype('float32') / 255

noise_factor = 0.5
x_train_noisy = x_train + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x_train.shape)
x_test_noisy = x_test + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x_test.shape)
x_train_noisy = np.clip(x_train_noisy, 0., 1.)
x_test_noisy = np.clip(x_test_noisy, 0., 1.)

print(x_train.shape[0], ' train samples')
print(x_test.shape[0], ' test samples')
    
def DAE_CNN(features_shape, act='relu'):

    # Input
    x = Input(name='inputs', shape=features_shape, dtype='float32')
    o = x
    
    # Encoder
    o = Conv2D(32, (3, 3), activation=act, padding='same', strides=(1,1), name='en_conv1')(o)
    o = MaxPooling2D((2, 2), strides=(2,2), padding='same', name='en_pool1')(o)
    o = Conv2D(32, (3, 3), activation=act, padding='same', strides=(1,1), name='en_conv2')(o)
    enc = MaxPooling2D((2, 2), strides=(2,2), padding='same', name='en_pool2')(o)
    
    # Decoder
    o = Conv2D(32, (3, 3), activation=act, padding='same', strides=(1,1), name='de_conv1')(enc)
    o = UpSampling2D((2, 2), name='upsampling1')(o)
    o = Conv2D(32, (3, 3), activation=act, padding='same', strides=(1,1), name='de_conv2')(o)
    o = UpSampling2D((2, 2), name='upsampling2')(o)
    dec = Conv2D(1, (3, 3), activation='sigmoid', padding='same', strides=(1,1), name='de_conv3')(o)
    
    # Print network summary
    Model(inputs=x, outputs=dec).summary()
    
    return Model(inputs=x, outputs=dec)

batch_size = 128
epochs = 40

autoenc = DAE_CNN(input_shape, act=LeakyReLU(alpha=0.1))
autoenc.compile(optimizer='adadelta', loss='binary_crossentropy')

autoenc.fit(x_train_noisy, x_train, epochs=epochs, batch_size=batch_size,
            shuffle=True, validation_data=(x_test_noisy, x_test))

decoded_imgs = autoenc.predict(x_test_noisy)

n = 10
plt.figure(figsize=(20, 4))
for i in range(1,n+1):
    # display original
    ax = plt.subplot(2, n, i)
    plt.imshow(x_test_noisy[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # display reconstruction
    ax = plt.subplot(2, n, i + n)
    plt.imshow(decoded_imgs[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()
