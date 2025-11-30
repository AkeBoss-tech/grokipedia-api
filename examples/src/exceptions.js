"use strict";
/**
 * Custom exceptions for Grokipedia API
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.GrokipediaRateLimitError = exports.GrokipediaAPIError = exports.GrokipediaNotFoundError = exports.GrokipediaError = void 0;
class GrokipediaError extends Error {
    constructor(message) {
        super(message);
        this.name = "GrokipediaError";
        Object.setPrototypeOf(this, GrokipediaError.prototype);
    }
}
exports.GrokipediaError = GrokipediaError;
class GrokipediaNotFoundError extends GrokipediaError {
    constructor(message) {
        super(message);
        this.name = "GrokipediaNotFoundError";
        Object.setPrototypeOf(this, GrokipediaNotFoundError.prototype);
    }
}
exports.GrokipediaNotFoundError = GrokipediaNotFoundError;
class GrokipediaAPIError extends GrokipediaError {
    constructor(message) {
        super(message);
        this.name = "GrokipediaAPIError";
        Object.setPrototypeOf(this, GrokipediaAPIError.prototype);
    }
}
exports.GrokipediaAPIError = GrokipediaAPIError;
class GrokipediaRateLimitError extends GrokipediaError {
    constructor(message = "Rate limit exceeded") {
        super(message);
        this.name = "GrokipediaRateLimitError";
        Object.setPrototypeOf(this, GrokipediaRateLimitError.prototype);
    }
}
exports.GrokipediaRateLimitError = GrokipediaRateLimitError;
