import os
import re
import PyPDF2
import pandas as pd
from datetime import datetime

def separar_nombre(nombre_completo):
    partes = nombre_completo.split()
    if len(partes) == 1:
        return partes[0], '', '', ''
    elif len(partes) == 2:
        return partes[0], '', partes[1], ''
    elif len(partes) == 3:
        return partes[0], '', partes[1], partes[2]
    else:
        return partes[0], partes[1], partes[2], ' '.join(partes[3:])

def extraer_info_pdf(texto, filename):
    info = {
        'Archivo': filename,
        'Fecha de emisión': None,
        'Número de factura': None,
        'NIT del emisor': None,
        'NIT del adquiriente': None,
        'Razón social del emisor': None,
        'Razón social del adquiriente': None,
        'Primer nombre emisor': None,
        'Segundo nombre emisor': None,
        'Primer apellido emisor': None,
        'Segundo apellido emisor': None,
        'Primer nombre adquiriente': None,
        'Segundo nombre adquiriente': None,
        'Primer apellido adquiriente': None,
        'Segundo apellido adquiriente': None,
        'Tipo de contribuyente emisor': None,
        'Tipo de contribuyente adquiriente': None,
        'Tipo de documento emisor': None,
        'Tipo de documento adquiriente': None,
        'Régimen fiscal emisor': None,
        'Régimen fiscal adquiriente': None,
        'Responsabilidad tributaria emisor': None,
        'Responsabilidad tributaria adquiriente': None,
        'Actividad económica emisor': None,
        'País emisor': None,
        'País adquiriente': None,
        'Departamento emisor': None,
        'Departamento adquiriente': None,
        'Municipio/Ciudad emisor': None,
        'Municipio/Ciudad adquiriente': None,
        'Dirección emisor': None,
        'Dirección adquiriente': None,
        'Teléfono/Móvil emisor': None,
        'Teléfono/Móvil adquiriente': None,
        'Correo emisor': None,
        'Correo adquiriente': None,
        'Subtotal': None,
        'Descuento detalle': None,
        'Recargo detalle': None,
        'Total bruto factura': None,
        'IVA': None,
        'INC': None,
        'Bolsas': None,
        'Otros impuestos': None,
        'Total impuesto': None,
        'Total neto factura': None,
        'Descuento Global': None,
        'Recargo Global': None,
        'Total factura': None,
        'Anticipos': None,
        'Retefuente': None,
        'Reteiva': None,
        'Reteica': None,
        'Forma de pago': None
    }
    
    # Patrones de expresiones regulares para información general
    patrones = {
        'Fecha de emisión': r'Fecha de Emisión:\s*(\d{2}/\d{2}/\d{4})',
        'Número de factura': r'Número de Factura:\s*([\w-]+)',
        'NIT del emisor': r'Nit del Emisor:\s*(\d+)',
        'NIT del adquiriente': r'Número Documento:\s*(\d+)',
        'Razón social del emisor': r'Razón Social:\s*(.+?)\n',
        'Razón social del adquiriente': r'Nombre o Razón Social:\s*(.+?)\n',
        'Tipo de contribuyente emisor': r'Tipo de Contribuyente:\s*(.+?)\n',
        'Tipo de contribuyente adquiriente': r'Tipo de Contribuyente:\s*(.+?)\n',
        'Régimen fiscal emisor': r'Régimen Fiscal:\s*(.+?)\n',
        'Régimen fiscal adquiriente': r'Régimen fiscal:\s*(.+?)\n',
        'Responsabilidad tributaria emisor': r'Responsabilidad tributaria:\s*(.+?)\n',
        'Responsabilidad tributaria adquiriente': r'Responsabilidad tributaria:\s*(.+?)\n',
        'Actividad económica emisor': r'Actividad Económica:\s*(.+?)\n',
        'Subtotal': r'Subtotal\s*([\d,.]+)',
        'Descuento detalle': r'Descuento detalle\s*([\d,.]+)',
        'Recargo detalle': r'Recargo detalle\s*([\d,.]+)',
        'Total bruto factura': r'Total Bruto Factura\s*([\d,.]+)',
        'IVA': r'IVA\s*([\d,.]+)',
        'INC': r'INC\s*([\d,.]+)',
        'Bolsas': r'Bolsas\s*([\d,.]+)',
        'Otros impuestos': r'Otros impuestos\s*([\d,.]+)',
        'Total impuesto': r'Total impuesto \(=\)\s*([\d,.]+)',
        'Total neto factura': r'Total neto factura \(=\)\s*([\d,.]+)',
        'Descuento Global': r'Descuento Global \(-\)\s*([\d,.]+)',
        'Recargo Global': r'Recargo Global \(\+\)\s*([\d,.]+)',
        'Total factura': r'Total factura \(=\)\s*COP \$ ([\d,.]+)',
        'Anticipos': r'Anticipos\s*([\d,.]+)',
        'Retefuente': r'Rete fuente\s*([\d,.]+)',
        'Reteiva': r'Rete IVA\s*([\d,.]+)',
        'Reteica': r'Rete ICA\s*([\d,.]+)',
        'Forma de pago': r'Forma de pago:\s*(.+?)\n'
    }
    
    for campo, patron in patrones.items():
        match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
        if match:
            info[campo] = match.group(1).strip()
        else:
            print(f"No se encontró coincidencia para: {campo}")
    
    # Extraer información específica del emisor y adquiriente
    emisor_section = re.search(r'Datos del Emisor / Vendedor(.*?)Datos del Adquiriente / Comprador', texto, re.DOTALL)
    adquiriente_section = re.search(r'Datos del Adquiriente / Comprador(.*?)Detalles de Productos', texto, re.DOTALL)
    
    if emisor_section:
        emisor_text = emisor_section.group(1)
        info['Correo emisor'] = re.search(r'Correo:\s*(.+?)\n', emisor_text)
        info['Teléfono/Móvil emisor'] = re.search(r'Teléfono / Móvil:\s*(.+?)\n', emisor_text)
        info['Departamento emisor'] = re.search(r'Departamento:\s*(.+?)\n', emisor_text)
        info['Municipio/Ciudad emisor'] = re.search(r'Municipio / Ciudad:\s*(.+?)\n', emisor_text)
        info['Dirección emisor'] = re.search(r'Dirección:\s*(.+?)\n', emisor_text)
        info['País emisor'] = re.search(r'País:\s*(.+?)\n', emisor_text)
        
        for key in ['Correo emisor', 'Teléfono/Móvil emisor', 'Departamento emisor', 'Municipio/Ciudad emisor', 'Dirección emisor', 'País emisor']:
            if info[key]:
                info[key] = info[key].group(1).strip()
    
    if adquiriente_section:
        adquiriente_text = adquiriente_section.group(1)
        info['Correo adquiriente'] = re.search(r'Correo:\s*(.+?)\n', adquiriente_text)
        info['Teléfono/Móvil adquiriente'] = re.search(r'Teléfono / Móvil:\s*(.+?)\n', adquiriente_text)
        info['Departamento adquiriente'] = re.search(r'Departamento:\s*(.+?)\n', adquiriente_text)
        info['Municipio/Ciudad adquiriente'] = re.search(r'Municipio / Ciudad:\s*(.+?)\n', adquiriente_text)
        info['Dirección adquiriente'] = re.search(r'Dirección:\s*(.+?)\n', adquiriente_text)
        info['País adquiriente'] = re.search(r'País:\s*(.+?)\n', adquiriente_text)
        
        for key in ['Correo adquiriente', 'Teléfono/Móvil adquiriente', 'Departamento adquiriente', 'Municipio/Ciudad adquiriente', 'Dirección adquiriente', 'País adquiriente']:
            if info[key]:
                info[key] = info[key].group(1).strip()
    
    # Convertir la fecha al formato MM/DD/YYYY
    if info['Fecha de emisión']:
        fecha = datetime.strptime(info['Fecha de emisión'], '%d/%m/%Y')
        info['Fecha de emisión'] = fecha.strftime('%m/%d/%Y')
    
    # Separar nombres del emisor y adquiriente
    if info['Razón social del emisor']:
        info['Primer nombre emisor'], info['Segundo nombre emisor'], info['Primer apellido emisor'], info['Segundo apellido emisor'] = separar_nombre(info['Razón social del emisor'])
    
    if info['Razón social del adquiriente']:
        info['Primer nombre adquiriente'], info['Segundo nombre adquiriente'], info['Primer apellido adquiriente'], info['Segundo apellido adquiriente'] = separar_nombre(info['Razón social del adquiriente'])
    
    return info

# El resto del código permanece igual...

# El resto del código permanece igual...

# Directorio donde se encuentran los archivos PDF
pdf_dir = r'C:\Users\USUARIO\Documents\EMPRESAS IMPUESTOS\LICO CASTILLO S.A.S\2024\CONTABILIDAD\JULIO\FACTURAS ENVIADAS'

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