from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
import tensorflow as tf
import keras as tfk
from keras import layers, losses
from keras.datasets import fashion_mnist
from keras.models import Model

blocksize = 2400


class Autoencoder(Model):

  def __init__(self, latent_dim):
    super(Autoencoder, self).__init__()
    self.latent_dim = latent_dim
    self.encoder = tfk.Sequential([
        tfk.layers.Dense(blocksize),
        tfk.layers.LeakyReLU(alpha=0.2),
        tfk.layers.Dense(blocksize // 2),
        tfk.layers.LeakyReLU(alpha=0.2),
        tfk.layers.Dense(blocksize // 4, activation="sigmoid"),
    ])
    self.decoder = tfk.Sequential([
        tfk.layers.Dense(blocksize // 2),
        tfk.layers.LeakyReLU(alpha=0.2),
        tfk.layers.Dense(blocksize),
    ])

  def call(self, x):
    return self.decoder(self.encoder(x))


autoencoder = Autoencoder(2048)
autoencoder.compile(optimizer='adam', loss=losses.MeanSquaredError())

# autoencoder.fit(
#     x_train, x_train, epochs=10, shuffle=True, validation_data=(x_test, x_test)
# )
