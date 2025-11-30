/**
 * Main client for interacting with Grokipedia API
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import {
  SearchResponse,
  PageResponse,
  SearchResult,
  ClientOptions,
  EditHistoryResponse,
} from "./types";
import {
  GrokipediaError,
  GrokipediaNotFoundError,
  GrokipediaAPIError,
  GrokipediaRateLimitError,
} from "./exceptions";

/**
 * Simple in-memory cache implementation
 */
class MemoryCache {
  private cache: Map<string, { data: any; expires: number }> = new Map();
  private ttl: number;

  constructor(ttl: number = 604800000) {
    // Default 7 days in milliseconds
    this.ttl = ttl;
  }

  get(key: string): any | null {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() > item.expires) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  set(key: string, data: any): void {
    this.cache.set(key, {
      data,
      expires: Date.now() + this.ttl,
    });
  }

  clear(): void {
    this.cache.clear();
  }
}

/**
 * Retry configuration for requests
 */
interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
}

/**
 * Client for interacting with Grokipedia API
 */
export class GrokipediaClient {
  private baseUrl: string;
  private timeout: number;
  private axiosInstance: AxiosInstance;
  private useCache: boolean;
  private cache: MemoryCache | null = null;

  static readonly BASE_URL = "https://grokipedia.com";
  static readonly DEFAULT_TIMEOUT = 30000; // 30 seconds

  constructor(options: ClientOptions = {}) {
    this.baseUrl = options.baseUrl || GrokipediaClient.BASE_URL;
    this.timeout = options.timeout || GrokipediaClient.DEFAULT_TIMEOUT;
    this.useCache = options.useCache !== false;

    this.axiosInstance = axios.create({
      baseURL: this.baseUrl,
      timeout: this.timeout,
      headers: {
        "User-Agent": "grokipedia-api/0.1.0",
        Accept: "application/json",
      },
    });

    if (this.useCache) {
      const cacheTtl = (options.cacheTtl || 604800) * 1000; // Convert to milliseconds
      this.cache = new MemoryCache(cacheTtl);
    }
  }

  /**
   * Retry logic with exponential backoff
   */
  private async retry<T>(
    fn: () => Promise<T>,
    config: RetryConfig = {
      maxAttempts: 3,
      baseDelay: 1000,
      maxDelay: 10000,
    },
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 0; attempt < config.maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // Don't retry on certain errors
        if (
          error instanceof GrokipediaNotFoundError ||
          (error instanceof GrokipediaAPIError &&
            (error as any).statusCode !== 429)
        ) {
          throw error;
        }

        // Calculate delay with exponential backoff
        if (attempt < config.maxAttempts - 1) {
          const delay = Math.min(
            config.baseDelay * Math.pow(2, attempt),
            config.maxDelay,
          );
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError!;
  }

  /**
   * Search for articles in Grokipedia
   */
  async search(
    query: string,
    limit: number = 12,
    offset: number = 0,
  ): Promise<SearchResponse> {
    return this.retry(async () => {
      // Try cache first if enabled
      if (this.useCache && this.cache) {
        const cacheKey = `search:${query}:${limit}:${offset}`;
        const cached = this.cache.get(cacheKey);
        if (cached !== null) {
          return cached;
        }
      }

      try {
        const response = await this.axiosInstance.get("/api/full-text-search", {
          params: {
            query,
            limit,
            offset,
          },
        });

        const result: SearchResponse = response.data;

        // Cache result if enabled
        if (this.useCache && this.cache) {
          const cacheKey = `search:${query}:${limit}:${offset}`;
          this.cache.set(cacheKey, result);
        }

        return result;
      } catch (error) {
        // If it's already a Grokipedia error, re-throw it
        if (
          error instanceof GrokipediaError ||
          error instanceof GrokipediaNotFoundError ||
          error instanceof GrokipediaAPIError ||
          error instanceof GrokipediaRateLimitError
        ) {
          throw error;
        }
        this.handleError(error as AxiosError, "search");
        throw error;
      }
    });
  }

  /**
   * Get a specific page by its slug
   */
  async getPage(
    slug: string,
    includeContent: boolean = true,
    validateLinks: boolean = true,
  ): Promise<PageResponse> {
    return this.retry(async () => {
      // Try cache first if enabled
      if (this.useCache && this.cache) {
        const cacheKey = `page:${slug}:${includeContent}:${validateLinks}`;
        const cached = this.cache.get(cacheKey);
        if (cached !== null) {
          return cached;
        }
      }

      try {
        const response = await this.axiosInstance.get("/api/page", {
          params: {
            slug,
            includeContent: includeContent.toString().toLowerCase(),
            validateLinks: validateLinks.toString().toLowerCase(),
          },
        });

        const data: PageResponse = response.data;

        if (!data.found) {
          throw new GrokipediaNotFoundError(`Page not found: ${slug}`);
        }

        // Cache result if enabled
        if (this.useCache && this.cache) {
          const cacheKey = `page:${slug}:${includeContent}:${validateLinks}`;
          this.cache.set(cacheKey, data);
        }

        return data;
      } catch (error) {
        // If it's already a Grokipedia error, re-throw it
        if (
          error instanceof GrokipediaError ||
          error instanceof GrokipediaNotFoundError ||
          error instanceof GrokipediaAPIError ||
          error instanceof GrokipediaRateLimitError
        ) {
          throw error;
        }
        this.handleError(error as AxiosError, "getPage", slug);
        throw error;
      }
    });
  }

  /**
   * Search for pages and return results as a list
   */
  async searchPages(
    query: string,
    limit: number = 12,
  ): Promise<SearchResult[]> {
    const results = await this.search(query, limit);
    return results.results || [];
  }

  /**
   * List edit requests for a specific page by its slug
   */
  async listEditRequestsBySlug(
    slug: string,
    limit: number = 10,
    offset: number = 0,
  ): Promise<EditHistoryResponse> {
    return this.retry(async () => {
      // Try cache first if enabled
      if (this.useCache && this.cache) {
        const cacheKey = `edit_requests:${slug}:${limit}:${offset}`;
        const cached = this.cache.get(cacheKey);
        if (cached !== null) {
          return cached;
        }
      }

      try {
        const response = await this.axiosInstance.get(
          "/api/list-edit-requests-by-slug",
          {
            params: {
              slug,
              limit,
              offset,
            },
          },
        );

        const result: EditHistoryResponse = response.data;

        // Cache result if enabled
        if (this.useCache && this.cache) {
          const cacheKey = `edit_requests:${slug}:${limit}:${offset}`;
          this.cache.set(cacheKey, result);
        }

        return result;
      } catch (error) {
        // If it's already a Grokipedia error, re-throw it
        if (
          error instanceof GrokipediaError ||
          error instanceof GrokipediaNotFoundError ||
          error instanceof GrokipediaAPIError ||
          error instanceof GrokipediaRateLimitError
        ) {
          throw error;
        }
        this.handleError(error as AxiosError, "listEditRequestsBySlug", slug);
        throw error;
      }
    });
  }

  /**
   * Handle API errors
   */
  private handleError(
    error: AxiosError,
    operation: string,
    slug?: string,
  ): void {
    if (error.response) {
      const status = error.response.status;

      if (status === 404) {
        if (slug) {
          throw new GrokipediaNotFoundError(`Page not found: ${slug}`);
        } else {
          throw new GrokipediaNotFoundError(
            `${operation} endpoint not found: ${error.message}`,
          );
        }
      }

      if (status === 429) {
        throw new GrokipediaRateLimitError("Rate limit exceeded");
      }

      throw new GrokipediaAPIError(
        `API error during ${operation}: ${error.message}`,
      );
    }

    if (error.request) {
      throw new GrokipediaError(
        `Request error during ${operation}: ${error.message}`,
      );
    }

    throw new GrokipediaError(`Error during ${operation}: ${error.message}`);
  }

  /**
   * Clear the cache
   */
  clearCache(): void {
    if (this.cache) {
      this.cache.clear();
    }
  }

  /**
   * Close the client (cleanup)
   */
  close(): void {
    // Axios doesn't require explicit cleanup, but we can clear cache
    this.clearCache();
  }
}
