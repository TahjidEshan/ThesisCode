import pandas as pd
from sklearn import svm
import numpy as np
import ast
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.layers.convolutional import Convolution2D
from keras.layers.convolutional import MaxPooling2D
from keras.utils import np_utils
from keras import backend as K
from sklearn.naive_bayes import GaussianNB


def svm(training_features, training_labels, test_features, test_labels):
    model = OneVsRestClassifier(estimator=SVC(
        kernel='poly', degree=2, random_state=0))
    model.fit(training_features, training_labels)
    print "SVM Accuracy:", (model.score(test_features, test_labels))
    return


def naiveBayes(training_features, training_labels, test_features, test_labels):
    model = GaussianNB()
    model.fit(training_features, training_labels)
    print "Naive Bayes Accuracy:", (model.score(test_features, test_labels))
    return


def logReg(training_features, training_labels, test_features, test_labels, learning_rate, training_epochs, X, Y, W):
    init = tf.initialize_all_variables()
    y_ = tf.nn.sigmoid(tf.matmul(X, W))
    cost_function = tf.reduce_mean(tf.reduce_sum((-Y * tf.log(y_)) - ((1 - Y) * tf.log(1 - y_)),
                                                 reduction_indices=[1]))
    optimizer = tf.train.GradientDescentOptimizer(
        learning_rate).minimize(cost_function)
    cost_history = np.empty(shape=[1], dtype=float)
    with tf.Session() as sess:
        sess.run(init)
        for epoch in range(training_epochs):
            sess.run(optimizer, feed_dict={
                     X: training_features, Y: training_labels})
            cost_history = np.append(cost_history, sess.run(cost_function,
                                                            feed_dict={X: training_features, Y: training_labels}))

        y_pred = sess.run(y_, feed_dict={X: test_features})
        correct_prediction = tf.equal(tf.argmax(y_, 1), tf.argmax(Y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        print "Logistics Regression Accuracy: ", (sess.run(accuracy, feed_dict={X: test_features, Y: test_labels}))
        return


def neuralNetKeras(training_data, training_labels, test_data, test_labels, n_dim):
    seed = 8
    np.random.seed(seed)
    model = Sequential()
    model.add(Dense(12, input_dim=n_dim, init='uniform', activation='relu'))
    model.add(Dense(8, init='uniform', activation='relu'))
    model.add(Dense(1, init='uniform', activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    model.fit(training_data, training_labels, nb_epoch=150, batch_size=10)
    scores = model.evaluate(test_data, test_labels)
    print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))
    return


def cnnKeras(training_data, training_labels, test_data, test_labels, n_dim):
    seed = 8
    np.random.seed(seed)
    num_classes = 2
    model = Sequential()
    model.add(Convolution2D(32, 1, 1, init='glorot_uniform', border_mode='valid',
                            input_shape=(2, 2000, 1500), activation='relu'))
    model.add(MaxPooling2D(pool_size=(1, 1)))
    model.add(Convolution2D(15, 1, 1, init='glorot_uniform', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='softmax'))
    # Compile model
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    model.fit(training_data, training_labels, validation_data=(
        test_data, test_labels), nb_epoch=15, batch_size=8, verbose=2)

    scores = model.evaluate(test_data, test_labels, verbose=1)
    print("Baseline Error: %.2f%%" % (100 - scores[1] * 100))
    return


def reshapeList(features):
    x = len(features)
    y = len(features[0][0]) * \
        len(features[0][0][0]) * len(features[0])
    features = np.reshape(features, (x, y))
    return np.array(features)


def readData(dataList):
    featureList = []
    for i in range(0, len(dataList.index)):
        temp = []
        features = ast.literal_eval(dataList.loc[i, 'features'])
        pixels = ast.literal_eval(dataList.loc[i, 'pixels'])
        temp.append(np.array(features))
        temp.append(np.array(pixels))
        featureList.append(np.array(temp))
    return featureList


def main():

    data = pd.read_csv('data.csv')
    # shuffle the data
    data = data.sample(frac=1).reset_index(drop=True)

    # Calculate length of 30% data for testing
    val_text = len(data.index) * (30.0 / 100.0)

    # divide training and test data
    test_data = data.tail(int(val_text)).reset_index(drop=True)
    training_data = data.head(len(data.index) - int(val_text))
    #test_data = data.tail(1).reset_index(drop=True)
    #training_data = data.head(1)

    # set labels
    # labels for svm
    training_labels = training_data['labels'].values
    test_labels = test_data['labels'].values
    # labels for tf classifiers
    training_X = np.array(training_labels)
    test_X = np.array(test_labels)
    training_X = np.reshape(training_X, (len(training_X), 1))
    test_X = np.reshape(test_X, (len(test_X), 1))

    training_features_final = []
    test_features_final = []

    print("Reading Data")
    training_features_final = readData(training_data)
    test_features_final = readData(test_data)
    print("Reshaping Data")
    train_cnn = np.reshape(training_features_final, (len(training_features_final), len(training_features_final[
        0]), len(training_features_final[0][0]), len(training_features_final[0][0][0])))
    test_cnn = np.reshape(test_features_final, (len(test_features_final), len(test_features_final[
        0]), len(test_features_final[0][0]), len(test_features_final[0][0][0])))
    training_features_final = reshapeList(training_features_final)
    test_features_final = reshapeList(test_features_final)

    # print(training_features_final.shape)
    '''
    ###SVM classifier using sklearn
    '''
    '''
    print("Initiating SVM")
    svm(training_features_final, training_labels,
        test_features_final, test_labels)
    '''
    '''
    ###Logistics Regression Using tensorflow
    '''
    #print("Initiating Logistics Regression")
    n_dim = training_features_final.shape[1]
    learning_rate = 0.1
    training_epochs = 10

    X = tf.placeholder(tf.float32, [None, n_dim])
    Y = tf.placeholder(tf.float32, [None, 1])
    #W = tf.Variable(tf.ones([n_dim, 2]))
    '''
    logReg(training_features_final, training_X, test_features_final,
           test_X, learning_rate, training_epochs, X, Y, W)
    '''
    # Starting CNN
    '''
    print("Starting Convolutional Neural Network")
    cnn(training_features_final, training_X, test_features_final,
        test_X, learning_rate, training_epochs, n_dim, X, Y)
    '''
    '''
    print("Initialising Neural Network")
    neuralNetKeras(training_features_final, training_X,
                   test_features_final, test_labels, n_dim)
    '''
    '''
    print("Initialising convolutional neural network ")
    cnnKeras(train_cnn, training_X,
             test_cnn, test_X, n_dim)
    '''
    print("Initialising Naive Bayes")
    naiveBayes(training_features_final, training_labels,
               test_features_final, test_labels)

if __name__ == '__main__':
    main()
