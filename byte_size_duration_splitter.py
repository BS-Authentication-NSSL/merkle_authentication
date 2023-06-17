import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

# Read the data from the CSV
data = pd.read_csv('byte_size_duration.csv')

# Create new columns
data['BelowThreshold'] = np.nan
data['AboveThreshold'] = np.nan

# Number of bins for the histogram
num_bins = 100

# Loop over unique byte sizes
for size in data['SIB1 additional size (bytes)'].unique():
    
    # Extract durations for the current size
    subset = data.loc[data['SIB1 additional size (bytes)'] == size]
    durations = subset['Time duration to transmit (milliseconds)']
    
    # Compute histogram of the durations
    hist, bin_edges = np.histogram(durations, bins=num_bins)

    # Find indices of the maxima
    maxima = argrelextrema(hist, np.greater)

    # If we found at least two maxima
    if len(maxima[0]) >= 2:
        # Take the two largest maxima
        max1, max2 = maxima[0][np.argsort(hist[maxima[0]])[-2:]]

        # Find index of the minimum count (the "valley") between these maxima
        if max2 - max1 > 1:
            idx_min_count = max1 + np.argmin(hist[max1:max2])
            # Compute threshold as the average of the bin edges of the valley
            threshold = (bin_edges[idx_min_count] + bin_edges[idx_min_count + 1]) / 2
        else:
            # If maxima are adjacent, take their average
            threshold = (bin_edges[max1] + bin_edges[max2]) / 2
    else:
        # If we didn't find two maxima, fall back to the median
        threshold = np.median(durations)
    
    print(f"Processing byte size {size}, found threshold at {threshold}")
    
    # Assign durations to new columns based on threshold
    below_threshold_indices = subset.loc[durations < threshold].index
    data.loc[below_threshold_indices, 'BelowThreshold'] = durations.loc[below_threshold_indices]
    
    above_threshold_indices = subset.loc[durations >= threshold].index
    data.loc[above_threshold_indices, 'AboveThreshold'] = durations.loc[above_threshold_indices]

# Save the new data to CSV
data.to_csv('byte_size_duration_with_threshold.csv', index=False)
