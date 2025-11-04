/**
 * Tests to verify builds work correctly
 * Tests both Node.js and browser build imports
 */

describe('Build Verification', () => {
  describe('Node.js Build', () => {
    it('should import CommonJS build', () => {
      // This test runs in Node.js environment
      expect(typeof require).toBe('function');
      
      // Test that we can import the built module
      const { GrokipediaClient } = require('../dist/index.js');
      expect(GrokipediaClient).toBeDefined();
      expect(typeof GrokipediaClient).toBe('function');
    });

    it('should have all exports in CommonJS build', () => {
      const module = require('../dist/index.js');
      
      expect(module.GrokipediaClient).toBeDefined();
      expect(module.GrokipediaError).toBeDefined();
      expect(module.GrokipediaNotFoundError).toBeDefined();
      expect(module.GrokipediaAPIError).toBeDefined();
      expect(module.GrokipediaRateLimitError).toBeDefined();
      
      // Test default export
      expect(module.default).toBeDefined();
    });
  });

  describe('Browser ESM Build', () => {
    it('should have browser ESM build files', () => {
      const fs = require('fs');
      const path = require('path');
      
      const esmPath = path.join(__dirname, '../dist/browser/grokipedia-api.esm.js');
      const umdPath = path.join(__dirname, '../dist/browser/grokipedia-api.umd.js');
      
      expect(fs.existsSync(esmPath)).toBe(true);
      expect(fs.existsSync(umdPath)).toBe(true);
    });

    it('should have source maps for browser builds', () => {
      const fs = require('fs');
      const path = require('path');
      
      const esmMapPath = path.join(__dirname, '../dist/browser/grokipedia-api.esm.js.map');
      const umdMapPath = path.join(__dirname, '../dist/browser/grokipedia-api.umd.js.map');
      
      expect(fs.existsSync(esmMapPath)).toBe(true);
      expect(fs.existsSync(umdMapPath)).toBe(true);
    });

    it('should have correct file sizes (not empty)', () => {
      const fs = require('fs');
      const path = require('path');
      
      const esmPath = path.join(__dirname, '../dist/browser/grokipedia-api.esm.js');
      const umdPath = path.join(__dirname, '../dist/browser/grokipedia-api.umd.js');
      
      const esmStats = fs.statSync(esmPath);
      const umdStats = fs.statSync(umdPath);
      
      // Files should not be empty
      expect(esmStats.size).toBeGreaterThan(1000); // At least 1KB
      expect(umdStats.size).toBeGreaterThan(10000); // UMD includes axios, so larger
    });
  });

  describe('TypeScript Definitions', () => {
    it('should have TypeScript definition files', () => {
      const fs = require('fs');
      const path = require('path');
      
      const indexDts = path.join(__dirname, '../dist/index.d.ts');
      const clientDts = path.join(__dirname, '../dist/client.d.ts');
      const typesDts = path.join(__dirname, '../dist/types.d.ts');
      
      expect(fs.existsSync(indexDts)).toBe(true);
      expect(fs.existsSync(clientDts)).toBe(true);
      expect(fs.existsSync(typesDts)).toBe(true);
    });
  });

  describe('Package.json Exports', () => {
    it('should have correct package.json exports field', () => {
      const fs = require('fs');
      const path = require('path');
      const packageJson = JSON.parse(
        fs.readFileSync(path.join(__dirname, '../package.json'), 'utf8')
      );
      
      expect(packageJson.exports).toBeDefined();
      expect(packageJson.exports['.']).toBeDefined();
      expect(packageJson.exports['.'].node).toBeDefined();
      expect(packageJson.exports['.'].browser).toBeDefined();
    });
  });
});

