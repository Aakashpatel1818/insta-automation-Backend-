# Contributing to Instagram Automation Pro

We love your input! We want to make contributing to this project as easy and transparent as possible.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

**Before Creating Bug Reports**
- Check the FAQ
- Search existing issues
- Check if the issue is reproducible

**When Creating a Bug Report, Please Include:**
- Clear descriptive title
- Detailed description of the behavior
- Specific examples to reproduce
- Screenshots if applicable
- Environment info (OS, Python/Node version, etc.)
- Logs if available

### Suggesting Enhancements

**Before Creating Enhancement Suggestions**
- Check if feature already exists
- Check if feature has been suggested before

**When Creating Suggestions, Include:**
- Clear title
- Detailed description of the enhancement
- Use cases and benefits
- Possible implementation approach (optional)

### Pull Requests

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/insta-automation.git
   cd insta-automation
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation as needed
   - Keep commits atomic and logical

3. **Test Your Changes**
   ```bash
   # Backend
   pytest tests/

   # Frontend
   npm run test
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Fill out the PR template
   - Reference related issues
   - Describe changes clearly

## Development Setup

See [SETUP.md](./SETUP.md) for detailed instructions.

## Styleguides

### Python Code Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Max line length: 100 characters
- Use meaningful variable names

```python
# Good
def validate_email(email: str) -> bool:
    """Validate email format."""
    return EMAIL_REGEX.test(email)

# Avoid
def v_e(e):
    return EMAIL_REGEX.test(e)
```

### JavaScript/TypeScript Code Style

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use const/let, not var
- Use arrow functions
- Add JSDoc comments for functions

```javascript
// Good
const validateEmail = (email: string): boolean => {
  /**
   * Validates email format
   * @param email - Email to validate
   * @returns true if valid, false otherwise
   */
  return EMAIL_REGEX.test(email);
};

// Avoid
var v_e = function(e) {
  return EMAIL_REGEX.test(e);
};
```

### Commit Messages

Use conventional commits format:

```
type(scope): subject

body (optional)
footer (optional)
```

Types: feat, fix, docs, style, refactor, test, chore

Examples:
```
feat(auth): add JWT token refresh endpoint
fix(rules): correct rule priority sorting
docs(readme): update installation instructions
test(api): add tests for auth routes
```

## Project Structure

```
insta-automation/
├── Backend (FastAPI)
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── Frontend (React + Vite)
│   ├── src/
│   ├── tests/
│   ├── package.json
│   └── README.md
│
├── docs/
├── SETUP.md
├── CONTRIBUTING.md
└── LICENSE
```

## Key Areas

### Backend
- **API Routes**: `app/api/routes/`
- **Database Models**: `app/db/models.py`
- **Configuration**: `app/core/`
- **Tests**: `tests/`

### Frontend
- **Pages**: `src/pages/`
- **Components**: `src/components/`
- **Hooks**: `src/hooks/`
- **Utilities**: `src/utils/`
- **Type Definitions**: `src/types/`

## Testing

### Backend Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app
```

### Frontend Tests

```bash
# Install test dependencies
npm install --save-dev vitest @testing-library/react

# Run tests
npm run test

# With coverage
npm run test:coverage
```

## Performance Considerations

### Backend
- Use async/await for I/O operations
- Cache frequently accessed data
- Use indexes for MongoDB queries
- Implement rate limiting
- Log structured logs

### Frontend
- Code split routes
- Lazy load components
- Optimize images
- Minimize bundle size
- Use memoization for expensive computations

## Documentation

- Update README.md for significant changes
- Add docstrings to functions
- Comment complex logic
- Update API documentation
- Include examples in comments

## Community

- Be respectful and inclusive
- Help other contributors
- Review PRs thoughtfully
- Share knowledge and experience

Thank you for contributing! 🌟
