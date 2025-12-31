#!/usr/bin/env python3
"""
Test script to verify MCP server connectivity using httpx directly.
Tests remote MCP server with SSE.
"""
import asyncio
import sys
import httpx
import json


async def test_remote_mcp(url: str, api_key: str):
    """Test remote MCP server via direct HTTP request"""
    print(f"\n{'='*60}")
    print(f"Testing Remote MCP Server: {url}")
    print(f"{'='*60}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test 1: Health check
            health_response = await client.get(
                url.replace("/mcp", "/healthz"),
                headers={"Authorization": f"Bearer {api_key}"}
            )
            print(f"✅ Health check: {health_response.status_code} - {health_response.text}")
            
            # Test 2: Try to connect to MCP endpoint
            print(f"\n🔌 Attempting SSE connection to {url}...")
            
            async with client.stream('GET', url, headers=headers) as response:
                print(f"   Response status: {response.status_code}")
                print(f"   Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    print("✅ Connection successful!")
                    print("   Reading SSE stream...")
                    
                    # Read first few events
                    event_count = 0
                    async for line in response.aiter_lines():
                        if line:
                            print(f"   Event: {line[:100]}...")
                            event_count += 1
                            if event_count >= 3:  # Read first 3 events
                                break
                    
                    print(f"\n✅ Successfully received {event_count} events from server")
                    return True
                else:
                    print(f"❌ Connection failed with status {response.status_code}")
                    body = await response.aread()
                    print(f"   Response body: {body.decode()[:200]}")
                    return False
                
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        
        import traceback
        print(f"\n   Full traceback:")
        traceback.print_exc()
        
        print(f"{'='*60}\n")
        return False


async def main():
    """Run MCP connection tests"""
    print("\n" + "="*60)
    print("MCP Server Connection Test")
    print("="*60)
    
    # Test configurations
    tests = [
        {
            "name": "Remote Production Server",
            "url": "http://10.55.125.43:8300/mcp",
            "api_key": "U1f1mzzSvNKhrtntjJeE0O1KUz-7r7TiuR1-ushQXoc"
        },
        {
            "name": "Remote Production Server (Alternative Key)",
            "url": "http://10.55.125.43:8300/mcp",
            "api_key": "dev-api-key-12345"
        }
    ]
    
    results = []
    for test_config in tests:
        result = await test_remote_mcp(test_config["url"], test_config["api_key"])
        results.append({
            "name": test_config["name"],
            "passed": result
        })
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{status}: {result['name']}")
    print("="*60 + "\n")
    
    # Exit with appropriate code
    all_passed = all(r["passed"] for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
