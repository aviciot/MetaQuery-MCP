#!/usr/bin/env node

/**
 * MCP HTTP-to-STDIO Proxy
 * Bridges Claude Desktop (stdio) with remote HTTP MCP server
 */

const https = require('http');
const readline = require('readline');

const MCP_SERVER_URL = process.env.MCP_SERVER_URL;
const MCP_AUTH_TOKEN = process.env.MCP_AUTH_TOKEN;

if (!MCP_SERVER_URL) {
  console.error('Error: MCP_SERVER_URL environment variable is required');
  process.exit(1);
}

// Setup readline interface for stdin/stdout
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Forward messages from Claude Desktop (stdin) to remote MCP server
rl.on('line', async (line) => {
  try {
    const message = JSON.parse(line);
    
    // Send request to remote MCP server
    const response = await fetch(MCP_SERVER_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(MCP_AUTH_TOKEN ? { 'Authorization': `Bearer ${MCP_AUTH_TOKEN}` } : {})
      },
      body: JSON.stringify(message)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    
    // Send response back to Claude Desktop (stdout)
    console.log(JSON.stringify(result));
    
  } catch (error) {
    // Send error response back to Claude Desktop
    const errorResponse = {
      jsonrpc: '2.0',
      id: null,
      error: {
        code: -32603,
        message: error.message
      }
    };
    console.log(JSON.stringify(errorResponse));
  }
});

// Handle process termination
process.on('SIGINT', () => {
  process.exit(0);
});

process.on('SIGTERM', () => {
  process.exit(0);
});
