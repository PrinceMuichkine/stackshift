# Stackshift

An AI powered CLI tool to help migrate web applications from Vite to Next.js.

## Features

- Intelligent analysis of Vite projects
- Automatic migration of components and routing
- Support for both Next.js App Router and Pages Router
- AI-powered code transformations
- Interactive assistance

## Installation

```bash
pip install stackshift
```

## Usage

1. Configure your API key:
```bash
stackshift setup
```

2. Scan your Vite project:
```bash
stackshift scan
```

3. Validate migration progress:
```bash
stackshift validate
```

4. Transform components:
```bash
stackshift transform
```

5. Get interactive assistance:
```bash
stackshift chat
```

## Options

- `--router`: Choose between "app" (default) and "pages" router
- `--fix`: Automatically fix validation issues
- Project path is optional if you're inside a Vite project

## Examples

```bash
# Scan current directory
stackshift scan

# Validate with Pages Router
stackshift validate --router pages

# Transform with automatic fixes
stackshift validate --fix

# Scan specific project
stackshift scan ./my-vite-project
```

## Requirements

- Python 3.8 or higher
- Anthropic API key
- Node.js and npm (for the Vite project)

## License

MIT License 