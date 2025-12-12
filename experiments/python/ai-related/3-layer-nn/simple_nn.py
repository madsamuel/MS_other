import numpy as np

# -------------------------
# 1. Create a simple dataset
# -------------------------
np.random.seed(0)

# 200 points, each with 2 features
N = 200
X = np.random.randn(N, 2)  # shape (N, 2)

# [ 0.64331447 -1.57062341]
# [-0.20690368  0.88017891]
# [-1.69810582  0.38728048]
# [-2.25556423 -1.02250684]
# ...

# Simple rule for labels:
# if x0 + x1 > 0 => class 1, else class 0
y = (X[:, 0] + X[:, 1] > 0).astype(np.float32).reshape(-1, 1)  # shape (N, 1)

# -------------------------
# 2. Define network structure
# -------------------------
input_dim = 2    # two input features
hidden_dim = 3   # three neurons in hidden layer
output_dim = 1   # one output (probability of class 1)

# Initialize weights and biases (small random numbers)
W1 = 0.1 * np.random.randn(input_dim, hidden_dim)  # (2, 3)
b1 = np.zeros((1, hidden_dim))                     # (1, 3)
W2 = 0.1 * np.random.randn(hidden_dim, output_dim) # (3, 1)
b2 = np.zeros((1, output_dim))                     # (1, 1)

# -------------------------
# 3. Define activation functions
# -------------------------
# Used for forward pass / prediction
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

# Used for training (backpropagation)
def sigmoid_derivative(z):
    s = sigmoid(z)
    return s * (1 - s)

def tanh_derivative(z): 
    # derivative of tanh is 1 - tanh(z)^2
    t = np.tanh(z)
    return 1 - t**2

# -------------------------
# 4. Forward pass
# -------------------------
def forward(X):
    """
    X: (N, 2)
    returns:
      z1, a1, z2, y_hat
    """
    z1 = X.dot(W1) + b1        # (N, 3)
    a1 = np.tanh(z1)           # hidden activations (N, 3)
    z2 = a1.dot(W2) + b2       # (N, 1)
    y_hat = sigmoid(z2)        # predicted probabilities (N, 1)
    return z1, a1, z2, y_hat


# -------------------------
# 5. Training loop (gradient descent)
# -------------------------
learning_rate = 0.1
epochs = 1000

for epoch in range(epochs):
    # Forward pass
    z1, a1, z2, y_hat = forward(X)

    # Mean Squared Error loss: L = mean( (y_hat - y)^2 )
    loss = np.mean((y_hat - y)**2)

    # -------------
    # Backpropagation
    # -------------

    # dL/dy_hat = 2*(y_hat - y)/N
    N_samples = X.shape[0]
    dL_dyhat = 2 * (y_hat - y) / N_samples    # (N, 1)

    # y_hat = sigmoid(z2) -> dy_hat/dz2 = sigmoid_derivative(z2)
    dL_dz2 = dL_dyhat * sigmoid_derivative(z2)       # (N, 1)

    # z2 = a1 * W2 + b2
    dL_dW2 = a1.T.dot(dL_dz2)                         # (3, 1)
    dL_db2 = np.sum(dL_dz2, axis=0, keepdims=True)    # (1, 1)

    # Propagate back to hidden layer
    dL_da1 = dL_dz2.dot(W2.T)                         # (N, 3)
    dL_dz1 = dL_da1 * tanh_derivative(z1)             # (N, 3)

    dL_dW1 = X.T.dot(dL_dz1)                          # (2, 3)
    dL_db1 = np.sum(dL_dz1, axis=0, keepdims=True)    # (1, 3)

    # Gradient descent update
    W2 -= learning_rate * dL_dW2
    b2 -= learning_rate * dL_db2
    W1 -= learning_rate * dL_dW1
    b1 -= learning_rate * dL_db1

    # Print progress every 100 epochs
    if epoch % 100 == 0:
        preds = (y_hat > 0.5).astype(int)
        accuracy = np.mean(preds == y)
        print(f"Epoch {epoch:4d} | Loss: {loss:.4f} | Accuracy: {accuracy:.3f}")


# -------------------------
# 6. Using the trained network
# -------------------------
def predict(X_new):
    _, _, _, y_hat_new = forward(X_new)
    return (y_hat_new > 0.5).astype(int)

# Example: predict on a few new points
X_test = np.array([
    [ 1.0,  1.0],  # should be class 1 (1+1 > 0)
    [-1.0, -1.0],  # should be class 0
    [ 0.5, -0.2],  # depends on sum
])

print("Test predictions:", predict(X_test).ravel())
