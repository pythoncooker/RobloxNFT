import requests
import xml.etree.ElementTree as ET
import sys
import json

def get_image_id(decal_id):
    try:
        api_url = f'https://assetdelivery.roblox.com/v1/asset/?id={decal_id}'
        response = requests.get(api_url)

        if response.status_code == 200:
            xml_data = ET.fromstring(response.text)
            content_url = xml_data.find(".//Content/url").text
            image_id = content_url.split("=")[1]
            return image_id
        else:
            return 'Failed to retrieve image ID'

    except Exception as e:
        return str(e)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <decal_id>")
        sys.exit(1)

    decal_id = int(sys.argv[1])
    result = get_image_id(decal_id)

    print(result)
