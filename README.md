# 🧠 Rails → Django Converter  
An intelligent pipeline that automatically converts **Ruby on Rails** applications into structured **Django** projects using **LangGraph nodes**, **tool orchestration**, and **LLM-based reasoning**.  
## ⚙️ Quick Start  
```bash
git clone https://github.com/yourusername/rails_to_django_2.git
cd rails_to_django_2
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --input ./my_rails_app --output ./out_django
After completion, you’ll find the generated Django project in out_django/.

🧩 Conversion Pipeline
Step	Node	Description	Uses LLM
1️⃣	planner_node	Builds pipeline plan and execution order	No
2️⃣	discovery_node	Reads and summarizes Rails structure	✅ Yes
3️⃣	converter_node	Generates Django blueprint from Rails summary	✅ Yes
4️⃣	builder_node	Builds actual Django files and templates	✅ Yes
5️⃣	integration_node	Writes final README, summary, and requirements	✅ Yes

rails_to_django_2/
├── main.py
├── nodes/
│   ├── planner_node.py
│   ├── discovery_node.py
│   ├── converter_node.py
│   ├── builder_node.py
│   └── integration_node.py
├── tools/
│   ├── file_tools.py
│   ├── log_utils.py
│   ├── django_builder.py
│   ├── template_converter.py
│   └── llm_utils.py
└── out_django/
    ├── my_django_app/
    ├── README.md
    └── logs/

Node Descriptions

discovery_node → reads Rails tree, collects files, and calls LLM for structural summary.

converter_node → transforms Rails summary into a Django JSON blueprint (settings_code, urls_code, apps, templates).

builder_node → writes Django files, converts .erb templates to Jinja2 via LLM.

integration_node → generates final documentation and conversion statistics.

🧠 LLM Integration
Phase	Model	Purpose
Discovery	gpt-4o	Summarize Rails models, controllers, and views
Conversion	gpt-4o	Create Django blueprint JSON
JSON Repair	gpt-4o-mini	Fix malformed JSON
Refinement	gpt-4o	Fill missing models/views/templates
Template Conversion	gpt-4o-mini	ERB → Django Template
README Generation	gpt-4o-mini	Write project documentation
📦 Output Artifacts

my_django_app/ → Generated Django app

conversion_summary.json → Conversion statistics

logs/ → LLM prompts/responses and node states

README.md → Auto-generated project guide

🧭 Notes

Requires OPENAI_API_KEY in environment

Default models: gpt-4o, gpt-4o-mini

Modular node design allows re-running specific stages

Full LLM-based reasoning with auto-repair and refinement