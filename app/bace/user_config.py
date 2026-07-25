import scipy.stats
import numpy as np
import csv
import os

author       = 'Bureaucrat Choice Experiment'
size_thetas  = 2500                      
max_opt_time = 5                          

conf_dict = dict(
    domain_size    = 1500,
    initial_random = 1,
    num_iteration  = 15,
)

answers = [0, 1] 

# -----------------------------------------------------------------------------
# 1. LOAD PARAMETERS FROM CSV (bace_parameters.csv)
# -----------------------------------------------------------------------------
def load_bace_parameters(filename='bace_parameters.csv'):
    """
    Reads the CSV file and returns a dictionary of parameters for the 'burs' population.
    Assumes row order: 
    0: Compliance Low, 1: Compliance High, 2: Public Support, 
    3: Underassessment, 4: Delinquency
    """
    params = {}
    
    # Map row indices to variable names for clarity
    # NOTE: This relies on the row order in your Excel sheet remaining fixed!
    var_map = {
        0: 'compliance_low',
        1: 'compliance_high',
        2: 'support_public',
        3: 'underassessment',
        4: 'delinquency'
    }

    try:
        # Check if file exists in the current directory
        file_path = os.path.join(os.path.dirname(__file__), filename)
        
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            row_idx = 0
            for row in reader:
                # Only process rows for Bureaucrats ('burs')
                if row['Population'] == 'burs':
                    if row_idx in var_map:
                        key = var_map[row_idx]
                        params[key] = {
                            'min': float(row['range_min']),
                            'max': float(row['range_max']),
                            'mean': float(row['range_mean']),
                            'theta_mean': float(row['theta_mean']),
                            'theta_sd': float(row['theta_sd']),
                            'granularity': float(row['granularity'])
                        }
                    row_idx += 1
                    
    except Exception as e:
        print(f"Error loading CSV: {e}")
        # Fallback values if file fails (Safety net)
        return None

    return params

# Load the config
BACE_CONFIG = load_bace_parameters()

# Safety check: if loading failed, raise error so you know immediately
if BACE_CONFIG is None:
    raise ValueError("Could not load 'bace_parameters.csv'. Make sure the file is in the same folder!")

# -----------------------------------------------------------------------------
# 2. DEFINE PRIORS (THETAS) DYNAMICALLY
# -----------------------------------------------------------------------------
theta_params = dict(
    # 1. Low Value Compliance
    beta_compliance_low = scipy.stats.norm(
        loc=BACE_CONFIG['compliance_low']['theta_mean'], 
        scale=BACE_CONFIG['compliance_low']['theta_sd']
    ),

    # 2. High Value Compliance
    beta_compliance_high = scipy.stats.norm(
        loc=BACE_CONFIG['compliance_high']['theta_mean'], 
        scale=BACE_CONFIG['compliance_high']['theta_sd']
    ),

    # 3. Public Support
    beta_support_public = scipy.stats.norm(
        loc=BACE_CONFIG['support_public']['theta_mean'], 
        scale=BACE_CONFIG['support_public']['theta_sd']
    ),

    # 4. Underassessment
    beta_underassessment = scipy.stats.norm(
        loc=BACE_CONFIG['underassessment']['theta_mean'], 
        scale=BACE_CONFIG['underassessment']['theta_sd']
    ),

    # 5. Delinquency
    beta_delinquency = scipy.stats.norm(
        loc=BACE_CONFIG['delinquency']['theta_mean'], 
        scale=BACE_CONFIG['delinquency']['theta_sd']
    ),

    # Noise parameter (kept as original since not in CSV)
    mu = scipy.stats.uniform(loc=0.1, scale=5)
)

# -----------------------------------------------------------------------------
# 3. DEFINE DESIGN PARAMETERS DYNAMICALLY
# -----------------------------------------------------------------------------
design_params = dict(
    # 1. Low Val Compliance
    compliance_low_a = scipy.stats.uniform(
        BACE_CONFIG['compliance_low']['min'], 
        BACE_CONFIG['compliance_low']['max'] - BACE_CONFIG['compliance_low']['min']
    ),
    compliance_low_b = scipy.stats.uniform(
        BACE_CONFIG['compliance_low']['min'], 
        BACE_CONFIG['compliance_low']['max'] - BACE_CONFIG['compliance_low']['min']
    ),

    # 2. High Val Compliance
    compliance_high_a = scipy.stats.uniform(
        BACE_CONFIG['compliance_high']['min'], 
        BACE_CONFIG['compliance_high']['max'] - BACE_CONFIG['compliance_high']['min']
    ),
    compliance_high_b = scipy.stats.uniform(
        BACE_CONFIG['compliance_high']['min'], 
        BACE_CONFIG['compliance_high']['max'] - BACE_CONFIG['compliance_high']['min']
    ),

    # 3. Public Support
    support_public_a = scipy.stats.uniform(
        BACE_CONFIG['support_public']['min'], 
        BACE_CONFIG['support_public']['max'] - BACE_CONFIG['support_public']['min']
    ),
    support_public_b = scipy.stats.uniform(
        BACE_CONFIG['support_public']['min'], 
        BACE_CONFIG['support_public']['max'] - BACE_CONFIG['support_public']['min']
    ),

    # 4. Underassessment
    # Note: Delinquency is excluded from design_params because it is constrained
    underassessment_a = scipy.stats.uniform(
        BACE_CONFIG['underassessment']['min'], 
        BACE_CONFIG['underassessment']['max'] - BACE_CONFIG['underassessment']['min']
    ),
    underassessment_b = scipy.stats.uniform(
        BACE_CONFIG['underassessment']['min'], 
        BACE_CONFIG['underassessment']['max'] - BACE_CONFIG['underassessment']['min']
    )
)

# -----------------------------------------------------------------------------
# 4. LIKELIHOOD FUNCTION (Uses Dynamic Means)
# -----------------------------------------------------------------------------
def likelihood_pdf(answer, thetas, design, profile=None):
    
    def get_utility(suffix):
        u = 0
        
        # 1. Low Value Compliance
        val_comp_low = design[f'compliance_low_{suffix}']
        # Uses mean from CSV (approx 43.5)
        u += thetas['beta_compliance_low'] * (val_comp_low - BACE_CONFIG['compliance_low']['mean'])

        # 2. High Value Compliance
        val_comp_high = design[f'compliance_high_{suffix}']
        # Uses mean from CSV (approx 58.5)
        u += thetas['beta_compliance_high'] * (val_comp_high - BACE_CONFIG['compliance_high']['mean'])

        # 3. Public Support
        val_support = design[f'support_public_{suffix}']
        # Uses mean from CSV (approx 73.5)
        u += thetas['beta_support_public'] * (val_support - BACE_CONFIG['support_public']['mean'])

        # 4. Underassessment
        val_under = design[f'underassessment_{suffix}']
        # Uses mean from CSV (approx 35.0)
        u += thetas['beta_underassessment'] * (val_under - BACE_CONFIG['underassessment']['mean'])

        # 5. Delinquency (Constrained: Underassessment Mean + Delinquency Mean)
        constraint_constant = BACE_CONFIG['underassessment']['mean'] + BACE_CONFIG['delinquency']['mean']
        val_delinq = constraint_constant - val_under
        # Uses mean from CSV (approx 41.5)
        u += thetas['beta_delinquency'] * (val_delinq - BACE_CONFIG['delinquency']['mean'])

        return u

    base_U_a = get_utility('a')
    base_U_b = get_utility('b')
    
    base_utility_diff = base_U_b - base_U_a
    likelihood = 1 / (1 + np.exp(-1 * thetas['mu'] * base_utility_diff))
    
    eps = 1e-10
    likelihood[likelihood < eps] = eps
    likelihood[likelihood > (1 - eps)] = 1 - eps

    if str(answer) == '1': return likelihood
    else: return 1 - likelihood