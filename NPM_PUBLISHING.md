# Publishing the npm Package

This guide explains how to publish the Node.js/npm version of `grokipedia-api` to npm.

## Prerequisites

1. **Node.js and npm**: Install Node.js 14+ (which includes npm)
   ```bash
   node --version  # Should be 14.0.0 or higher
   npm --version
   ```

2. **npm Account**: Create an account at [npmjs.com](https://www.npmjs.com/signup)

3. **Login to npm**:
   ```bash
   npm login
   ```

## Project Structure

This repository contains both:
- **Python package** (`grokipedia_api/`) - Published to PyPI
- **Node.js/TypeScript package** (`src/`) - Published to npm

Both packages share:
- Same API endpoints
- Same functionality
- Same documentation structure
- Same version numbering (recommended)

## Building the Package

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build TypeScript**:
   ```bash
   npm run build
   ```
   This compiles TypeScript from `src/` to JavaScript in `dist/`

3. **Verify build**:
   ```bash
   ls dist/
   # Should see: index.js, index.d.ts, client.js, client.d.ts, etc.
   ```

## Testing Before Publishing

1. **Test locally**:
   ```bash
   npm link
   ```

2. **In another project, link it**:
   ```bash
   cd /path/to/test-project
   npm link grokipedia-api
   ```

3. **Test the package**:
   ```javascript
   const { GrokipediaClient } = require('grokipedia-api');
   const client = new GrokipediaClient();
   // ... test your code
   ```

4. **Unlink when done**:
   ```bash
   npm unlink grokipedia-api
   ```

## Publishing to npm

### First Time Publishing

1. **Check package.json**:
   - Ensure `name` is available (check npm registry)
   - Verify `version` is correct
   - Review `description`, `keywords`, `author`

2. **Verify files to publish**:
   ```bash
   npm pack --dry-run
   ```
   This shows what will be included in the package.

3. **Publish**:
   ```bash
   npm publish
   ```

### Updating the Package

1. **Update version** (follow semantic versioning):
   ```bash
   npm version patch  # 0.1.0 -> 0.1.1 (bug fixes)
   npm version minor  # 0.1.0 -> 0.2.0 (new features)
   npm version major  # 0.1.0 -> 1.0.0 (breaking changes)
   ```
   Or manually edit `package.json` and run `npm version`

2. **Build**:
   ```bash
   npm run build
   ```

3. **Publish**:
   ```bash
   npm publish
   ```

## Version Synchronization

**Recommendation**: Keep Python and npm package versions in sync:

- Update both `package.json` and `pyproject.toml` when releasing
- Use the same version number for both packages
- Update both READMEs if needed

## Best Practices

### 1. Separate READMEs

- **Python**: `README.md` (for PyPI)
- **Node.js**: `README_NPM.md` (copy to `README.md` before npm publish, or use npm scripts)

### 2. Publishing Workflow

Create a script to publish both:

```bash
#!/bin/bash
# publish-both.sh

# Publish Python package
python -m build
twine upload dist/*

# Publish npm package
npm run build
npm publish

# Restore original README if needed
```

### 3. CI/CD Integration

Consider using GitHub Actions to automate publishing:

```yaml
# .github/workflows/publish.yml
name: Publish Packages

on:
  release:
    types: [created]

jobs:
  publish-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*

  publish-npm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run build
      - run: npm publish
```

## Troubleshooting

### "Package name already exists"
- Check if the name is taken: https://www.npmjs.com/package/grokipedia-api
- Use a scoped package: `@akeboss-tech/grokipedia-api`
- Update `package.json` with the scoped name

### "You must verify your email"
- Check your npm account email
- Verify email address

### "Insufficient permissions"
- Check you're logged in: `npm whoami`
- Verify package ownership or use a scoped package

### Build Errors
- Ensure TypeScript is installed: `npm install typescript -g`
- Check `tsconfig.json` configuration
- Verify all dependencies are installed

## Package Verification

After publishing, verify:

1. **Check npm registry**:
   ```bash
   npm view grokipedia-api
   ```

2. **Install and test**:
   ```bash
   npm install grokipedia-api
   node -e "const {GrokipediaClient} = require('grokipedia-api'); console.log('OK');"
   ```

3. **Check package contents**:
   ```bash
   npm pack grokipedia-api
   tar -tzf grokipedia-api-*.tgz | head -20
   ```

## Unpublishing

⚠️ **Only unpublish within 72 hours of publishing**

```bash
npm unpublish grokipedia-api@0.1.0
# Or unpublish entire package (use with caution)
npm unpublish grokipedia-api --force
```

## Related Documentation

- [npm Publishing Guide](https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry)
- [Semantic Versioning](https://semver.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)


