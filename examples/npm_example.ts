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
    console.log('3. Searching for "machine learning" (first 3 results)...');
    const pages = await client.searchPages('machine learning', 3);
    pages.forEach((page, index) => {
      console.log(`   ${index + 1}. ${page.title}`);
      console.log(`      Relevance: ${page.relevanceScore || 'N/A'}`);
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


