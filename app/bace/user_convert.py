from datetime import datetime, timezone
import re

# --- CONSTANTS (Bureaucrats) ---
ATR_LOW      = 0.0007   # Updated to 0.07% to match your surveycto code
ATR_HIGH     = 0.0008   # Updated to 0.08% to match your surveycto code

# Base Values (in PKR)
BASE_LOW  = 2.65 * (10**12)
BASE_HIGH = 8.39 * (10**12)

def add_to_profile(profile):
    profile['timestamp'] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return profile

def round_to_granularity(value, granularity):
    return float((granularity) * round(float(value) / granularity))

def choice_message(label, comp_low, comp_high, support, underassessment, design_dict): 

    # 1. Format Inputs & Calculate Delinquency
    try:
        granularity = 10
        
        c_low_val  = float(comp_low)
        c_high_val = float(comp_high)
        supp_val   = float(support)
        under_val  = float(underassessment)
        
        # Constraint Logic: Sum is fixed at 76
        delinq_val = 76.0 - under_val

        # Create display strings rounded to the granularity
        c_low_disp  = f"{round_to_granularity(c_low_val, granularity):.0f}%"
        c_high_disp = f"{round_to_granularity(c_high_val, granularity):.0f}%"
        supp_disp   = f"{round_to_granularity(supp_val, granularity):.0f}%"
        under_disp  = f"{round_to_granularity(under_val, granularity):.0f}%"
        delinq_disp = f"{round_to_granularity(delinq_val, granularity):.0f}%"

    except:
        c_low_val = c_high_val = supp_val = under_val = delinq_val = 0.0
        c_low_disp = c_high_disp = supp_disp = under_disp = delinq_disp = "0%"

    # 2. Calculate Financials (Using raw unrounded values for accuracy)
    c_low_dec  = c_low_val / 100.0
    c_high_dec = c_high_val / 100.0

    etr_low  = ATR_LOW * c_low_dec
    etr_high = ATR_HIGH * c_high_dec

    rev_low_raw  = BASE_LOW  * etr_low
    rev_high_raw = BASE_HIGH * etr_high
    total_rev_raw = rev_low_raw + rev_high_raw
    
    # Convert to Billions (1e9) for Display
    total_rev_billions = total_rev_raw / 1_000_000_000 

    # 3. Build HTML Table (Omitted static Tax Rates)
    html_table = f"""
        <table width='100%' class="bace_table">
            <tbody>
                <tr>
                    <th colspan="2">{label}</th>
                </tr>
                
                <tr>
                    <td>Compliance by Low-Value Properties:</td>
                    <td>{c_low_disp}</td>
                </tr>
                <tr>
                    <td>Compliance by High-Value Properties:</td>
                    <td>{c_high_disp}</td>
                </tr>
                <tr>
                    <td>Public Support:</td>
                    <td>{supp_disp}</td>
                </tr>
                <tr>
                    <td>Percentage of all Properties that are Underassessed:</td>
                    <td>{under_disp}</td>
                </tr>
                <tr>
                    <td>Percentage of all Properties that are Delinquent:</td>
                    <td>{delinq_disp}</td>
                </tr>

                <tr>
                    <td>Effective Tax Rate on Low-Value Properties:</td>
                    <td>{etr_low:.3%}</td>
                </tr>
                <tr>
                    <td>Effective Tax Rate on High-Value Properties:</td>
                    <td>{etr_high:.3%}</td>
                </tr>
                <tr>
                    <td>Total Revenue (PKR Billion):</td>
                    <td>{total_rev_billions:,.3f}</td>
                </tr>
            </tbody>
        </table>
    """
    return html_table

def convert_design(design, profile, request_data):
    # This function is called by the BACE core. 
    # 'design' comes from the optimizer, 'profile' from DB.
    print(f"DEBUG: design dictionary content: {design}")
    Q = request_data.get('question_number') or len(profile.get('design_history'))
    output_design = {f'{key}_{Q}': value for key, value in design.items()}

    output_design[f'message_0_{Q}'] = choice_message(
        "Option A",
        design.get('compliance_low_a', 0),
        design.get('compliance_high_a', 0),
        design.get('support_public_a', 0),
        design.get('underassessment_a', 0),
        design
    )

    output_design[f'message_1_{Q}'] = choice_message(
        "Option B",
        design.get('compliance_low_b', 0),
        design.get('compliance_high_b', 0),
        design.get('support_public_b', 0),
        design.get('underassessment_b', 0),
        design
    )

    return output_design