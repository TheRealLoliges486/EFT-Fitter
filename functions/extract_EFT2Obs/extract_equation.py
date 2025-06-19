import json

def build_equation_from_json(json_file_path, process="gamgam"):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    coeffs = data.get(process, {})
    
    terms = []

    for key, value in coeffs.items():
        if key.startswith("u_"):
            continue  # Skip uncertainty terms

        if key.startswith("A_"):
            var = key[2:]
            terms.append((value, f"{abs(value)} * {var}"))

        elif key.startswith("B_"):
            var_part = key[2:]

            # Handle squared terms like chbox_2 → chbox * chbox
            if var_part.endswith("_2"):
                var = var_part[:-2]
                terms.append((value, f"{abs(value)} * {var} * {var}"))

            # Handle cross terms like chbox_chbtil → chbox * chbtil
            elif "_" in var_part:
                vars = var_part.split("_")
                terms.append((value, f"{abs(value)} * {' * '.join(vars)}"))

            else:
                # Regular quadratic term (assumed square)
                terms.append((value, f"{abs(value)} * {var_part} * {var_part}"))

    # Build the equation with correct sign formatting
    equation = "1"
    for val, term_str in terms:
        if val >= 0:
            equation += f" + {term_str}"
        else:
            equation += f" - {term_str}"

    return equation

print("gamgam", build_equation_from_json("/t3home/niharrin/devel/work/tests/eft_fitter/functions/extract_EFT2Obs/mgalli/decay.json", process="gamgam"), "\n")
print("tot", build_equation_from_json("/t3home/niharrin/devel/work/tests/eft_fitter/functions/extract_EFT2Obs/mgalli/decay.json", process="tot"))