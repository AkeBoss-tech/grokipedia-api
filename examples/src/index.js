"use strict";
/**
 * Grokipedia API Client for Node.js
 *
 * A client library for accessing content from Grokipedia,
 * an open-source, comprehensive collection of all knowledge.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.GrokipediaRateLimitError = exports.GrokipediaAPIError = exports.GrokipediaNotFoundError = exports.GrokipediaError = exports.GrokipediaClient = void 0;
var client_1 = require("./client");
Object.defineProperty(exports, "GrokipediaClient", { enumerable: true, get: function () { return client_1.GrokipediaClient; } });
var exceptions_1 = require("./exceptions");
Object.defineProperty(exports, "GrokipediaError", { enumerable: true, get: function () { return exceptions_1.GrokipediaError; } });
Object.defineProperty(exports, "GrokipediaNotFoundError", { enumerable: true, get: function () { return exceptions_1.GrokipediaNotFoundError; } });
Object.defineProperty(exports, "GrokipediaAPIError", { enumerable: true, get: function () { return exceptions_1.GrokipediaAPIError; } });
Object.defineProperty(exports, "GrokipediaRateLimitError", { enumerable: true, get: function () { return exceptions_1.GrokipediaRateLimitError; } });
// Default export for convenience
const client_2 = require("./client");
exports.default = client_2.GrokipediaClient;
