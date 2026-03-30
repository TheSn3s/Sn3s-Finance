import json
import base64

log_file = "/home/ubuntu/.openclaw/agents/atef/sessions/70c9a80e-ca0a-4ec3-8570-12dbdd1b5378.jsonl"
output_file = "/home/ubuntu/.openclaw/workspace/atef_office/signature.png"

with open(log_file, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'message' and data.get('message', {}).get('role') == 'user':
                content = data['message']['content']
                for item in content:
                    if item.get('type') == 'image':
                        image_data = item.get('data')
                        if image_data:
                            # We want the LAST image sent
                            last_image = image_data
            
        except:
            continue

if last_image:
    with open(output_file, 'wb') as f:
        f.write(base64.b64decode(last_image))
    print("Success")
else:
    print("No image found")
