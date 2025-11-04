/**
 * Browser-specific tests for GrokipediaClient
 * Tests that the client works correctly in browser environments
 * Note: These are structural tests. Integration tests with actual API calls
 * are in client.test.ts (which runs in Node.js environment)
 */

import { GrokipediaClient } from './client';
import {
  GrokipediaError,
  GrokipediaNotFoundError,
  GrokipediaAPIError,
  GrokipediaRateLimitError,
} from './exceptions';

describe('GrokipediaClient (Browser)', () => {
  let client: GrokipediaClient;

  beforeEach(() => {
    // Verify we're in a browser-like environment
    expect(typeof window).toBe('object');
    
    client = new GrokipediaClient({
      useCache: false,
      timeout: 30000,
    });
  });

  afterEach(() => {
    if (client) {
      client.close();
    }
  });

  describe('Browser Environment', () => {
    it('should work in browser environment', () => {
      expect(client).toBeInstanceOf(GrokipediaClient);
      expect(typeof client.search).toBe('function');
      expect(typeof client.getPage).toBe('function');
      expect(typeof client.searchPages).toBe('function');
      expect(typeof client.clearCache).toBe('function');
      expect(typeof client.close).toBe('function');
    });

    it('should be instantiable with browser-compatible options', () => {
      const cachedClient = new GrokipediaClient({ 
        useCache: true,
        cacheTtl: 3600,
        timeout: 10000,
      });
      expect(cachedClient).toBeInstanceOf(GrokipediaClient);
      cachedClient.close();
    });
  });

  describe('API Methods Exist', () => {
    it('should have all required methods', () => {
      expect(typeof client.search).toBe('function');
      expect(typeof client.getPage).toBe('function');
      expect(typeof client.searchPages).toBe('function');
      expect(typeof client.clearCache).toBe('function');
      expect(typeof client.close).toBe('function');
    });

    it('should handle cache operations', () => {
      const cachedClient = new GrokipediaClient({ useCache: true });
      expect(() => cachedClient.clearCache()).not.toThrow();
      cachedClient.close();
    });
  });

  describe('Error Classes in Browser', () => {
    it('should have all error classes available', () => {
      expect(GrokipediaError).toBeDefined();
      expect(GrokipediaNotFoundError).toBeDefined();
      expect(GrokipediaAPIError).toBeDefined();
      expect(GrokipediaRateLimitError).toBeDefined();
    });

    it('should create error instances correctly', () => {
      const error = new GrokipediaError('Test error');
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(GrokipediaError);
      expect(error.message).toBe('Test error');
    });
  });
});
