import os
import pdfplumber
import re

# Ruta donde están las facturas
ruta_facturas = r'H:\My Drive\CODIMEC S.A.S - Contabilidad\2024\10. OCTUBRE\FACTURAS ENVIADAS\FACT VENTAS'

# Función para limpiar el nombre eliminando caracteres no válidos
def limpiar_nombre(nombre):
    return re.sub(r'[\\/*?:"<>|]', "", nombre)  # Elimina caracteres no permitidos en nombres de archivo

# Función para extraer los datos de la factura
def extraer_datos_factura(pdf_path):
    texto_completo = ""
    
    # Abrimos el PDF y extraemos el texto de todas las páginas
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text()

    # Extraer el día desde la "Fecha de Expedición" o "Fecha de Generación"
    dia = re.search(r'Fecha de (Expedición|Generación|Emisión):\s+(\d{2})/(\d{2})/(\d{4})', texto_completo)
    dia = dia.group(2) if dia else ""  # Si no encuentra, no agrega día

    # Extraer número de factura o documento (Ejemplos: FE-660, DSE2275, FEBG 41206)
    numero_documento = re.search(r'Número de (Factura|Documento|Nómina):\s+([A-Z0-9-]+)', texto_completo)
    numero_documento = numero_documento.group(2).strip() if numero_documento else "NumDocNoEncontrado"

    # Extraer datos de emisor y adquiriente
    emisor = re.search(r'Razón Social:\s+([^\n]+)', texto_completo)
    adquiriente = re.search(r'Datos del adquiriente\s+Razón Social:\s+([^\n]+)', texto_completo)
    
    emisor = emisor.group(1).strip() if emisor else "EmisorNoEncontrado"
    adquiriente = adquiriente.group(1).strip() if adquiriente else "AdquirienteNoEncontrado"

    # Detectar el tipo de documento: nota crédito, documento soporte, factura de venta, nómina
    es_nota_credito = "Nota Crédito" in texto_completo
    es_documento_soporte = "Documento Soporte" in texto_completo
    es_factura_venta = "Factura de Venta" in texto_completo
    es_nomina = "Nómina" in texto_completo or "Nomina" in texto_completo

    # Determinar proveedor dependiendo de si la empresa es emisor o adquiriente
    empresa = "Compañía de Ingenieros Mecánicos y Civiles S.A.S"
    if empresa in emisor:
        proveedor = adquiriente  # Si la empresa es el emisor, tomamos el adquiriente como proveedor
    elif empresa in adquiriente:
        proveedor = emisor  # Si la empresa es el adquiriente, tomamos el emisor como proveedor
    else:
        proveedor = emisor  # Si no se cumple la condición, tomamos al emisor como proveedor por defecto

    # Si es una nómina, el proveedor será el empleado y número de nómina
    if es_nomina:
        empleado = re.search(r'Nombre:\s+([^\n]+)', texto_completo)
        proveedor = empleado.group(1).strip() if empleado else "EmpleadoNoEncontrado"

    return dia, numero_documento, proveedor, es_nota_credito, es_documento_soporte, es_factura_venta, es_nomina

# Diccionario para meses abreviados
meses = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}

# Función para generar un nombre único si el archivo ya existe
def generar_nombre_unico(ruta, nombre_base):
    contador = 1
    nuevo_nombre = nombre_base
    nuevo_path = os.path.join(ruta, nuevo_nombre)
    while os.path.exists(nuevo_path):
        nuevo_nombre = f"{os.path.splitext(nombre_base)[0]}_{contador}{os.path.splitext(nombre_base)[1]}"
        nuevo_path = os.path.join(ruta, nuevo_nombre)
        contador += 1
    return nuevo_path

# Recorrer todos los archivos PDF en la carpeta
for i, archivo in enumerate(os.listdir(ruta_facturas), start=1):
    if archivo.endswith('.pdf'):
        archivo_completo = os.path.join(ruta_facturas, archivo)

        # Extraer los datos de la factura
        dia, numero_documento, proveedor, es_nota_credito, es_documento_soporte, es_factura_venta, es_nomina = extraer_datos_factura(archivo_completo)

        # Obtener el mes actual en abreviado
        mes_actual_abreviado = meses[9]  # Para septiembre (ajustar según el mes correspondiente)
        mes_actual_numero = 9  # Ajustar según el mes actual (septiembre = 9)

        # Determinar el prefijo según el tipo de documento
        if es_nota_credito:
            prefijo = "NC"
        elif es_documento_soporte:
            prefijo = "DSE"
        elif es_factura_venta:
            prefijo = "FVE"
        elif es_nomina:
            prefijo = "NOM"
        else:
            prefijo = "FAC"  # Asumimos que es una factura si no coincide con los anteriores

        # Limpiar el nombre del proveedor para evitar caracteres inválidos
        proveedor = limpiar_nombre(proveedor)

        # Formar el nuevo nombre
        if dia:  # Si el día está disponible, lo incluimos
            nuevo_nombre = f"{prefijo} - {dia} {mes_actual_abreviado}_{mes_actual_numero}_{numero_documento}_{proveedor}.pdf"
        else:  # Si no se encuentra el día, lo omitimos
            nuevo_nombre = f"{prefijo} - {mes_actual_abreviado}_{mes_actual_numero}_{numero_documento}_{proveedor}.pdf"

        # Limpiar el nuevo nombre por si algún dato aún contiene caracteres no válidos
        nuevo_nombre = limpiar_nombre(nuevo_nombre)

        # Verificar si ya existe un archivo con el mismo nombre y generar uno único si es necesario
        nuevo_path = generar_nombre_unico(ruta_facturas, nuevo_nombre)

        # Renombrar el archivo
        os.rename(archivo_completo, nuevo_path)

        print(f"Renombrado: {archivo} a {nuevo_path}")
