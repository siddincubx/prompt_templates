"""
Test script for the Prompt Template Engine API
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_api():
    """Test the API endpoints"""
    async with aiohttp.ClientSession() as session:
        
        print("🧪 Testing Prompt Template Engine API...")
        
        # Test 1: Get stats (should work even with empty database)
        print("\n1. Testing GET /api/stats")
        try:
            async with session.get(f"{BASE_URL}/api/stats") as resp:
                data = await resp.json()
                print(f"   ✅ Status: {resp.status}")
                print(f"   📊 Stats: {data}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Generate a template using AI
        print("\n2. Testing POST /api/generate-template")
        try:
            payload = {
                "requirement": "I want to generate a professional email invitation for a business meeting"
            }
            async with session.post(f"{BASE_URL}/api/generate-template", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ Status: {resp.status}")
                    print(f"   🤖 Generated template:")
                    print(f"      Text: {data.get('text', '')[:100]}...")
                    print(f"      Variables: {data.get('variables', [])}")
                    
                    # Store the generated template for next test
                    generated_template = data
                else:
                    error_data = await resp.json()
                    print(f"   ❌ Status: {resp.status}")
                    print(f"   ❌ Error: {error_data}")
                    generated_template = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            generated_template = None
        
        # Test 3: Create a template
        print("\n3. Testing POST /api/templates")
        try:
            if generated_template:
                payload = {
                    "name": "test-meeting-invitation",
                    "description": "Template for business meeting invitations",
                    "text": generated_template.get("text", ""),
                    "variables": generated_template.get("variables", []),
                    "category": "Business"
                }
            else:
                # Fallback template
                payload = {
                    "name": "test-simple-template",
                    "description": "A simple test template",
                    "text": "Hello <%= name %>, welcome to <%= event %>!",
                    "variables": ["name", "event"],
                    "category": "Test"
                }
            
            async with session.post(f"{BASE_URL}/api/templates", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"   ✅ Status: {resp.status}")
                    print(f"   📝 Created template ID: {data.get('id')}")
                    template_id = data.get('id')
                else:
                    error_data = await resp.json()
                    print(f"   ❌ Status: {resp.status}")
                    print(f"   ❌ Error: {error_data}")
                    template_id = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            template_id = None
        
        # Test 4: Get all templates
        print("\n4. Testing GET /api/templates")
        try:
            async with session.get(f"{BASE_URL}/api/templates") as resp:
                data = await resp.json()
                print(f"   ✅ Status: {resp.status}")
                print(f"   📋 Templates count: {len(data)}")
                for template in data[:2]:  # Show first 2 templates
                    print(f"      - {template.get('name')} ({template.get('variable_count')} variables)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Use a template (if we created one)
        if template_id:
            print(f"\n5. Testing POST /api/templates/{template_id}/use")
            try:
                payload = {
                    "variable_values": {
                        "name": "John Doe",
                        "event": "Product Launch Meeting"
                    }
                }
                async with session.post(f"{BASE_URL}/api/templates/{template_id}/use", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"   ✅ Status: {resp.status}")
                        print(f"   🎯 Final prompt: {data.get('final_prompt', '')[:100]}...")
                    else:
                        error_data = await resp.json()
                        print(f"   ❌ Status: {resp.status}")
                        print(f"   ❌ Error: {error_data}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test 6: Get categories
        print("\n6. Testing GET /api/categories")
        try:
            async with session.get(f"{BASE_URL}/api/categories") as resp:
                data = await resp.json()
                print(f"   ✅ Status: {resp.status}")
                print(f"   🏷️  Categories: {data}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n🎉 API testing completed!")

if __name__ == "__main__":
    asyncio.run(test_api())