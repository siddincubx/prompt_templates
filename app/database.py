"""
Database setup and connection management for SQLite
"""
import aiosqlite
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent.parent / "templates.db"

# Database schema
SCHEMA = """
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    text TEXT NOT NULL,
    variables TEXT NOT NULL, -- JSON array of variable names
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS template_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates (id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_created_at ON templates(created_at);
CREATE INDEX IF NOT EXISTS idx_template_usage_template_id ON template_usage(template_id);
"""

class DatabaseManager:
    """Database manager for template operations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
    
    async def init_db(self):
        """Initialize the database with schema"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await db.commit()
    
    async def get_connection(self):
        """Get database connection"""
        return await aiosqlite.connect(self.db_path)
    
    async def create_template(self, name: str, description: str, text: str, 
                            variables: List[str], category: str = None) -> int:
        """Create a new template and return its ID"""
        async with aiosqlite.connect(self.db_path) as db:
            variables_json = json.dumps(variables)
            cursor = await db.execute(
                """INSERT INTO templates (name, description, text, variables, category)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, description, text, variables_json, category)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get a template by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM templates WHERE id = ?", (template_id,)
            )
            row = await cursor.fetchone()
            if row:
                template = dict(row)
                template['variables'] = json.loads(template['variables'])
                return template
            return None
    
    async def get_template_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM templates WHERE name = ?", (name,)
            )
            row = await cursor.fetchone()
            if row:
                template = dict(row)
                template['variables'] = json.loads(template['variables'])
                return template
            return None
    
    async def get_all_templates(self, category: str = None, 
                               limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all templates with optional filtering and pagination"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = "SELECT * FROM templates"
            params = []
            
            if category:
                query += " WHERE category = ?"
                params.append(category)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            templates = []
            for row in rows:
                template = dict(row)
                template['variables'] = json.loads(template['variables'])
                templates.append(template)
            
            return templates
    
    async def update_template(self, template_id: int, name: str = None, 
                            description: str = None, text: str = None,
                            variables: List[str] = None, category: str = None) -> bool:
        """Update a template"""
        async with aiosqlite.connect(self.db_path) as db:
            # Build dynamic update query
            set_clauses = []
            params = []
            
            if name is not None:
                set_clauses.append("name = ?")
                params.append(name)
            if description is not None:
                set_clauses.append("description = ?")
                params.append(description)
            if text is not None:
                set_clauses.append("text = ?")
                params.append(text)
            if variables is not None:
                set_clauses.append("variables = ?")
                params.append(json.dumps(variables))
            if category is not None:
                set_clauses.append("category = ?")
                params.append(category)
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            params.append(template_id)
            
            query = f"UPDATE templates SET {', '.join(set_clauses)} WHERE id = ?"
            
            cursor = await db.execute(query, params)
            await db.commit()
            
            return cursor.rowcount > 0
    
    async def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        async with aiosqlite.connect(self.db_path) as db:
            # Delete usage records first
            await db.execute("DELETE FROM template_usage WHERE template_id = ?", (template_id,))
            
            # Delete template
            cursor = await db.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            await db.commit()
            
            return cursor.rowcount > 0
    
    async def increment_usage_count(self, template_id: int):
        """Increment usage count and log usage"""
        async with aiosqlite.connect(self.db_path) as db:
            # Update usage count
            await db.execute(
                "UPDATE templates SET usage_count = usage_count + 1 WHERE id = ?",
                (template_id,)
            )
            
            # Log usage
            await db.execute(
                "INSERT INTO template_usage (template_id) VALUES (?)",
                (template_id,)
            )
            
            await db.commit()
    
    async def get_categories(self) -> List[str]:
        """Get all unique categories"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT DISTINCT category FROM templates WHERE category IS NOT NULL ORDER BY category"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Search templates by name or description"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute(
                """SELECT * FROM templates 
                   WHERE name LIKE ? OR description LIKE ? 
                   ORDER BY created_at DESC""",
                (f"%{query}%", f"%{query}%")
            )
            rows = await cursor.fetchall()
            
            templates = []
            for row in rows:
                template = dict(row)
                template['variables'] = json.loads(template['variables'])
                templates.append(template)
            
            return templates
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total templates
            cursor = await db.execute("SELECT COUNT(*) FROM templates")
            total_templates = (await cursor.fetchone())[0]
            
            # Total usage
            cursor = await db.execute("SELECT SUM(usage_count) FROM templates")
            total_usage = (await cursor.fetchone())[0] or 0
            
            # Most used template
            cursor = await db.execute(
                "SELECT name, usage_count FROM templates ORDER BY usage_count DESC LIMIT 1"
            )
            most_used = await cursor.fetchone()
            
            # Categories count
            cursor = await db.execute(
                "SELECT COUNT(DISTINCT category) FROM templates WHERE category IS NOT NULL"
            )
            categories_count = (await cursor.fetchone())[0]
            
            return {
                "total_templates": total_templates,
                "total_usage": total_usage,
                "most_used_template": {
                    "name": most_used[0] if most_used else None,
                    "usage_count": most_used[1] if most_used else 0
                },
                "categories_count": categories_count
            }

# Global database manager instance
db_manager = DatabaseManager()