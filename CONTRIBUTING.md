# 🤝 Contributing to MR Bot

Thank you for your interest in contributing to MR Bot! This guide will help you get started with contributing to our Medical Representative tracking system.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

## 🤗 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and help them learn
- **Be collaborative**: Work together towards common goals
- **Be professional**: Keep discussions focused and constructive

## 🚀 Getting Started

### Prerequisites
- Python 3.12+ for backend development
- Node.js 18+ for frontend development
- Git for version control
- Basic knowledge of FastAPI and React/Next.js

### Areas for Contribution
- 🐛 **Bug fixes**: Help identify and fix issues
- ✨ **New features**: Add functionality to improve the system
- 📚 **Documentation**: Improve guides and API documentation
- 🧪 **Testing**: Add or improve test coverage
- 🎨 **UI/UX**: Enhance the frontend interface
- ⚡ **Performance**: Optimize code and queries

## 🛠️ Development Setup

### 1. Fork and Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/mr_bot.git
cd mr_bot

# Add the original repository as upstream
git remote add upstream https://github.com/originalowner/mr_bot.git
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Copy environment template
cp .env.example .env
# Edit .env with your development values
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local
# Edit .env.local with your development values
```

### 4. Run Development Servers
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 📝 How to Contribute

### 1. Choose an Issue
- Check the [Issues](https://github.com/originalowner/mr_bot/issues) page
- Look for issues labeled `good first issue` for beginners
- Comment on the issue to let others know you're working on it

### 2. Create a Branch
```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create a new branch for your feature
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/issue-description
```

### 3. Make Changes
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation if needed
- Commit your changes with clear messages

### 4. Test Your Changes
```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend
npm test

# Linting
black .
flake8 .
```

## 🔄 Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] No sensitive data committed

### PR Template
When creating a pull request, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (specify)

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Screenshots (if UI changes)
[Add screenshots here]

## Additional Notes
Any additional information or context
```

### Review Process
1. **Automated checks**: All CI checks must pass
2. **Code review**: At least one maintainer review required
3. **Testing**: Verify the changes work as expected
4. **Merge**: Maintainer will merge approved PRs

## 📏 Coding Standards

### Python (Backend)
```python
# Use Black for formatting
black .

# Follow PEP 8 guidelines
flake8 .

# Type hints required for new code
def create_visit(visit_data: dict) -> Visit:
    pass

# Docstrings for functions and classes
def process_location(lat: float, lng: float) -> dict:
    """
    Process geographic coordinates and return location data.
    
    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        
    Returns:
        dict: Processed location information
    """
    pass
```

### TypeScript (Frontend)
```typescript
// Use proper TypeScript types
interface VisitData {
  id: string;
  mrName: string;
  location: {
    lat: number;
    lng: number;
  };
}

// Use functional components with hooks
const VisitCard: React.FC<{ visit: VisitData }> = ({ visit }) => {
  return <div>{visit.mrName}</div>;
};

// Use proper error handling
try {
  const response = await fetch('/api/visits');
  const data = await response.json();
} catch (error) {
  console.error('Failed to fetch visits:', error);
}
```

### File Naming
- Python: `snake_case.py`
- TypeScript/React: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- CSS: `kebab-case.css`

### Commit Messages
```bash
# Format: type(scope): description
feat(api): add visit filtering endpoint
fix(ui): resolve map rendering issue
docs(readme): update installation instructions
test(parser): add unit tests for AI parsing
refactor(auth): simplify authentication logic
```

## 🧪 Testing Guidelines

### Backend Testing
```python
# Test file naming: test_*.py
# Location: same directory as the module being tested

import pytest
from main import app

def test_create_visit():
    """Test visit creation endpoint."""
    # Arrange
    visit_data = {"mr_name": "John", "location": "Hospital"}
    
    # Act
    response = client.post("/visits", json=visit_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["mr_name"] == "John"

# Use fixtures for common setup
@pytest.fixture
def sample_visit():
    return {"mr_name": "John", "location": "Hospital"}
```

### Frontend Testing
```typescript
// Use Jest and React Testing Library
import { render, screen } from '@testing-library/react';
import VisitCard from './VisitCard';

test('renders visit information', () => {
  const visit = { id: '1', mrName: 'John', location: { lat: 0, lng: 0 } };
  
  render(<VisitCard visit={visit} />);
  
  expect(screen.getByText('John')).toBeInTheDocument();
});
```

### Test Coverage
- Aim for >80% test coverage
- Test both happy paths and error cases
- Include integration tests for critical workflows

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Include type hints for Python code
- Add comments for complex logic

### API Documentation
- Update OpenAPI/Swagger documentation for new endpoints
- Include request/response examples
- Document error codes and messages

### User Documentation
- Update README.md for new features
- Add setup instructions for new dependencies
- Create tutorials for complex features

## 🐛 Bug Reports

When reporting bugs, include:
- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps to recreate the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, browser, etc.
- **Screenshots**: If applicable
- **Logs**: Relevant error messages or logs

## 💡 Feature Requests

For new features, provide:
- **Problem statement**: What problem does this solve?
- **Proposed solution**: How would you like it to work?
- **Alternatives**: Other solutions you've considered
- **Additional context**: Screenshots, mockups, examples

## 🎯 Development Workflow

### Daily Development
1. **Sync with upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make incremental commits**
   ```bash
   git add .
   git commit -m "feat(api): add visit validation"
   ```

3. **Push regularly**
   ```bash
   git push origin feature/your-feature
   ```

4. **Keep PRs small** - Easier to review and merge

### Code Review Guidelines
- **Be constructive**: Suggest improvements, don't just point out problems
- **Be specific**: Reference line numbers and provide examples
- **Be respectful**: Remember there's a person behind the code
- **Be thorough**: Check functionality, performance, and security

## 📞 Getting Help

If you need help:
- 💬 **Discussions**: Use GitHub Discussions for questions
- 📧 **Email**: Contact maintainers directly for sensitive issues
- 📖 **Documentation**: Check existing docs and guides
- 💡 **Issues**: Search existing issues for similar problems

## 🏆 Recognition

Contributors will be:
- Added to the Contributors section in README
- Mentioned in release notes for significant contributions
- Invited to join the maintainers team for consistent contributors

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to MR Bot! Your efforts help make this project better for everyone. 🚀
