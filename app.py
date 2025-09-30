import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="JSON to Excel Converter", layout="centered")

st.title("📝 JSON to Excel Converter")

uploaded_file = st.file_uploader("Upload JSON file", type="json")

if uploaded_file is not None:
    try:
        # Load JSON
        data = json.load(uploaded_file)
        
        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.json_normalize(data)
        else:
            st.error("Unsupported JSON structure.")
            st.stop()

        st.success("✅ JSON loaded successfully!")
        st.dataframe(df)

        # Convert to Excel in memory
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
            writer.save()
            st.download_button(
                label="📥 Download as Excel",
                data=buffer.getvalue(),
                file_name="converted.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
