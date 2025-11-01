# Publishing to PyPI

Complete guide for publishing Grokipedia API to PyPI.

## Understanding the Error

The error you saw:
```
ERROR: Could not find a version that satisfies the requirement requests>=2.31.0
```

**What it means:** Test PyPI only has packages you explicitly upload - NOT their dependencies!

**Solution:** Use `--extra-index-url` to fallback to the main PyPI for dependencies.

## Prerequisites

1. **PyPI Account**: Create one at https://pypi.org/account/register/
2. **Test PyPI Account**: Create one at https://test.pypi.org/account/register/
3. **API Tokens**: Get tokens from:
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/

## Publishing Steps

### Step 1: Update Metadata

Before publishing, update `pyproject.toml`:

```toml
# Line 12-13: Update author info
authors = [
    {name = "Your Real Name", email = "your.real.email@example.com"}
]

# Line 46-49: Update repository URLs
[project.urls]
Homepage = "https://github.com/yourusername/grokipedia-api"
Documentation = "https://github.com/yourusername/grokipedia-api"
Repository = "https://github.com/yourusername/grokipedia-api"
Issues = "https://github.com/yourusername/grokipedia-api/issues"
```

### Step 2: Build Distribution

```bash
# Activate your development environment
cd /Users/akashdubey/Documents/CodingProjects/grokipedia-api
source venv/bin/activate

# Install build tools
pip install --upgrade build twine

# Build distribution packages
python -m build
```

This creates the following in `dist/`:
- `grokipedia_api-0.1.0-py3-none-any.whl` (wheel)
- `grokipedia_api-0.1.0.tar.gz` (source distribution)

### Step 3: Check Build

```bash
# Validate package files
twine check dist/*
```

Should output: `PASSED` for all files.

### Step 4: Upload to Test PyPI

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*
```

You'll be prompted for:
- **Username**: `__token__`
- **Password**: Your Test PyPI API token

### Step 5: Test from Test PyPI

```bash
# Create a fresh test environment
python3 -m venv test_env
source test_env/bin/activate

# Install from Test PyPI WITH fallback to main PyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            grokipedia-api

# Test it works
python -c "from grokipedia_api import GrokipediaClient; print('✓ Success!')"

# Clean up
deactivate
rm -rf test_env
```

**Important**: Always use `--extra-index-url` when testing from Test PyPI!

### Step 6: Upload to Real PyPI

Once Test PyPI test passes:

```bash
# Upload to production PyPI
twine upload dist/*

# You'll be prompted for:
# Username: __token__
# Password: Your PyPI API token
```

### Step 7: Verify on PyPI

Visit: https://pypi.org/project/grokipedia-api

Check:
- ✓ Package page loads
- ✓ Description is correct
- ✓ Installation instructions work
- ✓ All files uploaded

### Step 8: Test Installation

```bash
# Test from production PyPI
python3 -m venv verify_env
source verify_env/bin/activate

# Now this should just work
pip install grokipedia-api

# Test it
python -c "from grokipedia_api import GrokipediaClient; print('✓ Success!')"

# Clean up
deactivate
rm -rf verify_env
```

## Updating the Package

To publish a new version:

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # or 0.2.0, etc.
   ```

2. **Update CHANGELOG** (if you have one)

3. **Build and upload**:
   ```bash
   python -m build
   twine check dist/*
   twine upload dist/*
   ```

## Common Issues

### "Package already exists"

**Problem**: Version already on PyPI

**Solution**: Increment version number in `pyproject.toml`

### "Invalid token"

**Problem**: Wrong API token

**Solution**: 
- Generate a new token
- Make sure you're using `__token__` as username
- Ensure token has proper scope

### "Could not find dependency"

**Problem**: Dependencies not on Test PyPI

**Solution**: Always use `--extra-index-url https://pypi.org/simple/` when installing from Test PyPI

### "Failed to build"

**Problem**: Missing dependencies or syntax errors

**Solution**: 
```bash
# Test local install first
pip install -e .
python -c "from grokipedia_api import GrokipediaClient"
```

## Security Best Practices

1. **Never commit API tokens** to git
2. **Use API tokens** instead of passwords
3. **Enable 2FA** on your PyPI account
4. **Use Test PyPI** first to catch issues
5. **Version numbering** follows semantic versioning

## Automation (Optional)

Create a publish script:

```bash
#!/bin/bash
# scripts/publish.sh

set -e

echo "Building package..."
python -m build

echo "Checking package..."
twine check dist/*

echo "Uploading to Test PyPI..."
twine upload --repository testpypi dist/*

echo "Done! Test with:"
echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ grokipedia-api"
```

Make it executable:
```bash
chmod +x scripts/publish.sh
```

## Resources

- [PyPI Help](https://pypi.org/help/)
- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)

