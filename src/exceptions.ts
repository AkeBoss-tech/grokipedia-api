/**
 * Custom exceptions for Grokipedia API
 */

export class GrokipediaError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "GrokipediaError";
    Object.setPrototypeOf(this, GrokipediaError.prototype);
  }
}

export class GrokipediaNotFoundError extends GrokipediaError {
  constructor(message: string) {
    super(message);
    this.name = "GrokipediaNotFoundError";
    Object.setPrototypeOf(this, GrokipediaNotFoundError.prototype);
  }
}

export class GrokipediaAPIError extends GrokipediaError {
  constructor(message: string) {
    super(message);
    this.name = "GrokipediaAPIError";
    Object.setPrototypeOf(this, GrokipediaAPIError.prototype);
  }
}

export class GrokipediaRateLimitError extends GrokipediaError {
  constructor(message: string = "Rate limit exceeded") {
    super(message);
    this.name = "GrokipediaRateLimitError";
    Object.setPrototypeOf(this, GrokipediaRateLimitError.prototype);
  }
}
