# StackShift

A CLI tool to help migrate web applications from Vite to Next.js, powered by AI.

## Features

- 🔍 Comprehensive project analysis
- 🤖 AI-powered migration suggestions
- 📦 Dependency compatibility checking
- 🛣️ Routing structure analysis
- ⚙️ Configuration migration assistance

## Installation

### Using pip

```bash
pip install stackshift
```

### From source

```bash
git clone https://github.com/yourusername/stackshift.git
cd stackshift
poetry install
```

## Usage

### Analyze a Vite project

```bash
stackshift analyze /path/to/your/vite/project
```

Options:
- `--skip-ai`: Skip AI-assisted analysis
- `--non-interactive`: Run in non-interactive mode
- `--version`: Show version information

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key for AI-assisted analysis

## Development

1. Clone the repository
2. Install poetry if you haven't already: `pip install poetry`
3. Install dependencies: `poetry install`
4. Run tests: `poetry run pytest`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT 