# Agent Guidelines for traffic-api

## Commands
- **Run app**: `uv run python src/run.py`
- **Lint/Type check**: `uv run pyrefly check`
- **Install deps**: `uv sync`
- **Run single test**: No tests configured yet - use `uv run pytest tests/test_file.py::test_function` when added

## Code Style
- **Imports**: Relative imports from `app.*`, standard library first, then third-party, then local
- **Types**: Use `|` union syntax, full type hints on all functions/parameters
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Models**: Use SQLModel with `Field()` for database columns, inherit from base models
- **Settings**: Use Pydantic BaseSettings with `field_validator(mode="before")` for complex validation
- **Error handling**: Return None for not found, raise exceptions for errors, no try/catch unless necessary
- **Comments**: Minimal comments, use descriptive names; avoid Spanish comments in English code
- **Formatting**: Follow pyrefly standards, use `# pyrefly: ignore` for SQLModel `__tablename__` assignments and other valid overrides