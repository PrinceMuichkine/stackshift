Directory structure:
└── vysakh0-dravid/
    ├── tests/
    │   ├── api/
    │   │   ├── test_openai_api.py
    │   │   ├── test_claude_api.py
    │   │   └── test_api_main.py
    │   ├── cli/
    │   │   ├── query/
    │   │   │   ├── test_dynamic_command_handler.py
    │   │   │   ├── test_file_operations.py
    │   │   │   ├── test_query_main.py
    │   │   │   └── test_image_handler.py
    │   │   └── monitor/
    │   │       ├── test_input_parser.py
    │   │       ├── test_error_handlers.py
    │   │       ├── test_dev_server_monitor.py
    │   │       ├── test_output_monitor.py
    │   │       ├── test_error_resolvers.py
    │   │       └── test_input_handler.py
    │   ├── metadata/
    │   │   ├── test_rate_limit_handler.py
    │   │   ├── test_project_metadata.py
    │   │   ├── test_common_utils.py
    │   │   ├── test_updater.py
    │   │   └── test_initializer.py
    │   └── utils/
    │       ├── test_file_utils.py
    │       ├── test_apply_changes.py
    │       ├── test_pretty_print_stream.py
    │       ├── test_utils.py
    │       ├── test_parser.py
    │       ├── test_step_executor.py
    │       ├── test_diff.py
    │       └── test_loader.py
    ├── .github/
    │   └── workflows/
    │       └── main.yml
    ├── drd.json
    ├── conftest.py
    ├── pyproject.toml
    ├── project_guidelines.txt
    ├── LICENSE
    ├── README.md
    ├── CONTRIBUTING.md
    └── src/
        └── drd/
            ├── api/
            │   ├── ollama_api.py
            │   ├── openai_api.py
            │   ├── main.py
            │   ├── __init__.py
            │   └── claude_api.py
            ├── main.py
            ├── .gitignore
            ├── cli/
            │   ├── main.py
            │   ├── commands.py
            │   ├── __init__.py
            │   ├── ask_handler.py
            │   ├── query/
            │   │   ├── main.py
            │   │   ├── dynamic_command_handler.py
            │   │   ├── image_handler.py
            │   │   ├── file_operations.py
            │   │   └── __init__.py
            │   └── monitor/
            │       ├── main.py
            │       ├── error_resolver.py
            │       ├── __init__.py
            │       ├── input_parser.py
            │       ├── state.py
            │       ├── server_monitor.py
            │       ├── output_monitor.py
            │       ├── history_tracker.py
            │       └── input_handler.py
            ├── __init__.py
            ├── prompts/
            │   ├── error_resolution_prompt.py
            │   ├── file_metada_desc_prompts.py
            │   ├── framework_prompts/
            │   │   ├── main_frameworks_prompt.py
            │   │   └── nextjs_prompt.py
            │   ├── instructions.py
            │   ├── get_project_info_prompts.py
            │   ├── file_operations.py
            │   ├── error_related_files_prompt.py
            │   ├── __init__.py
            │   ├── monitor_error_resolution.py
            │   └── metadata_update_prompts.py
            ├── metadata/
            │   ├── rate_limit_handler.py
            │   ├── common_utils.py
            │   ├── updater.py
            │   ├── initializer.py
            │   ├── project_metadata.py
            │   └── __init__.py
            └── utils/
                ├── pretty_print_stream.py
                ├── parser.py
                ├── input.py
                ├── loader.py
                ├── diff.py
                ├── __init__.py
                ├── file_utils.py
                ├── step_executor.py
                ├── utils.py
                └── apply_file_changes.py
