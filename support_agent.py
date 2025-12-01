"""
Support Agent
Uses Gemini AI to generate customer support responses
Accesses ticket data via MCP
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from a2a_protocol import A2AMessage, A2AResponse, a2a_logger
from agent_cards import SUPPORT_AGENT_CARD
from mcp_client import MCPClient

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class SupportAgent:
    """
    Specialist agent for customer support
    Uses Gemini AI for intelligent response generation
    """
    
    def __init__(self, mcp_server_path: str = "mcp_server.py"):
        """
        Initialize Support Agent
        
        Args:
            mcp_server_path: Path to MCP server script
        """
        self.agent_id = "support_agent"
        self.agent_card = SUPPORT_AGENT_CARD
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
            if method == "handle_support_query":
                result = await self.handle_support_query(
                    query=params.get("query"),
                    customer_context=params.get("customer_context"),
                    ticket_context=params.get("ticket_context")
                )
            
            elif method == "analyze_urgency":
                result = await self.analyze_urgency(params.get("query"))
            
            elif method == "generate_response":
                result = await self.generate_response(
                    query=params.get("query"),
                    context=params.get("context", {})
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
    
    async def handle_support_query(
        self,
        query: str,
        customer_context: Optional[Dict] = None,
        ticket_context: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Handle a complete support query using Gemini AI
        
        Args:
            query: Customer query
            customer_context: Customer information
            ticket_context: Previous tickets
            
        Returns:
            Support response with analysis
        """
        print(f"[{self.agent_id}] Handling support query with Gemini AI")
        
        # Build context for Gemini
        context_str = "Customer Context:\n"
        if customer_context:
            context_str += json.dumps(customer_context, indent=2)
        else:
            context_str += "No customer context available"
        
        if ticket_context:
            context_str += f"\n\nPrevious Tickets ({len(ticket_context)}):\n"
            context_str += json.dumps(ticket_context[:3], indent=2)  # Show top 3
        
        # Gemini prompt
        prompt = f"""You are a professional customer support agent. Analyze this query and provide a helpful response.

{context_str}

Customer Query: {query}

Respond with JSON containing:
{{
    "response": "Your professional customer-facing response",
    "query_type": "general_inquiry | technical_support | billing_question | cancellation_refund | feature_request | account_issue",
    "priority": "low | medium | high",
    "requires_escalation": true/false,
    "recommended_action": "What should be done next",
    "internal_notes": "Notes for support team"
}}

Be professional, empathetic, and helpful. Provide actionable solutions."""
        
        # Call Gemini
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        result = json.loads(response_text)
        
        print(f"[{self.agent_id}] ✓ Generated response (type: {result.get('query_type')}, priority: {result.get('priority')})")
        
        return result
    
    async def analyze_urgency(self, query: str) -> Dict[str, Any]:
        """
        Analyze query urgency using Gemini
        
        Args:
            query: Customer query
            
        Returns:
            Urgency analysis
        """
        print(f"[{self.agent_id}] Analyzing urgency with Gemini AI")
        
        prompt = f"""Analyze the urgency of this customer support query.

Query: {query}

Respond with JSON:
{{
    "priority": "low | medium | high",
    "is_urgent": true/false,
    "urgency_factors": ["factor1", "factor2"],
    "recommended_response_time": "immediate | within 1 hour | within 24 hours | within 3 days",
    "explanation": "Why this priority level"
}}

Consider factors like:
- Words indicating urgency (immediately, urgent, critical, emergency)
- Financial impact (charged twice, billing error, refund)
- Service disruption (cannot access, not working, down)
- Security concerns (hacked, unauthorized access)"""
        
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        result = json.loads(response_text)
        
        print(f"[{self.agent_id}] ✓ Priority: {result.get('priority')}, Urgent: {result.get('is_urgent')}")
        
        return result
    
    async def generate_response(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Generate customer-facing response using Gemini
        
        Args:
            query: Customer query
            context: Additional context
            
        Returns:
            Generated response
        """
        print(f"[{self.agent_id}] Generating response with Gemini AI")
        
        prompt = f"""Generate a professional customer support response.

Query: {query}

Context: {json.dumps(context, indent=2)}

Provide a warm, professional, and helpful response. Address the customer's concerns directly and offer clear next steps if applicable.

Respond with JSON:
{{
    "response": "Your customer-facing response"
}}"""
        
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        result = json.loads(response_text)
        
        print(f"[{self.agent_id}] ✓ Response generated")
        
        return result
    
    async def get_tickets(
        self,
        status: str = "all",
        priority: str = "all",
        customer_ids: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Get tickets via MCP
        
        Args:
            status: Ticket status filter
            priority: Priority filter
            customer_ids: Customer IDs filter
            
        Returns:
            Tickets data
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
