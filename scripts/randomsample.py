'''Define a random sample of segments to be used for cross-annotation based on a fixed seed = 42.'''
import random

seed = 42
nb_segments = 242
sample_size = int(nb_segments * 0.2)  # 48 segments

random.seed(seed)
segments = random.sample(range(1, nb_segments + 1), sample_size)
print(sorted(segments), "longueur", len(segments))
