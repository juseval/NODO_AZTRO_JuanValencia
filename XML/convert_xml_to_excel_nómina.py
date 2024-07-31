import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime

def safe_find(element, path, namespaces, attribute=None):
    found = element.find(path, namespaces)
    if found is not None:
        if attribute:
            return found.get(attribute, '')
        return found.text if found.text is not None else ''
    return ''

def parse_payroll(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
        return None
    
    ns = {
        '': 'dian:gov:co:facturaelectronica:NominaIndividual',
        'ds': 'http://www.w3.org/2000/09/xmldsig#',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'xades': 'http://uri.etsi.org/01903/v1.3.2#',
        'xades141': 'http://uri.etsi.org/01903/v1.4.1#',
        'xs': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    payroll_data = {
        'Nombre del Archivo': os.path.basename(xml_file),
        'Número de Nómina': safe_find(root, './/NumeroSecuenciaXML', ns, 'Numero'),
        'Fecha de Emisión': safe_find(root, './/InformacionGeneral', ns, 'FechaGen'),
        'ID del Empleado': safe_find(root, './/Trabajador', ns, 'NumeroDocumento'),
        'Nombre del Empleado': f"{safe_find(root, './/Trabajador', ns, 'PrimerNombre')} {safe_find(root, './/Trabajador', ns, 'PrimerApellido')}",
        'Nombre del Empleador': safe_find(root, './/Empleador', ns, 'RazonSocial'),
        'NIT del Empleador': safe_find(root, './/Empleador', ns, 'NIT'),
    }

    # Devengados
    devengados_concepts = [
        'Salario Básico', 'Auxilio de Transporte', 'HEDs', 'HENs', 'HEDDFs', 'HRDDFs', 'HENDFs', 'HRNDFs',
        'Vacaciones', 'Primas', 'Cesantías', 'Intereses a Cesantías', 'Incapacidades', 'Licencias',
        'Bonificaciones', 'Auxilios', 'Compensaciones', 'Bono EPCTVs', 'Comisiones'
    ]

    for concept in devengados_concepts:
        payroll_data[concept] = safe_find(root, f'.//Devengados/{concept.replace(" ", "")}', ns, 'Pago') or '0'

    # Otros conceptos
    otros_conceptos = ['Prov. Cesantías', 'Int. Cesantías', 'Prov. Vacaciones', 'Prov. Prima']
    for concepto in otros_conceptos:
        payroll_data[f'Otros - {concepto}'] = '0'  # Inicializar en 0

    otros = root.findall('.//Devengados/OtrosConceptos/OtroConcepto', ns)
    for otro in otros:
        descripcion = otro.get('DescripcionConcepto', '')
        valor = otro.get('ConceptoNS', '0')
        if any(concepto in descripcion for concepto in otros_conceptos):
            payroll_data[f'Otros - {descripcion}'] = valor

    # Deducciones
    deducciones_concepts = [
        'Salud', 'Pensión', 'FSP', 'SINDICATO', 'SANCIÓN', 'LIBRANZA', 'PAGOS A TERCERO', 'ANTICIPOS',
        'OTRAS DEDUCCIONES', 'PENSIÓN VOLUNTARIA', 'FPV', 'RETENCIÓN EN LA FUENTE', 'AFC', 'COOPERATIVA',
        'EMBARGO FISCAL', 'PLAN COMPLEMENTARIO SALUD', 'EDUCACIÓN', 'REINTEGRO', 'DEUDA'
    ]

    for concept in deducciones_concepts:
        payroll_data[f'Deducción - {concept}'] = safe_find(root, f'.//Deducciones/{concept.replace(" ", "")}', ns, 'Deduccion') or '0'

    payroll_data['Total Devengado'] = safe_find(root, './/DevengadosTotal', ns) or '0'
    payroll_data['Total Deducciones'] = safe_find(root, './/DeduccionesTotal', ns) or '0'
    payroll_data['Pago Neto'] = safe_find(root, './/ComprobanteTotal', ns) or '0'

    return payroll_data

# Ruta de los archivos XML
xml_directory = r'C:\Users\USUARIO\Documents\EMPRESAS IMPUESTOS\CODIMEC S.A.S\ENERO\NOMINA INDIVIDUAL\XML'

all_payrolls = []

for filename in os.listdir(xml_directory):
    if filename.endswith('.xml'):
        file_path = os.path.join(xml_directory, filename)
        payroll_data = parse_payroll(file_path)
        if payroll_data:
            all_payrolls.append(payroll_data)

# Convertir los datos en DataFrame
df_payrolls = pd.DataFrame(all_payrolls)

# Convertir columnas a formato numérico
numeric_columns = df_payrolls.columns.drop(['Nombre del Archivo', 'Número de Nómina', 'Fecha de Emisión', 'ID del Empleado', 'Nombre del Empleado', 'Nombre del Empleador', 'NIT del Empleador'])
df_payrolls[numeric_columns] = df_payrolls[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Formatear la fecha
df_payrolls['Fecha de Emisión'] = pd.to_datetime(df_payrolls['Fecha de Emisión']).dt.strftime('%m/%d/%Y')

# Definir el nombre del archivo de salida
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f'nomina_detallada_{timestamp}.xlsx'
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
output_path = os.path.join(desktop, output_file)

# Exportar a Excel
try:
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df_payrolls.to_excel(writer, index=False, sheet_name='Nómina')
        workbook = writer.book
        worksheet = writer.sheets['Nómina']
        
        # Formato para números
        num_format = workbook.add_format({'num_format': '#,##0.00'})
        
        for col_num, (col_name, col_data) in enumerate(df_payrolls.items()):
            if col_name not in ['Nombre del Archivo', 'Número de Nómina', 'Fecha de Emisión', 'ID del Empleado', 'Nombre del Empleado', 'Nombre del Empleador', 'NIT del Empleador']:
                worksheet.set_column(col_num, col_num, None, num_format)

    print(f"El archivo Excel '{output_file}' ha sido creado exitosamente en tu escritorio.")
except Exception as e:
    print(f"Error al guardar el archivo: {e}")
    alternative_path = os.path.join(os.path.dirname(__file__), output_file)
    try:
        df_payrolls.to_excel(alternative_path, index=False)
        print(f"El archivo Excel '{output_file}' ha sido creado exitosamente en el mismo directorio que el script.")
    except Exception as e:
        print(f"Error al guardar el archivo en la ubicación alternativa: {e}")