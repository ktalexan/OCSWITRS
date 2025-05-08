# Project general coding standards


## Code indentation
- Always use 4 spaces for indentation
- Avoid using tabs for indentation
- Ensure consistent indentation across all files
- Use a linter to enforce indentation rules

## Naming conventions
- Use PascalCase for component names, interfaces, and type aliases
- Use camelCase for variables, functions, and methods
- Prefix private class members with an underscore (e.g., `_privateMember`)
- use ALL_CAPS for constants (e.g., `MAX_LENGTH`)

## Error handling
- Use `try-catch` blocks for async operations and handle errors gracefully
- Implement proper error boundaries in React components to catch rendering errors
- Always log errors with contextual information.