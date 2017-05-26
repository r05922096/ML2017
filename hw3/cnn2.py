import sys, random
from mytool import parser
import numpy as np
import keras
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D, Flatten
from keras.optimizers import SGD, Adam
from keras.utils import np_utils
from keras.datasets import mnist
from keras.preprocessing.image import ImageDataGenerator


train_file = sys.argv[10] if len(sys.argv) > 10 else './data/train.csv'
test_file = sys.argv[1] if len(sys.argv) > 1 else './data/test.csv'
predict_file = sys.argv[2] if len(sys.argv) > 2 else './predict.csv'



def histogramEqualization(data):
	shape = data.shape
	data = data.reshape((-1))

	# generate histogram
	hist = [0]*256
	for pixel in data:
		hist[int(pixel)] += 1

	# sum
	sum_hist = [0]*256
	sum_hist[0] = hist[0]
	for idx in xrange(1,256,1):
		sum_hist[idx] = hist[idx] + sum_hist[idx-1]

	# Equalization
	for idx in xrange(len(data)):
		gray = int(data[idx])
		data[idx] = float(int(round(255.0*sum_hist[gray]/sum_hist[255])))

	data = data.reshape(shape)

def lightNormalize(dataset):
	print 'lightNormalize'
	for data in dataset:
		histogramEqualization(data)



# load data
X, Y = parser.parse(train_file)
test_X, test_Y = parser.parse(test_file)

# split data set
#lightNormalize(X)
#lightNormalize(test_X)
X = X/255
test_X = test_X/255
train_X, train_Y = X[:-1000], Y[:-1000]
evaluate_X, evaluate_Y = X[-1000:], Y[-1000:]


# data gen
datagen = ImageDataGenerator(
	rotation_range=40,
	shear_range=0.2,
    width_shift_range=0.2,
	height_shift_range=0.2,        
	horizontal_flip=True,
	fill_mode='nearest')

# init model
model = Sequential()

model.add(Conv2D(64, (5, 5), activation='relu', padding='same', input_shape=train_X.shape[1:]))
model.add(MaxPooling2D(pool_size=(3, 3), padding='same', strides=(2,2)))
model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(AveragePooling2D(pool_size=(3, 3), padding='same', strides=(2,2)))
model.add(Conv2D(128, (3, 3), activation='relu', padding='same'))
model.add(AveragePooling2D(pool_size=(3, 3), padding='same', strides=(2,2)))

model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.2))

model.add(Dense(7, activation='softmax'))
model.summary()
model.compile(loss='categorical_crossentropy',optimizer="adadelta",metrics=['accuracy'])


def train(max_iter=1):
	for i in xrange(max_iter):
		#model.fit(train_X,train_Y,batch_size=32,epochs=1)
		model.fit_generator(datagen.flow(train_X, train_Y, batch_size=64),
                    steps_per_epoch=len(train_X)/64, epochs=1)
		score = evaluate()
		if score > 0.635:
			save(score)

def evaluate():
	score = model.evaluate(evaluate_X,evaluate_Y)
	print '\nEvaluate Acc:', score[1]
	return score[1]

def save(score):
	fname = './model/model2_' + str(score).replace('.', '') + '.h5'
	model.save(fname)
	#model = load_model('./model/model.h5')

def output():
	test_Y = model.predict(test_X)
	test_Y = np.argmax(test_Y,axis=1)
	output = open(predict_file,'w')
	output.write("id,label\n")
	for idx in xrange(len(test_Y)):
		output.write(str(idx) + "," + str(test_Y[idx]) + "\n")
	output.close()


model = load_model('./model/model2.h5')
evaluate()
train(1000)
