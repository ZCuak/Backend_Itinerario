#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla itinerario
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinerario_backend.settings')
django.setup()

from django.db import connection

def check_itinerario_structure():
    """Verifica la estructura de la tabla itinerario"""
    
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE itinerario")
        columns = cursor.fetchall()
        
        print("📋 Estructura actual de la tabla 'itinerario':")
        print("-" * 50)
        
        for column in columns:
            field_name = column[0]
            field_type = column[1]
            null_allowed = column[2]
            key_type = column[3]
            default_value = column[4]
            
            print(f"  {field_name:<20} {field_type:<20} {'NULL' if null_allowed == 'YES' else 'NOT NULL':<10} {default_value or 'NULL'}")
        
        print("-" * 50)
        print(f"Total de campos: {len(columns)}")

if __name__ == "__main__":
    check_itinerario_structure() 