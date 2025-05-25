# Contributing to GitHub Sponsors Webhook Bot

Thank you for considering contributing to the GitHub Sponsors Webhook Bot! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others when contributing.

## How to Contribute

There are many ways to contribute to this project:

1. **Reporting Bugs**: If you find a bug, please create an issue with a detailed description of the problem, steps to reproduce, and your environment.
2. **Suggesting Enhancements**: Have an idea for a new feature or improvement? Create an issue with the tag "enhancement" and describe your suggestion.
3. **Code Contributions**: Want to fix a bug or implement a feature? Follow the steps below.

## Development Process

1. **Fork the Repository**: Create your own fork of the repository.
2. **Create a Branch**: Create a branch for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**: Implement your changes, following the coding standards below.
4. **Write Tests**: Add tests for your changes to ensure they work as expected.
5. **Run Tests**: Make sure all tests pass.
   ```bash
   pytest
   ```
6. **Commit Changes**: Commit your changes with a clear and descriptive commit message.
   ```bash
   git commit -m "Add feature: your feature description"
   ```
7. **Push Changes**: Push your changes to your fork.
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**: Submit a pull request from your fork to the main repository.

## Coding Standards

- Follow PEP 8 style guidelines for Python code.
- Write clear, descriptive comments and docstrings.
- Keep functions and methods focused on a single responsibility.
- Add type hints where appropriate.
- Maintain test coverage for new code.

## Pull Request Guidelines

- Provide a clear description of the changes in your pull request.
- Link to any related issues.
- Include screenshots or examples if applicable.
- Make sure all tests pass.
- Keep pull requests focused on a single change or feature.

## Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/overspend1/github-sponsors-webhook-bot.git
   cd github-sponsors-webhook-bot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. Create a `.env` file with your development credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. Run the bot locally:
   ```bash
   python github_sponsors_bot.py
   ```

## Testing

- Write unit tests for new functionality.
- Run tests with pytest:
  ```bash
  pytest
  ```
- For webhook testing, use the provided `test_webhook.py` script.

## Documentation

- Update documentation for any changes to functionality.
- Document new features, configuration options, or behavior changes.
- Keep the README up to date.

## Questions?

If you have any questions about contributing, please create an issue with the tag "question".

Thank you for your contributions!