# Install h2o library if you haven't already
!pip install h2o

import h2o
from h2o.estimators import H2OAutoML
import pandas as pd

# Initialize H2O instance
h2o.init()

# Sample data - Replace with your actual data
# This example assumes you have a pandas dataframe 'df' with 'latency', 'cpu', and 'memory' columns

data = {
    'timestamp': ['2025-05-01 00:00:00', '2025-05-01 01:00:00', '2025-05-01 02:00:00', '2025-05-01 03:00:00', '2025-05-01 04:00:00'],
    'latency': [10, 20, 15, 25, 12],
    'cpu': [80, 70, 75, 85, 90],
    'memory': [60, 65, 70, 55, 60]
}

# Convert to pandas DataFrame
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Convert pandas DataFrame to H2O Frame
hf = h2o.H2OFrame(df)

# Set 'timestamp' as the index if necessary
hf['timestamp'] = hf['timestamp'].asnumeric()

# Define the predictors (features) and the response (target variable)
# For anomaly detection, we're trying to model the relationship between 'latency', 'cpu', and 'memory'
predictors = ['latency', 'cpu', 'memory']
response = 'latency'  # We are trying to detect anomalies in latency based on CPU and memory

# Split the data into training and testing
train, test = hf.split_frame(ratios=[0.8])

# Use H2O AutoML to train the model
aml = H2OAutoML(max_models=20, seed=42, balance_classes=False)
aml.train(x=predictors, y=response, training_frame=train)

# Get the leaderboard to see the best models
leaderboard = aml.leaderboard
print(leaderboard)

# Make predictions (anomaly scores) on the test set
preds = aml.leader.predict(test)

# Add the predictions to the test dataset
test['predicted_latency'] = preds['p1']

# Calculate the residuals (difference between actual and predicted values)
test['residual'] = test['latency'] - test['predicted_latency']

# Identify potential anomalies by looking at large residuals
threshold = 5  # You can adjust this threshold based on your use case
test['anomaly'] = test['residual'].abs() > threshold

# Print the results with potential anomalies
print(test[['timestamp', 'latency', 'predicted_latency', 'residual', 'anomaly']])

# Shutdown H2O instance after use
h2o.shutdown(prompt=False)
