import pdfplumber
import re
import pandas as pd
import os
from pathlib import Path

MONTH_MAP = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

def parse_date_from_filename(filename):
    """
    Parses 'Month Year' (e.g., 'Agosto 2025.pdf') into ISO format 'YYYY-MM-DD'.
    Defaulting to the first of the month.
    """
    # Remove extension and normalize
    name = Path(filename).stem.lower().strip()
    match = re.search(r"(\w+)\s+(\d{4})", name)
    if match:
        month_name = match.group(1)
        year = match.group(2)
        month_num = MONTH_MAP.get(month_name, "01")
        return f"{year}-{month_num}-01"
    return "1970-01-01"

def extract_from_pdf(pdf_path, file_date):
    """
    Extracts 'Exceso de velocidad' data from a PDF file.
    """
    data = []
    # Regex pattern refined to capture:
    # 1: ID, 2: Manzana, 3: Lote, 4: Nombre, 5: Número de Infracción, 6: Monto
    pattern = re.compile(r"(\d+)\s+Mz\s+(\d+)\s+Lote\s+(\d+)\s+(.*?)\s+Multas Infracción nro\s+(\d+):\s+Exceso de velocidad.*?\s+([\d.,]+)")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                for line in text.split('\n'):
                    match = pattern.search(line)
                    if match:
                        data.append({
                            'Fecha': file_date,
                            'Manzana': match.group(2),
                            'Lote': match.group(3),
                            'Nombre': match.group(4).strip(),
                            'Número de Infracción': match.group(5),
                            'Monto': match.group(6)
                        })
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        
    return data

def main():
    # Target directory is updated as per user's preference
    target_dir = Path("/Users/sector7gp/Downloads/SMT-2026")
    all_extracted_data = []

    print(f"Searching for PDFs in {target_dir.absolute()}...")
    
    pdf_files = list(target_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the directory.")
        return

    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        file_date = parse_date_from_filename(pdf_file.name)
        extracted = extract_from_pdf(pdf_file, file_date)
        all_extracted_data.extend(extracted)

    if all_extracted_data:
        df = pd.DataFrame(all_extracted_data)
        # Ensure columns are in the specific order requested
        cols = ['Fecha', 'Manzana', 'Lote', 'Nombre', 'Número de Infracción', 'Monto']
        df = df[cols]
        
        output_file = "expenses.csv"
        # Using semicolon as separator as requested/implied
        df.to_csv(output_file, index=False, sep=';', encoding='utf-8-sig')
        print(f"\nSuccess! Extracted {len(all_extracted_data)} entries.")
        print(f"Data saved to {output_file}")
    else:
        print("\nNo matching expense data found in the PDFs.")

if __name__ == "__main__":
    # Test cases for the refined regex and date parsing
    test_lines = [
        "613 Mz 2 Lote 21 Heuser Mariano Multas Infracción nro 1073: Exceso de velocidad (mas de 30 km/h) 65.171,77",
    ]
    
    # Test date parsing
    assert parse_date_from_filename("Agosto 2025.pdf") == "2025-08-01"
    assert parse_date_from_filename("Mayo 2025.pdf") == "2025-05-01"
    
    re_pattern = re.compile(r"(\d+)\s+Mz\s+(\d+)\s+Lote\s+(\d+)\s+(.*?)\s+Multas Infracción nro\s+(\d+):\s+Exceso de velocidad.*?\s+([\d.,]+)")
    for tl in test_lines:
        match = re_pattern.search(tl)
        assert match, f"Regex failed on test line: {tl}"
        
    main()
