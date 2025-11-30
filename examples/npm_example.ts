/**
 * Example: Using Grokipedia API (TypeScript)
 * 
 * This example demonstrates how to use the Grokipedia API client in TypeScript.
 * 
 * Install with: npm install grokipedia-api
 * Compile with: tsc examples/npm_example.ts
 * Run with: node examples/npm_example.js
 */

import {
  GrokipediaClient,
  GrokipediaNotFoundError,
  GrokipediaRateLimitError,
  SearchResponse,
  PageResponse,
  EditHistoryResponse,
} from '../src/index';

async function main(): Promise<void> {
  console.log('Grokipedia API Example (TypeScript)\n');

  // Create a client with TypeScript types
  const client = new GrokipediaClient({
    useCache: true,
    timeout: 30000,
  });

  try {
    // 1. Search for articles
    console.log('1. Searching for "Python programming"...');
    const searchResults: SearchResponse = await client.search(
      'Python programming',
      5
    );
    console.log(`   Found ${searchResults.results.length} results\n`);

    searchResults.results.forEach((result, index) => {
      console.log(`   ${index + 1}. ${result.title}`);
      console.log(`      Slug: ${result.slug}`);
      console.log(`      Views: ${result.viewCount || 'N/A'}`);
      console.log(
        `      Snippet: ${result.snippet.substring(0, 100)}...\n`
      );
    });

    // 2. Get a specific page
    console.log('2. Getting page "United_Petroleum"...');
    const page: PageResponse = await client.getPage('United_Petroleum', true);
    console.log(`   Title: ${page.page.title}`);
    console.log(`   Description: ${page.page.description || 'N/A'}`);
    console.log(`   Content length: ${page.page.content.length} characters`);
    console.log(`   Citations: ${page.page.citations?.length || 0}`);
    console.log(`   Images: ${page.page.images?.length || 0}\n`);

    // 3. Access page metadata
    if (page.page.metadata) {
      console.log('   Metadata:');
      console.log(`      Categories: ${page.page.metadata.categories?.join(', ') || 'None'}`);
      console.log(`      Language: ${page.page.metadata.language || 'N/A'}`);
      console.log(`      Last Modified: ${page.page.metadata.lastModified || 'N/A'}\n`);
    }

    // 4. Search pages (returns just results array)
    console.log('4. Searching for "machine learning" (first 3 results)...');
    const pages = await client.searchPages('machine learning', 3);
    pages.forEach((page, index) => {
      console.log(`   ${index + 1}. ${page.title}`);
      console.log(`      Relevance: ${page.relevanceScore || 'N/A'}`);
    });

    // 5. Get edit history for a page
    console.log('\n5. Getting edit history for "United_States"...');
    const editHistory: EditHistoryResponse = await client.listEditRequestsBySlug(
      'United_States',
      5
    );
    console.log(`   Total edit requests: ${editHistory.totalCount}`);
    console.log(`   Has more: ${editHistory.hasMore}`);
    console.log(`   Showing first ${editHistory.editRequests.length} requests:\n`);
    editHistory.editRequests.forEach((editRequest, index) => {
      console.log(`   ${index + 1}. Status: ${editRequest.status}`);
      console.log(`      Summary: ${editRequest.summary}`);
      console.log(`      Type: ${editRequest.type}`);
      console.log(`      Section: ${editRequest.sectionTitle}`);
      console.log(`      Created: ${editRequest.createdAt}\n`);
    });

    console.log('\n✓ Example completed successfully!');
  } catch (error) {
    if (error instanceof GrokipediaNotFoundError) {
      console.error('Error: The requested resource was not found.');
    } else if (error instanceof GrokipediaRateLimitError) {
      console.error('Error: Rate limit exceeded. Please try again later.');
    } else {
      console.error('Error:', (error as Error).message);
    }
  } finally {
    // Clean up
    client.close();
  }
}

// Run the example
if (require.main === module) {
  main().catch(console.error);
}

export { main };


