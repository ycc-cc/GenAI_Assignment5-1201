"""
MCP Server for Customer Service System
Implements official MCP SDK with stdio transport
Provides 6 tools for customer and ticket management
"""

import sqlite3
import json
import asyncio
from datetime import datetime
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Database path
DB_PATH = "support.db"

# Initialize MCP Server
server = Server("customer-service-mcp")

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools
    Required by MCP protocol
    """
    return [
        Tool(
            name="get_customer",
            description="Retrieve detailed customer information by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The unique customer ID"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="list_customers",
            description="List customers with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["active", "disabled", "all"],
                        "description": "Filter customers by status",
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of customers to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                }
            }
        ),
        Tool(
            name="update_customer",
            description="Update customer information (name, email, phone, status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New customer name"
                    },
                    "email": {
                        "type": "string",
                        "description": "New email address"
                    },
                    "phone": {
                        "type": "string",
                        "description": "New phone number"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "disabled"],
                        "description": "New account status"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="create_ticket",
            description="Create a new support ticket for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID who created the ticket"
                    },
                    "issue": {
                        "type": "string",
                        "description": "Description of the issue"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "default": "medium",
                        "description": "Priority level of the ticket"
                    }
                },
                "required": ["customer_id", "issue"]
            }
        ),
        Tool(
            name="get_customer_history",
            description="Get all tickets associated with a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID to get ticket history for"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="get_tickets",
            description="Query tickets with various filters (status, priority, customer IDs)",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["open", "in_progress", "resolved", "all"],
                        "description": "Filter by ticket status"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "all"],
                        "description": "Filter by priority level"
                    },
                    "customer_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Filter by specific customer IDs"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """
    Handle MCP tool calls
    Routes to appropriate database operation
    """
    
    try:
        # Route to appropriate handler
        if name == "get_customer":
            result = _get_customer(arguments["customer_id"])
        
        elif name == "list_customers":
            result = _list_customers(
                status=arguments.get("status", "all"),
                limit=arguments.get("limit", 10)
            )
        
        elif name == "update_customer":
            result = _update_customer(
                customer_id=arguments["customer_id"],
                name=arguments.get("name"),
                email=arguments.get("email"),
                phone=arguments.get("phone"),
                status=arguments.get("status")
            )
        
        elif name == "create_ticket":
            result = _create_ticket(
                customer_id=arguments["customer_id"],
                issue=arguments["issue"],
                priority=arguments.get("priority", "medium")
            )
        
        elif name == "get_customer_history":
            result = _get_customer_history(arguments["customer_id"])
        
        elif name == "get_tickets":
            result = _get_tickets(
                status=arguments.get("status", "all"),
                priority=arguments.get("priority", "all"),
                customer_ids=arguments.get("customer_ids")
            )
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        # Return as MCP TextContent
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    except Exception as e:
        # Error handling
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }, indent=2)
        )]

# ============================================================================
# Database Operations
# ============================================================================

def _get_customer(customer_id: int):
    """Get customer by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "success": True,
            "customer": dict(row)
        }
    return {"error": "Customer not found", "customer_id": customer_id}

def _list_customers(status="all", limit=10):
    """List customers with optional status filter"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status == "all":
        cursor.execute("SELECT * FROM customers LIMIT ?", (limit,))
    else:
        cursor.execute(
            "SELECT * FROM customers WHERE status = ? LIMIT ?",
            (status, limit)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "success": True,
        "count": len(rows),
        "customers": [dict(row) for row in rows]
    }

def _update_customer(customer_id, name=None, email=None, phone=None, status=None):
    """Update customer information"""
    fields = []
    values = []
    
    # Build dynamic UPDATE query
    if name:
        fields.append("name = ?")
        values.append(name)
    if email:
        fields.append("email = ?")
        values.append(email)
    if phone:
        fields.append("phone = ?")
        values.append(phone)
    if status:
        fields.append("status = ?")
        values.append(status)
    
    if not fields:
        return {"error": "No fields to update"}
    
    # Add updated_at timestamp
    values.append(datetime.now().isoformat())
    values.append(customer_id)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = f"UPDATE customers SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    
    if cursor.rowcount > 0:
        # Fetch updated customer
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        return {
            "success": True,
            "message": "Customer updated successfully",
            "customer": dict(row)
        }
    
    conn.close()
    return {"error": "Customer not found or no changes made", "customer_id": customer_id}

def _create_ticket(customer_id, issue, priority="medium"):
    """Create new support ticket"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify customer exists
    cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cursor.fetchone():
        conn.close()
        return {"error": "Customer not found", "customer_id": customer_id}
    
    # Insert ticket
    cursor.execute("""
        INSERT INTO tickets (customer_id, issue, status, priority)
        VALUES (?, ?, 'open', ?)
    """, (customer_id, issue, priority))
    
    ticket_id = cursor.lastrowid
    conn.commit()
    
    # Fetch created ticket
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {
        "success": True,
        "message": "Ticket created successfully",
        "ticket": dict(row)
    }

def _get_customer_history(customer_id):
    """Get all tickets for a customer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify customer exists
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    
    if not customer:
        conn.close()
        return {"error": "Customer not found", "customer_id": customer_id}
    
    # Get tickets
    cursor.execute(
        "SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC",
        (customer_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "success": True,
        "customer": dict(customer),
        "ticket_count": len(rows),
        "tickets": [dict(row) for row in rows]
    }

def _get_tickets(status="all", priority="all", customer_ids=None):
    """Query tickets with filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    
    # Add filters
    if status != "all":
        query += " AND status = ?"
        params.append(status)
    
    if priority != "all":
        query += " AND priority = ?"
        params.append(priority)
    
    if customer_ids:
        placeholders = ",".join("?" * len(customer_ids))
        query += f" AND customer_id IN ({placeholders})"
        params.extend(customer_ids)
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "success": True,
        "count": len(rows),
        "tickets": [dict(row) for row in rows]
    }

# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """
    Run MCP server with stdio transport
    This allows agents to communicate via stdin/stdout
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server Starting (stdio transport)")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print("Waiting for MCP client connections...")
    print("=" * 60)
    asyncio.run(main())
