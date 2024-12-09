import pandas as pd
import numpy as np
import datetime

def generate_rice_crop_dataset(start_time, end_time, interval_minutes=5):
  """Generates a synthetic rice crop monitoring dataset.

  Args:
    start_time: Start time of the dataset.
    end_time: End time of the dataset.
    interval_minutes: Interval between data points in minutes.

  Returns:
    A pandas DataFrame containing the generated dataset.
  """

  # Define parameter ranges (adjust as needed)
  n_range = (80, 120)
  p_range = (40, 60)
  k_range = (80, 100)
  humidity_range = (70, 90)
  ph_range = (6, 7)
  temperature_range = (25, 35)

  # Generate timestamps
  time_index = pd.date_range(start=start_time, end=end_time, freq=f'{interval_minutes}min')

  # Generate data points with noise
  data = {
      'N': np.random.uniform(n_range[0], n_range[1], len(time_index)) + np.random.normal(0, 2, len(time_index)),
      'P': np.random.uniform(p_range[0], p_range[1], len(time_index)) + np.random.normal(0, 1, len(time_index)),
      'K': np.random.uniform(k_range[0], k_range[1], len(time_index)) + np.random.normal(0, 1, len(time_index)),
      'humidity': np.random.uniform(humidity_range[0], humidity_range[1], len(time_index)) + np.random.normal(0, 1, len(time_index)),
      'soil_pH': np.random.uniform(ph_range[0], ph_range[1], len(time_index)) + np.random.normal(0, 0.1, len(time_index)),
      'temperature': np.random.uniform(temperature_range[0], temperature_range[1], len(time_index)) + np.random.normal(0, 1, len(time_index))
  }

  df = pd.DataFrame(data, index=time_index)
  # Round off specific columns
  df = df.round(3)

# Now, df has its specified columns rounded off to the defined number of decimal places
  df['crop_name'] = 'Rice'
  return df

# Example usage
start_time = datetime.datetime(2024, 7, 13, 0, 0)
end_time = start_time + datetime.timedelta(days=3)
dataset = generate_rice_crop_dataset(start_time, end_time)
dataset.index.name = 'timestamp'
dataset.to_csv('rice_crop_dataset.csv')
print(dataset.head())
