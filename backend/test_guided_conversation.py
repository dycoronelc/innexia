import requests
import json

def test_guided_conversation():
    base_url = "http://localhost:8000"
    
    # Probar endpoint de preguntas
    print("🔍 Probando endpoint de preguntas...")
    try:
        response = requests.get(f"{base_url}/api/guided-conversation/questions")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Preguntas cargadas: {data['total_questions']} preguntas")
            for i, question in enumerate(data['questions'], 1):
                print(f"  {i}. {question['question']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "="*50)
    
    # Probar endpoint de generación (sin autenticación para ver el error)
    print("🔍 Probando endpoint de generación...")
    try:
        test_data = {
            "business_idea": "Una aplicación de delivery de comida saludable",
            "answers": {
                "location": "Bogotá",
                "target_customers": "Profesionales jóvenes",
                "budget": "$50,000 USD",
                "competition": "Hay competidores pero hay espacio",
                "resources": "Equipo de 3 personas",
                "timeline": "6 meses"
            }
        }
        
        response = requests.post(
            f"{base_url}/api/guided-conversation/generate",
            json=test_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Endpoint protegido correctamente (requiere autenticación)")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_guided_conversation()

