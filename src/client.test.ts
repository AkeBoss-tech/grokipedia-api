/**
 * Basic tests for GrokipediaClient
 */

import { GrokipediaClient } from './client';
import {
  GrokipediaError,
  GrokipediaNotFoundError,
  GrokipediaAPIError,
  GrokipediaRateLimitError,
} from './exceptions';

describe('GrokipediaClient', () => {
  let client: GrokipediaClient;

  beforeEach(() => {
    client = new GrokipediaClient({
      useCache: false, // Disable cache for tests
      timeout: 30000,
    });
  });

  afterEach(() => {
    client.close();
  });

  describe('Initialization', () => {
    it('should create a client with default options', () => {
      const defaultClient = new GrokipediaClient();
      expect(defaultClient).toBeInstanceOf(GrokipediaClient);
      defaultClient.close();
    });

    it('should create a client with custom options', () => {
      const customClient = new GrokipediaClient({
        baseUrl: 'https://grokipedia.com',
        timeout: 10000,
        useCache: true,
        cacheTtl: 3600,
      });
      expect(customClient).toBeInstanceOf(GrokipediaClient);
      customClient.close();
    });
  });

  describe('Search', () => {
    it('should search for articles', async () => {
      const results = await client.search('Python', 3);
      expect(results).toHaveProperty('results');
      expect(Array.isArray(results.results)).toBe(true);
      expect(results.results.length).toBeGreaterThan(0);
    }, 30000);

    it('should return search results with correct structure', async () => {
      const results = await client.search('Python', 1);
      if (results.results.length > 0) {
        const result = results.results[0];
        expect(result).toHaveProperty('title');
        expect(result).toHaveProperty('slug');
        expect(typeof result.title).toBe('string');
        expect(typeof result.slug).toBe('string');
      }
    }, 30000);
  });

  describe('Get Page', () => {
    it('should get a page by slug', async () => {
      const page = await client.getPage('Python_(programming_language)', true);
      expect(page).toHaveProperty('page');
      expect(page).toHaveProperty('found');
      expect(page.found).toBe(true);
      expect(page.page).toHaveProperty('title');
      expect(page.page).toHaveProperty('slug');
    }, 30000);

    it('should throw NotFoundError for non-existent page', async () => {
      await expect(
        client.getPage('NonExistentPage_12345', true)
      ).rejects.toThrow(GrokipediaNotFoundError);
    }, 30000);
  });

  describe('Search Pages', () => {
    it('should return array of search results', async () => {
      const pages = await client.searchPages('Python', 3);
      expect(Array.isArray(pages)).toBe(true);
      expect(pages.length).toBeGreaterThan(0);
      if (pages.length > 0) {
        expect(pages[0]).toHaveProperty('title');
        expect(pages[0]).toHaveProperty('slug');
      }
    }, 30000);
  });

  describe('List Edit Requests', () => {
    it('should list edit requests for a page', async () => {
      const editHistory = await client.listEditRequestsBySlug('United_States', 5);
      expect(editHistory).toHaveProperty('editRequests');
      expect(editHistory).toHaveProperty('totalCount');
      expect(editHistory).toHaveProperty('hasMore');
      expect(Array.isArray(editHistory.editRequests)).toBe(true);
      expect(typeof editHistory.totalCount).toBe('number');
      expect(typeof editHistory.hasMore).toBe('boolean');
    }, 30000);

    it('should return edit requests with correct structure', async () => {
      const editHistory = await client.listEditRequestsBySlug('United_States', 1);
      if (editHistory.editRequests.length > 0) {
        const editRequest = editHistory.editRequests[0];
        expect(editRequest).toHaveProperty('id');
        expect(editRequest).toHaveProperty('slug');
        expect(editRequest).toHaveProperty('status');
        expect(editRequest).toHaveProperty('summary');
        expect(typeof editRequest.id).toBe('string');
        expect(typeof editRequest.slug).toBe('string');
      }
    }, 30000);
  });

  describe('Cache Management', () => {
    it('should clear cache', () => {
      const cachedClient = new GrokipediaClient({ useCache: true });
      expect(() => cachedClient.clearCache()).not.toThrow();
      cachedClient.close();
    });
  });
});

describe('Error Classes', () => {
  it('GrokipediaError should be instance of Error', () => {
    const error = new GrokipediaError('Test error');
    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(GrokipediaError);
    expect(error.message).toBe('Test error');
  });

  it('GrokipediaNotFoundError should be instance of GrokipediaError', () => {
    const error = new GrokipediaNotFoundError('Not found');
    expect(error).toBeInstanceOf(GrokipediaError);
    expect(error).toBeInstanceOf(GrokipediaNotFoundError);
    expect(error.message).toBe('Not found');
  });

  it('GrokipediaAPIError should be instance of GrokipediaError', () => {
    const error = new GrokipediaAPIError('API error');
    expect(error).toBeInstanceOf(GrokipediaError);
    expect(error).toBeInstanceOf(GrokipediaAPIError);
    expect(error.message).toBe('API error');
  });

  it('GrokipediaRateLimitError should be instance of GrokipediaError', () => {
    const error = new GrokipediaRateLimitError('Rate limit');
    expect(error).toBeInstanceOf(GrokipediaError);
    expect(error).toBeInstanceOf(GrokipediaRateLimitError);
    expect(error.message).toBe('Rate limit');
  });
});

