from avatar_generator import AvatarGenerator
from imageapi import get_image_id
import rblxopencloud
import time
import os

def publish_decal(api_key, group_id, decal_path, decal_name, decal_description):
    group = rblxopencloud.Group(group_id, api_key=api_key)

    with open(decal_path, 'rb') as file:
        asset = group.upload_asset(file, rblxopencloud.AssetType.Decal, decal_name, decal_description)

        if isinstance(asset, rblxopencloud.Asset):
            return asset.id
        elif isinstance(asset, rblxopencloud.PendingAsset):
            print("Decal upload is pending processing. Checking status...")

            while True:
                operation = asset.fetch_operation()
                if operation:
                    print(f"Decal processing complete! Asset ID: {operation.id}")
                    return operation.id

                time.sleep(1)
        else:
            return "Unexpected response from the upload process."

def publish_generated_avatar(n=1, owner_user="No Owner"):
    api_key = "RRAgWwln/0OnsFVuqOPTmqToe4kh+sL3ixqJPBMoDh4S8kJ9"
    group_id = 33212905
    decal_description = "This is a decal uploaded from a group!"

    # Create an instance of AvatarGenerator
    generator = AvatarGenerator("./images")

    # Generate avatars and get the file paths, names, and metadata
    avatar_paths, avatar_names, avatar_metadata = generator.generate_avatar(n, owner_user)

    # Publish each avatar as a decal
    asset_ids = []
    image_ids = []
    for avatar_path, avatar_name, metadata in zip(avatar_paths, avatar_names, avatar_metadata):
        # Use metadata in your publishing process
        print(f"Metadata for {avatar_name}: {metadata}")
        
        asset_id = publish_decal(api_key, group_id, avatar_path, avatar_name, decal_description)
        print(f"Decal published successfully! Asset ID: {asset_id}")
        asset_ids.append(asset_id)
        image_id = get_image_id(asset_id)
        image_ids.append(image_id)

    return asset_ids, image_ids, avatar_metadata
