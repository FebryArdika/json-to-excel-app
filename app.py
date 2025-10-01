import streamlit as st
import csv
import json
import io
import zipfile

st.title("Gabungkan Data JSON ke CSV")

uploaded_files = st.file_uploader("Upload file JSON (boleh lebih dari satu)", type="json", accept_multiple_files=True)

if uploaded_files:
    all_data = []

    for uploaded_file in uploaded_files:
        try:
            data = json.load(uploaded_file)
            all_data.append(data)
        except Exception as e:
            st.warning(f"Gagal parsing {uploaded_file.name}: {e}")

    if all_data:
        # Buat CSV di memori
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(("Cluster", "Date", "Min", "Mean", "Max", "MetrixName"))

        for data in all_data:
            for item in data.get("items", []):
                for series in item.get("timeSeries", []):
                    metric = series.get("metadata", {}).get("metricName", "")
                    cluster = series.get("metadata", {}).get("attributes", {}).get("clusterName", "")
                    for time in series.get("data", []):
                        stats = time.get("aggregateStatistics", {})
                        timestamp = time.get("timestamp", "")
                        min_val = stats.get("min", "")
                        mean_val = stats.get("mean", "")
                        max_val = stats.get("max", "")
                        writer.writerow((cluster, timestamp, min_val, mean_val, max_val, metric))

        # Konversi CSV ke downloadable file
        st.success("Data berhasil diproses!")

        st.download_button(
            label="Download CSV",
            data=output.getvalue(),
            file_name="collected.csv",
            mime="text/csv"
        )
