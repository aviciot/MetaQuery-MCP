#!/usr/bin/env python3
"""
API Key Generator for MCP Server Authentication

Generates cryptographically secure API keys for use in settings.yaml.
Usage: python generate_api_key.py [--count N]
"""

import secrets
import sys

def generate_api_key():
    """Generate a secure random API key"""
    return secrets.token_urlsafe(32)

def main():
    count = 1
    
    # Parse command line args
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print(__doc__)
            print("\nExamples:")
            print("  python generate_api_key.py           # Generate 1 key")
            print("  python generate_api_key.py --count 5 # Generate 5 keys")
            return
        
        if sys.argv[1] == "--count" and len(sys.argv) > 2:
            count = int(sys.argv[2])
    
    print(f"\n🔐 Generated {count} secure API key(s):\n")
    print("-" * 80)
    
    for i in range(count):
        key = generate_api_key()
        print(f"\n{i+1}. {key}")
        
        if i == 0:
            print("\n   Add to settings.yaml:")
            print("   authentication:")
            print("     enabled: true")
            print("     api_keys:")
            print(f"       - name: 'client_{i+1}'")
            print(f"         key: '{key}'")
            print(f"         description: 'Description here'")
    
    print("\n" + "-" * 80)
    print("\n💡 Usage in Claude Desktop config:")
    print("   {")
    print('     "mcpServers": {')
    print('       "performance": {')
    print('         "url": "http://localhost:8300/mcp",')
    print('         "headers": {')
    print(f'           "Authorization": "Bearer {generate_api_key()}"')
    print('         }')
    print('       }')
    print('     }')
    print('   }\n')

if __name__ == "__main__":
    main()
