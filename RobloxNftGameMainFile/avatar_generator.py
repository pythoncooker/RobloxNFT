import os
import random
from layer import Layer
from PIL import Image
from typing import List
import re
import json

class AvatarGenerator:
    def __init__(self, images_path: str, output_path: str = "./output", used_combinations_file: str = "./used_combinations.json"):
        self.layers: List[Layer] = self.load_image_layers(images_path)
        self.output_path: str = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.used_combinations_file = used_combinations_file
        self.used_combinations = self.load_used_combinations()

    def load_image_layers(self, images_path: str) -> List[Layer]:
        sub_paths = sorted(os.listdir(images_path))
        layers: List[Layer] = [Layer(os.path.join(images_path, sub_path)) for sub_path in sub_paths]
        return layers  
    
    def save_used_combinations(self):
        # Convert sets of tuples to sets of lists before saving to JSON
        converted_combinations = [list(combination) for combination in self.used_combinations]
        with open(self.used_combinations_file, 'w') as file:
            json.dump(converted_combinations, file)

    def load_used_combinations(self):
        try:
            with open(self.used_combinations_file, 'r') as file:
                # Convert sets of lists to sets of tuples after loading from JSON
                loaded_combinations = [tuple(combination) for combination in json.load(file)]
                return set(loaded_combinations)
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def save_used_combinations(self):
        with open(self.used_combinations_file, 'w') as file:
            json.dump(list(self.used_combinations), file)

    def generate_image_sequence(self) -> List[str]:
        return [layer.get_random_image_path() for layer in self.layers]

    def render_avatar_image(self, image_path_sequence: List[str]) -> Image.Image:
        base_size = (1024, 1024)
        base_image = Image.new("RGBA", base_size)
        for image_path in image_path_sequence:
            try:
                layer_image = Image.open(image_path).resize(base_size, Image.BOX)
                base_image = Image.alpha_composite(base_image, layer_image)
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
        return base_image

    def save_image(self, image: Image.Image, i: int = 0):
        image_index = str(i).zfill(4)
        image_file_name = f'avatar_{image_index}.png'  # Updated naming convention
        image_save_path = os.path.join(self.output_path, image_file_name)
        image.save(image_save_path)

    # Inside the AvatarGenerator class in avatar_generator.py

    def generate_avatar(self, n: int = 1, owner_user: str = "No Owner") -> tuple[List[str], List[str], List[dict]]:
        print("Generating Avatar!")
        latest_avatar_number = self.get_latest_avatar_number()
        generated_image_paths = []
        generated_image_names = []
        generated_metadata = []

        for i in range(latest_avatar_number + 1, latest_avatar_number + n + 1):
            image_path_sequence = self.generate_image_sequence()

            # Keep generating new sets of images until a unique combination is found
            while tuple(image_path_sequence) in self.used_combinations or self.is_combination_duplicate(image_path_sequence):
                image_path_sequence = self.generate_image_sequence()

                # If all combinations are exhausted, print a message and break the loop
                if len(self.used_combinations) == len(set(tuple(image_path_sequence) for _ in range(n))):
                    print("All possible combinations exhausted.")
                    break

            # Add the current combination to the set of used combinations
            self.used_combinations.add(tuple(image_path_sequence))

            image = self.render_avatar_image(image_path_sequence)
            image_name = f'avatar_{str(i).zfill(4)}'  # Updated naming convention
            image_path = os.path.join(self.output_path, f'{image_name}.png')
            self.save_image(image, i)

            # Generate metadata for the avatar
            metadata = self.generate_metadata(image_path_sequence, owner_user)
            generated_metadata.append(metadata)

            generated_image_paths.append(image_path)
            generated_image_names.append(image_name)

            # Save metadata to a file
            metadata_file_path = os.path.join(self.output_path, f'{image_name}_metadata.json')
            self.save_metadata(metadata, metadata_file_path)

        # Save the used combinations to the file
        self.save_used_combinations()

        print("Generated Image Paths:", generated_image_paths)
        print("Generated Image Names:", generated_image_names)
        return generated_image_paths, generated_image_names, generated_metadata

    def generate_metadata(self, image_path_sequence, owner_name):
        metadata = {}
        layer_order = ["Background", "Shirt", "BodyColor", "Face", "FaceAccessory", "Hair", "NeckAccessory", "Hat"]

        metadata['OriginalOwner'] = owner_name
        
        for layer_index, image_path in enumerate(image_path_sequence):
            layer_name = layer_order[layer_index]
            # Save the entire substring after '#' in a variable
            substring_after_hash = os.path.basename(image_path).split('#')[1]

            # Remove ".PNG" from the substring and add '%' after the number
            rarity = substring_after_hash.replace('.PNG', '') + '%'

            metadata[layer_name] = {
                'Name': os.path.basename(image_path).split('#')[0],
                'Rarity': rarity,
            }

        return metadata
    
    def get_element_type(self, image_path):
        # Extract the element type from the image path (e.g., "7_Hats")
        return os.path.basename(os.path.dirname(image_path))
    
    def save_metadata(self, metadata, metadata_file_path):
        with open(metadata_file_path, 'w') as metadata_file:
            json.dump(metadata, metadata_file, indent=2)

    def is_combination_duplicate(self, new_combination):
        # Check if the new combination is an exact copy of any existing combination in the JSON file
        return any(new_combination == list(existing_combination) for existing_combination in self.used_combinations)

    def get_latest_avatar_number(self):
        avatar_files = [file for file in os.listdir(self.output_path) if re.match(r'avatar_\d{4}\.png', file)]
        
        if avatar_files:
            latest_avatar_file = max(avatar_files)
            latest_avatar_number = int(re.search(r'\d{4}', latest_avatar_file).group())
            return latest_avatar_number
        else:
            return 0
