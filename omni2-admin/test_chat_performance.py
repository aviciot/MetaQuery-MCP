"""Test chat performance and identify bottlenecks."""
import time
import httpx
import asyncio

async def test_chat_performance():
    """Measure chat response time step by step."""
    
    print("🔍 Testing Chat Performance")
    print("=" * 60)
    
    # Simple test message
    test_message = "What is 2+2?"
    
    # Test 1: Direct Omni2 API
    print("\n1️⃣  Testing Omni2 API directly...")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/chat/ask",
                json={
                    "user_id": "admin@omni2.local",
                    "message": test_message
                }
            )
            omni2_time = time.time() - start
            print(f"   ✅ Omni2 API: {omni2_time:.2f}s")
            print(f"   Response: {response.json().get('answer', '')[:100]}")
    except Exception as e:
        print(f"   ❌ Omni2 API failed: {e}")
        omni2_time = None
    
    # Test 2: Admin API proxy
    print("\n2️⃣  Testing Admin API proxy...")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First login to get token
            login_response = await client.post(
                "http://localhost:8500/api/v1/auth/login",
                json={
                    "email": "admin@omni2.com",
                    "password": "admin123"
                }
            )
            token = login_response.json()["access_token"]
            
            # Now test chat
            response = await client.post(
                "http://localhost:8500/api/v1/chat",
                json={
                    "user_id": "admin@omni2.local",
                    "message": test_message
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            admin_time = time.time() - start
            print(f"   ✅ Admin API: {admin_time:.2f}s")
            if omni2_time:
                overhead = admin_time - omni2_time
                print(f"   📊 Proxy overhead: {overhead:.2f}s ({overhead/admin_time*100:.1f}%)")
    except Exception as e:
        print(f"   ❌ Admin API failed: {e}")
        admin_time = None
    
    # Test 3: Complex query with tools
    print("\n3️⃣  Testing complex query with tool calls...")
    complex_message = "Show me database health"
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/chat/ask",
                json={
                    "user_id": "admin@omni2.local",
                    "message": complex_message
                },
                headers={"X-Source": "omni2-admin-dashboard"}
            )
            complex_time = time.time() - start
            data = response.json()
            print(f"   ✅ Complex query: {complex_time:.2f}s")
            print(f"   Tool calls: {data.get('tool_calls', 0)}")
            print(f"   Tools used: {', '.join(data.get('tools_used', []))}")
            print(f"   Iterations: {data.get('iterations', 1)}")
    except Exception as e:
        print(f"   ❌ Complex query failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 Analysis:")
    if omni2_time:
        print(f"   • Simple query: ~{omni2_time:.1f}s (normal for LLM)")
        if omni2_time < 3:
            print("     ✅ Fast - likely cached or no tools needed")
        elif omni2_time < 10:
            print("     ⚠️  Moderate - includes LLM thinking time")
        else:
            print("     ❌ Slow - check Omni2 logs for bottlenecks")
    
    print("\n🔧 Recommendations:")
    print("   1. Add streaming responses for better UX")
    print("   2. Show 'Thinking...' indicator during LLM calls")
    print("   3. Display tool calls in real-time")
    print("   4. Consider caching common queries")
    print("   5. Check network latency to Claude API")

if __name__ == "__main__":
    asyncio.run(test_chat_performance())
