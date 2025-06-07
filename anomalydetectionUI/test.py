from pathlib import Path
import json

data = {"test": "123"}
file = Path("./status_registry.json")
with file.open("w") as f:
    json.dump(data, f)
