# tools/template_converter.py
import os
from openai import OpenAI

client = OpenAI()

def convert_template_with_llm(content: str, template_name: str = "") -> str:
    """
    Convert an ERB or mixed Rails template to a Django/Jinja2 HTML template using LLM.
    Returns clean Jinja2-compatible HTML.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert at converting Ruby on Rails ERB templates "
                        "into Django Jinja2 templates (.html). Output only the final Jinja2 HTML code. "
                        "Preserve layout, forms, loops, and logic. Use {% ... %} and {{ ... }} syntax properly. "
                        "Do not wrap in markdown or explain anything."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Convert this ERB template into a Django Jinja2 template:\n\n---\n{content}\n---",
                },
            ],
            temperature=0.3,
            max_tokens=4000,
        )
        new_content = response.choices[0].message.content.strip()
        return new_content
    except Exception as e:
        print(f"⚠️ Template LLM conversion failed for {template_name}: {e}")
        return content


def convert_filename(name: str) -> str:
    """Change ERB or similar Rails template extensions to .html."""
    base, ext = os.path.splitext(name)
    if ext == ".erb":
        return base + ".html"
    if ext == ".html.erb":
        return base + ".html"
    return name
