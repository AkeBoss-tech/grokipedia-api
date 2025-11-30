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
    console.log('4. Searching for "machine learning" (first 3 results)...');
    const pages = await client.searchPages('machine learning', 3);
    pages.forEach((page, index) => {
      console.log(`   ${index + 1}. ${page.title}`);
      console.log(`      Relevance: ${page.relevanceScore || 'N/A'}`);
    });

    // 4. Get edit history for a page
    console.log('\n5. Getting edit history for "United_States"...');
    const editHistory = await client.listEditRequestsBySlug('United_States', 5);
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


