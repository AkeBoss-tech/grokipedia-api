/**
 * Grokipedia API Client for Node.js
 *
 * A client library for accessing content from Grokipedia,
 * an open-source, comprehensive collection of all knowledge.
 */

export { GrokipediaClient } from "./client";
export {
  GrokipediaError,
  GrokipediaNotFoundError,
  GrokipediaAPIError,
  GrokipediaRateLimitError,
} from "./exceptions";
export type {
  Citation,
  Image,
  PageMetadata,
  PageStats,
  Page,
  PageResponse,
  SearchResult,
  SearchResponse,
  ClientOptions,
  SupportingEvidence,
  EditRequest,
  EditHistoryResponse,
} from "./types";

// Default export for convenience
import { GrokipediaClient } from "./client";
export default GrokipediaClient;
