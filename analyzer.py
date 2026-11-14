import pandas as pd
import matplotlib.pyplot as plt

# 1. Load data from CSV
df = pd.read_csv('simcore_stats.csv')

# 2. Group data by 'Day' and calculate the mean for each column
daily_stats = df.groupby('Day').mean(numeric_only=True)

# 3. Create a figure with 3 subplots
fig, axes = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle('SimCore City Analytics (Average Stats)', fontsize=16) 

# 4. Plot 1: Average Money
axes[0].plot(daily_stats.index, daily_stats['Money'], color='green', linewidth=2)
axes[0].set_ylabel('Average Money')
axes[0].set_title('Economy Trend')
axes[0].grid(True, linestyle='--', alpha=0.7)

# 5. Plot 2: Average Health
axes[1].plot(daily_stats.index, daily_stats['Health'], color='red', linewidth=2)
axes[1].set_ylabel('Average Health')
axes[1].set_title('Health Trend')
axes[1].grid(True, linestyle='--', alpha=0.7)

# 6. Plot 3: Average Music Skill
axes[2].plot(daily_stats.index, daily_stats['MusicSkill'], color='blue', linewidth=2)
axes[2].set_ylabel('Average Music Skill')
axes[2].set_xlabel('Day')
axes[2].set_title('Music Skill Trend')
axes[2].grid(True, linestyle='--', alpha=0.7)

# Adjust layout for the first figure
plt.tight_layout()
plt.subplots_adjust(top=0.92) 

# --- NEW FEATURE: BAR CHART FOR FINAL MONEY ---

# Get the last day's data
last_day = df['Day'].max()
final_stats = df[df['Day'] == last_day]

# Sort by money (ascending=False means descending order, highest first)
final_stats_sorted = final_stats.sort_values(by='Money', ascending=False)

# Create a new figure for the bar chart
plt.figure(figsize=(10, 6))
plt.bar(final_stats_sorted['Name'], final_stats_sorted['Money'], color='gold')

# Add titles and labels
plt.title(f'Final Money Distribution (Day {last_day})', fontsize=16)
plt.xlabel('Citizens')
plt.ylabel('Money (Rubles)')

# Rotate x-axis labels so they don't overlap
plt.xticks(rotation=45) 
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout and show both plots
plt.tight_layout()
plt.show()