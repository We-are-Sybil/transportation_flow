from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ServiceType(str, Enum):
    AIRPORT_TRANSFER = "airport_transfer"
    HOURLY_RENTAL = "hourly_rental"
    POINT_TO_POINT = "point_to_point"
    MULTI_DAY = "multi_day"

class TransportationRequest(BaseModel):
    """Complete transportation service request"""
    # Request metadata
    fecha_solicitud: datetime = Field(description="Request date")
    
    # Client information
    nombre_solicitante: str = Field(description="Applicant name")
    cc_nit: str = Field(description="ID or NIT number")
    quien_solicita: str = Field(description="Who is requesting (person/role)")
    celular_contacto: str = Field(description="Contact phone number")
    
    # Service details
    fecha_inicio_servicio: datetime = Field(description="Service start date")
    hora_inicio_servicio: str = Field(description="Service start time")
    direccion_inicio: str = Field(description="Pickup address (City)")
    hora_terminacion: Optional[str] = Field(None, description="Service end time")
    direccion_terminacion: Optional[str] = Field(None, description="Drop-off address (City)")
    
    # Service characteristics
    caracteristicas_servicio: str = Field(description="Service characteristics (frequencies, schedules, conditions)")
    cantidad_pasajeros: int = Field(description="Number of passengers")
    equipaje_carga: bool = Field(description="Whether they carry luggage or cargo")
    
    # Multiple services
    es_servicio_multiple: bool = Field(default=False, description="If multiple services or extends several days")
    servicios_adicionales: Optional[List[dict]] = Field(None, description="Additional service details")
    
    # Derived fields
    service_type: Optional[ServiceType] = None
    
    @validator('celular_contacto')
    def validate_phone(cls, v):
        # Remove spaces and validate Colombian phone format
        phone = v.replace(" ", "").replace("-", "")
        if not phone.startswith("+57") and len(phone) == 10:
            phone = f"+57{phone}"
        return phone

class PartialRequest(BaseModel):
    """Partial request for step-by-step collection"""
    nombre_solicitante: Optional[str] = None
    cc_nit: Optional[str] = None
    celular_contacto: Optional[str] = None
    fecha_inicio_servicio: Optional[str] = None
    hora_inicio_servicio: Optional[str] = None
    direccion_inicio: Optional[str] = None
    direccion_terminacion: Optional[str] = None
    cantidad_pasajeros: Optional[int] = None
    equipaje_carga: Optional[bool] = None
    raw_message: str = Field(description="Original message from user")
    
    def get_missing_fields(self) -> List[str]:
        """Return list of required fields that are missing"""
        required = [
            'nombre_solicitante', 'cc_nit', 'celular_contacto',
            'fecha_inicio_servicio', 'hora_inicio_servicio', 
            'direccion_inicio', 'cantidad_pasajeros'
        ]
        missing = []
        for field in required:
            if getattr(self, field) is None:
                missing.append(field)
        return missing

class ValidationResult(BaseModel):
    """Result of request validation"""
    is_complete: bool
    missing_fields: List[str]
    parsed_data: PartialRequest
    suggested_questions: List[str]
