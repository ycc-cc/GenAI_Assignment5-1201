"""
Customer Data Agent
Uses Gemini AI for data validation and MCP for database operations
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from a2a_protocol import A2AMessage, A2AResponse, a2a_logger
from agent_cards import DATA_AGENT_CARD
from mcp_client import MCPClient

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class CustomerDataAgent:
    """
    Specialist agent for customer data operations
    Uses LLM for validation and MCP for data access
    """
    
    def __init__(self, mcp_server_path: str = "mcp_server.py"):
        """
        Initialize Data Agent
        
        Args:
            mcp_server_path: Path to MCP server script
        """
        self.agent_id = "data_agent"
        self.agent_card = DATA_AGENT_CARD
        self.mcp_server_path = mcp_server_path
        self.mcp_client: Optional[MCPClient] = None
        
        # Initialize Gemini
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        print(f"[{self.agent_id}] Initialized with Gemini AI")
    
    async def connect_mcp(self):
        """Connect to MCP server"""
        self.mcp_client = MCPClient(self.mcp_server_path)
        await self.mcp_client.connect()
        print(f"[{self.agent_id}] Connected to MCP server")
    
    async def handle_message(self, message: A2AMessage) -> A2AResponse:
        """
        Handle A2A message
        
        Args:
            message: Incoming A2A message
            
        Returns:
            A2A response
        """
        a2a_logger.log_message(message)
        
        method = message.method
        params = message.params
        
        try:
            # Route to appropriate method
            if method == "get_customer":
                result = await self.get_customer(params.get("customer_id"))
            
            elif method == "list_customers":
                result = await self.list_customers(
                    status=params.get("status", "all"),
                    limit=params.get("limit", 10)
                )
            
            elif method == "update_customer":
                result = await self.update_customer(
                    customer_id=params.get("customer_id"),
                    **{k: v for k, v in params.items() if k != "customer_id"}
                )
            
            elif method == "get_customer_history":
                result = await self.get_customer_history(params.get("customer_id"))
            
            elif method == "create_ticket":
                result = await self.create_ticket(
                    customer_id=params.get("customer_id"),
                    issue=params.get("issue"),
                    priority=params.get("priority", "medium")
                )
            
            elif method == "get_tickets":
                result = await self.get_tickets(**params)
            
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # Create response
            response = A2AResponse(
                result=result,
                id=message.id,
                from_agent=self.agent_id
            )
        
        except Exception as e:
            # Error response
            response = A2AResponse(
                error={
                    "code": -32603,
                    "message": str(e)
                },
                id=message.id,
                from_agent=self.agent_id
            )
        
        a2a_logger.log_response(response)
        return response
    
    async def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """
        Get customer by ID
        Uses MCP tool
        """
        print(f"[{self.agent_id}] → MCP Tool: get_customer (ID: {customer_id})")
        
        result = await self.mcp_client.call_tool(
            "get_customer",
            {"customer_id": customer_id}
        )
        
        if result.get("success"):
            print(f"[{self.agent_id}] ✓ Customer found")
        else:
            print(f"[{self.agent_id}] ✗ {result.get('error')}")
        
        return result
    
    async def list_customers(self, status: str = "all", limit: int = 10) -> Dict[str, Any]:
        """
        List customers with filters
        Uses MCP tool
        """
        print(f"[{self.agent_id}] → MCP Tool: list_customers (status: {status}, limit: {limit})")
        
        result = await self.mcp_client.call_tool(
            "list_customers",
            {"status": status, "limit": limit}
        )
        
        if result.get("success"):
            print(f"[{self.agent_id}] ✓ Found {result.get('count')} customers")
        else:
            print(f"[{self.agent_id}] ✗ {result.get('error')}")
        
        return result
    
    async def update_customer(
        self,
        customer_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update customer information
        Uses Gemini to validate data before updating via MCP
        """
        print(f"[{self.agent_id}] Validating update for customer {customer_id}")
        
        # Build update data
        update_data = {"customer_id": customer_id}
        if name:
            update_data["name"] = name
        if email:
            update_data["email"] = email
        if phone:
            update_data["phone"] = phone
        if status:
            update_data["status"] = status
        
        # Use Gemini to validate email format if provided
        if email:
            validation_prompt = f"""
Validate this email address: {email}

Respond with JSON:
{{
    "valid": true/false,
    "message": "explanation"
}}
"""
            response = self.model.generate_content(validation_prompt)
            response_text = response.text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            validation = json.loads(response_text)
            
            if not validation.get("valid"):
                return {
                    "error": f"Invalid email: {validation.get('message')}",
                    "customer_id": customer_id
                }
        
        # Call MCP tool
        print(f"[{self.agent_id}] → MCP Tool: update_customer")
        result = await self.mcp_client.call_tool("update_customer", update_data)
        
        if result.get("success"):
            print(f"[{self.agent_id}] ✓ Customer updated")
        else:
            print(f"[{self.agent_id}] ✗ {result.get('error')}")
        
        return result
    
    async def get_customer_history(self, customer_id: int) -> Dict[str, Any]:
        """
        Get customer ticket history
        Uses MCP tool
        """
        print(f"[{self.agent_id}] → MCP Tool: get_customer_history (ID: {customer_id})")
        
        result = await self.mcp_client.call_tool(
            "get_customer_history",
            {"customer_id": customer_id}
        )
        
        if result.get("success"):
            ticket_count = result.get("ticket_count", 0)
            print(f"[{self.agent_id}] ✓ Found {ticket_count} tickets")
        else:
            print(f"[{self.agent_id}] ✗ {result.get('error')}")
        
        return result
    
    async def create_ticket(
        self,
        customer_id: int,
        issue: str,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Create new support ticket
        Uses MCP tool
        """
        print(f"[{self.agent_id}] → MCP Tool: create_ticket")
        print(f"  Customer: {customer_id}, Priority: {priority}")
        
        result = await self.mcp_client.call_tool(
            "create_ticket",
            {
                "customer_id": customer_id,
                "issue": issue,
                "priority": priority
            }
        )
        
        if result.get("success"):
            ticket = result.get("ticket", {})
            print(f"[{self.agent_id}] ✓ Ticket created (ID: {ticket.get('id')})")
        else:
            print(f"[{self.agent_id}] ✗ {result.get('error')}")
        
        return result
    
    async def get_tickets(
        self,
        status: str = "all",
        priority: str = "all",
        customer_ids: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Query tickets with filters
        Uses MCP tool
        """
        print(f"[{self.agent_id}] → MCP Tool: get_tickets")
        
        params = {"status": status, "priority": priority}
        if customer_ids:
            params["customer_ids"] = customer_ids
        
        result = await self.mcp_client.call_tool("get_tickets", params)
        
        if result.get("success"):
            count = result.get("count", 0)
            print(f"[{self.agent_id}] ✓ Found {count} tickets")
        else:
            print(f"[{self.agent_id}] ✗ {result.get('error')}")
        
        return result
    
    async def disconnect_mcp(self):
        """Disconnect from MCP server"""
        if self.mcp_client:
            await self.mcp_client.disconnect()
            print(f"[{self.agent_id}] Disconnected from MCP server")
