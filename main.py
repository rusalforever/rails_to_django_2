import os
from graph import build_graph
from state import ConversionState
from tools import file_tools
from rich.console import Console
from rich.table import Table

console = Console()

def main():
    console.print("\n====================================")
    console.print("🚀 Starting Rails → Django conversion")
    console.print("====================================")

    input_dir = "./my_rails_app"
    output_dir = "./out_django"

    console.print(f"Input directory:  {input_dir}")
    console.print(f"Output directory: {output_dir}\n")

    state = ConversionState(input_dir=input_dir, output_dir=output_dir)
    graph = build_graph()

    try:
        console.print("🧠 Executing graph...")
        final_state = graph.invoke(state)
    except Exception as e:
        console.print(f"❌ Graph execution failed: {e}")
        return

    console.print("\n✅ Conversion complete!\n")

    # Ensure final_state is a dict
    if hasattr(final_state, "dict"):
        final_state_dict = final_state.dict()
    elif isinstance(final_state, dict):
        final_state_dict = final_state
    else:
        final_state_dict = vars(final_state)

    # Prepare final summary table
    table = Table(title="Final Conversion State", header_style="bold magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Value Summary", style="green")

    for key, value in final_state_dict.items():
        if isinstance(value, (list, dict)):
            summary = f"{len(value)} {'items' if isinstance(value, list) else 'keys'}"
        else:
            summary = str(value)
        table.add_row(key, summary)

    console.print(table)

    # Ensure logs directory exists
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    final_state_path = os.path.join(logs_dir, "final_state.json")
    file_tools.write_json(final_state_path, final_state_dict, makedirs=True)

    console.print(f"📝 Final state written to: {final_state_path}\n")


if __name__ == "__main__":
    main()
