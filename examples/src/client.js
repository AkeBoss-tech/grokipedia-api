"use strict";
/**
 * Main client for interacting with Grokipedia API
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.GrokipediaClient = void 0;
const axios_1 = __importDefault(require("axios"));
const exceptions_1 = require("./exceptions");
/**
 * Simple in-memory cache implementation
 */
class MemoryCache {
    constructor(ttl = 604800000) {
        this.cache = new Map();
        // Default 7 days in milliseconds
        this.ttl = ttl;
    }
    get(key) {
        const item = this.cache.get(key);
        if (!item)
            return null;
        if (Date.now() > item.expires) {
            this.cache.delete(key);
            return null;
        }
        return item.data;
    }
    set(key, data) {
        this.cache.set(key, {
            data,
            expires: Date.now() + this.ttl,
        });
    }
    clear() {
        this.cache.clear();
    }
}
/**
 * Client for interacting with Grokipedia API
 */
class GrokipediaClient {
    constructor(options = {}) {
        this.cache = null;
        this.baseUrl = options.baseUrl || GrokipediaClient.BASE_URL;
        this.timeout = options.timeout || GrokipediaClient.DEFAULT_TIMEOUT;
        this.useCache = options.useCache !== false;
        this.axiosInstance = axios_1.default.create({
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
    async retry(fn, config = {
        maxAttempts: 3,
        baseDelay: 1000,
        maxDelay: 10000,
    }) {
        let lastError;
        for (let attempt = 0; attempt < config.maxAttempts; attempt++) {
            try {
                return await fn();
            }
            catch (error) {
                lastError = error;
                // Don't retry on certain errors
                if (error instanceof exceptions_1.GrokipediaNotFoundError ||
                    (error instanceof exceptions_1.GrokipediaAPIError &&
                        error.statusCode !== 429)) {
                    throw error;
                }
                // Calculate delay with exponential backoff
                if (attempt < config.maxAttempts - 1) {
                    const delay = Math.min(config.baseDelay * Math.pow(2, attempt), config.maxDelay);
                    await new Promise((resolve) => setTimeout(resolve, delay));
                }
            }
        }
        throw lastError;
    }
    /**
     * Search for articles in Grokipedia
     */
    async search(query, limit = 12, offset = 0) {
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
                const result = response.data;
                // Cache result if enabled
                if (this.useCache && this.cache) {
                    const cacheKey = `search:${query}:${limit}:${offset}`;
                    this.cache.set(cacheKey, result);
                }
                return result;
            }
            catch (error) {
                // If it's already a Grokipedia error, re-throw it
                if (error instanceof exceptions_1.GrokipediaError ||
                    error instanceof exceptions_1.GrokipediaNotFoundError ||
                    error instanceof exceptions_1.GrokipediaAPIError ||
                    error instanceof exceptions_1.GrokipediaRateLimitError) {
                    throw error;
                }
                this.handleError(error, "search");
                throw error;
            }
        });
    }
    /**
     * Get a specific page by its slug
     */
    async getPage(slug, includeContent = true, validateLinks = true) {
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
                const data = response.data;
                if (!data.found) {
                    throw new exceptions_1.GrokipediaNotFoundError(`Page not found: ${slug}`);
                }
                // Cache result if enabled
                if (this.useCache && this.cache) {
                    const cacheKey = `page:${slug}:${includeContent}:${validateLinks}`;
                    this.cache.set(cacheKey, data);
                }
                return data;
            }
            catch (error) {
                // If it's already a Grokipedia error, re-throw it
                if (error instanceof exceptions_1.GrokipediaError ||
                    error instanceof exceptions_1.GrokipediaNotFoundError ||
                    error instanceof exceptions_1.GrokipediaAPIError ||
                    error instanceof exceptions_1.GrokipediaRateLimitError) {
                    throw error;
                }
                this.handleError(error, "getPage", slug);
                throw error;
            }
        });
    }
    /**
     * Search for pages and return results as a list
     */
    async searchPages(query, limit = 12) {
        const results = await this.search(query, limit);
        return results.results || [];
    }
    /**
     * List edit requests for a specific page by its slug
     */
    async listEditRequestsBySlug(slug, limit = 10, offset = 0) {
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
                const response = await this.axiosInstance.get("/api/list-edit-requests-by-slug", {
                    params: {
                        slug,
                        limit,
                        offset,
                    },
                });
                const result = response.data;
                // Cache result if enabled
                if (this.useCache && this.cache) {
                    const cacheKey = `edit_requests:${slug}:${limit}:${offset}`;
                    this.cache.set(cacheKey, result);
                }
                return result;
            }
            catch (error) {
                // If it's already a Grokipedia error, re-throw it
                if (error instanceof exceptions_1.GrokipediaError ||
                    error instanceof exceptions_1.GrokipediaNotFoundError ||
                    error instanceof exceptions_1.GrokipediaAPIError ||
                    error instanceof exceptions_1.GrokipediaRateLimitError) {
                    throw error;
                }
                this.handleError(error, "listEditRequestsBySlug", slug);
                throw error;
            }
        });
    }
    /**
     * Handle API errors
     */
    handleError(error, operation, slug) {
        if (error.response) {
            const status = error.response.status;
            if (status === 404) {
                if (slug) {
                    throw new exceptions_1.GrokipediaNotFoundError(`Page not found: ${slug}`);
                }
                else {
                    throw new exceptions_1.GrokipediaNotFoundError(`${operation} endpoint not found: ${error.message}`);
                }
            }
            if (status === 429) {
                throw new exceptions_1.GrokipediaRateLimitError("Rate limit exceeded");
            }
            throw new exceptions_1.GrokipediaAPIError(`API error during ${operation}: ${error.message}`);
        }
        if (error.request) {
            throw new exceptions_1.GrokipediaError(`Request error during ${operation}: ${error.message}`);
        }
        throw new exceptions_1.GrokipediaError(`Error during ${operation}: ${error.message}`);
    }
    /**
     * Clear the cache
     */
    clearCache() {
        if (this.cache) {
            this.cache.clear();
        }
    }
    /**
     * Close the client (cleanup)
     */
    close() {
        // Axios doesn't require explicit cleanup, but we can clear cache
        this.clearCache();
    }
}
exports.GrokipediaClient = GrokipediaClient;
GrokipediaClient.BASE_URL = "https://grokipedia.com";
GrokipediaClient.DEFAULT_TIMEOUT = 30000; // 30 seconds
