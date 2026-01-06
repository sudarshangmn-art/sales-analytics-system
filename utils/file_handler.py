def read_sales_data(filename):
    encodings = ['utf-8', 'latin-1', 'cp1252']
    lines = []

    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                all_lines = file.readlines()

                for line in all_lines[1:]:
                    line = line.strip()
                    if line:
                        lines.append(line)

            return lines

        except UnicodeDecodeError:
            continue

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []

    print("Error: Unable to read file with supported encodings.")
    return []
