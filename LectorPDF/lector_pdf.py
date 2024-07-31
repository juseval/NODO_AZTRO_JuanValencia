import os
import pandas as pd
from datetime import datetime
import PyPDF2
import re

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def parse_invoice(pdf_file):
    text = extract_text_from_pdf(pdf_file)
    
    invoice_data = {
        'FileName': os.path.basename(pdf_file),
        'InvoiceID': re.search(r'Número de Factura:\s*(\S+)', text).group(1) if re.search(r'Número de Factura:\s*(\S+)', text) else '',
        'IssueDate': re.search(r'Fecha de Emisión:\s*(\S+)', text).group(1) if re.search(r'Fecha de Emisión:\s*(\S+)', text) else '',
        'DueDate': re.search(r'Fecha de Vencimiento:\s*(\S+)', text).group(1) if re.search(r'Fecha de Vencimiento:\s*(\S+)', text) else '',
        'DocumentCurrencyCode': 'COP',  # Asumiendo que todas las facturas están en pesos colombianos
        'Notes': '',
        'Subtotal': re.search(r'Subtotal\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Subtotal\s*([\d,.]+)', text) else '0',
        'Descuento detalle': re.search(r'Descuento detalle\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Descuento detalle\s*([\d,.]+)', text) else '0',
        'Recargo detalle': re.search(r'Recargo detalle\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Recargo detalle\s*([\d,.]+)', text) else '0',
        'Total Bruto Factura': re.search(r'Total Bruto Factura\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Total Bruto Factura\s*([\d,.]+)', text) else '0',
        'IVA': re.search(r'IVA\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'IVA\s*([\d,.]+)', text) else '0',
        'INC': re.search(r'INC\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'INC\s*([\d,.]+)', text) else '0',
        'Bolsas': re.search(r'Bolsas\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Bolsas\s*([\d,.]+)', text) else '0',
        'Otros impuestos': re.search(r'Otros impuestos\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Otros impuestos\s*([\d,.]+)', text) else '0',
        'Total impuesto': re.search(r'Total impuesto \(=\)\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Total impuesto \(=\)\s*([\d,.]+)', text) else '0',
        'Total neto factura': re.search(r'Total neto factura \(=\)\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Total neto factura \(=\)\s*([\d,.]+)', text) else '0',
        'Descuento Global': re.search(r'Descuento Global \(-\)\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Descuento Global \(-\)\s*([\d,.]+)', text) else '0',
        'Recargo Global': re.search(r'Recargo Global \(\+\)\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Recargo Global \(\+\)\s*([\d,.]+)', text) else '0',
        'Total factura': re.search(r'Total factura \(=\)\s*COP \$\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Total factura \(=\)\s*COP \$\s*([\d,.]+)', text) else '0',
        'Anticipos': re.search(r'Anticipos\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Anticipos\s*([\d,.]+)', text) else '0',
        'Rete fuente': re.search(r'Rete fuente\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Rete fuente\s*([\d,.]+)', text) else '0',
        'Rete IVA': re.search(r'Rete IVA\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Rete IVA\s*([\d,.]+)', text) else '0',
        'Rete ICA': re.search(r'Rete ICA\s*([\d,.]+)', text).group(1).replace('.', '').replace(',', '.') if re.search(r'Rete ICA\s*([\d,.]+)', text) else '0',
    }
    
    # Extraer datos del emisor
    invoice_data.update({
        'SupplierName': re.search(r'Razón Social:\s*(.+)', text).group(1) if re.search(r'Razón Social:\s*(.+)', text) else '',
        'SupplierID': re.search(r'Nit del Emisor:\s*(\S+)', text).group(1) if re.search(r'Nit del Emisor:\s*(\S+)', text) else '',
        'SupplierAddress': re.search(r'Dirección:\s*(.+)', text).group(1) if re.search(r'Dirección:\s*(.+)', text) else '',
        'SupplierCity': re.search(r'Municipio / Ciudad:\s*(.+)', text).group(1) if re.search(r'Municipio / Ciudad:\s*(.+)', text) else '',
        'SupplierDepartment': re.search(r'Departamento:\s*(.+)', text).group(1) if re.search(r'Departamento:\s*(.+)', text) else '',
    })

    # Extraer datos del adquiriente
    invoice_data.update({
        'CustomerName': re.search(r'Nombre o Razón Social:\s*(.+)', text).group(1) if re.search(r'Nombre o Razón Social:\s*(.+)', text) else '',
        'CustomerID': re.search(r'Número Documento:\s*(\S+)', text).group(1) if re.search(r'Número Documento:\s*(\S+)', text) else '',
        'CustomerAddress': re.search(r'Dirección:\s*(.+)', text).group(1) if re.search(r'Dirección:\s*(.+)', text) else '',
        'CustomerCity': re.search(r'Municipio / Ciudad:\s*(.+)', text).group(1) if re.search(r'Municipio / Ciudad:\s*(.+)', text) else '',
        'CustomerDepartment': re.search(r'Departamento:\s*(.+)', text).group(1) if re.search(r'Departamento:\s*(.+)', text) else '',
    })
    
    return invoice_data

pdf_directory = r'C:\Users\USUARIO\Documents\EMPRESAS IMPUESTOS\CODIMEC S.A.S\JUNIO\FACTURAS\All\PDF'

all_invoices = []

for filename in os.listdir(pdf_directory):
    if filename.endswith('.pdf'):
        file_path = os.path.join(pdf_directory, filename)
        invoice_data = parse_invoice(file_path)
        if invoice_data:
            all_invoices.append(invoice_data)

df_invoices = pd.DataFrame(all_invoices)

numeric_columns = ['Subtotal', 'Descuento detalle', 'Recargo detalle', 'Total Bruto Factura', 
                   'IVA', 'INC', 'Bolsas', 'Otros impuestos', 'Total impuesto', 'Total neto factura', 
                   'Descuento Global', 'Recargo Global', 'Total factura', 'Anticipos', 'Rete fuente', 
                   'Rete IVA', 'Rete ICA']

for col in numeric_columns:
    df_invoices[col] = pd.to_numeric(df_invoices[col], errors='coerce')

date_columns = ['IssueDate', 'DueDate']
for col in date_columns:
    df_invoices[col] = pd.to_datetime(df_invoices[col], format='%d/%m/%Y', errors='coerce').dt.strftime('%m/%d/%Y')

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f'facturas_electronicas_detalladas_{timestamp}.xlsx'

desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
output_path = os.path.join(desktop, output_file)

try:
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df_invoices.to_excel(writer, sheet_name='Facturas', index=False)
        
        workbook = writer.book
        worksheet_facturas = writer.sheets['Facturas']
        
        date_format = workbook.add_format({'num_format': 'mm/dd/yyyy'})
        number_format = workbook.add_format({'num_format': '#,##0.00'})
        
        for col_num, column in enumerate(df_invoices.columns):
            if column in date_columns:
                worksheet_facturas.set_column(col_num, col_num, None, date_format)
            elif column in numeric_columns:
                worksheet_facturas.set_column(col_num, col_num, None, number_format)
    
    print(f"El archivo Excel '{output_file}' ha sido creado exitosamente en tu escritorio.")
    
    print("\nResumen de datos faltantes:")
    print("\nFacturas:")
    print(df_invoices.isnull().sum())
    
except Exception as e:
    print(f"Error al guardar el archivo: {e}")
    alternative_path = os.path.join(os.path.dirname(__file__), output_file)
    try:
        with pd.ExcelWriter(alternative_path) as writer:
            df_invoices.to_excel(writer, sheet_name='Facturas', index=False)
        print(f"El archivo Excel '{output_file}' ha sido creado exitosamente en el mismo directorio que el script.")
    except Exception as e:
        print(f"Error al guardar el archivo en la ubicación alternativa: {e}")