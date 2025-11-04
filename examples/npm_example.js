#!/usr/bin/env node
/**
 * Example: Using Grokipedia API (Node.js)
 * 
 * This example demonstrates how to use the Grokipedia API client in Node.js.
 * 
 * Install with: npm install grokipedia-api
 */

// Use local build for testing, or 'grokipedia-api' when published
const { GrokipediaClient } = require('../dist/index.js');

async function main() {
  console.log('Grokipedia API Example\n');
  
  // Create a client
  const client = new GrokipediaClient({
    useCache: true,
    timeout: 30000,
  });

  try {
    // 1. Search for articles
    console.log('1. Searching for "Python programming"...');
    const searchResults = await client.search('Python programming', 5);
    console.log(`   Found ${searchResults.results.length} results\n`);
    
    searchResults.results.forEach((result, index) => {
      console.log(`   ${index + 1}. ${result.title}`);
      console.log(`      Slug: ${result.slug}`);
      console.log(`      Views: ${result.viewCount || 'N/A'}`);
      console.log(`      Snippet: ${result.snippet.substring(0, 100)}...\n`);
    });

    // 2. Get a specific page
    console.log('2. Getting page "United_Petroleum"...');
    const page = await client.getPage('United_Petroleum', true);
    console.log(`   Title: ${page.page.title}`);
    console.log(`   Description: ${page.page.description || 'N/A'}`);
    console.log(`   Content length: ${page.page.content.length} characters`);
    console.log(`   Citations: ${page.page.citations?.length || 0}`);
    console.log(`   Images: ${page.page.images?.length || 0}\n`);

    // 3. Search pages (returns just results array)
    console.log('3. Searching for "machine learning" (first 3 results)...');
    const pages = await client.searchPages('machine learning', 3);
    pages.forEach((page, index) => {
      console.log(`   ${index + 1}. ${page.title}`);
      console.log(`      Relevance: ${page.relevanceScore || 'N/A'}`);
    });

    console.log('\n✓ Example completed successfully!');
  } catch (error) {
    console.error('Error:', error.message);
    if (error.name === 'GrokipediaNotFoundError') {
      console.error('The requested resource was not found.');
    } else if (error.name === 'GrokipediaRateLimitError') {
      console.error('Rate limit exceeded. Please try again later.');
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

module.exports = { main };


