#!/usr/bin/env python
"""Test the conversational flow"""
from transportation_flow.main import TransportationSystemFlow

# Test conversation
flow = TransportationSystemFlow()

# First message
print("TEST 1: Initial message")
result1 = flow.kickoff(inputs={
    "message": "Hola, necesito un servicio de transporte",
    "sender_id": "test_user"
})
print(f"Result: {result1}\n")

# Simulate user response
if result1.get("status") == "waiting_for_response":
    print("\nTEST 2: User provides more info")
    result2 = flow.continue_conversation(
        "Soy Juan Pérez, necesito el servicio para mañana a las 3pm",
        result1["conversation_id"]
    )
    print(f"Result: {result2}")
