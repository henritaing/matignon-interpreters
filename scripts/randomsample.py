'''Define a random sample of segments to be used for cross-annotation based on a fixed seed = 42.'''
import numpy as np
import random

seed = 42
nb_segments = 242
sample_size = int(np.floor(nb_segments * 0.2)) # 20% of the segments

segments = [random.randint(1, nb_segments) for _ in range(sample_size)]
print(segments, "longueur", len(segments))
