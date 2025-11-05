"""
Comprehensive test script for Prompt Template Engine
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any

class PromptTemplateEngineTest:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_server_health(self):
        """Test if the server is running"""
        print("🏥 Testing server health...")
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    print("✅ Server is running and accessible")
                    return True
                else:
                    print(f"❌ Server responded with status {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Server health check failed: {e}")
            return False
    
    async def test_api_endpoints(self):
        """Test all API endpoints"""
        print("\n🔌 Testing API endpoints...")
        
        # Test getting templates (should be empty initially)
        async with self.session.get(f"{self.base_url}/api/templates") as response:
            if response.status == 200:
                templates = await response.json()
                print(f"✅ GET /api/templates - Retrieved {len(templates)} templates")
            else:
                print(f"❌ GET /api/templates failed with status {response.status}")
        
        # Test getting categories
        async with self.session.get(f"{self.base_url}/api/categories") as response:
            if response.status == 200:
                categories = await response.json()
                print(f"✅ GET /api/categories - Retrieved {len(categories)} categories")
            else:
                print(f"❌ GET /api/categories failed with status {response.status}")
        
        # Test getting stats
        async with self.session.get(f"{self.base_url}/api/stats") as response:
            if response.status == 200:
                stats = await response.json()
                print(f"✅ GET /api/stats - Total templates: {stats.get('total_templates', 0)}")
            else:
                print(f"❌ GET /api/stats failed with status {response.status}")
    
    async def test_template_creation(self):
        """Test creating a new template"""
        print("\n📝 Testing template creation...")
        
        template_data = {
            "name": "test-email-template",
            "description": "A test template for email generation",
            "text": "Generate a professional email to <%= recipientName %> about <%= subject %>. The email should mention that the meeting is scheduled for <%= meetingDate %> at <%= location %>.",
            "variables": ["recipientName", "subject", "meetingDate", "location"],
            "category": "Email"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/templates",
                json=template_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    created_template = await response.json()
                    print(f"✅ Template created successfully with ID: {created_template['id']}")
                    return created_template['id']
                else:
                    error_text = await response.text()
                    print(f"❌ Template creation failed with status {response.status}: {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Template creation failed: {e}")
            return None
    
    async def test_template_usage(self, template_id: int):
        """Test using a template with variables"""
        print(f"\n🎯 Testing template usage for template ID: {template_id}...")
        
        usage_data = {
            "variable_values": {
                "recipientName": "John Doe",
                "subject": "quarterly review meeting",
                "meetingDate": "December 15th, 2024",
                "location": "Conference Room A"
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/templates/{template_id}/use",
                json=usage_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Template used successfully!")
                    print(f"📄 Generated prompt preview: {result['final_prompt'][:100]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Template usage failed with status {response.status}: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Template usage failed: {e}")
            return False
    
    async def test_ai_generation(self):
        """Test AI template generation"""
        print("\n🤖 Testing AI template generation...")
        
        generation_request = {
            "requirement": "I want to generate product descriptions for e-commerce websites with compelling features and benefits"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/generate-template",
                json=generation_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    generated = await response.json()
                    print("✅ AI template generation successful!")
                    print(f"📝 Generated template preview: {generated['text'][:100]}...")
                    print(f"🏷️ Variables found: {', '.join(generated['variables'])}")
                    return generated
                else:
                    error_text = await response.text()
                    print(f"❌ AI generation failed with status {response.status}: {error_text}")
                    return None
        except Exception as e:
            print(f"❌ AI generation failed: {e}")
            return None
    
    async def test_web_pages(self):
        """Test web page accessibility"""
        print("\n🌐 Testing web pages...")
        
        pages_to_test = [
            "/",
            "/templates",
            "/templates/create"
        ]
        
        for page in pages_to_test:
            try:
                async with self.session.get(f"{self.base_url}{page}") as response:
                    if response.status == 200:
                        content = await response.text()
                        if "Prompt Template Engine" in content:
                            print(f"✅ Page {page} loads correctly")
                        else:
                            print(f"⚠️ Page {page} loads but may have content issues")
                    else:
                        print(f"❌ Page {page} failed with status {response.status}")
            except Exception as e:
                print(f"❌ Page {page} test failed: {e}")
    
    async def test_search_functionality(self):
        """Test search functionality"""
        print("\n🔍 Testing search functionality...")
        
        search_query = "email"
        try:
            async with self.session.get(f"{self.base_url}/api/templates/search/{search_query}") as response:
                if response.status == 200:
                    results = await response.json()
                    print(f"✅ Search for '{search_query}' returned {len(results)} results")
                else:
                    print(f"❌ Search failed with status {response.status}")
        except Exception as e:
            print(f"❌ Search test failed: {e}")
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Prompt Template Engine Test Suite")
        print("=" * 50)
        
        # Test 1: Server Health
        if not await self.test_server_health():
            print("💀 Server is not accessible. Aborting tests.")
            return
        
        # Test 2: API Endpoints
        await self.test_api_endpoints()
        
        # Test 3: Template Creation
        template_id = await self.test_template_creation()
        
        # Test 4: Template Usage (if creation was successful)
        if template_id:
            await self.test_template_usage(template_id)
        
        # Test 5: AI Generation
        await self.test_ai_generation()
        
        # Test 6: Web Pages
        await self.test_web_pages()
        
        # Test 7: Search
        await self.test_search_functionality()
        
        print("\n" + "=" * 50)
        print("🎉 Test suite completed!")
        print("\n💡 To manually test the application:")
        print("   1. Open http://127.0.0.1:8000 in your browser")
        print("   2. Try creating a template using AI generation")
        print("   3. Use the template with some variables")
        print("   4. Browse and search existing templates")

async def main():
    """Main test function"""
    async with PromptTemplateEngineTest() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())