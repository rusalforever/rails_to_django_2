# nodes/builder_node.py
"""
builder_node.py — Django project generation step.

This node calls tools/django_builder.create_core_files() to build
the Django project skeleton using both static templates and LLM context.
It then updates the ConversionState and logs a summary.
"""

from rich.console import Console
from rich.table import Table
from tools import django_builder, log_utils


console = Console()


def run(state):
    """Generate Django project files based on blueprint + LLM context."""
    state.current_node = "builder_node"
    console.print("[bold cyan]🏗️ Building Django project structure...[/bold cyan]")

    try:
        result = django_builder.create_core_files(state)
    except Exception as e:
        console.print(f"[bold red]❌ Builder node failed:[/bold red] {e}")
        raise

    generated = result.get("generated", [])
    console.print(f"[green]✅ Generated {len(generated)} core Django files.[/green]\n")

    # 📘 Create a nice summary table
    table = Table(title="Generated Django Files", header_style="bold magenta")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")

    for f in generated:
        table.add_row(f, "✅ written")

    console.print(table)

    # 🧾 Log the result for debugging
    log_utils.log_state(
        "builder_node",
        {"generated_files": generated, "project_root": state.project_root},
        f"{state.output_dir}/logs/builder.json"
    )

    return state
