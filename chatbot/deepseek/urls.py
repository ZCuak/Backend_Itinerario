from django.urls import path
from . import views

urlpatterns = [
    # API básica de DeepSeek
    path('test-prompt/', views.test_prompt, name='test_prompt'),
    
    # API de procesamiento de lenguaje natural
    path('procesar-consulta/', views.procesar_consulta_nlp, name='procesar_consulta_nlp'),
    path('analizar-intencion/', views.analizar_intencion_usuario, name='analizar_intencion_usuario'),
    path('extraer-caracteristicas/', views.extraer_caracteristicas_texto, name='extraer_caracteristicas_texto'),
    
    # API de generación de contenido
    path('generar-resumen/', views.generar_resumen_lugar, name='generar_resumen_lugar'),
    path('extraer-caracteristicas-lugar/', views.extraer_caracteristicas_lugar, name='extraer_caracteristicas_lugar'),
    
    # API de procesamiento en lotes
    path('procesar-lotes/', views.procesar_lotes_lugares, name='procesar_lotes_lugares'),
] 