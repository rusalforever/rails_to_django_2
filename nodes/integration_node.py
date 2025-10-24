import os
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from openai import OpenAI
from tools import file_tools, log_utils

console = Console()

def call_llm(prompt: str) -> str:
    model = os.getenv("MODEL_NAME", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ OPENAI_API_KEY не знайдено в середовищі")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": (
                "You are a concise documentation assistant. "
                "Write a clean, professional README.md for a Django project converted from Ruby on Rails. "
                "Use only Markdown; no JSON or code fences."
            )},
            {"role": "user", "content": prompt}
        ],
        temperature=0.25,
    )
    return response.choices[0].message.content.strip()


def run(state):
    state.current_node = "integration_node"
    console.print("[bold cyan]Integrating all generated components (via LLM)...[/bold cyan]")

    output_dir = state.output_dir
    project_root = getattr(state, "project_root", None) or os.path.join(output_dir, "converted_project")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(project_root, exist_ok=True)

    rails_units = getattr(state, "rails_units", {}) or {}
    blueprint = getattr(state, "django_blueprint", {}) or {}
    generated_files = getattr(state, "generated_files", []) or []
    files_to_read = getattr(state, "files_to_read", []) or []

    apps = [app.get("name") for app in blueprint.get("apps", [])]
    models_count = sum(1 for app in blueprint.get("apps", []) if app.get("models_code"))
    views_count = sum(1 for app in blueprint.get("apps", []) if app.get("views_code"))
    templates_count = sum(len(app.get("templates", [])) for app in blueprint.get("apps", []))

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "input_dir": getattr(state, "input_dir", None),
        "output_dir": getattr(state, "output_dir", None),
        "project_root": project_root,
        "rails_summary": getattr(state, "rails_summary", {}),
        "rails_units": rails_units,
        "django_blueprint": blueprint,
        "generated_files": generated_files,
        "stats": {
            "rails_files_analyzed": len(files_to_read),
            "django_files_generated": len(generated_files),
            "apps": apps,
            "models_count": models_count,
            "views_count": views_count,
            "templates_count": templates_count
        }
    }

    summary_path = os.path.join(output_dir, "conversion_summary.json")
    file_tools.write_json(summary_path, summary, makedirs=True)

    prompt = f"""
Create a clear, minimal, professional README.md for a Django project automatically
converted from Ruby on Rails using an AI pipeline.

Rules:
- Write **Markdown** only (no JSON or raw data).
- Include these sections (in this order):
  1. 🧠 Project Overview – short 2-3 sentence intro.
  2. ⚙️ Quick Start – commands to run (migrate, runserver).
  3. 🧩 Conversion Summary – short bullet/table summary of key counts.
  4. 📦 Applications – list app names and number of templates.
  5. 🧱 Project Structure – a simplified tree of key files.
  6. 🪄 Features – what’s supported.
  7. 🧭 Notes – include timestamp and note that it’s AI-generated.
- Write in English, concise and human-readable.

Conversion summary for context:
{json.dumps(summary, indent=2, ensure_ascii=False)}
"""

    readme_text = call_llm(prompt)
    readme_path = os.path.join(output_dir, "README.md")
    file_tools.write_file(readme_path, readme_text, makedirs=True)

    # requirements.txt
    req_path = os.path.join(project_root, "requirements.txt")
    if not os.path.exists(req_path):
        reqs = blueprint.get("requirements") or ["Django>=5,<6", "Pillow"]
        file_tools.write_file(req_path, "\n".join(reqs))

    state.integration = {
        "readme": readme_path,
        "summary": summary_path,
        "requirements": req_path,
    }

    log_utils.log_state("integration_node", state.integration, os.path.join(output_dir, "logs", "integration.json"))

    console.print("[green]✅ LLM-based README generation complete![/green]\n")
    table = Table(title="Integration Summary", header_style="bold magenta")
    table.add_column("Artifact", style="cyan")
    table.add_column("Path", style="green")
    for k, v in state.integration.items():
        table.add_row(k, v)
    console.print(table)

    return state
