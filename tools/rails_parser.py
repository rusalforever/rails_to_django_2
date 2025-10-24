"""
tools/rails_parser.py
LLM-backed parser for analyzing Ruby on Rails projects
and summarizing structure for Rails → Django conversion.
"""

import os
import json
import math
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client using environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# ---------------------------------------------------------------------
# summarize_structure
# ---------------------------------------------------------------------
def summarize_structure(tree_json: dict):
    """
    Summarize Rails project structure from file tree.
    Splits into smaller chunks to stay under token limits.
    Returns a merged JSON summary with candidate files to read.
    """

    all_files = tree_json.get("files", [])
    if not all_files:
        return {"models": [], "controllers": [], "routes_files": [], "views": [], "candidates_to_read": []}

    chunk_size = 150  # number of files per LLM call
    total_chunks = math.ceil(len(all_files) / chunk_size)
    summaries = []

    for i in range(total_chunks):
        start = i * chunk_size
        end = start + chunk_size
        subset = {"files": all_files[start:end]}

        prompt = (
            "You are an expert in Ruby on Rails project architecture. "
            "Analyze the following file paths and classify them into models, controllers, routes, and views. "
            "Output ONLY valid JSON with keys: models, controllers, routes_files, views.\n\n"
            f"Chunk {i + 1}/{total_chunks}:\n{subset}"
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
        )

        content = response.choices[0].message.content.strip()

        try:
            summaries.append(json.loads(content))
        except json.JSONDecodeError:
            summaries.append({"error": "invalid_json", "raw": content})

    # Merge summaries
    merged = {"models": [], "controllers": [], "routes_files": [], "views": []}
    for s in summaries:
        for key in merged.keys():
            if key in s and isinstance(s[key], list):
                merged[key].extend(s[key])

    merged["candidates_to_read"] = [
        f for f in all_files if f.endswith((".rb", ".erb", ".haml"))
    ]
    return merged


# ---------------------------------------------------------------------
# analyze_units
# ---------------------------------------------------------------------
def analyze_units(units: dict):
    """
    Deeply analyze Rails models, controllers, routes, and views via LLM.

    Args:
        units (dict): mapping of {path: content} for selected files.

    Returns:
        dict: structured analysis including models, controllers, routes, views, dependencies
    """
    if not units:
        return {"models": [], "controllers": [], "routes": [], "views": [], "dependencies": []}

    file_paths = list(units.keys())
    batch_size = 20
    total_batches = math.ceil(len(file_paths) / batch_size)
    results = []

    for i in range(total_batches):
        batch_files = file_paths[i * batch_size : (i + 1) * batch_size]
        batch_content = {p: units[p][:80000] for p in batch_files}  # limit size per file

        prompt = (
            "You are a Ruby on Rails expert. Analyze these files to extract:\n"
            "- models (attributes, associations)\n"
            "- controllers (actions, filters)\n"
            "- routes (resources, verbs)\n"
            "- views (variables, partials)\n"
            "Output ONLY JSON with keys: models, controllers, routes, views, dependencies.\n\n"
            f"Batch {i + 1}/{total_batches}:\n"
            f"{json.dumps(batch_content)[:12000]}"
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4000,
        )

        text = response.choices[0].message.content.strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = {"error": "invalid_json", "raw_text": text}

        results.append(parsed)

    # Merge batch results
    merged = {"models": [], "controllers": [], "routes": [], "views": [], "dependencies": []}
    for r in results:
        for key in merged.keys():
            if key in r and isinstance(r[key], list):
                merged[key].extend(r[key])

    return merged


# ---------------------------------------------------------------------
# Utility (optional): lightweight validation or pretty-print
# ---------------------------------------------------------------------
def debug_summary(summary: dict):
    """Pretty-print summary for debugging."""
    print(json.dumps(summary, indent=2, ensure_ascii=False))
