import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime

def safe_find(element, path, namespaces):
    try:
        return element.find(path, namespaces).text or ''
    except AttributeError:
        return ''

def split_name(full_name):
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], '', '', '', full_name
    elif len(parts) == 2:
        return parts[0], '', parts[1], '', full_name
    elif len(parts) == 3:
        return parts[0], '', parts[1], parts[2], full_name
    elif len(parts) >= 4:
        return parts[0], parts[1], parts[2], parts[3], full_name
    else:
        return '', '', '', '', full_name

def determine_invoice_type(description):
    services = ['servicio', 'mensajería', 'mano de obra', 'transporte', 'asesoría', 'asistencia', 
                'honorarios', 'soporte', 'mantenimiento', 'póliza', 'consultoría', 'alquiler', 
                'arrendamiento', 'capacitación', 'instalación', 'parqueo', 'curso', 'alojamiento', 
                'obra', 'flete', 'intereses', 'diseño', 'carga terrestre', 'inspección']
    
    description = description.lower()
    
    for service in services:
        if service in description:
            return 'Servicio'
    
    return 'Producto'

def parse_invoice(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
        return None, None, None, None
    
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
        
        'Subtotal': safe_find(root, './/cac:LegalMonetaryTotal/cbc:LineExtensionAmount', ns),
        'Descuento detalle': safe_find(root, './/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount', ns),
        'Recargo detalle': safe_find(root, './/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount', ns),
        'Total Bruto Factura': safe_find(root, './/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount', ns),
        'Total Bruto Gravado': 0,
        'Total Bruto No Gravado': 0,
        'IVA': '0',
        'INC': '0',
        'Bolsas': '0',
        'Otros impuestos': '0',
        'Total impuesto': safe_find(root, './/cac:TaxTotal/cbc:TaxAmount', ns),
        'Total neto factura': safe_find(root, './/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount', ns),
        'Descuento Global': '0',
        'Recargo Global': '0',
        'Total factura': safe_find(root, './/cac:LegalMonetaryTotal/cbc:PayableAmount', ns),
        'Anticipos': safe_find(root, './/cac:LegalMonetaryTotal/cbc:PrepaidAmount', ns),
        'Rete fuente': '0',
        'Rete IVA': '0',
        'Rete ICA': '0',
        'InvoicePeriodDescription': safe_find(root, './/cac:InvoicePeriod/cbc:Description', ns),
        'ItemDescription': safe_find(root, './/cac:Item/cbc:Description', ns),
        'TipoFactura': ''
    }
    
    for tax_subtotal in root.findall('.//cac:TaxTotal/cac:TaxSubtotal', ns):
        tax_category = safe_find(tax_subtotal, './/cac:TaxCategory/cac:TaxScheme/cbc:Name', ns).upper()
        tax_amount = safe_find(tax_subtotal, './/cbc:TaxAmount', ns)
        
        if 'IVA' in tax_category:
            invoice_data['IVA'] = tax_amount
        elif 'INC' in tax_category:
            invoice_data['INC'] = tax_amount
        elif 'BOLSAS' in tax_category:
            invoice_data['Bolsas'] = tax_amount
        else:
            invoice_data['Otros impuestos'] = str(float(invoice_data['Otros impuestos']) + float(tax_amount or '0'))

    for withholding_tax_total in root.findall('.//cac:WithholdingTaxTotal', ns):
        tax_category = safe_find(withholding_tax_total, './/cac:TaxCategory/cac:TaxScheme/cbc:Name', ns).upper()
        tax_amount = safe_find(withholding_tax_total, './/cbc:TaxAmount', ns)
        
        if 'FUENTE' in tax_category:
            invoice_data['Rete fuente'] = tax_amount
        elif 'IVA' in tax_category:
            invoice_data['Rete IVA'] = tax_amount
        elif 'ICA' in tax_category:
            invoice_data['Rete ICA'] = tax_amount

    invoice_lines = []
    total_bruto_gravado = 0
    total_bruto_no_gravado = 0
    for line in root.findall('.//cac:InvoiceLine', ns):
        line_data = {
            'InvoiceID': invoice_data['InvoiceID'],
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

        line_amount = float(line_data['LineExtensionAmount'] or 0)
        tax_percent = float(line_data['TaxPercent'] or 0)
        if tax_percent > 0:
            total_bruto_gravado += line_amount
        else:
            total_bruto_no_gravado += line_amount

    invoice_data['Total Bruto Gravado'] = total_bruto_gravado
    invoice_data['Total Bruto No Gravado'] = total_bruto_no_gravado
    
    invoice_data['TipoFactura'] = 'Producto'
    
    for line in invoice_lines:
        description = line.get('Description', '').lower()
        invoice_type = determine_invoice_type(description)
        if invoice_type == 'Servicio':
            invoice_data['TipoFactura'] = 'Servicio'
            break
    
    supplier_name = safe_find(root, './/cac:AccountingSupplierParty//cbc:RegistrationName', ns)
    supplier_first_name, supplier_second_name, supplier_first_lastname, supplier_second_lastname, supplier_full_name = split_name(supplier_name)
    
    supplier_data = {
        'SupplierName': supplier_name,
        'SupplierFirstName': supplier_first_name,
        'SupplierSecondName': supplier_second_name,
        'SupplierFirstLastName': supplier_first_lastname,
        'SupplierSecondLastName': supplier_second_lastname
    }
    
    customer_name = safe_find(root, './/cac:AccountingCustomerParty//cbc:RegistrationName', ns)
    customer_first_name, customer_second_name, customer_first_lastname, customer_second_lastname, customer_full_name = split_name(customer_name)
    
    customer_data = {
        'CustomerName': customer_name,
        'CustomerFirstName': customer_first_name,
        'CustomerSecondName': customer_second_name,
        'CustomerFirstLastName': customer_first_lastname,
        'CustomerSecondLastName': customer_second_lastname
    }
    
    return invoice_data, invoice_lines, supplier_data, customer_data

def process_invoices(xml_directory):
    invoice_data_list = []
    invoice_lines_list = []
    suppliers_list = []
    customers_list = []

    for xml_file in os.listdir(xml_directory):
        if xml_file.endswith('.xml'):
            invoice_data, invoice_lines, supplier_data, customer_data = parse_invoice(os.path.join(xml_directory, xml_file))
            if invoice_data:
                invoice_data_list.append(invoice_data)
            if invoice_lines:
                invoice_lines_list.extend(invoice_lines)
            if supplier_data:
                suppliers_list.append(supplier_data)
            if customer_data:
                customers_list.append(customer_data)
    
    df_invoices = pd.DataFrame(invoice_data_list)
    df_invoice_lines = pd.DataFrame(invoice_lines_list)
    df_suppliers = pd.DataFrame(suppliers_list)
    df_customers = pd.DataFrame(customers_list)
    
    with pd.ExcelWriter('invoices.xlsx') as writer:
        df_invoices.to_excel(writer, sheet_name='Facturas', index=False)
        df_invoice_lines.to_excel(writer, sheet_name='Detalles', index=False)
        df_suppliers.to_excel(writer, sheet_name='Emisores', index=False)
        df_customers.to_excel(writer, sheet_name='Adquirientes', index=False)

# Reemplaza con la ruta de tus archivos XML
xml_directory = r'C:\Users\USUARIO\Documents\EMPRESAS IMPUESTOS\CODIMEC S.A.S\ENERO\FACTURAS ENVIADAS\ALL\XML'
process_invoices(xml_directory)
