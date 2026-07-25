import re

# --- CONSTANTS (Bureaucrats) ---
ATR_LOW     = 0.0007   # 0.07%
ATR_HIGH    = 0.0008   # 0.08%
ATR_OVERALL = 0.0005   # 0.05%

# Base Values (in PKR)
# 2.65e12 = 2.65 Trillion
BASE_LOW  = 2.65 * (10**12)
BASE_HIGH = 8.39 * (10**12)

def round_to_granularity(value, granularity):
    return float((granularity) * round(float(value) / granularity))

def convert_design_surveycto(design, profile, request_data, split_to_rows="|", split_to_vars=":"):
    output = ""
    
    # --- 1. EXTRACT AND FORMAT INPUTS ---
    try:
        # Compliance (Inputs are continuous floats e.g., 45.0 for 45%)
        comp_low_a_val  = float(design.get('compliance_low_a', 0))
        comp_low_b_val  = float(design.get('compliance_low_b', 0))

        comp_high_a_val = float(design.get('compliance_high_a', 0))
        comp_high_b_val = float(design.get('compliance_high_b', 0))

        # Support
        supp_a_val = float(design.get('support_public_a', 0))
        supp_b_val = float(design.get('support_public_b', 0))

        # Underassessment
        under_a_val = float(design.get('underassessment_a', 0))
        under_b_val = float(design.get('underassessment_b', 0))

        # Delinquency (Constraint: Sum = 76)
        delinq_a_val = 76.0 - under_a_val
        delinq_b_val = 76.0 - under_b_val

    except Exception as e:
        print(f"Error parsing design: {e}")
        return {'output': "Error"}

    # --- 2. CALCULATE METRICS (Option A) ---
    # Convert % to decimal 
    c_low_dec_a = comp_low_a_val / 100.0
    c_high_dec_a = comp_high_a_val / 100.0

    etr_low_a  = ATR_LOW * c_low_dec_a
    etr_high_a = ATR_HIGH * c_high_dec_a

    rev_low_a  = BASE_LOW * etr_low_a
    rev_high_a = BASE_HIGH * etr_high_a
    
    # Revenue in Billions
    total_rev_a = (rev_low_a + rev_high_a) / 1_000_000_000 

    # --- 3. CALCULATE METRICS (Option B) ---
    c_low_dec_b = comp_low_b_val / 100.0
    c_high_dec_b = comp_high_b_val / 100.0

    etr_low_b  = ATR_LOW * c_low_dec_b
    etr_high_b = ATR_HIGH * c_high_dec_b

    rev_low_b  = BASE_LOW * etr_low_b
    rev_high_b = BASE_HIGH * etr_high_b
    
    # Revenue in Billions
    total_rev_b = (rev_low_b + rev_high_b) / 1_000_000_000 

    # --- 4. BUILD OUTPUT ---
    granularity = 10
    
    # --- SECTION 1: DECISION VARIABLES (GREEN ROWS) ---
    output += f"Compliance by Low-Value Properties{split_to_vars}{round_to_granularity(comp_low_a_val, granularity):.0f}%{split_to_vars}{round_to_granularity(comp_low_b_val, granularity):.0f}%{split_to_rows}"
    output += f"Compliance by High-Value Properties{split_to_vars}{round_to_granularity(comp_high_a_val, granularity):.0f}%{split_to_vars}{round_to_granularity(comp_high_b_val, granularity):.0f}%{split_to_rows}"
    output += f"Public Support{split_to_vars}{round_to_granularity(supp_a_val, granularity):.0f}%{split_to_vars}{round_to_granularity(supp_b_val, granularity):.0f}%{split_to_rows}"
    output += f"Percentage of all Properties that are Underassessed{split_to_vars}{round_to_granularity(under_a_val, granularity):.0f}%{split_to_vars}{round_to_granularity(under_b_val, granularity):.0f}%{split_to_rows}"
    output += f"Percentage of all Properties that are Delinquent{split_to_vars}{round_to_granularity(delinq_a_val, granularity):.0f}%{split_to_vars}{round_to_granularity(delinq_b_val, granularity):.0f}%{split_to_rows}"

    # --- SECTION 2: FIXED & CALCULATED (GREY ROWS) ---
    # Static Tax Rate rows omitted. Only ETR and Total Revenue remain.
    
    output += f"Effective Tax Rate on Low-Value Properties{split_to_vars}{etr_low_a:.3%}{split_to_vars}{etr_low_b:.3%}{split_to_rows}"
    output += f"Effective Tax Rate on High-Value Properties{split_to_vars}{etr_high_a:.3%}{split_to_vars}{etr_high_b:.3%}{split_to_rows}"
    output += f"Total Revenue (PKR Billion){split_to_vars}{total_rev_a:,.3f}{split_to_vars}{total_rev_b:,.3f}{split_to_rows}"
    
    print(output)
    return {'output': output}

def convert_dict_to_string(obj, parent_key='', split_to_rows='|', split_to_vars=':'):
    output = []
    for key, val in obj.items():
        new_key = f"{parent_key}_{key}" if parent_key else key
        if isinstance(val, dict):
            nested_output = convert_dict_to_string(val, new_key, split_to_rows, split_to_vars)
            output.append(nested_output)
        else:
            output.append(f"{new_key}{split_to_vars}{val}")
    return split_to_rows.join(output)