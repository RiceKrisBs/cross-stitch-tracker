#!/bin/bash
# Run linting on the codebase

echo "Running Ruff linter..."
ruff check .

if [ $? -eq 0 ]; then
    echo "✓ Linting passed!"

    echo ""
    echo "Running Ruff formatter..."
    ruff format .

    if [ $? -eq 0 ]; then
        echo "✓ Formatting complete!"
    else
        echo "✗ Formatting failed"
        exit 1
    fi
else
    echo "✗ Linting failed"
    exit 1
fi
