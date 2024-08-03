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
    services = ['SERVICIO', 'MENSAJERIA', 'MANO DE OBRA', 'TRANSPORTE', 'ASESORIA', 'ASISTENCIA', 
                'HONORARIOS', 'SOPORTE', 'MANTENIMIENTO', 'POLIZA', 'CONSULTORIA', 'ALQUILER', 
                'ARRENDAMIENTO', 'CAPACITACION', 'INSTALACION', 'PARQUEO', 'CURSO', 'ALOJAMIENTO', 
                'OBRA', 'FLETE', 'INTERESES', 'DISEÑO', 'CARGA TERRESTRE', 'INSPECCION']
    
    description = description.upper()
    
    for service in services:
        if service in description:
            return 'Servicio'
    
    return 'Producto'

def determine_document_type(root, ns):
    invoice_type_code = safe_find(root, './/cbc:InvoiceTypeCode', ns)
    credit_note = safe_find(root, './/cbc:CreditNoteTypeCode', ns)
    debit_note = safe_find(root, './/cbc:DebitNoteTypeCode', ns)
    
    if credit_note:
        return 'NotaCredito'
    elif debit_note:
        return 'NotaDebito'
    elif invoice_type_code == '01':
        return 'FacturaElectronica'
    elif invoice_type_code == '05':
        return 'DocumentoSoporte'
    else:
        return 'Desconocido'

def parse_document(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
        return None, None, None, None, None

    ns = {'': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'}
    
    document_type = determine_document_type(root, ns)
    
    document_data = {
        'FileName': os.path.basename(xml_file),
        'DocumentID': safe_find(root, './/cbc:ID', ns),
        'Prefijo': safe_find(root, './/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/CustomFieldExtension/CustomField[@Name="Prefijo"]', ns),
        'IssueDate': safe_find(root, './/cbc:IssueDate', ns),
        'IssueTime': safe_find(root, './/cbc:IssueTime', ns),
        'DueDate': safe_find(root, './/cbc:DueDate', ns),
        'DocumentTypeCode': safe_find(root, './/cbc:InvoiceTypeCode', ns) or safe_find(root, './/cbc:CreditNoteTypeCode', ns) or safe_find(root, './/cbc:DebitNoteTypeCode', ns),
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
    
        'Subtotal': float(safe_find(root, './/cac:LegalMonetaryTotal/cbc:LineExtensionAmount', ns) or 0),
        'Descuento detalle': float(safe_find(root, './/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount', ns) or 0),
        'Recargo detalle': float(safe_find(root, './/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount', ns) or 0),
        'Total Bruto Factura': float(safe_find(root, './/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount', ns) or 0),
        'Total Bruto Gravado': 0,
        'Total Bruto No Gravado': 0,
        'IVA': 0,
        'TarifaIVA': 0,
        'INC': 0,
        'TarifaINC': 0,
        'Bolsas': 0,
        'TarifaBolsas': 0,
        'Otros impuestos': 0,
        'Total impuesto': float(safe_find(root, './/cac:TaxTotal/cbc:TaxAmount', ns) or 0),
        'Total neto factura': float(safe_find(root, './/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount', ns) or 0),
        'Descuento Global': 0,
        'Recargo Global': 0,
        'Total factura': float(safe_find(root, './/cac:LegalMonetaryTotal/cbc:PayableAmount', ns) or 0),
        'Anticipos': float(safe_find(root, './/cac:LegalMonetaryTotal/cbc:PrepaidAmount', ns) or 0),
        'RetencionFuente': 0,
        'TarifaRetencionFuente': 0,
        'Rete IVA': 0,
        'TarifaReteIVA': 0,
        'Rete ICA': 0,
        'TarifaReteICA': 0,
        'InvoicePeriodDescription': safe_find(root, './/cac:InvoicePeriod/cbc:Description', ns),
        'ItemDescription': safe_find(root, './/cac:Item/cbc:Description', ns),
        'TipoFactura': '',
        'DocumentType': document_type,
    }
    
    for tax_subtotal in root.findall('.//cac:TaxTotal/cac:TaxSubtotal', ns):
        tax_category = safe_find(tax_subtotal, './/cac:TaxCategory/cac:TaxScheme/cbc:Name', ns).upper()
        tax_amount = float(safe_find(tax_subtotal, './/cbc:TaxAmount', ns) or 0)
        tax_percent = float(safe_find(tax_subtotal, './/cac:TaxCategory/cbc:Percent', ns) or 0)
        
        if 'IVA' in tax_category:
            document_data['IVA'] = tax_amount
            document_data['TarifaIVA'] = tax_percent
        elif 'INC' in tax_category:
            document_data['INC'] = tax_amount
            document_data['TarifaINC'] = tax_percent
        elif 'BOLSAS' in tax_category:
            document_data['Bolsas'] = tax_amount
            document_data['TarifaBolsas'] = tax_percent
        else:
            document_data['Otros impuestos'] += tax_amount
            
    for withholding_tax_total in root.findall('.//cac:WithholdingTaxTotal', ns):
        tax_category = safe_find(withholding_tax_total, './/cac:TaxCategory/cac:TaxScheme/cbc:Name', ns).upper()
        tax_amount = float(safe_find(withholding_tax_total, './/cbc:TaxAmount', ns) or 0)
        tax_percent = float(safe_find(withholding_tax_total, './/cac:TaxCategory/cbc:Percent', ns) or 0)
        
        if 'FUENTE' in tax_category:
            document_data['RetencionFuente'] = tax_amount
            document_data['TarifaRetencionFuente'] = tax_percent
        elif 'IVA' in tax_category:
            document_data['Rete IVA'] = tax_amount
            document_data['TarifaReteIVA'] = tax_percent
        elif 'ICA' in tax_category:
            document_data['Rete ICA'] = tax_amount
            document_data['TarifaReteICA'] = tax_percent
            
    document_lines = []
    total_bruto_gravado = 0
    total_bruto_no_gravado = 0
    for line in root.findall('.//cac:InvoiceLine', ns) or root.findall('.//cac:CreditNoteLine', ns) or root.findall('.//cac:DebitNoteLine', ns):
        line_data = {
            'DocumentID': document_data['DocumentID'],
            'FileName': os.path.basename(xml_file),
            'LineID': safe_find(line, 'cbc:ID', ns),
            'Description': safe_find(line, './/cbc:Description', ns),
            'Quantity': float(safe_find(line, 'cbc:InvoicedQuantity', ns) or safe_find(line, 'cbc:CreditedQuantity', ns) or safe_find(line, 'cbc:DebitedQuantity', ns) or 0),
            'UnitCode': line.find('cbc:InvoicedQuantity', ns).attrib.get('unitCode') if line.find('cbc:InvoicedQuantity', ns) is not None else None,
            'LineExtensionAmount': float(safe_find(line, 'cbc:LineExtensionAmount', ns) or 0),
            'TaxAmount': float(safe_find(line, './/cac:TaxTotal/cbc:TaxAmount', ns) or 0),
            'TaxCategory': safe_find(line, './/cac:TaxCategory/cbc:Name', ns),
            'TaxScheme': safe_find(line, './/cac:TaxCategory/cac:TaxScheme/cbc:Name', ns)
        }
        
        total_bruto_line = line_data['LineExtensionAmount']
        tax_amount = line_data['TaxAmount']
        total_bruto_gravado += total_bruto_line if 'IVA' in line_data['TaxScheme'].upper() else 0
        total_bruto_no_gravado += total_bruto_line if 'IVA' not in line_data['TaxScheme'].upper() else 0

        document_lines.append(line_data)
    
    document_data['Total Bruto Gravado'] = total_bruto_gravado
    document_data['Total Bruto No Gravado'] = total_bruto_no_gravado
    
    document_data['TipoFactura'] = 'Producto'  # Default to 'Producto'

    for line in document_lines:
        description = line.get('Description', '')
        invoice_type = determine_invoice_type(description)
        if invoice_type == 'Servicio':
            document_data['TipoFactura'] = 'Servicio'
            break
    
    # Supplier data extraction
    supplier_name = safe_find(root, './/cac:AccountingSupplierParty//cbc:RegistrationName', ns)
    supplier_id = safe_find(root, './/cac:AccountingSupplierParty//cbc:CompanyID', ns)
    supplier_type_document = safe_find(root, './/cac:AccountingSupplierParty//cbc:CompanyID', ns)
    supplier_first_name, supplier_second_name, supplier_first_lastname, supplier_second_lastname, supplier_full_name = split_name(supplier_name)
    
    supplier_data = {
        'SupplierID': safe_find(root, './/cac:AccountingSupplierParty//cbc:CompanyID', ns),
        'SupplierName': safe_find(root, './/cac:AccountingSupplierParty//cbc:RegistrationName', ns),
        'SupplierFirstName': supplier_first_name,
        'SupplierSecondName': supplier_second_name,
        'SupplierFirstLastName': supplier_first_lastname,
        'SupplierSecondLastName': supplier_second_lastname,
        'SupplierTaxScheme': safe_find(root, './/cac:AccountingSupplierParty//cac:TaxScheme/cbc:Name', ns),
        'SupplierFiscalRegime': safe_find(root, './/cac:AccountingSupplierParty//cbc:TaxLevelCode', ns),
        'SupplierPhone': safe_find(root, './/cac:AccountingSupplierParty//cbc:Telephone', ns),
        'SupplierEmail': safe_find(root, './/cac:AccountingSupplierParty//cbc:ElectronicMail', ns),
        'SupplierAddress': safe_find(root, './/cac:AccountingSupplierParty//cac:Address/cac:AddressLine/cbc:Line', ns),
        'SupplierCity': safe_find(root, './/cac:AccountingSupplierParty//cac:Address/cbc:CityName', ns),
        'SupplierCityCode': safe_find(root, './/cac:AccountingSupplierParty//cac:Address/cbc:ID', ns),
        'SupplierDepartment': safe_find(root, './/cac:AccountingSupplierParty//cac:Address/cbc:CountrySubentity', ns),        
    }
    
    # Customer data extraction
    customer_name = safe_find(root, './/cac:AccountingCustomerParty//cbc:RegistrationName', ns)
    customer_id = safe_find(root, './/cac:AccountingCustomerParty//cbc:CompanyID', ns)
    customer_type_document = safe_find(root, './/cac:AccountingCustomerParty//cbc:CompanyID', ns)
    customer_first_name, customer_second_name, customer_first_lastname, customer_second_lastname, customer_full_name = split_name(customer_name)
    
    customer_data = {
        'CustomerID': safe_find(root, './/cac:AccountingCustomerParty//cbc:CompanyID', ns),
        'CustomerName': safe_find(root, './/cac:AccountingCustomerParty//cbc:RegistrationName', ns),
        'CustomerFirstName':customer_first_name,
        'CustomerSecondName':customer_second_name,
        'CustomerFirstLastName':customer_first_lastname,
        'CustomerSecondLastName':customer_second_lastname,
        'CustomerTaxScheme': safe_find(root, './/cac:AccountingCustomerParty//cac:TaxScheme/cbc:Name', ns),
        'CustomerFiscalRegime': safe_find(root, './/cac:AccountingCustomerParty//cbc:TaxLevelCode', ns),
        'CustomerPhone': safe_find(root, './/cac:AccountingCustomerParty//cbc:Telephone', ns),
        'CustomerEmail': safe_find(root, './/cac:AccountingCustomerParty//cbc:ElectronicMail', ns),
        'CustomerAddress': safe_find(root, './/cac:AccountingCustomerParty//cac:Address/cac:AddressLine/cbc:Line', ns),
        'CustomerCity': safe_find(root, './/cac:AccountingCustomerParty//cac:Address/cbc:CityName', ns),
        'CustomerCityCode': safe_find(root, './/cac:AccountingCustomerParty//cac:Address/cbc:ID', ns),
        'CustomerDepartment': safe_find(root, './/cac:AccountingCustomerParty//cac:Address/cbc:CountrySubentity', ns),      
    }
    
    document_data['SupplierID'] = supplier_id
    document_data['SupplierName'] = supplier_name
    document_data['CustomerID'] = customer_id
    document_data['CustomerName'] = customer_name
    
    return document_data, document_lines, supplier_data, customer_data, document_type

def process_documents(xml_directory, output_directory):
    document_data_list = []
    document_lines_list = []
    suppliers_list = []
    customers_list = []

    for xml_file in os.listdir(xml_directory):
        if xml_file.endswith('.xml'):
            document_data, document_lines, supplier_data, customer_data, document_type = parse_document(os.path.join(xml_directory, xml_file))
            if document_data:
                document_data_list.append(document_data)
            if document_lines:
                document_lines_list.extend(document_lines)
            if supplier_data:
                suppliers_list.append(supplier_data)
            if customer_data:
                customers_list.append(customer_data)
                
    df_documents = pd.DataFrame(document_data_list)
    df_document_lines = pd.DataFrame(document_lines_list)
    df_suppliers = pd.DataFrame(suppliers_list).drop_duplicates(subset=['SupplierID'])
    df_customers = pd.DataFrame(customers_list).drop_duplicates(subset=['CustomerID'])
    
    # Create the output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Facturas_Electronicas_Detalladas_{timestamp}.xlsx"
    output_path = os.path.join(output_directory, output_filename)
    
    with pd.ExcelWriter(output_path) as writer:
        df_documents[df_documents['DocumentType'] == 'FacturaElectronica'].to_excel(writer, sheet_name='Facturas Electronicas', index=False)
        df_documents[df_documents['DocumentType'] == 'NotaCredito'].to_excel(writer, sheet_name='Notas Credito', index=False)
        df_documents[df_documents['DocumentType'] == 'NotaDebito'].to_excel(writer, sheet_name='Notas Debito', index=False)
        df_documents[df_documents['DocumentType'] == 'DocumentoSoporte'].to_excel(writer, sheet_name='Documentos Soporte', index=False)
        df_document_lines.to_excel(writer, sheet_name='Detalles', index=False)
        df_suppliers.to_excel(writer, sheet_name='Emisores', index=False)
        df_customers.to_excel(writer, sheet_name='Adquirientes', index=False)

    print(f"Excel file has been created: {output_path}")

# Example usage
xml_directory = r'C:\Users\USUARIO\Documents\EMPRESAS IMPUESTOS\LICO CASTILLO S.A.S\2024\CONTABILIDAD\JULIO\FACTURAS RECIBIDAS\XML'
output_directory = r'C:\Users\USUARIO\Desktop'

# Create output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

process_documents(xml_directory, output_directory)