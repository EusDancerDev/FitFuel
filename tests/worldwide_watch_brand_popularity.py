import matplotlib.pyplot as plt

# Data for most popular sports watches
brands = ['Apple', 'Garmin', 'Samsung', 'Fitbit', 'Others']
market_share = [21, 17, 12, 10, 40]  # Example percentages

# Firmware support data (fictional for visualization purposes)
brands_firmware = ['Apple', 'Garmin', 'Samsung', 'Fitbit']
firmware_versions = [10, 3, 4, 5]  # Number of major supported versions

# Plotting brand popularity
fig, ax = plt.subplots(1, 2, figsize=(12, 6))

def format_percentage(pct):
    return f'{pct:.1f}%'

# Market share pie chart with circle line and bold labels
wedges, texts, autotexts = ax[0].pie(
    market_share, 
    labels=brands,
    autopct=format_percentage,
    startangle=140, 
    colors=plt.cm.Paired.colors,
    wedgeprops={'edgecolor': 'black', 'linewidth': 1.5},  # Set circle line
    textprops={'fontweight': 'bold', 'fontsize': 12.5}  # Make brand labels bold and set fontsize
)

# Customise percentage labels
for autotext in autotexts:
    autotext.set_color('blue')  # Set percentage label colour
    autotext.set_fontsize(11)   # Set percentage label font size
    autotext.set_fontweight('bold')  # Set percentage label font weight

ax[0].set_title('Most Popular Sports Watches (2024)', fontsize=14.5, fontweight='bold')

# Firmware versions bar chart
ax[1].bar(brands_firmware, firmware_versions, color=plt.cm.Paired.colors[:len(brands_firmware)])
ax[1].set_title('Supported Firmware Versions by Brand (2024)', fontsize=14.5, fontweight='bold')
ax[1].set_ylabel('Number of Major Versions', fontsize=12, fontweight='bold')
ax[1].tick_params(axis='both', length=8, labelsize=10)
ax[1].grid(axis='y', linestyle='--', alpha=0.9)

# Show the plots
plt.tight_layout()
# plt.show()
plt.savefig('worldwide_watch_brand_popularity.png', dpi=300, bbox_inches='tight')

