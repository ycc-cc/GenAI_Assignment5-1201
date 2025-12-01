"""
Agent-to-Agent (A2A) Communication Protocol
Implements JSON-RPC 2.0 for inter-agent messaging
"""

import json
import uuid
from typing import Any, Dict, Optional
from datetime import datetime

class A2AMessage:
    """
    JSON-RPC 2.0 message format for A2A communication
    """
    
    def __init__(
        self,
        method: str,
        params: Dict[str, Any],
        from_agent: str,
        to_agent: str,
        id: Optional[str] = None
    ):
        self.jsonrpc = "2.0"
        self.method = method
        self.params = params
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.id = id or str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary"""
        msg = cls(
            method=data["method"],
            params=data["params"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            id=data.get("id")
        )
        if "timestamp" in data:
            msg.timestamp = data["timestamp"]
        return msg
    
    @classmethod
    def from_json(cls, json_str: str) -> 'A2AMessage':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class A2AResponse:
    """
    JSON-RPC 2.0 response format
    """
    
    def __init__(
        self,
        result: Any = None,
        error: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        from_agent: str = None
    ):
        self.jsonrpc = "2.0"
        self.result = result
        self.error = error
        self.id = id
        self.from_agent = from_agent
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        response = {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "from_agent": self.from_agent,
            "timestamp": self.timestamp
        }
        
        if self.error:
            response["error"] = self.error
        else:
            response["result"] = self.result
        
        return response
    
    def to_json(self) -> str:
        """Convert response to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AResponse':
        """Create response from dictionary"""
        resp = cls(
            result=data.get("result"),
            error=data.get("error"),
            id=data.get("id"),
            from_agent=data.get("from_agent")
        )
        if "timestamp" in data:
            resp.timestamp = data["timestamp"]
        return resp
    
    @classmethod
    def from_json(cls, json_str: str) -> 'A2AResponse':
        """Create response from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class A2ALogger:
    """
    Logger for A2A communication
    Tracks all inter-agent messages for debugging and analysis
    """
    
    def __init__(self):
        self.messages = []
    
    def log_message(self, message: A2AMessage):
        """Log an A2A message"""
        self.messages.append({
            "type": "message",
            "data": message.to_dict()
        })
        print(f"\n[A2A MESSAGE] {message.from_agent} → {message.to_agent}")
        print(f"  Method: {message.method}")
        print(f"  ID: {message.id}")
    
    def log_response(self, response: A2AResponse):
        """Log an A2A response"""
        self.messages.append({
            "type": "response",
            "data": response.to_dict()
        })
        print(f"\n[A2A RESPONSE] {response.from_agent}")
        print(f"  ID: {response.id}")
        if response.error:
            print(f"  Error: {response.error}")
        else:
            print(f"  Success: Response returned")
    
    def get_conversation(self, message_id: str) -> list:
        """Get all messages related to a specific message ID"""
        return [
            msg for msg in self.messages
            if msg["data"].get("id") == message_id
        ]
    
    def get_all_messages(self) -> list:
        """Get all logged messages"""
        return self.messages
    
    def clear(self):
        """Clear all logged messages"""
        self.messages = []
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of A2A communications"""
        total = len(self.messages)
        messages = sum(1 for m in self.messages if m["type"] == "message")
        responses = sum(1 for m in self.messages if m["type"] == "response")
        errors = sum(
            1 for m in self.messages
            if m["type"] == "response" and m["data"].get("error")
        )
        
        return {
            "total_communications": total,
            "messages_sent": messages,
            "responses_received": responses,
            "errors": errors
        }


# Global logger instance
a2a_logger = A2ALogger()
