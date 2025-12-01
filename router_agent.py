"""
Router Agent
Uses Gemini AI to analyze queries and coordinate between specialist agents
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from a2a_protocol import A2AMessage, A2AResponse, a2a_logger
from agent_cards import ROUTER_AGENT_CARD

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class RouterAgent:
    """
    Orchestrator agent that analyzes queries and coordinates specialist agents
    Uses Gemini AI for intelligent routing decisions
    """
    
    def __init__(self, data_agent, support_agent):
        """
        Initialize Router Agent
        
        Args:
            data_agent: CustomerDataAgent instance
            support_agent: SupportAgent instance
        """
        self.agent_id = "router_agent"
        self.agent_card = ROUTER_AGENT_CARD
        self.data_agent = data_agent
        self.support_agent = support_agent
        
        # Initialize Gemini
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        print(f"[{self.agent_id}] Initialized with Gemini AI")
    
    async def route_query(self, query: str, customer_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Main entry point - analyze and route customer query
        
        Args:
            query: Customer query text
            customer_id: Optional customer ID
            
        Returns:
            Complete response with routing details
        """
        print(f"\n{'='*60}")
        print(f"[{self.agent_id}] Routing query: {query}")
        print(f"{'='*60}")
        
        # Step 1: Analyze query intent using Gemini
        intent_analysis = await self._analyze_intent(query, customer_id)
        
        print(f"\n[{self.agent_id}] Intent Analysis:")
        print(f"  Type: {intent_analysis.get('type')}")
        print(f"  Requires Data Agent: {intent_analysis.get('requires_data_agent')}")
        print(f"  Requires Support Agent: {intent_analysis.get('requires_support_agent')}")
        
        # Step 2: Route based on intent
        query_type = intent_analysis.get("type")
        
        if query_type == "simple_data_retrieval":
            result = await self._handle_simple_query(query, customer_id, intent_analysis)
        
        elif query_type == "coordinated_support":
            result = await self._handle_coordinated_query(query, customer_id, intent_analysis)
        
        elif query_type == "complex_multi_agent":
            result = await self._handle_complex_query(query, customer_id, intent_analysis)
        
        elif query_type == "escalation":
            result = await self._handle_escalation(query, customer_id, intent_analysis)
        
        elif query_type == "multi_intent":
            result = await self._handle_multi_intent(query, customer_id, intent_analysis)
        
        else:
            result = {"error": f"Unknown query type: {query_type}"}
        
        print(f"\n{'='*60}")
        print(f"[{self.agent_id}] Query completed")
        print(f"{'='*60}\n")
        
        return result
    
    async def _analyze_intent(self, query: str, customer_id: Optional[int]) -> Dict[str, Any]:
        """
        Use Gemini to analyze query intent
        
        Args:
            query: Customer query
            customer_id: Customer ID if available
            
        Returns:
            Intent analysis
        """
        print(f"[{self.agent_id}] Analyzing intent with Gemini AI...")
        
        prompt = f"""Analyze this customer service query and determine how to route it.

Customer Query: {query}
Customer ID: {customer_id if customer_id else "Not provided"}

Analyze the query and respond with JSON:
{{
    "type": "simple_data_retrieval | coordinated_support | complex_multi_agent | escalation | multi_intent",
    "intents": ["list of intents like 'get_customer', 'update_email', 'create_ticket', etc"],
    "requires_data_agent": true/false,
    "requires_support_agent": true/false,
    "customer_id_mentioned": integer or null,
    "urgency": "low | medium | high",
    "explanation": "Brief explanation of routing decision"
}}

Query Types:
- simple_data_retrieval: Direct data fetch (e.g., "Get customer 5", "Show customer info")
- coordinated_support: Needs both data and support (e.g., "I need help with my account")
- complex_multi_agent: Multiple operations (e.g., "Show all active customers with open tickets")
- escalation: Urgent issues (e.g., "charged twice", "refund immediately")
- multi_intent: Multiple actions (e.g., "Update email AND show history")

Extract customer ID if mentioned (e.g., "customer 5", "ID 12345", "I'm customer 1")."""
        
        response = self.model.generate_content(prompt)

        response_text = response.text.strip()

        response_text = response_text.replace('```json', '').replace('```', '').strip()

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[{self.agent_id}] ⚠️  Failed to parse JSON, using fallback")
            print(f"Response: {response_text[:200]}...")
            # Fallback
            result = {
                "type": "simple_data_retrieval",
                "intents": ["get_customer"],
                "requires_data_agent": True,
                "requires_support_agent": False,
                "customer_id_mentioned": customer_id,
                "urgency": "low",
                "explanation": "Fallback due to parsing error"
            }
                
        return result
    
    async def _handle_simple_query(
        self,
        query: str,
        customer_id: Optional[int],
        intent_analysis: Dict
    ) -> Dict[str, Any]:
        """Handle simple data retrieval query"""
        print(f"[{self.agent_id}] Handling SIMPLE QUERY")
        
        # Extract customer ID from analysis if not provided
        if not customer_id:
            customer_id = intent_analysis.get("customer_id_mentioned")
        
        if not customer_id:
            return {"error": "Customer ID required but not provided"}
        
        # Create A2A message to data agent
        message = A2AMessage(
            method="get_customer",
            params={"customer_id": customer_id},
            from_agent=self.agent_id,
            to_agent="data_agent"
        )
        
        # Send to data agent
        response = await self.data_agent.handle_message(message)
        
        return response.result
    
    async def _handle_coordinated_query(
        self,
        query: str,
        customer_id: Optional[int],
        intent_analysis: Dict
    ) -> Dict[str, Any]:
        """Handle coordinated query requiring both data and support agents"""
        print(f"[{self.agent_id}] Handling COORDINATED QUERY")
        
        # Extract customer ID
        if not customer_id:
            customer_id = intent_analysis.get("customer_id_mentioned")
        
        # Step 1: Get customer context from data agent
        customer_context = None
        if customer_id:
            data_message = A2AMessage(
                method="get_customer",
                params={"customer_id": customer_id},
                from_agent=self.agent_id,
                to_agent="data_agent"
            )
            data_response = await self.data_agent.handle_message(data_message)
            customer_context = data_response.result.get("customer")
        
        # Step 2: Send to support agent with context
        support_message = A2AMessage(
            method="handle_support_query",
            params={
                "query": query,
                "customer_context": customer_context
            },
            from_agent=self.agent_id,
            to_agent="support_agent"
        )
        support_response = await self.support_agent.handle_message(support_message)
        
        return {
            "customer_context": customer_context,
            "support_response": support_response.result
        }
    
    async def _handle_complex_query(
        self,
        query: str,
        customer_id: Optional[int],
        intent_analysis: Dict
    ) -> Dict[str, Any]:
        """Handle complex multi-agent query"""
        print(f"[{self.agent_id}] Handling COMPLEX MULTI-AGENT QUERY")
        
        # Example: "Show all active customers with open tickets"
        
        # Step 1: Get active customers
        data_message1 = A2AMessage(
            method="list_customers",
            params={"status": "active", "limit": 50},
            from_agent=self.agent_id,
            to_agent="data_agent"
        )
        data_response1 = await self.data_agent.handle_message(data_message1)
        customers = data_response1.result.get("customers", [])
        
        # Step 2: Get their IDs
        customer_ids = [c["id"] for c in customers]
        
        if not customer_ids:
            return {"message": "No active customers found"}
        
        # Step 3: Get open tickets for these customers
        support_message = A2AMessage(
            method="get_tickets",
            params={
                "status": "open",
                "customer_ids": customer_ids
            },
            from_agent=self.agent_id,
            to_agent="support_agent"
        )
        support_response = await self.support_agent.handle_message(support_message)
        
        return {
            "active_customers_count": len(customers),
            "open_tickets": support_response.result.get("tickets", []),
            "summary": f"Found {len(customers)} active customers with {support_response.result.get('count', 0)} open tickets"
        }
    
    async def _handle_escalation(
        self,
        query: str,
        customer_id: Optional[int],
        intent_analysis: Dict
    ) -> Dict[str, Any]:
        """Handle urgent escalation"""
        print(f"[{self.agent_id}] Handling ESCALATION (Urgent)")
        
        # Analyze urgency
        urgency_message = A2AMessage(
            method="analyze_urgency",
            params={"query": query},
            from_agent=self.agent_id,
            to_agent="support_agent"
        )
        urgency_response = await self.support_agent.handle_message(urgency_message)
        urgency_analysis = urgency_response.result
        
        # Generate response with escalation flag
        support_message = A2AMessage(
            method="handle_support_query",
            params={
                "query": query,
                "customer_context": {"escalation": True, "urgency": urgency_analysis}
            },
            from_agent=self.agent_id,
            to_agent="support_agent"
        )
        support_response = await self.support_agent.handle_message(support_message)
        
        return {
            "urgency_analysis": urgency_analysis,
            "support_response": support_response.result,
            "escalated": True
        }
    
    async def _handle_multi_intent(
        self,
        query: str,
        customer_id: Optional[int],
        intent_analysis: Dict
    ) -> Dict[str, Any]:
        """Handle query with multiple intents"""
        print(f"[{self.agent_id}] Handling MULTI-INTENT QUERY")
        
        intents = intent_analysis.get("intents", [])
        results = {}
        
        # Extract customer ID
        if not customer_id:
            customer_id = intent_analysis.get("customer_id_mentioned")
        
        # Process each intent
        for intent in intents:
            if intent == "update_email":
                # Extract email using Gemini
                extract_prompt = f"Extract the email address from: {query}. Respond with only the email address."
                email_response = self.model.generate_content(extract_prompt)
                email = email_response.text.strip()
                
                # Update via data agent
                message = A2AMessage(
                    method="update_customer",
                    params={"customer_id": customer_id, "email": email},
                    from_agent=self.agent_id,
                    to_agent="data_agent"
                )
                response = await self.data_agent.handle_message(message)
                results["email_update"] = response.result
            
            elif "history" in intent or "ticket" in intent:
            # Get history via data agent
                message = A2AMessage(
                    method="get_customer_history",
                    params={"customer_id": customer_id},
                    from_agent=self.agent_id,
                    to_agent="data_agent"
                )
                response = await self.data_agent.handle_message(message)
                results["ticket_history"] = response.result
        
        return {
            "intents_processed": intents,
            "results": results
        }
