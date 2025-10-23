import csv
from collections import defaultdict

# Configuration
INPUT_CSV = "input.csv" # input.csv is the file that contains the files to be deduped
OUTPUT_CSV = "deduped_files.csv"

def extract_base_name_and_extension(filename):
    """
    Extract base name and extension from filename.
    For example: "xyz.mp4" -> ("xyz", ".mp4")
    """
    if '.' in filename:
        base_name = filename.rsplit('.', 1)[0]  # Everything before last dot
        extension = '.' + filename.rsplit('.', 1)[1]  # Last dot + extension
        return base_name, extension
    else:
        return filename, ""

def rename_duplicates(input_file, output_file):
    """
    Reads CSV, finds duplicate new_name values, and creates renamed column with unique names.
    ALL files get numbered, even unique ones get -1.
    """
    
    # First pass: Read all rows and count occurrences of each new_name
    new_name_counts = defaultdict(int)
    rows = []
    
    print("📊 Analyzing duplicates in new_name column...")
    
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            new_name = row.get('new_name', '').strip()
            new_name_counts[new_name] += 1
            rows.append(row)
    
    # Print statistics
    total_rows = len(rows)
    unique_names = len(new_name_counts)
    duplicates_count = sum(1 for count in new_name_counts.values() if count > 1)
    
    print(f"📈 Found {total_rows} total rows")
    print(f"📈 {unique_names} unique new_name values")
    print(f"📈 {duplicates_count} names have duplicates")
    
    # Second pass: Create renamed column - ALL files get numbered
    new_name_counters = defaultdict(int)
    
    print("✏️  Creating renamed column...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Add 'renamed' column to fieldnames
        output_fieldnames = list(fieldnames) + ['renamed']
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        
        for row in rows:
            new_name = row.get('new_name', '').strip()
            
            if not new_name:
                # If new_name is empty, keep renamed empty too
                row['renamed'] = ''
            else:
                # Increment counter for this new_name (even if it's unique)
                new_name_counters[new_name] += 1
                
                # Extract base name and extension
                base_name, extension = extract_base_name_and_extension(new_name)
                
                # Create numbered name (ALL files get numbered)
                numbered_name = f"{base_name}-{new_name_counters[new_name]}{extension}"
                row['renamed'] = numbered_name
            
            writer.writerow(row)
    
    print(f"✅ Output written to: {output_file}")
    
    # Show some examples of renamed files
    print("\n📝 Examples of renamed files:")
    example_count = 0
    for original, count in new_name_counts.items():
        if example_count < 5:  # Show first 5 examples
            base_name, extension = extract_base_name_and_extension(original)
            if count == 1:
                print(f"   {original} → {base_name}-1{extension} (unique)")
            else:
                print(f"   {original} → {base_name}-1{extension}, {base_name}-2{extension}, ... ({count} copies)")
            example_count += 1

if __name__ == "__main__":
    print("🚀 Starting duplicate renaming process...")
    print(f"📂 Input file: {INPUT_CSV}")
    print(f"📂 Output file: {OUTPUT_CSV}")
    print()
    
    try:
        rename_duplicates(INPUT_CSV, OUTPUT_CSV)
        print("\n🏁 Process completed successfully!")
        
    except FileNotFoundError:
        print(f"❌ Input file '{INPUT_CSV}' not found!")
        print("Please make sure the CSV file exists in the current directory.")
        
    except Exception as e:
        print(f"❌ Error: {e}")