import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime

def safe_find(element, path, namespaces):
    try:
        return element.find(path, namespaces).text
    except AttributeError:
        return None

def parse_invoice(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
        return None, None
    
    ns = {'': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
          'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
          'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
          'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'}
    
    invoice_data = {
        'FileName': os.path.basename(xml_file),
        'InvoiceID': safe_find(root, './/cbc:ID', ns),
        'Prefijo': safe_find(root, './/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/CustomFieldExtension/CustomField[@Name="Prefijo"]', ns),
        'IssueDate': safe_find(root, './/cbc:IssueDate', ns),
        'IssueTime': safe_find(root, './/cbc:IssueTime', ns),
        'DueDate': safe_find(root, './/cbc:DueDate', ns),
        'InvoiceTypeCode': safe_find(root, './/cbc:InvoiceTypeCode', ns),
        'DocumentCurrencyCode': safe_find(root, './/cbc:DocumentCurrencyCode', ns),
        'Notes': safe_find(root, './/cbc:Note', ns),
        
        # Emisor (Supplier)
        'SupplierName': safe_find(root, './/cac:AccountingSupplierParty//cbc:RegistrationName', ns),
        'SupplierID': safe_find(root, './/cac:AccountingSupplierParty//cbc:CompanyID', ns),
        'SupplierTaxScheme': safe_find(root, './/cac:AccountingSupplierParty//cac:TaxScheme/cbc:Name', ns),
        'SupplierFiscalRegime': safe_find(root, './/cac:AccountingSupplierParty//cbc:TaxLevelCode', ns),
        'SupplierPhone': safe_find(root, './/cac:AccountingSupplierParty//cbc:Telephone', ns),
        'SupplierEmail': safe_find(root, './/cac:AccountingSupplierParty//cbc:ElectronicMail', ns),
        'SupplierAddress': safe_find(root, './/cac:AccountingSupplierParty//cac:Address/cac:AddressLine/cbc:Line', ns),
        'SupplierCity': safe_find(root, './/cac:AccountingSupplierParty//cac:Address/cbc:CityName', ns),
        'SupplierCityCode': safe_find(root, './/cac:AccountingSupplierParty//cac:Address/cbc:ID', ns),
        'SupplierDepartment': safe_find(root, './/cac:AccountingSupplierParty//cac:Address/cbc:CountrySubentity', ns),
        
        # Adquiriente (Customer)
        'CustomerName': safe_find(root, './/cac:AccountingCustomerParty//cbc:RegistrationName', ns),
        'CustomerID': safe_find(root, './/cac:AccountingCustomerParty//cbc:CompanyID', ns),
        'CustomerTaxScheme': safe_find(root, './/cac:AccountingCustomerParty//cac:TaxScheme/cbc:Name', ns),
        'CustomerFiscalRegime': safe_find(root, './/cac:AccountingCustomerParty//cbc:TaxLevelCode', ns),
        'CustomerPhone': safe_find(root, './/cac:AccountingCustomerParty//cbc:Telephone', ns),
        'CustomerEmail': safe_find(root, './/cac:AccountingCustomerParty//cbc:ElectronicMail', ns),
        'CustomerAddress': safe_find(root, './/cac:AccountingCustomerParty//cac:Address/cac:AddressLine/cbc:Line', ns),
        'CustomerCity': safe_find(root, './/cac:AccountingCustomerParty//cac:Address/cbc:CityName', ns),
        'CustomerCityCode': safe_find(root, './/cac:AccountingCustomerParty//cac:Address/cbc:ID', ns),
        'CustomerDepartment': safe_find(root, './/cac:AccountingCustomerParty//cac:Address/cbc:CountrySubentity', ns),
        
        # Totales
        'LineExtensionAmount': safe_find(root, './/cac:LegalMonetaryTotal/cbc:LineExtensionAmount', ns),
        'TaxExclusiveAmount': safe_find(root, './/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount', ns),
        'TaxInclusiveAmount': safe_find(root, './/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount', ns),
        'AllowanceTotalAmount': safe_find(root, './/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount', ns),
        'ChargeTotalAmount': safe_find(root, './/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount', ns),
        'PrepaidAmount': safe_find(root, './/cac:LegalMonetaryTotal/cbc:PrepaidAmount', ns),
        'PayableAmount': safe_find(root, './/cac:LegalMonetaryTotal/cbc:PayableAmount', ns),
    }
    
    # Impuestos totales
    tax_total = root.find('.//cac:TaxTotal', ns)
    if tax_total is not None:
        invoice_data['TotalTaxAmount'] = safe_find(tax_total, 'cbc:TaxAmount', ns)
    
    # Retenciones
    withholding_total = root.find('.//cac:WithholdingTaxTotal', ns)
    if withholding_total is not None:
        invoice_data['WithholdingTaxAmount'] = safe_find(withholding_total, 'cbc:TaxAmount', ns)
    
    # Forma de pago y medio de pago
    payment_means = root.find('.//cac:PaymentMeans', ns)
    if payment_means is not None:
        invoice_data['PaymentMeansCode'] = safe_find(payment_means, 'cbc:PaymentMeansCode', ns)
        invoice_data['PaymentDueDate'] = safe_find(payment_means, 'cbc:PaymentDueDate', ns)
    
    invoice_lines = []
    for line in root.findall('.//cac:InvoiceLine', ns):
        line_data = {
            'InvoiceID': invoice_data['InvoiceID'],  # Añadimos el InvoiceID a cada línea
            'FileName': os.path.basename(xml_file),
            'LineID': safe_find(line, 'cbc:ID', ns),
            'Description': safe_find(line, './/cbc:Description', ns),
            'Quantity': safe_find(line, 'cbc:InvoicedQuantity', ns),
            'UnitCode': line.find('cbc:InvoicedQuantity', ns).attrib.get('unitCode') if line.find('cbc:InvoicedQuantity', ns) is not None else None,
            'LineExtensionAmount': safe_find(line, 'cbc:LineExtensionAmount', ns),
            'TaxAmount': safe_find(line, './/cac:TaxTotal/cbc:TaxAmount', ns),
            'TaxPercent': safe_find(line, './/cac:TaxTotal//cbc:Percent', ns),
            'ItemCode': safe_find(line, './/cac:Item/cac:StandardItemIdentification/cbc:ID', ns),
        }
        invoice_lines.append(line_data)
    
    return invoice_data, invoice_lines

# Directorio donde se encuentran los archivos XML
xml_directory = r'C:\Users\USUARIO\Documents\EMPRESAS IMPUESTOS\CODIMEC S.A.S\JUNIO\DSE\XML'

all_invoices = []
all_invoice_lines = []

# Procesamos todos los archivos XML en el directorio
for filename in os.listdir(xml_directory):
    if filename.endswith('.xml'):
        file_path = os.path.join(xml_directory, filename)
        invoice_data, invoice_lines = parse_invoice(file_path)
        if invoice_data:
            all_invoices.append(invoice_data)
        if invoice_lines:
            all_invoice_lines.extend(invoice_lines)

# Creamos DataFrames con los datos extraídos
df_invoices = pd.DataFrame(all_invoices)
df_invoice_lines = pd.DataFrame(all_invoice_lines)

# Generamos un nombre de archivo único basado en la fecha y hora actual
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f'facturas_electronicas_detalladas_{timestamp}.xlsx'

# Guardamos en el escritorio del usuario
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
output_path = os.path.join(desktop, output_file)

# Exportamos los DataFrames a Excel
try:
    with pd.ExcelWriter(output_path) as writer:
        df_invoices.to_excel(writer, sheet_name='Facturas', index=False)
        df_invoice_lines.to_excel(writer, sheet_name='Líneas de Factura', index=False)
    print(f"El archivo Excel '{output_file}' ha sido creado exitosamente en tu escritorio.")
    
    # Imprimir información sobre datos faltantes
    print("\nResumen de datos faltantes:")
    print("\nFacturas:")
    print(df_invoices.isnull().sum())
    print("\nLíneas de Factura:")
    print(df_invoice_lines.isnull().sum())
    
except Exception as e:
    print(f"Error al guardar el archivo: {e}")
    alternative_path = os.path.join(os.path.dirname(__file__), output_file)
    try:
        with pd.ExcelWriter(alternative_path) as writer:
            df_invoices.to_excel(writer, sheet_name='Facturas', index=False)
            df_invoice_lines.to_excel(writer, sheet_name='Líneas de Factura', index=False)
        print(f"El archivo Excel '{output_file}' ha sido creado exitosamente en el mismo directorio que el script.")
    except Exception as e:
        print(f"Error al guardar el archivo en la ubicación alternativa: {e}")