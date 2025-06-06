#!/usr/bin/env python3
"""
Deep debugging to see exactly what's happening with Ollama + CrewAI
"""

import os
import requests
import json
from crewai.llm import LLM
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def test_ollama_openai_api():
    """Test Ollama's OpenAI-compatible API directly"""
    print("=== Testing Ollama OpenAI API Directly ===")
    
    url = "http://localhost:11434/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer ollama"  # Ollama doesn't need real auth
    }
    
    payload = {
        "model": "phi3:3.8b",
        "messages": [
            {"role": "user", "content": "Say hello! Keep it very short."}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_crewai_llm_directly():
    """Test CrewAI LLM object directly without agents"""
    print("\n=== Testing CrewAI LLM Object Directly ===")
    
    try:
        os.environ["OPENAI_API_KEY"] = "sk-proj-1111"
        # Create LLM with debug info
        llm = LLM(
            model="ollama/phi3:3.8b",
            base_url="http://localhost:11434",
        )
        
        print(f"LLM created: {llm}")
        print(f"Model: {llm.model}")
        print(f"Base URL: {llm.base_url}")
        
        # Try a simple completion
        print("Attempting simple completion...")
        
        # Use the call method directly
        messages = [{"role": "user", "content": "Say 'Hello from CrewAI!' Keep it short."}]
        
        result = llm.call(messages)
        print(f"✅ LLM Direct Call Success: {result}")
        return True
        
    except Exception as e:
        print(f"❌ LLM Direct Call Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_different_model():
    """Test with the 8b model instead of 14b"""
    print("\n=== Testing with phi3:3.8b (smaller model) ===")
    
    try:
        os.environ["OPENAI_API_KEY"] = "sk-proj-1111"
        llm = ChatOpenAI(
            model="ollama/phi3:3.8b",
            base_url="http://localhost:11434", 
        )
        
        messages = [{"role": "user", "content": "Hello"}]
        result = llm.call(messages)
        print(f"✅ 8b Model Success: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 8b Model Failed: {str(e)}")
        return False

def test_environment_approach():
    """Test using environment variables approach"""
    print("\n=== Testing Environment Variables Approach ===")
    
    # Set environment variables
    os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
    os.environ["OPENAI_MODEL_NAME"] = "ollama/phi3:3.8b"
    os.environ["OPENAI_API_KEY"] = "ollama"
    
    try:
        # Create LLM without explicit parameters
        llm = LLM()
        print(f"Environment LLM: {llm}")
        
        messages = [{"role": "user", "content": "Hello"}]
        result = llm.call(messages)
        print(f"✅ Environment Approach Success: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Environment Approach Failed: {str(e)}")
        return False

def main():
    print("Deep Debugging Ollama + CrewAI Connection...\n")
    
    # Test 1: Direct Ollama OpenAI API
    if test_ollama_openai_api():
        print("✅ Ollama OpenAI API works")
    else:
        print("❌ Ollama OpenAI API broken - fix this first!")
        return
    
    # Test 2: CrewAI LLM directly 
    if test_crewai_llm_directly():
        print("✅ CrewAI LLM works")
        return
    
    # Test 3: Try smaller model
    if test_different_model():
        print("✅ Smaller model works - use phi3:3.8b")
        return
    
    # Test 4: Environment variables
    if test_environment_approach():
        print("✅ Environment approach works")
        return
    
    print("\n❌ All approaches failed. This might be a CrewAI version issue.")
    
    # Print debug info
    print("\n=== Debug Information ===")
    print(f"Python version: {os.sys.version}")
    
    try:
        import crewai
        print(f"CrewAI version: {crewai.__version__}")
    except:
        print("Cannot get CrewAI version")

if __name__ == "__main__":
    main()
