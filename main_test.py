"""
Multi-Agent Customer Service System - Test Suite
Tests all 5 required scenarios plus bonus scenario
"""

import asyncio
import json
from pathlib import Path

from data_agent import CustomerDataAgent
from support_agent import SupportAgent
from router_agent import RouterAgent
from a2a_protocol import a2a_logger


async def setup_system():
    """Initialize all agents and connect to MCP"""
    print("\n" + "="*60)
    print("INITIALIZING MULTI-AGENT SYSTEM")
    print("="*60)
    
    # Initialize agents
    data_agent = CustomerDataAgent("mcp_server.py")
    support_agent = SupportAgent("mcp_server.py")
    
    # Connect to MCP
    await data_agent.connect_mcp()
    await support_agent.connect_mcp()
    
    # Initialize router
    router = RouterAgent(data_agent, support_agent)
    
    print("\n✓ All agents initialized and connected")
    
    return router, data_agent, support_agent


async def test_scenario_1(router):
    """
    Scenario 1: Simple Query
    "Get customer information for ID 5"
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 1: Simple Query")
    print("="*60)
    
    query = "Get customer information for ID 5"
    result = await router.route_query(query, customer_id=5)
    
    print(f"\n[RESULT]")
    print(json.dumps(result, indent=2, default=str))


async def test_scenario_2(router):
    """
    Scenario 2: Coordinated Query
    "I'm customer 1 and need help upgrading my account"
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 2: Coordinated Query")
    print("="*60)
    
    query = "I'm customer 1 and need help upgrading my account"
    result = await router.route_query(query)
    
    print(f"\n[RESULT]")
    print(json.dumps(result, indent=2, default=str))


async def test_scenario_3(router):
    """
    Scenario 3: Complex Query
    "Show me all active customers who have open tickets"
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 3: Complex Query")
    print("="*60)
    
    query = "Show me all active customers who have open tickets"
    result = await router.route_query(query)
    
    print(f"\n[RESULT]")
    print(json.dumps(result, indent=2, default=str))


async def test_scenario_4(router):
    """
    Scenario 4: Escalation
    "I've been charged twice, please refund immediately!"
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 4: Escalation")
    print("="*60)
    
    query = "I've been charged twice, please refund immediately!"
    result = await router.route_query(query)
    
    print(f"\n[RESULT]")
    print(json.dumps(result, indent=2, default=str))


async def test_scenario_5(router):
    """
    Scenario 5: Multi-Intent
    "Update my email to charlie.new@example.com and show my ticket history"
    """
    print("\n" + "="*60)
    print("TEST SCENARIO 5: Multi-Intent")
    print("="*60)
    
    query = "Update my email to charlie.new@example.com and show my ticket history"
    result = await router.route_query(query, customer_id=5)  # Charlie Brown is ID 5
    
    print(f"\n[RESULT]")
    print(json.dumps(result, indent=2, default=str))


async def test_bonus_scenario(router):
    """
    Bonus Scenario: Complex Coordination
    "What are all the high-priority tickets currently open?"
    """
    print("\n" + "="*60)
    print("BONUS SCENARIO: High Priority Tickets")
    print("="*60)
    
    query = "What are all the high-priority tickets currently open?"
    result = await router.route_query(query)
    
    print(f"\n[RESULT]")
    print(json.dumps(result, indent=2, default=str))


async def cleanup_system(data_agent, support_agent):
    """Disconnect all agents"""
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    
    await data_agent.disconnect_mcp()
    await support_agent.disconnect_mcp()
    
    print("\n✓ All agents disconnected")


async def main():
    """Run all test scenarios"""
    
    # Setup
    router, data_agent, support_agent = await setup_system()
    
    try:
        # Run all scenarios
        await test_scenario_1(router)
        await asyncio.sleep(1)
        
        await test_scenario_2(router)
        await asyncio.sleep(1)
        
        await test_scenario_3(router)
        await asyncio.sleep(1)
        
        await test_scenario_4(router)
        await asyncio.sleep(1)
        
        await test_scenario_5(router)
        await asyncio.sleep(1)
        
        await test_bonus_scenario(router)
        
        # Show A2A communication summary
        print("\n" + "="*60)
        print("A2A COMMUNICATION SUMMARY")
        print("="*60)
        summary = a2a_logger.summary()
        print(json.dumps(summary, indent=2))
        
    finally:
        # Cleanup
        await cleanup_system(data_agent, support_agent)
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Verify database exists
    db_path = Path("support.db")
    if not db_path.exists():
        print("ERROR: support.db not found. Please run database_setup.py first.")
        exit(1)
    
    # Run tests
    asyncio.run(main())
