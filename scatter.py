import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from preprocess import getData


data = getData()

cat = data['category']

types = np.unique(cat)
# color based on https://stackoverflow.com/questions/12236566
colors = cm.gist_rainbow(np.linspace(0,1,len(types)))
color = 0
for category in types:
    segment = data[data['category'] == category]
    plt.plot(segment['avg'], segment['popularity'], marker='o', linestyle='none', color=colors[color])
    color += 1
plt.xlabel('Average traffic')
plt.ylabel('Popularity (percent)')
plt.title('Popularity per average traffic')
plt.savefig('scatter.png')
