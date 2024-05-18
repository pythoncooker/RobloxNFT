import os
import random
import re

class Layer:
    def __init__(self, path: str):
        self.path = path
        self.used_images = set()
        self.image_paths = self.load_image_paths()

    def load_image_paths(self):
        image_paths = [os.path.join(self.path, image) for image in os.listdir(self.path)]
        image_paths.sort(key=lambda x: self.extract_weight(x))
        return image_paths

    def extract_weight(self, image):
        match = re.search(r'#(\d+)', image)
        return int(match.group(1)) if match else 1  # Default weight is 1 if not specified

    def get_random_image_path(self):
        weights = [self.extract_weight(image) for image in self.image_paths]
        total_weight = sum(weights)

        cumulative_probabilities = [sum(weights[:i+1]) / total_weight for i in range(len(weights))]
        random_value = random.uniform(0, 1)

        selected_index = next(i for i, prob in enumerate(cumulative_probabilities) if prob >= random_value)
        random_image_path = self.image_paths[selected_index]

        self.used_images.add(random_image_path)
        return random_image_path

    def get_unique_id(self):
        return hash(self.path)  
