import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
file_path = 'ios_version-ww-monthly-202311-202411-bar.csv'
data = pd.read_csv(file_path).iloc[:-1]

# Extract the iOS versions and their market shares
ios_versions = data['iOS Version']
market_shares = data['Market Share Perc. (Nov 2023 - Nov 2024)']

# Create a bar graph with fig and ax
fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.bar(ios_versions, market_shares, color='skyblue')

# Find the index of the highest market share
max_index = market_shares.idxmax()

# Highlight the bar and label with the highest market share
bars[max_index].set_color('orange')

# Set x-tick labels to include all iOS versions
ax.set_xticks(range(len(ios_versions)))
ax.set_xticklabels(ios_versions, rotation=90, fontsize=8)

# Set the x- and y-tick label additional parameters
ax.tick_params(axis='x', rotation=90, labelsize=8.6)
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='both', length=9.5, width=1.2)

# Set the x- and y-labels
ax.set_xlabel('iOS Version', fontsize=12, fontweight="bold")
ax.set_ylabel('Market Share (%)', fontsize=13, fontweight="bold")

# Highlight the label of the highest market share
ax.get_xticklabels()[max_index].set_color('green')
ax.get_xticklabels()[max_index].set_fontweight('bold')

# Add percentage labels on top of each bar
for bar, share in zip(bars, market_shares):
    yval = bar.get_height()
    ax.annotate(f'{share:.2f}%', xy=(bar.get_x() + bar.get_width()/2, yval), 
                xytext=(0, 3), textcoords='offset points',
                ha='center', va='bottom', fontsize=8, rotation=90, color='black',
                fontweight='bold')

# Set labels and title
ax.set_xlabel('iOS Version')
ax.set_ylabel('Market Share (%)')
fig.suptitle('iOS Version Market Share (Nov 2023 - Nov 2024)', fontsize=16, fontweight='bold')
ax.set_title('Sorted by most popular iOS version', ha='center')

# Set y-axis limits
max_ylim = ax.get_ylim()[1]
ax.set_ylim(0, max_ylim+1)

# Set the grid
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Show the plot
fig.tight_layout()
# plt.show()
fig.savefig('ios_version-ww-monthly-202311-202411_popularity_usage.png', dpi=300)