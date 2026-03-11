from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime
import json

class BusinessModelCanvasBase(BaseModel):
    key_partners: Optional[Union[List[str], str]] = []
    key_activities: Optional[Union[List[str], str]] = []
    key_resources: Optional[Union[List[str], str]] = []
    value_propositions: Optional[Union[List[str], str]] = []
    customer_relationships: Optional[Union[List[str], str]] = []
    channels: Optional[Union[List[str], str]] = []
    customer_segments: Optional[Union[List[str], str]] = []
    cost_structure: Optional[Union[List[str], str]] = []
    revenue_streams: Optional[Union[List[str], str]] = []
    
    @field_validator('key_partners', 'key_activities', 'key_resources', 'value_propositions', 
                    'customer_relationships', 'channels', 'customer_segments', 'cost_structure', 'revenue_streams')
    @classmethod
    def convert_to_json_string(cls, v):
        if isinstance(v, list):
            return json.dumps(v, ensure_ascii=False)
        elif isinstance(v, str):
            # Si ya es un string JSON, devolverlo tal como está
            try:
                json.loads(v)
                return v
            except json.JSONDecodeError:
                # Si no es JSON válido, convertirlo a lista y luego a JSON
                return json.dumps([v], ensure_ascii=False)
        return json.dumps([], ensure_ascii=False)

class BusinessModelCanvasCreate(BusinessModelCanvasBase):
    project_id: int

class BusinessModelCanvasUpdate(BaseModel):
    key_partners: Optional[Union[List[str], str]] = None
    key_activities: Optional[Union[List[str], str]] = None
    key_resources: Optional[Union[List[str], str]] = None
    value_propositions: Optional[Union[List[str], str]] = None
    customer_relationships: Optional[Union[List[str], str]] = None
    channels: Optional[Union[List[str], str]] = None
    customer_segments: Optional[Union[List[str], str]] = None
    cost_structure: Optional[Union[List[str], str]] = None
    revenue_streams: Optional[Union[List[str], str]] = None
    
    @field_validator('key_partners', 'key_activities', 'key_resources', 'value_propositions', 
                    'customer_relationships', 'channels', 'customer_segments', 'cost_structure', 'revenue_streams')
    @classmethod
    def convert_to_json_string(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return json.dumps(v, ensure_ascii=False)
        elif isinstance(v, str):
            # Si ya es un string JSON, devolverlo tal como está
            try:
                json.loads(v)
                return v
            except json.JSONDecodeError:
                # Si no es JSON válido, convertirlo a lista y luego a JSON
                return json.dumps([v], ensure_ascii=False)
        return json.dumps([], ensure_ascii=False)

class BusinessModelCanvasInDB(BaseModel):
    id: int
    project_id: int
    key_partners: Optional[str] = None
    key_activities: Optional[str] = None
    key_resources: Optional[str] = None
    value_propositions: Optional[str] = None
    customer_relationships: Optional[str] = None
    channels: Optional[str] = None
    customer_segments: Optional[str] = None
    cost_structure: Optional[str] = None
    revenue_streams: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @field_validator('key_partners', 'key_activities', 'key_resources', 'value_propositions', 
                    'customer_relationships', 'channels', 'customer_segments', 'cost_structure', 'revenue_streams')
    @classmethod
    def parse_json_string(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

class BusinessModelCanvas(BusinessModelCanvasInDB):
    pass

