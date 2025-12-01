"""
Agent Cards - Define capabilities and interfaces for each agent
Based on A2A protocol specifications
"""

from typing import Dict, List, Any

# Router Agent Card
ROUTER_AGENT_CARD = {
    "agent_id": "router_agent",
    "name": "Router Agent",
    "description": "Orchestrates customer queries and coordinates between specialist agents",
    "version": "1.0.0",
    "capabilities": [
        "query_analysis",
        "intent_detection",
        "agent_coordination",
        "response_synthesis"
    ],
    "methods": [
        {
            "name": "route_query",
            "description": "Analyze and route customer query to appropriate agents",
            "parameters": {
                "query": "string",
                "customer_id": "integer (optional)"
            },
            "returns": "Complete response with coordination details"
        },
        {
            "name": "coordinate_agents",
            "description": "Coordinate multiple agents for complex queries",
            "parameters": {
                "query": "string",
                "required_agents": "array of agent names"
            },
            "returns": "Coordinated response"
        }
    ],
    "supported_intents": [
        "simple_data_retrieval",
        "coordinated_support",
        "complex_multi_agent",
        "escalation",
        "multi_intent"
    ]
}

# Customer Data Agent Card
DATA_AGENT_CARD = {
    "agent_id": "data_agent",
    "name": "Customer Data Agent",
    "description": "Manages customer data and ticket information via MCP",
    "version": "1.0.0",
    "capabilities": [
        "customer_retrieval",
        "customer_listing",
        "customer_update",
        "ticket_creation",
        "ticket_history",
        "ticket_query"
    ],
    "methods": [
        {
            "name": "get_customer",
            "description": "Retrieve customer information by ID",
            "parameters": {
                "customer_id": "integer"
            },
            "returns": "Customer object",
            "mcp_tool": "get_customer"
        },
        {
            "name": "list_customers",
            "description": "List customers with optional filters",
            "parameters": {
                "status": "string (active/disabled/all)",
                "limit": "integer"
            },
            "returns": "Array of customer objects",
            "mcp_tool": "list_customers"
        },
        {
            "name": "update_customer",
            "description": "Update customer information",
            "parameters": {
                "customer_id": "integer",
                "name": "string (optional)",
                "email": "string (optional)",
                "phone": "string (optional)",
                "status": "string (optional)"
            },
            "returns": "Updated customer object",
            "mcp_tool": "update_customer"
        },
        {
            "name": "get_customer_history",
            "description": "Get ticket history for a customer",
            "parameters": {
                "customer_id": "integer"
            },
            "returns": "Customer object with ticket array",
            "mcp_tool": "get_customer_history"
        },
        {
            "name": "create_ticket",
            "description": "Create new support ticket",
            "parameters": {
                "customer_id": "integer",
                "issue": "string",
                "priority": "string (low/medium/high)"
            },
            "returns": "Created ticket object",
            "mcp_tool": "create_ticket"
        },
        {
            "name": "get_tickets",
            "description": "Query tickets with filters",
            "parameters": {
                "status": "string (optional)",
                "priority": "string (optional)",
                "customer_ids": "array of integers (optional)"
            },
            "returns": "Array of ticket objects",
            "mcp_tool": "get_tickets"
        }
    ],
    "mcp_server": "customer-service-mcp",
    "transport": "stdio"
}

# Support Agent Card
SUPPORT_AGENT_CARD = {
    "agent_id": "support_agent",
    "name": "Support Agent",
    "description": "Handles customer support queries using AI and MCP tools",
    "version": "1.0.0",
    "capabilities": [
        "query_analysis",
        "support_response_generation",
        "priority_assessment",
        "escalation_detection",
        "ticket_management"
    ],
    "methods": [
        {
            "name": "handle_support_query",
            "description": "Process customer support query with AI",
            "parameters": {
                "query": "string",
                "customer_context": "object (optional)",
                "ticket_context": "array (optional)"
            },
            "returns": "Support response with analysis"
        },
        {
            "name": "analyze_urgency",
            "description": "Analyze query urgency and priority",
            "parameters": {
                "query": "string"
            },
            "returns": "Priority assessment object"
        },
        {
            "name": "generate_response",
            "description": "Generate customer-facing support response",
            "parameters": {
                "query": "string",
                "context": "object"
            },
            "returns": "Support response string"
        }
    ],
    "supported_query_types": [
        "general_inquiry",
        "technical_support",
        "billing_question",
        "cancellation_refund",
        "feature_request",
        "account_issue"
    ],
    "priority_levels": ["low", "medium", "high"],
    "uses_llm": True,
    "llm_model": "gemini-1.5-pro"
}

# Agent registry
AGENT_REGISTRY = {
    "router_agent": ROUTER_AGENT_CARD,
    "data_agent": DATA_AGENT_CARD,
    "support_agent": SUPPORT_AGENT_CARD
}

def get_agent_card(agent_id: str) -> Dict[str, Any]:
    """Get agent card by ID"""
    return AGENT_REGISTRY.get(agent_id)

def list_all_agents() -> List[Dict[str, Any]]:
    """List all registered agents"""
    return list(AGENT_REGISTRY.values())

def get_agent_capabilities(agent_id: str) -> List[str]:
    """Get list of capabilities for an agent"""
    card = get_agent_card(agent_id)
    return card.get("capabilities", []) if card else []

def get_agent_methods(agent_id: str) -> List[Dict[str, Any]]:
    """Get list of methods for an agent"""
    card = get_agent_card(agent_id)
    return card.get("methods", []) if card else []
