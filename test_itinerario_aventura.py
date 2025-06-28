#!/usr/bin/env python3
"""
Script de prueba para generar un itinerario de aventura
"""
import requests
import json
from datetime import datetime, timedelta

def test_generar_itinerario_aventura():
    """Prueba la generación de un itinerario de aventura"""
    
    # Configurar fechas (2 días desde mañana)
    fecha_inicio = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    fecha_fin = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Datos del itinerario
    datos_itinerario = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "preferencias_usuario": "Quiero un viaje lleno de aventura, deportes extremos, actividades al aire libre y experiencias emocionantes",
        "presupuesto_total": 900.0,
        "nivel_precio_preferido": 2,  # Moderado
        "titulo": "Aventura Extrema en Lima"
    }
    
    print("🎯 Generando itinerario de aventura...")
    print(f"📅 Fechas: {fecha_inicio} a {fecha_fin}")
    print(f"💰 Presupuesto: S/. {datos_itinerario['presupuesto_total']}")
    print(f"🎨 Preferencias: {datos_itinerario['preferencias_usuario']}")
    print("-" * 60)
    
    try:
        # Hacer la petición a la API
        response = requests.post(
            'http://localhost:8000/api/itinerarios/generar/',
            headers={'Content-Type': 'application/json'},
            json=datos_itinerario,
            timeout=60  # 60 segundos de timeout
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            
            if resultado.get('success'):
                print("✅ ¡Itinerario generado exitosamente!")
                print(f"🆔 ID del itinerario: {resultado['itinerario']['id']}")
                print(f"📋 Título: {resultado['itinerario']['titulo']}")
                print(f"📊 Estadísticas:")
                print(f"   - Costo total: S/. {resultado['itinerario']['estadisticas']['costo_total']}")
                print(f"   - Actividades totales: {resultado['itinerario']['estadisticas']['total_actividades']}")
                print(f"   - Actividades por día: {resultado['itinerario']['estadisticas']['actividades_por_dia']}")
                
                print("\n🏨 Tipos de establecimientos seleccionados:")
                tipos = resultado['itinerario']['tipos_establecimientos_seleccionados']
                for categoria, tipos_list in tipos.items():
                    print(f"   - {categoria}: {', '.join(tipos_list)}")
                
                print("\n📅 DETALLE POR DÍAS:")
                for dia in resultado['dias']:
                    print(f"\n🌅 DÍA {dia['dia_numero']} - {dia['fecha']}")
                    
                    if dia['hotel']:
                        print(f"🏨 Hotel: {dia['hotel']['nombre']} (Rating: {dia['hotel']['rating']})")
                    
                    print(f"📋 Actividades ({len(dia['actividades'])}):")
                    for actividad in dia['actividades']:
                        print(f"   🕐 {actividad['hora_inicio']}-{actividad['hora_fin']} | "
                              f"{actividad['tipo_actividad'].upper()} | "
                              f"{actividad['lugar']['nombre']} "
                              f"(S/. {actividad['costo_estimado'] if actividad['costo_estimado'] else 'N/A'})")
                    
                    print(f"💰 Costo del día: S/. {dia['costo_total_dia']}")
                
                # Verificar variedad de restaurantes
                restaurantes_por_dia = {}
                for dia in resultado['dias']:
                    restaurantes_dia = []
                    for actividad in dia['actividades']:
                        if actividad['tipo_actividad'] == 'restaurante':
                            restaurantes_dia.append(actividad['lugar']['nombre'])
                    restaurantes_por_dia[dia['dia_numero']] = restaurantes_dia
                
                print("\n🍽️ VARIEDAD DE RESTAURANTES:")
                for dia_num, restaurantes in restaurantes_por_dia.items():
                    if restaurantes:
                        print(f"   Día {dia_num}: {', '.join(restaurantes)}")
                    else:
                        print(f"   Día {dia_num}: Sin restaurantes")
                
                # Verificar que no haya restaurantes duplicados
                todos_restaurantes = []
                for restaurantes in restaurantes_por_dia.values():
                    todos_restaurantes.extend(restaurantes)
                
                restaurantes_unicos = set(todos_restaurantes)
                if len(todos_restaurantes) == len(restaurantes_unicos):
                    print("✅ ¡Variedad garantizada! No hay restaurantes duplicados.")
                else:
                    print("⚠️  Hay restaurantes duplicados.")
                
            else:
                print("❌ Error en la generación del itinerario:")
                print(f"   {resultado.get('error', 'Error desconocido')}")
                
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: El servidor no está ejecutándose en localhost:8000")
        print("💡 Asegúrate de que el servidor Django esté iniciado")
    except requests.exceptions.Timeout:
        print("❌ Timeout: La generación del itinerario tardó demasiado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_generar_itinerario_aventura() 