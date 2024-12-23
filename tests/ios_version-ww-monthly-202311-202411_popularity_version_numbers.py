import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
file_path = 'ios_version-ww-monthly-202311-202411-bar.csv'
data = pd.read_csv(file_path).iloc[:-1]

# Keep the original iOS version strings
data['Original Version'] = data['iOS Version']

# Remove the 'iOS ' prefix and convert to float for sorting
data['iOS Version'] = data['iOS Version'].str.replace('iOS ', '').astype(float)

# Sort the data by the float-converted iOS version
data.sort_values(by='iOS Version', ascending=False, inplace=True)
data.reset_index(drop=True, inplace=True)

# Extract the sorted iOS versions and their market shares
ios_versions_sorted = data['Original Version']
market_shares_sorted = data['Market Share Perc. (Nov 2023 - Nov 2024)']

# Create a bar graph with fig and ax
fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.bar(ios_versions_sorted, market_shares_sorted, color='skyblue')

# Find the index of the highest market share in the sorted data
max_index_sorted = market_shares_sorted.idxmax()

# Set bar colours based on iOS version
for bar, version in zip(bars, ios_versions_sorted):
    if version.startswith('iOS 18'):
        bar.set_color('green')
    elif version.startswith('iOS 17'):
        bar.set_color('DarkKhaki')
    else:
        bar.set_color('grey')

# Highlight the bar with the highest market share
bars[max_index_sorted].set_color('orange')

# Set the x- and y-labels
ax.set_xlabel('iOS Version', fontsize=12, fontweight="bold")
ax.set_ylabel('Market Share (%)', fontsize=13, fontweight="bold")

# Set x-tick labels to include all sorted iOS versions
ax.set_xticks(range(len(ios_versions_sorted)))
ax.set_xticklabels(ios_versions_sorted)

# Set the x- and y-tick label additional parameters
ax.tick_params(axis='x', rotation=90, labelsize=8.6)
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='both', length=9.5, width=1.2)

# Highlight the label of the highest market share
ax.get_xticklabels()[max_index_sorted].set_color('green')
ax.get_xticklabels()[max_index_sorted].set_fontweight('bold')

# Add percentage labels on top of each bar
for bar, share in zip(bars, market_shares_sorted):
    yval = bar.get_height()
    ax.annotate(f'{share:.2f}%', xy=(bar.get_x() + bar.get_width()/2, yval), 
                xytext=(0, 3), textcoords='offset points',
                ha='center', va='bottom', fontsize=8, rotation=90, color='black',
                fontweight='bold')

# Set labels and title
ax.set_xlabel('iOS Version')
ax.set_ylabel('Market Share (%)')
fig.suptitle('iOS Version Market Share (Nov 2023 - Nov 2024)', fontsize=16, fontweight='bold')
ax.set_title('Sorted by iOS Version', ha='center')

# Set y-axis limits
max_ylim = ax.get_ylim()[1]
ax.set_ylim(0, max_ylim+1)

# Set the grid
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Add a legend to the plot
legend_labels = ['Current (iOS 18)', 'Supported (iOS 17)', 'Obsolete', 'Most Popular']
legend_colors = ['green', 'DarkKhaki', 'grey', 'orange']
legend_handles = [plt.Line2D([0], [0], color=color, lw=4) for color in legend_colors]
ax.legend(legend_handles, legend_labels, loc='upper right', fontsize=13)

# Show the plot
fig.tight_layout()
plt.show() 
# fig.savefig('ios_version-ww-monthly-202311-202411_popularity_version_numbers.png', dpi=300)