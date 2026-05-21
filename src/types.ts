/**
 * Type definitions for Grokipedia API responses
 */

export interface Citation {
  id: string;
  title: string;
  description: string;
  url: string;
  favicon?: string;
}

export interface Image {
  id: string;
  caption: string;
  url: string;
  position?: string;
  width?: number;
  height?: number;
}

export interface PageMetadata {
  categories?: string[];
  lastModified?: string;
  contentLength?: string;
  version?: string;
  lastEditor?: string;
  language?: string;
  isRedirect?: boolean;
  redirectTarget?: string;
  isWithheld?: boolean;
  creationSource?: number;
  visibility?: number;
}

export interface PageStats {
  totalViews?: string;
  recentViews?: string;
  dailyAvgViews?: number;
  qualityScore?: number;
  lastViewed?: string;
}

export interface Page {
  slug: string;
  title: string;
  content: string;
  citations?: Citation[];
  images?: Image[];
  metadata?: PageMetadata;
  stats?: PageStats;
  description?: string;
}

export interface PageResponse {
  page: Page;
  found: boolean;
}

export interface SearchResult {
  title: string;
  slug: string;
  snippet: string;
  relevanceScore?: number;
  viewCount?: string;
  titleHighlights?: string[];
  snippetHighlights?: string[];
  creationSource?: number;
  visibility?: number;
  providers?: number[];
  snippetVariants?: Array<Record<string, unknown>>;
  scrollAnchorText?: string;
}

export interface SearchResponse {
  results: SearchResult[];
  totalCount?: number;
  total_count?: number;
  searchTimeMs?: number;
  search_time_ms?: number;
  facets?: Array<Record<string, unknown>>;
}

export interface ClientOptions {
  baseUrl?: string;
  timeout?: number;
  useCache?: boolean;
  cacheTtl?: number;
}

export interface SupportingEvidence {
  url?: string;
  description?: string;
}

export interface EditRequest {
  supportingEvidence?: SupportingEvidence[];
  id: string;
  slug: string;
  userId: string;
  status: string;
  type: string | number;
  summary: string;
  originalContent: string;
  proposedContent: string;
  sectionTitle: string;
  createdAt: string | number;
  updatedAt: string | number;
  reviewedBy?: string;
  reviewedAt?: string | number;
  reviewReason?: string;
  upvoteCount: number;
  downvoteCount: number;
  userVote?: string;
  editStartHeader?: string;
  editEndHeader?: string;
}

export interface EditHistoryResponse {
  editRequests: EditRequest[];
  totalCount: number;
  hasMore: boolean;
}
