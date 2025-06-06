#!/usr/bin/env python
import os
import json
import uuid
from datetime import datetime
from crewai.flow.flow import Flow, start, listen
from dotenv import load_dotenv
from transportation_flow.schemas.conversation_state import ConversationState
from transportation_flow.schemas.transportation_models import PartialRequest
from transportation_flow.crews.extraction_crew.extraction_crew import ExtractionCrew
from transportation_flow.crews.summary_crew.summary_crew import SummaryCrew

load_dotenv()

class TransportationSystemFlow(Flow[ConversationState]):
    """Conversational flow for transportation requests using proper crews"""
    
    @start()
    def receive_message(self, message: str, sender_id: str = "test_user"):
        """Entry point: receive a message from user"""
        print(f"\n{'='*60}")
        print(f"📨 New message from {sender_id}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        
        # Initialize conversation state if new
        if not self.state.conversation_id:
            self.state.conversation_id = str(uuid.uuid4())
            self.state.sender_id = sender_id
        
        # Add message to history
        self.state.add_message("user", message)
        
        # Build context from previous messages
        context = ""
        if len(self.state.messages) > 1:
            # Get last 3 messages for context
            recent_messages = self.state.messages[-4:-1]  # Exclude current message
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in recent_messages
            ])
        
        # Extract information using crew
        extraction_crew = ExtractionCrew().extraction_crew()
        result = extraction_crew.kickoff(inputs={
            "message": message,
            "context": context
        })
        
        # Parse extracted information
        try:
            extracted_data = json.loads(str(result))
            print(f"\n📊 Extracted data: {json.dumps(extracted_data, indent=2)}")
            
            # Update state with new information
            self.state.update_from_partial(extracted_data)
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse extraction result: {e}")
            print(f"Raw result: {result}")
        
        return self.check_and_respond()
    
    @listen("receive_message")
    def check_and_respond(self):
        """Check if information is complete and respond accordingly"""
        missing = self.state.missing_fields
        
        if not missing:
            # All information complete
            print("\n✅ All information collected!")
            self.state.status = "complete"
            return self.create_service_summary()
        
        # Still missing information
        print(f"\n❓ Missing fields: {missing}")
        self.state.attempts += 1
        
        # Prepare current information for the crew
        current_info = {
            k: v for k, v in self.state.partial_request.model_dump().items()
            if v is not None and k != "raw_message"
        }
        
        # Use conversation crew to ask for missing info
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
        
        # Run conversation crew
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
    
    @listen("check_and_respond")
    def create_service_summary(self):
        """Create final summary using summary crew"""
        if self.state.status != "complete":
            return
        
        print("\n📋 Creating service summary...")
        
        # Prepare request data
        request_data = self.state.partial_request.model_dump()
        
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
            "conversation_id": self.state.conversation_id
        }
    
    def continue_conversation(self, message: str, conversation_id: str):
        """Continue an existing conversation"""
        # Verify conversation ID matches
        if self.state.conversation_id != conversation_id:
            print(f"⚠️ Warning: Conversation ID mismatch")
        
        # Process the new message
        return self.receive_message(message, self.state.sender_id)


def kickoff():
    """Interactive conversation test"""
    print("🚀 Starting Transportation System Interactive Test")
    print("Type 'exit' to quit\n")
    
    flow = TransportationSystemFlow()
    conversation_id = None
    
    while True:
        # Get user input
        message = input("\n👤 You: ").strip()
        
        if message.lower() == 'exit':
            print("\n👋 Goodbye!")
            break
        
        # Process message
        if conversation_id:
            # Continue existing conversation
            result = flow.continue_conversation(message, conversation_id)
        else:
            # Start new conversation
            result = flow.kickoff(inputs={
                "message": message,
                "sender_id": "interactive_user"
            })
        
        # Handle result
        if isinstance(result, dict):
            if result.get("status") == "waiting_for_response":
                # Save conversation ID for continuation
                conversation_id = result.get("conversation_id")
                # Question already printed by the flow
            elif result.get("status") == "complete":
                # Service complete
                print("\n🎉 Service request complete!")
                print("\nStart a new request or type 'exit' to quit.")
                conversation_id = None
                flow = TransportationSystemFlow()  # Reset for new conversation


def plot():
    flow = TransportationSystemFlow()
    return flow.plot()


if __name__ == "__main__":
    kickoff()
