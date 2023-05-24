from jsonschema import validate
import json
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

schema = {
    "type":"object",
    "properties": {
        "chatId": { 
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "contacts": {
            "type": "object",
            "additionalProperties": { "type": "string"}
        },
        "models": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                  "text_prompt": { "type": "string" },
                  "include_image": { "type": "boolean" },
                  "reference_size": {
                      "type": "number",
                      "exclusiveMinimum": 0,
                      "maximum": 1
                  }
                }
            }
        }
    }
}

def validate_config():
    with open(f"{dir_path}/../../chat/config.json", "r") as configfile:
        config = json.load(configfile)
    validate(instance=config, schema=schema)