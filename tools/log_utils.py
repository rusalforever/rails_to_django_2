import json, os, datetime

def log_state(node, state_subset, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({
            "timestamp": datetime.datetime.now().isoformat(),
            "node": node,
            "state": state_subset
        }, f, indent=2)
    return {"logged": True, "path": path}

def log_llm_call(node, prompt, response, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({
            "node": node,
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.datetime.now().isoformat()
        }, f, indent=2)
    return {"logged": True, "path": path}
