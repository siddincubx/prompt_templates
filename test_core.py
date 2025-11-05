"""
Simple test to verify template creation functionality
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import db_manager
from app.services.template_service import template_service
from app.models import TemplateCreate

async def test_template_creation():
    """Test template creation functionality"""
    print("🧪 Testing template creation...")
    
    # Initialize database
    await db_manager.init_db()
    print("✅ Database initialized")
    
    # Create a test template
    test_template = TemplateCreate(
        name="test-welcome-email",
        description="A test template for welcome emails",
        text="Welcome to our platform, <%= userName %>! We're excited to have you join our community. Your account has been created with the email <%= userEmail %>. Please visit <%= loginUrl %> to get started.",
        variables=["userName", "userEmail", "loginUrl"],
        category="Email"
    )
    
    try:
        created_template = await template_service.create_template(test_template)
        print(f"✅ Template created successfully with ID: {created_template.id}")
        print(f"📝 Template name: {created_template.name}")
        print(f"🏷️ Variables: {', '.join(created_template.variables)}")
        
        # Test template usage
        usage_result = await template_service.use_template(
            created_template.id,
            {
                "userName": "John Doe",
                "userEmail": "john@example.com",
                "loginUrl": "https://example.com/login"
            }
        )
        print(f"✅ Template usage successful")
        print(f"📄 Generated prompt: {usage_result.final_prompt[:100]}...")
        
        return created_template.id
        
    except Exception as e:
        print(f"❌ Template creation/usage failed: {e}")
        return None

async def test_ai_generation():
    """Test AI template generation"""
    print("\n🤖 Testing AI template generation...")
    
    try:
        from app.services.ai_service import ai_service
        
        result = await ai_service.generate_template(
            "I want to create personalized birthday invitations for family and friends"
        )
        
        print("✅ AI generation successful!")
        print(f"📝 Generated template preview: {result['text'][:100]}...")
        print(f"🏷️ Variables: {', '.join(result['variables'])}")
        print(f"💡 Suggested name: {result['suggested_name']}")
        print(f"📂 Suggested category: {result['suggested_category']}")
        
        return result
        
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        return None

async def main():
    """Main test function"""
    print("🚀 Starting Template Engine Core Tests")
    print("=" * 40)
    
    # Test template creation
    template_id = await test_template_creation()
    
    # Test AI generation
    ai_result = await test_ai_generation()
    
    print("\n" + "=" * 40)
    if template_id and ai_result:
        print("✅ All core tests passed!")
        print("\n🌐 You can now test the web interface:")
        print("   1. Start the server: python main.py")
        print("   2. Open: http://127.0.0.1:8000")
        print("   3. Go to: http://127.0.0.1:8000/templates/create")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())