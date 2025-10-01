import streamlit as st
import csv
import json
import io
import zipfile
import re

st.set_page_config(page_title="JSON to CSV Converter", layout="centered")
st.title("Konversi File JSON ke CSV")

menu = st.sidebar.selectbox("Pilih Jenis Konversi", [
    "Dengan aggregateStatistics",
    "Dengan value biasa"
])

def clean_value(val):
    if isinstance(val, str):
        return re.sub(r"[^\w\s.,\-]", "", val).strip()
    return val

# =============================
# Menu 1: Dengan aggregateStatistics
# =============================
if menu == "Dengan aggregateStatistics":
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

            st.success("Data berhasil dikonversi.")
            st.download_button(
                label="Download CSV",
                data=output.getvalue(),
                file_name="aggregate_statistics.csv",
                mime="text/csv"
            )

# =============================
# Menu 2: Dengan value biasa
# =============================
elif menu == "Dengan value biasa":
    uploaded_files = st.file_uploader("Upload file JSON (boleh lebih dari satu)", type="json", accept_multiple_files=True)

    if uploaded_files:
        all_rows = []

        for uploaded_file in uploaded_files:
            try:
                data = json.load(uploaded_file)

                if not isinstance(data, dict) or "items" not in data:
                    st.warning(f"Format JSON tidak sesuai (tidak ada 'items'): {uploaded_file.name}")
                    continue

                for item in data["items"]:
                    for ts in item.get("timeSeries", []):
                        meta = ts.get("metadata", {})
                        metric_name = clean_value(meta.get("metricName", ""))
                        cluster = clean_value(meta.get("attributes", {}).get("clusterDisplayName", ""))
                        for point in ts.get("data", []):
                            all_rows.append({
                                "Cluster": cluster,
                                "Timestamp": point.get("timestamp", ""),
                                "Value": point.get("value", ""),
                                "MetricName": metric_name
                            })
                st.success(f"Sukses parsing: {uploaded_file.name}")

            except Exception as e:
                st.warning(f"Gagal parsing {uploaded_file.name}: {e}")

        if all_rows:
            output = io.StringIO()
            header = ["Cluster", "Timestamp", "Value", "MetricName"]
            writer = csv.DictWriter(output, fieldnames=header)
            writer.writeheader()
            writer.writerows(all_rows)

            st.download_button(
                label="Download CSV",
                data=output.getvalue(),
                file_name="value_based_data.csv",
                mime="text/csv"
            )
