# -*- coding: utf-8 -*-
"""pretrainedinception.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QwnFTVUAOuphokBepLxQ_Z9mjZ_xUZXD
"""

from google.colab import drive
drive.mount('/content/drive')

!unzip -uq "/content/drive/My Drive/Data.zip"

from keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1. / 255)
valid_datagen= ImageDataGenerator(rescale=1. / 255)

train_data_dir="/content/Data/Train"
validation_data_dir="/content/Data/Valid"
img_height, img_width=512,512
batch_size=16

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical')

nb_train_samples=6049

validation_generator = valid_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical')

nb_validation_samples=1397

test_generator = test_datagen.flow_from_directory(
    directory=r"/content/Data/Test",
    target_size=(224, 224),
    batch_size=1,
    class_mode=None,
    shuffle=False,
    seed=42
)

nb_test_samples=1863

import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras import regularizers
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Convolution2D, MaxPooling2D, ZeroPadding2D, GlobalAveragePooling2D, AveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, CSVLogger
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.regularizers import l2
from tensorflow import keras
import numpy as np

inception = InceptionV3(weights='imagenet', include_top=False)
x = inception.output
x = GlobalAveragePooling2D()(x)
x = Dense(128,activation='relu')(x)
x = Dropout(0.2)(x)

predictions = Dense(9,kernel_regularizer=regularizers.l2(0.005), activation='softmax')(x)

model = Model(inputs=inception.input, outputs=predictions)
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])
checkpointer = ModelCheckpoint(filepath='best_model_inception.hdf5', verbose=1, save_best_only=True)

history = model.fit_generator(train_generator,
                    steps_per_epoch = nb_train_samples //batch_size,
                    validation_data=validation_generator,
                    validation_steps= nb_validation_samples //batch_size,
                    epochs=15,
                    verbose=1,
                    callbacks=[checkpointer])

import matplotlib.pyplot as plt
def plot_accuracy(history,title):
    plt.title(title)
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train_accuracy', 'validation_accuracy'], loc='best')
    plt.show()
def plot_loss(history,title):
    plt.title(title)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train_loss', 'validation_loss'], loc='best')
    plt.show()

plot_accuracy(history,'FOOD')
plot_loss(history,'FOOD')

for layer in model.layers:
    print(layer.name)

validation_generator = valid_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_height, img_width),
    batch_size=1,
    class_mode='categorical')

model.evaluate_generator(generator=validation_generator,
steps= nb_validation_samples //batch_size)

test_generator.reset()
pred=model.predict_generator(test_generator,
steps=test_generator.n//test_generator.batch_size,
verbose=1)

predicted_class_indices=np.argmax(pred,axis=1)
print(predicted_class_indices)

labels = (train_generator.class_indices)
labels = dict((v,k) for k,v in labels.items())
predictions = [labels[k] for k in predicted_class_indices]

import pandas as pd
filenames=test_generator.filenames
results=pd.DataFrame({"Filename":filenames,
                      "Predictions":predictions})
results.to_csv("results.csv",index=False)

df=pd.read_csv('results.csv', delimiter = ',')
df

from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import numpy as np
import os
label=['burger','burrito','club_sandwich','donuts','drink','french_fries','ice_cream','pizza','samosa']
length=[223,239,200,289,39,200,200,273,200]
j=-1
s=0
cnt=0
for i in length:
  s=s+i
  j=j+1
  if cnt >100:
        break
  for n in range(s-i,s):
    if (str(df["Predictions"][n])!=str(label[j])):
      img=str("/content/Data/Test/"+df["Filename"][n])
      img = image.load_img(img, target_size=(512, 512))
      img = image.img_to_array(img)                    
      img = np.expand_dims(img, axis=0)         
      img /= 255. 
      plt.imshow(img[0])
      plt.show()
      cnt+=1
      print("predicted ="+ str(df["Predictions"][n]))
      print("actual ="+ str(label[j]))
      if cnt >100:
        break

cl=[]
j=0
prev=0
for i in length:
  prev+=i
  cl.append(prev)
y_true=[]
prev=0
k=-1
for i in cl:
  k+=1
  for j in range(prev,i):
    y_true.append(k)
  prev=i
print(y_true)
print(len(y_true))

from sklearn.metrics import confusion_matrix
cm=(confusion_matrix(y_true, predicted_class_indices))
cmn=cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
cm=np.array(cm)
print(cm)
import seaborn as sns; sns.set()
import numpy as np; np.random.seed(0)
ax = sns.heatmap(cmn,center=1,linewidths=.5,xticklabels=label, yticklabels=label)

from sklearn.metrics import classification_report
print(classification_report(y_true, predicted_class_indices, target_names=label))

