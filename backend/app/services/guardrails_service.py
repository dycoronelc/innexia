import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class GuardrailResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

@dataclass
class GuardrailCheck:
    result: GuardrailResult
    message: str
    confidence: float
    details: Optional[Dict] = None

class GuardrailsService:
    """
    Servicio de guardrails inspirado en OpenAI AgentKit
    Implementa validaciones de seguridad y contenido para el chatbot de emprendimiento
    """
    
    def __init__(self):
        # Patrones de PII (Información Personal Identificable)
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b'
        }
        
        # Palabras y frases de moderación para emprendimiento
        self.moderation_keywords = {
            'high_risk': [
                'estafa', 'fraude', 'pirámide', 'ponzi', 'esquema ponzi',
                'dinero fácil', 'riqueza rápida', 'inversión garantizada',
                'retorno asegurado', 'sin riesgo', '100% garantizado'
            ],
            'medium_risk': [
                'inversión sin riesgo', 'ganancias seguras', 'multinivel',
                'marketing de red', 'oportunidad única', 'última oportunidad'
            ]
        }
        
        # Patrones de jailbreak específicos para emprendimiento
        self.jailbreak_patterns = [
            r'ignora.*instrucciones',
            r'actúa.*como.*(?:banquero|inversor|asesor financiero)',
            r'no.*eres.*un.*asistente.*de.*emprendimiento',
            r'dame.*consejos.*financieros.*no.*relacionados.*con.*emprendimiento',
            r'ayúdame.*con.*(?:inversiones|trading|forex).*sin.*contexto.*de.*negocio'
        ]

    def check_pii(self, text: str) -> GuardrailCheck:
        """
        Detecta y redacta información personal identificable
        """
        detected_pii = []
        redacted_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected_pii.append({
                    'type': pii_type,
                    'count': len(matches),
                    'matches': matches[:3]  # Solo primeros 3 para logging
                })
                
                # Redactar la información
                redacted_text = re.sub(pattern, f'[REDACTED_{pii_type.upper()}]', redacted_text, flags=re.IGNORECASE)
        
        if detected_pii:
            return GuardrailCheck(
                result=GuardrailResult.FAIL,
                message=f"Se detectó información personal: {', '.join([pii['type'] for pii in detected_pii])}",
                confidence=0.9,
                details={'detected_pii': detected_pii, 'redacted_text': redacted_text}
            )
        
        return GuardrailCheck(
            result=GuardrailResult.PASS,
            message="No se detectó información personal",
            confidence=1.0
        )

    def check_moderation(self, text: str) -> GuardrailCheck:
        """
        Clasifica y bloquea contenido potencialmente dañino o fraudulento
        """
        text_lower = text.lower()
        detected_risks = []
        
        # Verificar palabras de alto riesgo
        high_risk_found = []
        for keyword in self.moderation_keywords['high_risk']:
            if keyword in text_lower:
                high_risk_found.append(keyword)
        
        # Verificar palabras de riesgo medio
        medium_risk_found = []
        for keyword in self.moderation_keywords['medium_risk']:
            if keyword in text_lower:
                medium_risk_found.append(keyword)
        
        if high_risk_found:
            return GuardrailCheck(
                result=GuardrailResult.FAIL,
                message=f"Contenido de alto riesgo detectado: {', '.join(high_risk_found)}",
                confidence=0.95,
                details={'risk_level': 'high', 'keywords': high_risk_found}
            )
        
        if medium_risk_found:
            return GuardrailCheck(
                result=GuardrailResult.WARNING,
                message=f"Contenido de riesgo medio detectado: {', '.join(medium_risk_found)}",
                confidence=0.7,
                details={'risk_level': 'medium', 'keywords': medium_risk_found}
            )
        
        return GuardrailCheck(
            result=GuardrailResult.PASS,
            message="Contenido apropiado para emprendimiento",
            confidence=1.0
        )

    def check_jailbreak(self, text: str) -> GuardrailCheck:
        """
        Detecta intentos de jailbreak o manipulación del asistente
        """
        text_lower = text.lower()
        
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, text_lower):
                return GuardrailCheck(
                    result=GuardrailResult.FAIL,
                    message="Intento de manipulación detectado. Mantén el foco en emprendimiento y creación de negocios.",
                    confidence=0.8,
                    details={'pattern_matched': pattern}
                )
        
        return GuardrailCheck(
            result=GuardrailResult.PASS,
            message="Consulta apropiada para el asistente de emprendimiento",
            confidence=1.0
        )

    def check_business_relevance(self, text: str) -> GuardrailCheck:
        """
        Verifica que la consulta esté relacionada con emprendimiento y creación de negocios
        """
        business_keywords = [
            'negocio', 'empresa', 'emprendimiento', 'startup', 'proyecto',
            'idea de negocio', 'plan de negocio', 'modelo de negocio',
            'mercado', 'clientes', 'producto', 'servicio', 'ventas',
            'marketing', 'finanzas', 'inversión', 'socios', 'equipo',
            'bmc', 'canvas', 'actividades', 'recursos', 'propuesta de valor'
        ]
        
        text_lower = text.lower()
        relevant_keywords = [kw for kw in business_keywords if kw in text_lower]
        
        if len(relevant_keywords) == 0:
            return GuardrailCheck(
                result=GuardrailResult.WARNING,
                message="La consulta no parece estar relacionada con emprendimiento. Intenta reformular tu pregunta enfocándote en creación de negocios.",
                confidence=0.6,
                details={'suggested_keywords': business_keywords[:5]}
            )
        
        return GuardrailCheck(
            result=GuardrailResult.PASS,
            message="Consulta relevante para emprendimiento",
            confidence=0.9,
            details={'matched_keywords': relevant_keywords}
        )

    def validate_input(self, text: str) -> Dict:
        """
        Ejecuta todas las validaciones de guardrails
        """
        checks = {
            'pii': self.check_pii(text),
            'moderation': self.check_moderation(text),
            'jailbreak': self.check_jailbreak(text),
            'business_relevance': self.check_business_relevance(text)
        }
        
        # Determinar resultado general
        has_failures = any(check.result == GuardrailResult.FAIL for check in checks.values())
        has_warnings = any(check.result == GuardrailResult.WARNING for check in checks.values())
        
        if has_failures:
            overall_result = GuardrailResult.FAIL
            overall_message = "La consulta no cumple con los estándares de seguridad"
        elif has_warnings:
            overall_result = GuardrailResult.WARNING
            overall_message = "La consulta tiene advertencias menores"
        else:
            overall_result = GuardrailResult.PASS
            overall_message = "La consulta es apropiada"
        
        return {
            'overall_result': overall_result.value,
            'overall_message': overall_message,
            'checks': {name: {
                'result': check.result.value,
                'message': check.message,
                'confidence': check.confidence,
                'details': check.details
            } for name, check in checks.items()},
            'should_proceed': overall_result != GuardrailResult.FAIL,
            'warnings': [check.message for check in checks.values() if check.result == GuardrailResult.WARNING]
        }

# Instancia global del servicio
guardrails_service = GuardrailsService()

