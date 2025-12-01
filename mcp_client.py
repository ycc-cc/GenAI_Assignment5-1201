"""
MCP Client - Simplified version that directly calls MCP server functions
"""

import json
from typing import Any, Dict
import sys
import os

# Import MCP server functions directly
sys.path.insert(0, os.path.dirname(__file__))
from mcp_server import (
    _get_customer,
    _list_customers,
    _update_customer,
    _create_ticket,
    _get_customer_history,
    _get_tickets
)


class MCPClient:
    """
    Simplified MCP client that directly calls server functions
    """
    
    def __init__(self, server_script_path: str = "mcp_server.py"):
        self.server_script_path = server_script_path
        self.available_tools = [
            "get_customer",
            "list_customers", 
            "update_customer",
            "create_ticket",
            "get_customer_history",
            "get_tickets"
        ]
    
    async def connect(self):
        """Connect to MCP server (simplified - just initialize)"""
        print(f"[MCP Client] Connected to server")
        print(f"[MCP Client] Available tools: {len(self.available_tools)}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool by directly invoking the function
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        try:
            # Route to appropriate function
            if tool_name == "get_customer":
                result = _get_customer(arguments["customer_id"])
            
            elif tool_name == "list_customers":
                result = _list_customers(
                    status=arguments.get("status", "all"),
                    limit=arguments.get("limit", 10)
                )
            
            elif tool_name == "update_customer":
                result = _update_customer(
                    customer_id=arguments["customer_id"],
                    name=arguments.get("name"),
                    email=arguments.get("email"),
                    phone=arguments.get("phone"),
                    status=arguments.get("status")
                )
            
            elif tool_name == "create_ticket":
                result = _create_ticket(
                    customer_id=arguments["customer_id"],
                    issue=arguments["issue"],
                    priority=arguments.get("priority", "medium")
                )
            
            elif tool_name == "get_customer_history":
                result = _get_customer_history(arguments["customer_id"])
            
            elif tool_name == "get_tickets":
                result = _get_tickets(
                    status=arguments.get("status", "all"),
                    priority=arguments.get("priority", "all"),
                    customer_ids=arguments.get("customer_ids")
                )
            
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            return result
        
        except Exception as e:
            return {
                "error": str(e),
                "tool": tool_name,
                "arguments": arguments
            }
    
    async def list_tools(self):
        """List available MCP tools"""
        return self.available_tools
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        print("[MCP Client] Disconnected")