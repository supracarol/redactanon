# RedactAnon ⚡

![RedactAnon](assets/redactnon.png)

![CI](https://github.com/supracarol/redactanon/actions/workflows/ci.yml/badge.svg?branch=main)

**Safely share files with LLMs and search engines by automatically removing personal data while keeping it easily restorable.**

RedactAnon is a powerful CLI tool that scrubs sensitive information from your files before sharing them with AI models, search engines, or collaborators. Unlike irreversible redaction tools, RedactAnon maintains intelligent mappings that let you instantly restore all original values when needed.

⚠️ **Note**: This project is currently under heavy development. Use at your own risk and always keep backups of important files.

## Why RedactAnon?

**Share files with AI models and search engines without risking your privacy.**

RedactAnon automatically detects and removes sensitive personal information from your files, making them safe to share with LLMs like ChatGPT, Claude, and Gemini, or to index in search engines. What makes RedactAnon special is its **reversible approach** - you can instantly restore all original data with a single command.

### Key Benefits:
- **🤖 LLM-Ready**: Safely chat with AI assistants using your real code and logs
- **⚡ Effortless Restoration**: Bring back original data anytime with automatic mapping
- **🛡️ Comprehensive Protection**: Removes emails, IPs, phones, SSNs, credit cards, and custom patterns
- **🔄 Simple Configuration**: Works out-of-the-box with smart defaults

### Perfect For:
- Sharing code with AI coding assistants
- Debugging with AI using real log files
- Collaborative development without privacy concerns
- Search engine indexing of documentation
- Preparing test data from production files

## Features

- **Reversible Anonymization**: Replace sensitive data with fake values that can be restored later
- **Pattern Detection**: Built-in patterns for common sensitive data types (emails, IP addresses, phone numbers, etc.)
- **Realistic Dummy Data**: Uses the [Faker](https://faker.readthedocs.io/) library to generate realistic fake data that maintains the format and appearance of original data
- **Custom Patterns**: Support for user-defined regex patterns via TOML or simple text configuration
- **Smart Mapping**: Consistent replacement - same original value always maps to the same fake value
- **Directory Processing**: Process entire directories with optional backup creation
- **Automatic Mapping**: Intelligent mapping system with UUID-based file linking

## Installation

### Method 1: Direct Installation from GitHub

Install directly from the GitHub repository using modern Python package managers:

**Using pipx (recommended for CLI tools):**
```bash
# Install pipx if you haven't already
pip install pipx

# Install redactanon directly from GitHub
pipx install git+https://github.com/supracarol/redactanon.git

# Run the tool
redactanon --help
```

**Using uvx (modern alternative):**
```bash
# Install using uvx (part of uv toolchain)
uvx git+https://github.com/supracarol/redactanon.git --help

# Or install and run
uv tool install redactanon --from git+https://github.com/supracarol/redactanon.git
```

**Using pip directly:**
```bash
# Install directly with pip
pip install git+https://github.com/supracarol/redactanon.git

# Run the tool
redactanon --help
```

### Method 2: Local Development Installation

```bash
# Clone the repository
git clone https://github.com/supracarol/redactanon.git
cd redactanon

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package in development mode
pip install -e .

# Run the tool
redactanon --help
```

## Usage

### Basic Anonymization

```bash
# Anonymize a file or directory in-place
redactanon anon /path/to/file_or_directory

# Anonymize to a destination directory (creates backup)
redactanon anon /source/path /destination/path
```

### Custom Configuration

```bash
# Use custom TOML configuration
redactanon anon /path/to/files --config patterns.toml

# Use simple text configuration
redactanon anon /path/to/files --simple-config patterns.txt

# Use only custom patterns (disable defaults)
redactanon anon /path/to/files --config patterns.toml --no-defaults
```

### Restoration

```bash
# Restore files using stored mappings
redactanon restore /path/to/anonymized/files

# Restore using specific mapping file
redactanon restore /path/to/files --mappings custom_mappings.json
```

### Mapfile Behavior

RedactAnon automatically manages mapping files for reversible anonymization:

**For single files:**
- Default: Creates `<filename>.map.json` in the current directory
- Custom: Use `--mapfile <path>` to specify a custom location

**For directories:**
- Default: Creates `~/.redactanon/mappings/<uuid>.json` and `.redactanon-id` in the directory
- Custom: Use `--mapfile <path>` to specify a custom location (still creates `.redactanon-id`)

Examples:
```bash
# Single file - creates document.txt.map.json
redactanon anon document.txt

# Directory - creates ~/.redactanon/mappings/<uuid>.json
redactanon anon /path/to/folder

# Custom mapfile for file
redactanon anon --mapfile my_mappings.json document.txt

# Custom mapfile for directory
redactanon anon --mapfile project_mappings.json /path/to/project
```

## Configuration

### TOML Configuration Format

Create a `patterns.toml` file:

```toml
[email]
pattern = '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
type = "email"
# Optional: specify custom replacement value
replacement = "user@example.com"

[ip_address]
pattern = '\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
type = "ip_address"
# Optional: let system generate random replacement
# replacement = "192.168.1.100"

[custom_name]
pattern = "John Doe"
type = "name"
replacement = "Anonymous User"
```

### Simple Text Configuration Format

Create a `patterns.txt` file:

```
John Doe=Anonymous User
192.168.1.100=10.0.0.1
confidential-project=public-project
+1-555-555-0199
secret-api-key
```

## Built-in Patterns

RedactAnon includes built-in patterns for:
- Email addresses
- IPv4 and IPv6 addresses
- US phone numbers
- US Social Security Numbers
- Credit card numbers (Visa, MasterCard, American Express, Discover)

## How It Works

### Smart Reversible Anonymization

RedactAnon uses a sophisticated mapping system that makes file sharing both safe and flexible:

1. **🔍 Detection**: Scans files for sensitive data using powerful regex patterns
2. **🔗 Smart Mapping**: Creates intelligent bidirectional mappings (original ↔ fake values)
3. **🔄 Consistent Replacement**: Same original value always gets the same fake replacement
4. **💾 Automatic Storage**: Maps are saved to `~/.redactanon/mappings/` with UUID linking
5. **⚡ Instant Restoration**: Restore original files anytime using stored mappings

### Effortless Remapping

Unlike traditional redaction tools, RedactAnon remembers exactly what it changed:

```bash
# Anonymize your files
redactanon anon sensitive-document.txt

# Share safely with LLMs, then restore anytime
redactanon restore sensitive-document.txt
```

The mapping files are lightweight JSON that can be easily backed up, shared between team members, or stored wherever you need them using the `--mapfile` option.

## Privacy Features

- Mapping files stored privately in user's home directory (`~/.redactanon/mappings/`)
- UUID-based linking prevents accidental mapping mismatches
- `.redactanon-id` files in processed directories for reliable mapping association
- No sensitive data stored in processed files

## Future Plans

### Advanced Entity Recognition
Future versions will incorporate Named Entity Recognition (NER) models for more sophisticated redaction of:
- Person names in various contexts
- Organization names
- Locations and addresses
- Medical terms
- Financial data

This will complement the current regex-based approach with AI-powered detection.

## Requirements

- Python 3.7+
- Faker>=40.0.0 (automatically installed with the package)

## Development

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest src/redactanon/tests/ -v
```

### Development Dependencies

This project uses setuptools extras for development dependencies:
- `pip install -e .` - Install runtime dependencies only
- `pip install -e .[dev]` - Install runtime + development dependencies (pytest, black, mypy, flake8, isort, bandit, pre-commit)
- `pip install -e .[test]` - Install runtime + test dependencies (pytest)

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency. To set up pre-commit:

```bash
# Install development dependencies (includes pre-commit)
pip install -e .[dev]

# Install the pre-commit hooks
pre-commit install
```

The pre-commit hooks will automatically run on every commit and include:
- **Code formatting**: Black for automatic code formatting
- **Import sorting**: isort for organizing imports
- **Linting**: flake8 for code style checking
- **Type checking**: mypy for static type checking
- **Security scanning**: bandit for security issue detection
- **General quality**: Various pre-commit-hooks for common issues

To run pre-commit on all files manually:
```bash
pre-commit run --all-files
```

### Project Structure

```
redactanon/
├── src/
│   └── redactanon/
│       ├── cli.py         # Main CLI entry point
│       ├── core/
│       │   ├── pattern_engine.py  # Pattern detection logic
│       │   ├── data_generator.py  # Fake data generation
│       │   ├── mapping_manager.py # Mapping storage and retrieval
│       │   └── file_processor.py  # File processing logic
│       ├── patterns/
│       │   ├── builtin.py         # Built-in pattern definitions
│       │   └── user_patterns.py   # User pattern handling
│       ├── utils/
│       │   ├── config_loader.py   # Configuration management
│       │   └── validators.py      # Input validation utilities
│       └── tests/
│           ├── test_patterns.py
│           ├── test_generator.py
│           └── test_mappings.py
├── config/
│   └── default_patterns.toml
└── README.md
```
