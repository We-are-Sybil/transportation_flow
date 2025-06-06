#!/usr/bin/env python3
"""
Detailed debug test for Ollama + CrewAI integration
This will show us exactly what's failing
"""

import os
import requests
import json
from crewai import Agent, Task, Crew
from crewai.llm import LLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ollama_api_directly():
    """Test Ollama API with direct requests"""
    print("=== Testing Ollama API Directly ===")
    
    try:
        # Test 1: List models
        response = requests.get("http://localhost:11434/api/tags")
        print(f"Models API Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()["models"]
            print(f"Available models: {[m['name'] for m in models]}")
        
        # Test 2: Try a direct chat completion
        print("\n--- Testing direct chat completion ---")
        chat_data = {
            "model": "phi3:3.8b",  # Use the 8b model you have
            "messages": [
                {"role": "user", "content": "Say hello in one word"}
            ],
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            headers={"Content-Type": "application/json",},
            json=chat_data,
        )
        
        print(f"Chat API Status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct API Response: {result}")
            return True
        else:
            print(f"❌ Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Direct API test failed: {str(e)}")
        return False

def test_crewai_llm_only():
    """Test just the LLM object without CrewAI agents"""
    print("\n=== Testing LLM Object Only ===")
    
    try:
        # Create LLM with explicit config
        llm = LLM(
            model="ollama/phi3:3.8b",  # Use the 8b model
            base_url="http://localhost:11434",
            api_key="ollama"
        )
        
        print(f"Created LLM: {llm.model} at {llm.base_url}")
        
        # Try to invoke the LLM directly
        print("Calling LLM directly...")
        response = llm.call([
            {"role": "user", "content": "Say hello"}
        ])
        
        print(f"✅ LLM Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_minimal_agent():
    """Test the most minimal possible CrewAI agent"""
    print("\n=== Testing Minimal CrewAI Agent ===")
    
    try:
        # Create LLM
        llm = LLM(
            model="ollama/phi3:3.8b",
            base_url="http://localhost:11434",
            api_key="ollama"
        )
        
        # Create minimal agent
        agent = Agent(
            role="Helper",
            goal="Say hello",
            backstory="You help with tests.",
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=1,  # Limit iterations
            memory=False  # Disable memory
        )
        
        # Create minimal task
        task = Task(
            description="Just say 'Hello'",
            expected_output="The word Hello",
            agent=agent
        )
        
        # Create minimal crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )
        
        print("Running minimal crew...")
        result = crew.kickoff()
        
        print(f"✅ Minimal crew result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Minimal crew failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 Debugging Ollama + CrewAI Integration\n")
    
    # Test 1: Direct Ollama API
    print("Step 1: Testing Ollama API directly...")
    api_works = test_ollama_api_directly()
    
    if not api_works:
        print("\n❌ Ollama API is not working. Fix this first:")
        print("1. Make sure ollama is running: ollama serve")
        print("2. Test manually: curl http://localhost:11434/api/tags")
        return
    
    # Test 2: LLM object only
    print("\nStep 2: Testing LLM object...")
    llm_works = test_crewai_llm_only()
    
    if not llm_works:
        print("\n❌ LLM integration failed. This is a compatibility issue.")
        return
    
    # Test 3: Minimal agent
    print("\nStep 3: Testing minimal CrewAI agent...")
    agent_works = test_minimal_agent()
    
    if agent_works:
        print("\n🎉 Success! CrewAI + Ollama is working!")
        print("Ready to proceed to Step 2: Building the transportation system")
    else:
        print("\n❌ CrewAI agent failed. Need to investigate further.")

if __name__ == "__main__":
    main()
