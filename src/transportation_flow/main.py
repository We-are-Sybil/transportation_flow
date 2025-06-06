#!/usr/bin/env python
import os
import json
import uuid
from datetime import datetime
from crewai.flow.flow import Flow, start, listen
from dotenv import load_dotenv
from transportation_flow.schemas.conversation_state import ConversationState
from transportation_flow.crews.extraction_crew.extraction_crew import ExtractionCrew
from transportation_flow.crews.summary_crew.summary_crew import SummaryCrew

load_dotenv()

class TransportationSystemFlow(Flow[ConversationState]):
    """Simple conversational flow for transportation requests"""
    
    @start()
    def initialize_conversation(self):
        """Initialize the conversation - this is the entry point"""
        print(f"\n{'='*60}")
        print(f"🚀 Starting Transportation Flow")
        print(f"Flow ID: {self.state.id}")
        print(f"{'='*60}\n")
        
        # Initialize conversation state if needed
        if not self.state.conversation_id:
            self.state.conversation_id = str(uuid.uuid4())
        
        # The state will be initialized based on what we pass to kickoff()
        print(f"State initialized: {self.state}")
        
        return "Flow initialized successfully"
    
    @listen("initialize_conversation")
    def process_user_message(self, init_result):
        """Process the user's message with extraction crew"""
        # Get the message from state (passed via kickoff inputs)
        message = getattr(self.state, 'current_message', '')
        sender_id = getattr(self.state, 'sender_id', 'unknown')
        
        print(f"📨 Processing message from {sender_id}: {message}")
        
        if not message:
            return {
                "error": "No message to process",
                "status": "error"
            }
        
        # Add message to history
        self.state.add_message("user", message)
        
        # Build context from previous messages for better extraction
        context = ""
        if len(self.state.messages) > 1:
            recent_messages = self.state.messages[-4:-1]  # Last 3 messages excluding current
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in recent_messages
            ])
        
        # Extract information using crew
        try:
            extraction_crew = ExtractionCrew().extraction_crew()
            result = extraction_crew.kickoff(inputs={
                "message": message,
                "context": context
            })
            
            # Parse extracted information
            extracted_data = json.loads(str(result))
            print(f"📊 Extracted data: {json.dumps(extracted_data, indent=2)}")
            
            # Update state with new information
            self.state.update_from_partial(extracted_data)
            
            return {
                "extraction_result": extracted_data,
                "status": "extracted"
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse extraction result: {e}")
            return {
                "error": f"Extraction parsing failed: {e}",
                "status": "error"
            }
        except Exception as e:
            print(f"❌ Extraction crew failed: {e}")
            return {
                "error": f"Extraction failed: {e}",
                "status": "error"
            }
    
    @listen("process_user_message")
    def check_completeness_and_respond(self, extraction_result):
        """Check if we have all information or need to ask for more"""
        if extraction_result.get("status") == "error":
            return extraction_result
        
        missing = self.state.missing_fields
        
        if not missing:
            # All information complete - proceed to summary
            print("\n✅ All information collected!")
            self.state.status = "complete"
            return {
                "status": "complete",
                "message": "Information complete - creating summary"
            }
        
        # Still missing information - ask for it
        print(f"\n❓ Missing fields: {missing}")
        self.state.attempts += 1
        
        # Prepare current information for conversation crew
        current_info = {
            k: v for k, v in self.state.partial_request.model_dump().items()
            if v is not None and k != "raw_message"
        }
        
        # Use conversation crew to ask for missing info
        try:
            conversation_crew = ExtractionCrew().conversation_crew()
            
            # Format missing fields in Spanish
            field_names = {
                'nombre_solicitante': 'nombre completo',
                'cc_nit': 'cédula o NIT',
                'celular_contacto': 'número de celular',
                'fecha_inicio_servicio': 'fecha del servicio',
                'hora_inicio_servicio': 'hora de inicio',
                'direccion_inicio': 'dirección de recogida',
                'direccion_terminacion': 'dirección de destino',
                'cantidad_pasajeros': 'cantidad de pasajeros',
                'equipaje_carga': 'si llevan equipaje'
            }
            
            missing_fields_spanish = [field_names.get(f, f) for f in missing[:3]]
            
            # Generate question
            question = conversation_crew.kickoff(inputs={
                "current_info": json.dumps(current_info, ensure_ascii=False),
                "missing_fields": ", ".join(missing_fields_spanish)
            })
            
            # Store the question
            self.state.current_question = str(question)
            self.state.add_message("assistant", str(question))
            
            print(f"\n🤖 Assistant: {question}")
            
            return {
                "status": "waiting_for_response",
                "question": str(question),
                "missing_fields": missing,
                "conversation_id": self.state.conversation_id
            }
            
        except Exception as e:
            print(f"❌ Conversation crew failed: {e}")
            return {
                "error": f"Question generation failed: {e}",
                "status": "error"
            }
    
    @listen("check_completeness_and_respond")
    def create_final_summary(self, completion_result):
        """Create final summary if all information is complete"""
        if completion_result.get("status") != "complete":
            return completion_result
        
        print("\n📋 Creating service summary...")
        
        # Prepare request data
        request_data = self.state.partial_request.model_dump()
        
        try:
            # Use summary crew
            summary_crew = SummaryCrew().crew()
            summary = summary_crew.kickoff(inputs={
                "request_data": json.dumps(request_data, ensure_ascii=False)
            })
            
            # Add summary to conversation
            self.state.add_message("assistant", str(summary))
            
            print(f"\n✅ Summary created:\n{summary}")
            
            return {
                "status": "complete",
                "summary": str(summary),
                "request_data": request_data,
                "conversation_id": self.state.conversation_id,
                "final_result": True
            }
            
        except Exception as e:
            print(f"❌ Summary creation failed: {e}")
            return {
                "error": f"Summary creation failed: {e}",
                "status": "error"
            }


def test_single_message():
    """Test with a single message"""
    print("🧪 Testing single message...")
    
    flow = TransportationSystemFlow()
    
    # Test message
    test_message = "Quiero un servicio de transporte al aeropuerto mañana a las 3am."
    
    # Create initial state with the message
    result = flow.kickoff(inputs={
        "current_message": test_message,
        "sender_id": "test_user"
    })
    
    print(f"\n📤 Final result: {result}")
    print(f"📊 Final state: {flow.state}")
    
    return flow, result


def interactive_conversation():
    """Interactive conversation test"""
    print("🚀 Starting Transportation System Interactive Test")
    print("Type 'exit' to quit, 'new' to start fresh conversation\n")
    
    flow = None
    
    while True:
        # Get user input
        message = input("\n👤 You: ").strip()
        
        if message.lower() == 'exit':
            print("\n👋 Goodbye!")
            break
        
        if message.lower() == 'new':
            print("\n🔄 Starting new conversation...")
            flow = None
            continue
        
        if not flow:
            # Start new conversation
            flow = TransportationSystemFlow()
            result = flow.kickoff(inputs={
                "current_message": message,
                "sender_id": "interactive_user"
            })
        else:
            # Continue existing conversation
            # Update the state with new message and re-run from process_user_message
            flow.state.current_message = message
            result = flow.process_user_message("continuing")
            
            # Process the result through the chain
            if result.get("status") == "extracted":
                result = flow.check_completeness_and_respond(result)
                
                if result.get("status") == "complete":
                    result = flow.create_final_summary(result)
        
        # Handle result
        if isinstance(result, dict):
            if result.get("status") == "waiting_for_response":
                # Continue conversation
                pass
            elif result.get("status") == "complete" and result.get("final_result"):
                # Service complete
                print("\n🎉 Service request complete!")
                print("\nType 'new' for a new request or 'exit' to quit.")
                flow = None
            elif result.get("status") == "error":
                print(f"\n❌ Error: {result.get('error')}")
                print("Please try again or type 'new' to start over.")


def kickoff():
    """Main entry point"""
    print("Choose test mode:")
    print("1. Single message test")
    print("2. Interactive conversation")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_single_message()
    else:
        interactive_conversation()


def plot():
    """Generate flow diagram"""
    flow = TransportationSystemFlow()
    return flow.plot()


if __name__ == "__main__":
    kickoff()
