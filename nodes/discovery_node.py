# nodes/discovery_node.py
import os
import json
from tools import file_tools, rails_parser, log_utils


def run(state: dict) -> dict:
    """
    Discovery Node:
    - Lists project files.
    - Summarizes Rails structure using rails_parser.
    - Reads selected files safely (skipping directories/binaries).
    - Analyzes files deeply using rails_parser.
    - Logs results to /logs/discovery_node.json
    """

    input_dir = state.get("input_dir")
    output_dir = state.get("output_dir")
    plan = state.get("plan")

    state["current_node"] = "discovery_node"

    # Step 1: list files (with optional glob filtering)
    globs = plan.get("discovery", {}).get("select_globs") if plan else None
    print(f"🔍 Listing files under {input_dir}...")
    tree = file_tools.list_tree(input_dir, globs)

    # Step 2: summarize Rails structure (LLM)
    print("🧩 Summarizing Rails structure...")
    summary = rails_parser.summarize_structure(tree)
    candidates = summary.get("candidates_to_read", [])

    # Step 3: read selected files safely
    print(f"📖 Reading {len(candidates)} selected files...")
    files_data = file_tools.read_files(
        [os.path.join(input_dir, c) if not os.path.isabs(c) else c for c in candidates],
        max_bytes_per_file=80_000,
    )

    # Step 4: LLM-based analysis of read files
    print("🧠 Analyzing Rails units via LLM...")
    analysis = rails_parser.analyze_units(files_data)

    # Step 5: Update state
    state.update(
        {
            "rails_summary": summary,
            "files_to_read": candidates,
            "rails_units": analysis,
        }
    )

    # Step 6: Logging
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_utils.log_state(
        node="discovery_node",
        state_subset={
            "rails_summary": summary,
            "files_to_read": candidates,
        },
        path=os.path.join(logs_dir, "discovery_node.json"),
    )

    # Optional: log LLM call info if present
    if "llm_response" in state:
        log_utils.log_llm_call(
            node="discovery_node",
            prompt="rails_parser.summarize_structure",
            response=json.dumps(summary, indent=2),
            path=os.path.join(logs_dir, "discovery_node_llm.json"),
        )

    return state
