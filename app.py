from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FILE = "outputs/final_output.xlsx"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_files():

    # Upload files
    main_steam = request.files['main_steam']
    mnc = request.files['mnc']
    mnc1 = request.files['mnc1']

    # Selected scope
    selected_scope = request.form['scope']

    # Valid scopes
    valid_scopes = ['P', 'E', 'V']

    if selected_scope not in valid_scopes:
        return "Invalid Scope Selected. Please choose P, E, or V."

    # Save files
    main_path = os.path.join(UPLOAD_FOLDER, main_steam.filename)
    mnc_path = os.path.join(UPLOAD_FOLDER, mnc.filename)
    mnc1_path = os.path.join(UPLOAD_FOLDER, mnc1.filename)

    main_steam.save(main_path)
    mnc.save(mnc_path)
    mnc1.save(mnc1_path)

    # Read Excel files
    df_main = pd.read_excel(main_path)
    df_mnc = pd.read_excel(mnc_path)
    df_mnc1 = pd.read_excel(mnc1_path)

    # Combine MNC files
    combined_mnc = pd.concat(
        [df_mnc, df_mnc1],
        ignore_index=True
    )

    # Clean headers
    df_main.columns = (
        df_main.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    combined_mnc.columns = (
        combined_mnc.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Check SCOPE column
    if 'SCOPE' not in combined_mnc.columns:
        return "SCOPE column not found in MNC files."

    # Filter selected scope
    combined_mnc = combined_mnc[
        combined_mnc['SCOPE']
        .astype(str)
        .str.strip()
        == selected_scope
    ]

    # Create empty dataframe with MAIN STEAM structure
    aligned_mnc = pd.DataFrame(
        columns=df_main.columns
    )

    # Fill matching columns
    for col in combined_mnc.columns:

        matching_cols = [
            c for c in df_main.columns
            if c == col
        ]

        if len(matching_cols) > 0:

            for match_col in matching_cols:

                aligned_mnc[match_col] = combined_mnc[col]

    # Concatenate
    final_df = pd.concat(
        [df_main, aligned_mnc],
        ignore_index=True
    )

    # Save output
    final_df.to_excel(
        OUTPUT_FILE,
        index=False
    )

    # Download file
    return send_file(
        OUTPUT_FILE,
        as_attachment=True
    )


if __name__ == '__main__':
    app.run(
    host='0.0.0.0',
    port=5000,
    debug=True
)