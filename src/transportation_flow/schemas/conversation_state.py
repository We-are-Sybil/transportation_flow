from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from transportation_flow.schemas.transportation_models import (
    TransportationRequest, PartialRequest
)

class ConversationState(BaseModel):
    """State model for transportation request conversations"""
    
    # Flow inputs - these can be set via kickoff(inputs={...})
    current_message: Optional[str] = Field(default="", description="Current message being processed")
    sender_id: Optional[str] = Field(default="", description="User/sender identifier")
    
    # Conversation tracking
    conversation_id: Optional[str] = Field(default="", description="Unique conversation identifier")
    
    # Request data
    partial_request: PartialRequest = Field(
        default_factory=PartialRequest,
        description="Accumulated request information"
    )
    missing_fields: List[str] = Field(
        default_factory=list,
        description="Fields still needed"
    )
    
    # Conversation history
    messages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Conversation history"
    )
    current_question: Optional[str] = Field(
        None,
        description="Current question waiting for answer"
    )
    
    # Flow control
    status: str = Field(
        default="collecting_info",
        description="Current conversation status"
    )
    attempts: int = Field(
        default=0,
        description="Number of information collection attempts"
    )
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def update_from_partial(self, new_data: dict):
        """Update partial request with new data"""
        for key, value in new_data.items():
            if value is not None and hasattr(self.partial_request, key):
                setattr(self.partial_request, key, value)
        
        # Update missing fields
        self.missing_fields = self.partial_request.get_missing_fields()
        
        # Update status
        if not self.missing_fields:
            self.status = "complete"
    
    def get_context_summary(self) -> str:
        """Get a summary of the conversation context"""
        if not self.messages:
            return "No previous conversation"
        
        return f"Conversation with {len(self.messages)} messages, status: {self.status}"
