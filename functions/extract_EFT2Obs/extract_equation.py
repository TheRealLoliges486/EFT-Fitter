import json

def build_decay_equation_from_json(json_file_path, process="gamgam"):
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
        if val > 0:
            equation += f" + {term_str}"
        elif val == 0:
            continue
        else:
            equation += f" - {term_str}"

    return equation

def build_weighted_production_equation_from_json(json_file_path, xsec_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    with open(xsec_file_path, 'r') as f:
        xsec = json.load(f)
    
    run3_to_run2_bins = {
        "0.0": ["0.0", "5.0", "10.0"],
        "15.0": ["15.0", "20.0", "25.0"],
        "30.0": ["30.0", "35.0"],
        "45.0": ["45.0", "60.0"],
        "80.0": ["80.0", "100.0"],
        "120.0": ["120.0", "140.0", "170.0"],
        "200.0": ["200.0", "250.0"],
        "350.0": ["350.0", "450.0"]
    }
    
    run2_bins_to_scale_index = {
        "0.0": 0,
        "5.0": 1,
        "10.0": 2,
        "15.0": 0,
        "20.0": 1,
        "25.0": 2,
        "30.0": 0,
        "35.0": 1,
        "45.0": 0,
        "60.0": 1,
        "80.0": 0,
        "100.0": 1,
        "120.0": 0,
        "140.0": 1,
        "170.0": 2,
        "200.0": 0,
        "250.0": 1,
        "350.0": 0,
        "450.0": 1
    }
    
    run2_bins = [
        "0.0", "5.0", "10.0",
        "15.0", "20.0", "25.0",
        "30.0", "35.0",
        "45.0", "60.0",
        "80.0", "100.0",
        "120.0", "140.0", "170.0",
        "200.0", "250.0",
        "350.0", "450.0"
    ]
            
    # Create a dictionary to hold the scaled cross-sections for each stack    
    scaled_run2_xsecs = {}
    
    for key, run2_bin_list in run3_to_run2_bins.items():
        total_run2_bin_xsec = 0.0
        scaled_run_2_bin_list = []
        for run2_bin in run2_bin_list:
            if run2_bin in xsec:
                total_run2_bin_xsec += xsec[run2_bin]
            else:
                print(f"Warning: {run2_bin} not found in xsec data.")
        
        for run2_bin in run2_bin_list:
            if run2_bin in xsec:
                scaled_run_2_bin_list.append(xsec[run2_bin] / total_run2_bin_xsec)
            else:
                print(f"Warning: {run2_bin} not found in xsec data.")
        scaled_run2_xsecs[key] = scaled_run_2_bin_list
    
    print("xsec_stacks", scaled_run2_xsecs)
    
    # Want to extract all unique Wilson Coefficients (do not contain the u_ terms)
    all_wilsons = set()

    for run2_bin in run2_bins:
        coeffs = data.get(run2_bin, {})
        all_wilsons.update(coeffs.keys())
    all_wilsons = list(all_wilsons)
    
    result = {}
    
    for run3_bin in run3_to_run2_bins.keys():
        result[run3_bin] = {}
        current_scaled_xsecs = scaled_run2_xsecs[run3_bin]
        
        for wilson_coeff in all_wilsons:
            result[run3_bin][wilson_coeff] = 0.0
        
        for run2_bin in run3_to_run2_bins[run3_bin]:
            current_scaled_xsec = current_scaled_xsecs[run2_bins_to_scale_index[run2_bin]]
            current_coeffs = data.get(run2_bin, {})
            
            for wilson_coeff in all_wilsons:
                if wilson_coeff not in current_coeffs:
                    result[run3_bin][wilson_coeff] = 0.0 * current_scaled_xsec
                else:
                    result[run3_bin][wilson_coeff] += current_coeffs[wilson_coeff] * current_scaled_xsec
    
    return result


# Decay:
# print("gamgam", build_decay_equation_from_json("/t3home/niharrin/devel/work/tests/eft_fitter/functions/extract_EFT2Obs/mgalli/decay.json", process="gamgam"), "\n")
# print("tot", build_decay_equation_from_json("/t3home/niharrin/devel/work/tests/eft_fitter/functions/extract_EFT2Obs/mgalli/decay.json", process="tot"))

# Production:
# my_dict = build_weighted_production_equation_from_json(json_file_path="/t3home/niharrin/devel/work/tests/eft_fitter/functions/extract_EFT2Obs/mgalli/FullProduction_pt_h.json", xsec_file_path="/t3home/niharrin/devel/work/tests/eft_fitter/functions/extract_EFT2Obs/mgalli/xsec_hig_19_016.json")

# with open("./mgalli/run3_binning_massi_param.json", "w") as json_file:
#     json.dump(my_dict, json_file, indent=4, sort_keys=True, ensure_ascii=False)

print("0.0", build_decay_equation_from_json("/t3home/niharrin/devel/work/tests/eft_fitter/functions/extract_EFT2Obs/mgalli/run3_binning_massi_param.json", process="0.0"))