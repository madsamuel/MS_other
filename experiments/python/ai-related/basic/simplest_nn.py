import numpy as np

# Simplest Neural Network: Single Neuron (Perceptron)
class SimpleNN:
    def __init__(self, input_size, learning_rate=0.01):
        """Initialize weights and bias with small random values"""
        self.weights = np.random.randn(input_size) * 0.01
        self.bias = np.random.randn() * 0.01
        self.learning_rate = learning_rate
    
    def forward(self, X):
        """Compute output: activation(weights * input + bias)"""
        z = np.dot(X, self.weights) + self.bias
        return 1 / (1 + np.exp(-z))  # Sigmoid activation
    
    def backward(self, X, y, output):
        """Compute gradients and update weights"""
        error = output - y
        d_weights = np.dot(X.T, error) / len(X)
        d_bias = np.mean(error)
        
        self.weights -= self.learning_rate * d_weights
        self.bias -= self.learning_rate * d_bias
    
    def train(self, X, y, epochs=100):
        """Train the network"""
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(X, y, output)
            if epoch % 20 == 0:
                loss = np.mean((output - y) ** 2)
                print(f"Epoch {epoch}, Loss: {loss:.4f}")
    
    def predict(self, X):
        """Make predictions"""
        return (self.forward(X) > 0.5).astype(int)


# Example: AND gate
if __name__ == "__main__":
    # Training data (AND logic)
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([[0], [0], [0], [1]])
    
    # Create and train network
    nn = SimpleNN(input_size=2, learning_rate=0.5)
    nn.train(X, y, epochs=100)
    
    # Test
    print("\nPredictions:")
    for i in range(len(X)):
        pred = nn.predict(X[i:i+1])
        print(f"Input: {X[i]} -> Predicted: {pred[0]}, Actual: {y[i][0]}")
