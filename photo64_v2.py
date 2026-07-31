import cv2
import base64
import numpy as np
from PIL import Image
import io
import time
import conexion
import os


def capturar_y_convertir():
    """
    Captura una foto de la cámara, la convierte a base64 y la guarda en un archivo txt
    """
    # Inicializar cámara
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara")
        return None
    
    # Variables para el temporizador
    inicio = time.time()
    foto_tomada = False

    tiempo_segundos = conexion.configurador()
    tiempo_segundos = tiempo_segundos[5]
    
    while True:
        # Capturar frame
        ret, frame = cap.read()
        
        if not ret:
            # print("Error al capturar el frame")
            break
        
        # Redimensionar para mejor visualización
        frame_redimensionado = cv2.resize(frame, (640, 480))
        
        # Crear imagen con marco
        marco_size = 30
        alto, ancho = 480, 640
        imagen_con_marco = np.ones((alto + marco_size*2, ancho + marco_size*2, 3), dtype=np.uint8) * 240
        
        # Dibujar recuadro interior (donde va la imagen)
        cv2.rectangle(imagen_con_marco, 
                     (marco_size-2, marco_size-2), 
                     (ancho + marco_size+2, alto + marco_size+2), 
                     (0, 0, 255), 3)  # Recuadro rojo
        
        # Dibujar segundo recuadro interior más sutil
        cv2.rectangle(imagen_con_marco, 
                     (marco_size-8, marco_size-8), 
                     (ancho + marco_size+8, alto + marco_size+8), 
                     (100, 100, 100), 1)
        
        # Colocar la imagen dentro del marco
        imagen_con_marco[marco_size:marco_size+alto, marco_size:marco_size+ancho] = frame_redimensionado
        
        # Mostrar contador en la esquina superior izquierda
        tiempo_transcurrido = time.time() - inicio
        segundos_restantes = max(0, int(tiempo_segundos) - int(tiempo_transcurrido))
        
        if segundos_restantes > 0:
            cv2.putText(imagen_con_marco, f"Foto en: {segundos_restantes}s", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(imagen_con_marco, "¡CAPTURANDO!", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Mostrar la imagen con el marco
        cv2.imshow('Marco de Captura', imagen_con_marco)
        
        # Tomar foto automáticamente después de 3 segundos
        if tiempo_transcurrido >= float(tiempo_segundos) and not foto_tomada:
            foto_tomada = True
            foto = frame_redimensionado.copy()
            # print("📸 Foto capturada!")
            break
        
        # Salir con ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    # Cerrar la ventana inmediatamente después de capturar
    cap.release()
    cv2.destroyAllWindows()
    
    if not foto_tomada:
        # print("No se tomó ninguna foto")
        return None
    
    # Convertir la imagen a base64 con el menor tamaño posible
    # print("🔄 Comprimiendo y convirtiendo a base64...")
    
    # Convertir de BGR a RGB para PIL
    foto_rgb = cv2.cvtColor(foto, cv2.COLOR_BGR2RGB)
    imagen_pil = Image.fromarray(foto_rgb)
    
    # Guardar en buffer con compresión máxima
    buffer = io.BytesIO()
    imagen_pil.save(buffer, format='PNG', optimize=True, compress_level=9)
    
    # Obtener bytes y convertir a base64
    imagen_bytes = buffer.getvalue()
    imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
    
    # Mostrar información en consola
    # print("\n" + "="*60)
    # print("INFORMACIÓN DE LA IMAGEN")
    # print("="*60)
    # print(f"📐 Dimensiones: {foto.shape[1]}x{foto.shape[0]} píxeles")
    # print(f"💾 Tamaño original: {len(imagen_bytes):,} bytes")
    # print(f"📝 Tamaño base64: {len(imagen_base64):,} caracteres")
    # print("="*60)
        
    
    # Mostrar solo un resumen del base64 en consola
    
    # print(f"📄 Primeros 100 caracteres: {imagen_base64[:100]}...")
    # print(f"📄 Últimos 100 caracteres: ...{imagen_base64[-100:]}")
    # print(f"✅ Longitud total: {len(imagen_base64):,} caracteres")
    
    # Mostrar la foto capturada con su marco final (se cierra automáticamente)
    mostrar_foto_final_con_cierre_automatico(imagen_base64, foto)
    
    return imagen_base64


def mostrar_foto_final_con_cierre_automatico(imagen_base64, foto_original):
    """
    Muestra la foto capturada con un marco y la cierra automáticamente después de 2 segundos
    """
    try:
        tiempo_segundos = conexion.configurador()
        tiempo_segundos = tiempo_segundos[5]

        # Decodificar para mostrar
        imagen_bytes = base64.b64decode(imagen_base64)
        buffer = io.BytesIO(imagen_bytes)
        imagen_pil = Image.open(buffer)
        imagen_cv = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)
        
        # Crear imagen de visualización
        alto, ancho = 480, 640
        display_img = np.ones((alto + 80, ancho, 3), dtype=np.uint8) * 255
        
        # Colocar la foto en la parte superior
        display_img[0:alto, 0:ancho] = imagen_cv
        
        # Dibujar marco rojo alrededor de la foto
        cv2.rectangle(display_img, (2, 2), (ancho-2, alto-2), (0, 0, 255), 3)
        
        # Agregar información en la parte inferior
        # info_texto = f"Base64: {len(imagen_base64):,} caracteres"
        # cv2.putText(display_img, info_texto, (10, alto + 30), 
        #            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # cv2.putText(display_img, "Guardado en archivo .txt", 
        #            (10, alto + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 0), 1)
        
        # Mostrar la imagen
        cv2.imshow(f'Foto Capturada - Cerrando en {tiempo_segundos} segundos...', display_img)
        
        # Esperar 3 segundos y cerrar automáticamente
        tiempo_inicio = time.time()
        while time.time() - tiempo_inicio < float(tiempo_segundos):
            if cv2.waitKey(1) & 0xFF == 27:  # Permitir cerrar con ESC
                break
            time.sleep(0.1)
        
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"❌ Error al mostrar la foto final: {e}")
        # Mostrar la foto original si hay error
        cv2.imshow('Foto Capturada', foto_original)
        time.sleep(2)
        cv2.destroyAllWindows()

print(capturar_y_convertir())