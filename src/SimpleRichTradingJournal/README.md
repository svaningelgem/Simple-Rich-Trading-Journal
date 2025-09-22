# Simple Rich Trading Journal (SRTJ)

Refactored for modularity with SQLAlchemy storage, YAML config, and repository pattern.

## Setup
1. `poetry install`
2. Copy `config.example.yaml` to `config.yaml` and edit (e.g., storage.url).
3. `poetry run srtj migrate` (if from old pickle).
4. `poetry run srtj demo` for sample data.
5. `poetry run srtj run`

## TODO
- Implement sessions + RBAC (filter repo by user_id).
- Expand plugins for custom calcs/auth.
- Add Alembic for schema migrations.
- UI polish: Full theme application, note editor.

## Structure
- config/: YAML + Pydantic.
- storage/: Repo + SQL models.
- core/: Pure calcs/utils.
- ui/: Dash layouts/components.
- cli.py: Commands.