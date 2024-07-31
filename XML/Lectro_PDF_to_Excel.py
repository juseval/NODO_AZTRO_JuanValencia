import os
import re
import PyPDF2
import pandas as pd

def extraer_info_pdf(texto, filename):
    info = {
        'Archivo': filename,
        'Fecha de expedición': None,
        'Número de consecutivo': None,
        'ID (NIT o C.C.)': None,
        'Descripción': None,
        'Tipo': None,
        'Valor gravado con IVA': None,
        'Valor no gravado con IVA': None,
        'Valor de IVA': None,
        'Valor de retención': None,
        'Tarifa de retención': None,
        'Valor total': None,
        'Forma de pago': None
    }
    
    # Imprimir el texto extraído para depuración
    print(f"Texto extraído de {filename}:")
    print(texto[:500])  # Imprimir los primeros 500 caracteres
    print("...")
    
    # Patrones de expresiones regulares (estos son ejemplos y necesitarán ajustes)
    patrones = {
        'Fecha de expedición': r'Fecha.*?:\s*(\d{2}[/-]\d{2}[/-]\d{4})',
        'Número de consecutivo': r'(?:Consecutivo|Factura No\.):\s*(\w+)',
        'ID (NIT o C.C.)': r'(?:NIT|C\.C\.).*?:\s*(\d[\d\.-]*)',
        'Valor gravado con IVA': r'Valor.*?gravado.*?:\s*\$?\s*([\d,.]+)',
        'Valor no gravado con IVA': r'Valor.*?no.*?gravado.*?:\s*\$?\s*([\d,.]+)',
        'Valor de IVA': r'IVA.*?:\s*\$?\s*([\d,.]+)',
        'Valor de retención': r'Retención.*?:\s*\$?\s*([\d,.]+)',
        'Tarifa de retención': r'Tarifa.*?retención.*?:\s*(\d+(?:\.\d+)?)%',
        'Valor total': r'Total.*?:\s*\$?\s*([\d,.]+)',
        'Forma de pago': r'Forma.*?pago.*?:\s*(\w+)'
    }
    
    for campo, patron in patrones.items():
        match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
        if match:
            info[campo] = match.group(1)
        else:
            print(f"No se encontró coincidencia para: {campo}")
    
    # Extraer y analizar la descripción
    desc_match = re.search(r'Descripción.*?:\s*(.+)', texto, re.IGNORECASE | re.DOTALL)
    if desc_match:
        descripcion = desc_match.group(1)
        info['Descripción'] = descripcion
        
        # Análisis simple para determinar si es un servicio o producto
        if 'servicio' in descripcion.lower():
            info['Tipo'] = 'Servicio'
        else:
            info['Tipo'] = 'Producto'
    else:
        print("No se encontró la descripción")
    
    return info

# Directorio donde se encuentran los archivos PDF
pdf_dir = r'H:\My Drive\CODIMEC S.A.S - Contabilidad\2024\1 - ENERO\EGRESOS'

# Lista para almacenar la información extraída
data = []

# Recorrer todos los archivos PDF en el directorio
for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):
        filepath = os.path.join(pdf_dir, filename)
        
        # Abrir el archivo PDF
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Extraer texto de todas las páginas
            texto_completo = ''
            for page in reader.pages:
                texto_completo += page.extract_text()
            
            # Extraer información
            info = extraer_info_pdf(texto_completo, filename)
            data.append(info)

# Crear un DataFrame con la información extraída
df = pd.DataFrame(data)

# Exportar el DataFrame a Excel
df.to_excel('informacion_extraida.xlsx', index=False)

print("La información ha sido extraída y guardada en 'informacion_extraida.xlsx'")