import random, time
from neural_networks import NeuralNetwork, DataSetParser
"""
# Parameters.
epochs = 2000
learningRate = 0.1
neuralNetworkRepresentation = [7, 5, 3]
dataSetFileName = 'seeds.txt'
dataSetNumberOfParameters = 8

# Neural network construction.
nn = NeuralNetwork.NeuralNetwork(neuralNetworkRepresentation)

# Adapted Data Set.
parser = DataSetParser.DataSetParser(dataSetFileName, dataSetNumberOfParameters)
parser.adaptData()
adaptedData = parser.getAdaptedData()
random.shuffle(adaptedData)

# Learning process.
start_time = time.time()
nn.learn(adaptedData, epochs, learningRate)
elapsed_time = time.time() - start_time
print('Learning elapsed time: '+str(elapsed_time) +' seconds.')
"""

NeuronsArray = [[[[1,1], 1], [[1,2], 1], [[1,3], 1]], [[[4, 4, 4], 0.5]]]
print("init")
NN = NeuralNetwork.NeuralNetwork([1,1,1])
NN.setModelParameters(NeuronsArray)
NN2 = NeuralNetwork.NeuralNetwork([2,3,1])
print("initialized!")
print(NN.getOutputLayer().getPreviousLayer().getNeurons())
print(NN.getOutputLayer().getNeurons())