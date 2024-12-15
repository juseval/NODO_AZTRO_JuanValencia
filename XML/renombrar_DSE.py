import os
import re
import PyPDF2
from datetime import datetime

# Función para limpiar el nombre del vendedor
def limpiar_nombre_vendedor(nombre):
    nombre_limpio = re.sub(r'[<>:"/\\|?*]', '', nombre)
    nombre_limpio = nombre_limpio.replace('?', 'ñ')
    return nombre_limpio

# Función para extraer el contenido de un PDF
def extraer_contenido_pdf(ruta_pdf):
    with open(ruta_pdf, 'rb') as archivo:
        lector_pdf = PyPDF2.PdfReader(archivo)
        contenido = ''
        for pagina in lector_pdf.pages:
            contenido += pagina.extract_text()
        return contenido

# Función para extraer la fecha y el nombre del vendedor
def extraer_datos(contenido):
    fecha_generacion = re.search(r'Fecha de generación:\s*(\d{2}/\d{2}/\d{4})', contenido)
    fecha_generacion = fecha_generacion.group(1) if fecha_generacion else None

    razon_social_vendedor = re.search(r'Datos del vendedor\s*Razón social:\s*(.+?)\n', contenido)
    razon_social_vendedor = razon_social_vendedor.group(1).strip() if razon_social_vendedor else None
    
    return fecha_generacion, razon_social_vendedor

# Función para extraer el número de documento (DSEXXXX)
def extraer_numero_documento(contenido):
    numero_documento = re.search(r'Número de documento:\s*(DSE\d+)', contenido)
    return numero_documento.group(1) if numero_documento else 'NumDocNoEncontrado'

# Función para formatear la fecha
def formatear_fecha(fecha):
    fecha_obj = datetime.strptime(fecha, '%d/%m/%Y')
    mes_abreviado = fecha_obj.strftime('%b').upper()  # Mes abreviado en letras
    dia = fecha_obj.day
    return f'{mes_abreviado}_{dia}'

# Verificar si el archivo ya existe y generar un nombre único
def generar_nombre_unico(ruta_carpeta, nuevo_nombre_base):
    contador = 1
    nuevo_nombre = nuevo_nombre_base
    while os.path.exists(os.path.join(ruta_carpeta, nuevo_nombre)):
        nuevo_nombre = f"{nuevo_nombre_base}_{contador}.pdf"
        contador += 1
    return nuevo_nombre

# Ruta de la carpeta
ruta_carpeta = r'H:\My Drive\CODIMEC S.A.S - Contabilidad\2024\10. OCTUBRE\FACTURAS ENVIADAS\FACT VENTAS'

# Renombrar los archivos PDF
for archivo in os.listdir(ruta_carpeta):
    if archivo.endswith('.pdf'):
        ruta_pdf = os.path.join(ruta_carpeta, archivo)
        
        # Asegurarse de que el archivo no esté siendo utilizado por otro proceso
        try:
            contenido = extraer_contenido_pdf(ruta_pdf)
            
            # Extraer la fecha de generación, la razón social del vendedor y el número de documento
            fecha_generacion, razon_social_vendedor = extraer_datos(contenido)
            numero_documento = extraer_numero_documento(contenido)  # Extraer el número de documento
            
            if fecha_generacion and razon_social_vendedor:
                razon_social_vendedor_limpia = limpiar_nombre_vendedor(razon_social_vendedor)
                fecha_formateada = formatear_fecha(fecha_generacion)
                nuevo_nombre_base = f'DSE_{fecha_formateada}_{numero_documento}_{razon_social_vendedor_limpia}.pdf'
                
                # Generar un nombre único si el archivo ya existe
                nuevo_nombre = generar_nombre_unico(ruta_carpeta, nuevo_nombre_base)
                
                # Renombrar el archivo
                nueva_ruta_pdf = os.path.join(ruta_carpeta, nuevo_nombre)
                os.rename(ruta_pdf, nueva_ruta_pdf)
                print(f'Renombrado: {archivo} -> {nuevo_nombre}')
            else:
                print(f'No se pudo extraer la información de: {archivo}')
        
        except PermissionError as e:
            print(f"Error de permiso al acceder al archivo {archivo}: {e}")
        
        except Exception as e:
            print(f"Error inesperado al procesar el archivo {archivo}: {e}")
