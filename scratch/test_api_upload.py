import requests
import json

pdf_path = 'C:/Users/nares/.gemini/antigravity-ide/brain/b2162b4d-ff00-4035-a909-5eee5b58910e/.user_uploaded/media_1789525936799.pdf'
with open(pdf_path, 'rb') as f:
    files = {'file': ('sale_deed_3978_2010.pdf', f, 'application/pdf')}
    data = {
        'doc_type': 'sale_deed',
        'lang': 'ta',
        'max_pages': 5
    }
    print('Sending PDF upload request to http://127.0.0.1:8000/api/ocr/process (first 5 pages)...')
    res = requests.post('http://127.0.0.1:8000/api/ocr/process', files=files, data=data, timeout=180)
    print('HTTP Response:', res.status_code)
    if res.ok:
        res_json = res.json()
        ext = res_json.get('extraction', {})
        print('Document Type Name:', ext.get('document_type_name'))
        fields = ext.get('fields', {})
        keys_to_show = [
            'document_number', 'registration_date', 'sro_details',
            'vendor_details', 'purchaser_details', 'poa_agent_details',
            'survey_number', 'village_taluk_district', 'land_extent',
            'apartment_uds_floor', 'boundaries', 'consideration_amount',
            'pan_number', 'payment_breakdown', 'utility_tax_identifiers',
            'document_drafter'
        ]
        print('\n=== EXTRACTED SALE DEED FIELDS FROM REAL PDF ===')
        for k in keys_to_show:
            v = fields.get(k, {})
            val = v.get('value') if isinstance(v, dict) else v
            print(f'{k}: {val}')
    else:
        print('Upload failed:', res.text[:500])
