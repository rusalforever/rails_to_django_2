# nodes/converter_node.py
"""
converter_node.py — converts Rails summary and units into a full Django blueprint.

Now ensures that:
- LLM always generates top-level 'settings_code' and 'urls_code'
- If any Rails templates (layouts, devise, action_text, etc.) are missing from Django blueprint,
  refinement runs automatically to recover them.
"""

import json
from openai import OpenAI
from tools import log_utils

client = OpenAI()


def _try_parse_json(text: str):
    """Try to parse JSON safely, stripping markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except Exception:
        return None


def _repair_json_with_llm(raw_text: str):
    """Ask LLM to fix broken JSON."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a JSON repair assistant. Output valid JSON only."},
                {"role": "user", "content": f"Fix this invalid JSON:\n\n{raw_text}"}
            ],
            temperature=0,
        )
        fixed = response.choices[0].message.content.strip()
        return _try_parse_json(fixed)
    except Exception as e:
        print(f"⚠️ JSON repair failed: {e}")
        return None


def _refine_blueprint_with_llm(blueprint: dict, rails_summary: dict, rails_units: dict):
    """
    Ask LLM to fill in missing Django code for models, views, urls, admin, templates,
    and ensure top-level settings_code and urls_code exist.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in converting Ruby on Rails projects to Django. "
                        "Given a partially filled Django blueprint, complete all missing code blocks. "
                        "Output valid JSON only, matching the original structure."
                    ),
                },
                {
                    "role": "user",
                    "content": f"""
Here is the partially filled Django blueprint:
{json.dumps(blueprint, indent=2)}

Here are the Rails project details for reference:
SUMMARY:
{json.dumps(rails_summary, indent=2)}

UNITS:
{json.dumps(rails_units, indent=2)}

Rules:
- Preserve the same JSON structure and keys.
- Always include 'settings_code' (full Django 5.x settings.py) and 'urls_code' (root urls.py).
- Fill all missing fields: 'models_code', 'views_code', 'urls_code', 'admin_code', and 'templates.content'.
- settings_code must include BASE_DIR, INSTALLED_APPS, MIDDLEWARE, STATIC_URL, MEDIA_URL, DEBUG=True.
- urls_code must include admin route and include() for each app.
- If any Rails templates exist under /app/views/layouts, /app/views/devise, or /app/views/action_text,
  recreate them in Django templates directory with equivalent Jinja2 code.
- Each app must be valid Django code (no placeholders, no markdown, no comments).
Return strictly valid JSON only.
"""
                }
            ],
            temperature=0.4,
            max_tokens=8000,
        )
        fixed = response.choices[0].message.content.strip()
        return _try_parse_json(fixed)
    except Exception as e:
        print(f"⚠️ Refinement failed: {e}")
        return None


def run(state):
    """Main converter node: converts Rails summary to Django blueprint via LLM."""
    state.current_node = "converter_node"

    rails_summary = state.get("rails_summary", {}) or {}
    rails_units = state.get("rails_units", {}) or {}

    prompt = f"""
You are a senior Django architect.
Given the Rails summary and units, produce a complete JSON Django blueprint.

Output JSON with this exact structure:
{{
  "project_name": "<django_project_name>",
  "settings_code": "<full valid Django 5.x settings.py>",
  "urls_code": "<root urls.py including admin and app includes>",
  "apps": [
    {{
      "name": "<app_name>",
      "models_code": "<Django models>",
      "views_code": "<Django class-based views>",
      "urls_code": "<Django urls.py for the app>",
      "admin_code": "<Django admin registration>",
      "templates": [{{"name": "template_name.html", "content": "<valid Django HTML template>"}}]
    }}
  ],
  "settings_overrides": {{"MEDIA": true, "STATIC": true}},
  "requirements": ["Django>=5,<6", "Pillow"]
}}

Rules:
- Always include both 'settings_code' and 'urls_code' at the top level.
- settings_code must include BASE_DIR, INSTALLED_APPS, MIDDLEWARE, STATIC_URL, MEDIA_URL.
- urls_code must include admin route and includes for all apps.
- Include converted templates for layouts, devise, and action_text if present in Rails views.
- Do NOT include markdown, comments, or extra text — only valid JSON.
"""

    raw_content = None
    parsed = None

    # 1️⃣ First LLM attempt to generate full blueprint
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You convert Rails apps to complete Django project blueprints."},
                {
                    "role": "user",
                    "content": prompt
                               + "\n\nRails summary:\n"
                               + json.dumps(rails_summary, indent=2)
                               + "\n\nRails units:\n"
                               + json.dumps(rails_units, indent=2),
                },
            ],
            temperature=0.3,
            max_tokens=8000,
        )
        raw_content = response.choices[0].message.content.strip()
        parsed = _try_parse_json(raw_content)
    except Exception as e:
        print(f"⚠️ LLM call failed: {e}")

    # 2️⃣ Try to repair invalid JSON
    if parsed is None and raw_content:
        print("⚠️ Invalid JSON returned by LLM, attempting repair...")
        parsed = _repair_json_with_llm(raw_content)

    # 3️⃣ Fallback (minimal) — only if all parsing failed
    if parsed is None:
        print("⚠️ All JSON parsing attempts failed — using minimal fallback blueprint.")
        parsed = {
            "project_name": "converted_project",
            "settings_code": "",
            "urls_code": "",
            "apps": [],
            "settings_overrides": {"MEDIA": True, "STATIC": True},
            "requirements": ["Django>=5,<6", "Pillow"],
        }

    # 4️⃣ Refinement trigger check
    rails_templates = [
        f for f in rails_summary.get("candidates_to_read", [])
        if "/app/views/" in f
    ]
    total_rails_views = len(rails_templates)
    django_templates_count = sum(len(a.get("templates", [])) for a in parsed.get("apps", []))

    needs_refine = (
        not parsed.get("settings_code")
        or not parsed.get("urls_code")
        or any(
            app.get("models_code") == ""
            or app.get("views_code") == ""
            or app.get("urls_code") == ""
            or app.get("admin_code") == ""
            or any(t.get("content") == "" for t in app.get("templates", []))
            for app in parsed.get("apps", [])
        )
        or django_templates_count < total_rails_views
    )

    refined = None
    if needs_refine:
        print(f"✨ Refining blueprint (Rails templates: {total_rails_views}, Django templates: {django_templates_count})...")
        refined = _refine_blueprint_with_llm(parsed, rails_summary, rails_units)
        if refined:
            parsed = refined

    # 🧾 Save all versions for debugging
    log_dir = f"{state.output_dir}/logs"
    log_utils.log_state("converter_raw", {"raw": raw_content}, f"{log_dir}/converter_raw.json")
    log_utils.log_state("converter_parsed", parsed, f"{log_dir}/converter_parsed.json")
    if refined:
        log_utils.log_state("converter_refined", refined, f"{log_dir}/converter_refined.json")

    state.django_blueprint = parsed
    return state
