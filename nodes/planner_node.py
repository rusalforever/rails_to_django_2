from tools import file_tools, log_utils

def run(state):
    state.current_node = "planner_node"

    tree = file_tools.list_tree(state.input_dir)
    plan = {
        "phases": ["discovery", "conversion", "build", "integration"],
        "discovery": {"select_globs": [
            "app/models/**/*.rb",
            "app/controllers/**/*.rb",
            "config/routes.rb",
            "app/views/**/*"
        ]},
        "selection_strategy": "Select main Rails MVC files",
        "llm_requirements": [
            "use rails_parser.summarize_structure",
            "then rails_parser.analyze_units on selected files"
        ],
        "risks": ["possible meta-programming issues"],
        "assumptions": ["standard Rails 5+ layout"]
    }

    state.plan = plan
    log_utils.log_state("planner_node", plan, f"{state.output_dir}/logs/planner.json")
    return state
