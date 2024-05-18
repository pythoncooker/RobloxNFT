from flask import Flask, request, jsonify
from publisher import publish_generated_avatar

app = Flask(__name__)

# Initialize received_data globally
received_data = None

@app.route('/')
def index():
    return "Hello, this is the Flask server!"

@app.route('/image_avatar5', methods=['GET', 'POST'])
def image_avatar():
    global received_data
    
    if request.method == 'GET':
        # Publish avatars and get asset IDs and metadata
        num_avatars = 5  # Adjust the number of avatars as needed
        asset_ids, image_ids, avatar_metadata = publish_generated_avatar(num_avatars, received_data)

        # Organize metadata and send it back to Roblox
        organized_metadata = organize_metadata(asset_ids, image_ids, avatar_metadata)
        data = {"asset_ids": asset_ids, "image_ids": image_ids, "metadata": organized_metadata}
        print("SENT >>", data)
        return jsonify(message=data)
    
    elif request.method == 'POST':
        received_data = request.get_data(as_text=True) 
        print("RECEIVED >>", received_data)
        return ""
    
def organize_metadata(asset_ids, image_ids, avatar_metadata):
    # Organize metadata based on asset IDs
    organized_metadata = {}
    for asset_id, image_id, metadata in zip(asset_ids, image_ids, avatar_metadata):
        metadata['ImageID'] = image_id  
        organized_metadata[asset_id] = metadata

    return organized_metadata

if __name__ == '__main__':
    app.run(host='localhost', port=56555, debug=False)
