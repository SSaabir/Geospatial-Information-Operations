import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Read the data
df = pd.read_csv('preprocessed_climate_dataset5.csv')

# Remove any NaN values
df = df.dropna(subset=['humidity', 'rainsum'])

# Create the correlation plot
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='humidity', y='rainsum', alpha=0.5)
plt.xlabel('Humidity (%)')
plt.ylabel('Rainfall (mm)')
plt.title('Relationship between Humidity and Rainfall')

# Add correlation coefficient to plot
corr = df['humidity'].corr(df['rainsum'])
plt.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
         transform=plt.gca().transAxes, 
         fontsize=10)

# Add a trend line
sns.regplot(data=df, x='humidity', y='rainsum', 
            scatter=False, color='red', line_kws={'linestyle': '--'})

plt.tight_layout()
plt.savefig('humidity_rainfall_correlation.png')
plt.close()