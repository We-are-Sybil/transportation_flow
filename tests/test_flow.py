#!/usr/bin/env python
"""
Simple test script to verify the basic flow structure works
Run this first to test the core flow without crews
"""

import os
import json
import uuid
from datetime import datetime
from crewai.flow.flow import Flow, start, listen
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Minimal state for testing
class SimpleState(BaseModel):
    current_message: Optional[str] = ""
    sender_id: Optional[str] = ""
    conversation_id: Optional[str] = ""
    processed_messages: List[str] = Field(default_factory=list)
    status: str = "starting"

class TestFlow(Flow[SimpleState]):
    """Minimal test flow to verify structure"""
    
    @start()
    def initialize(self):
        """Initialize the flow"""
        print(f"🚀 Flow starting with ID: {self.state.id}")
        print(f"📨 Message: {self.state.current_message}")
        print(f"👤 Sender: {self.state.sender_id}")
        
        if not self.state.conversation_id:
            self.state.conversation_id = str(uuid.uuid4())
        
        self.state.status = "initialized"
        return "Flow initialized"
    
    @listen("initialize")
    def process_message(self, init_result):
        """Process the message"""
        print(f"⚙️ Processing: {init_result}")
        
        message = self.state.current_message
        if message:
            self.state.processed_messages.append(f"Processed: {message}")
            self.state.status = "processed"
            return f"Processed message: {message}"
        else:
            self.state.status = "no_message"
            return "No message to process"
    
    @listen("process_message")
    def finalize(self, process_result):
        """Finalize the flow"""
        print(f"✅ Finalizing: {process_result}")
        
        self.state.status = "complete"
        return {
            "final_status": self.state.status,
            "conversation_id": self.state.conversation_id,
            "processed_count": len(self.state.processed_messages),
            "result": process_result
        }

def test_basic_flow():
    """Test the basic flow structure"""
    print("🧪 Testing basic flow structure...")
    
    # Test 1: With message
    print("\n--- Test 1: With message ---")
    flow1 = TestFlow()
    result1 = flow1.kickoff(inputs={
        "current_message": "Hola, necesito un transporte",
        "sender_id": "test_user_1"
    })
    
    print(f"Result: {result1}")
    print(f"Final state: {flow1.state}")
    
    # Test 2: Without message
    print("\n--- Test 2: Without message ---")
    flow2 = TestFlow()
    result2 = flow2.kickoff(inputs={
        "sender_id": "test_user_2"
    })
    
    print(f"Result: {result2}")
    print(f"Final state: {flow2.state}")
    
    return result1, result2

if __name__ == "__main__":
    test_basic_flow()
