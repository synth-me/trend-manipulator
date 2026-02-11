from datetime import datetime, timedelta
from dateutil import parser
import pandas as pd
import math
from jinja2 import Environment, FileSystemLoader
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

# Middleware-compatible date format
DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"

CALC_METHODS = {
    "linear": lambda x: x,
    "linear_double": lambda x: x * 2,
    "sin": lambda x: math.sin(x),
    "cos": lambda x: math.cos(x),
    "square": lambda x: x ** 2,
    "sqrt": lambda x: math.sqrt(x) if x >= 0 else 0,
    "log": lambda x: math.log(x + 1)
}

env = Environment(loader=FileSystemLoader(searchpath="."), autoescape=False)
template = env.get_template("template.jinja2")

def _render_xml(context: dict, file_path: str):
    xml_content = template.render(**context)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

def _load_existing_trend(xml_path: str):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    log_data = []
    for record in root.findall("TrendLogValueRecord"):
        # We parse the incoming string immediately to a datetime object for internal logic
        log_data.append({
            "time": parser.parse(record.attrib["Timestamp"]),
            "value": float(record.attrib["Value"])
        })

    metadata = {
        "name": root.attrib.get("Log"),
        "description": root.attrib.get("LogDescription"),
        "unit": root.attrib.get("Unit"),
        # We store these as strings for now, but they will be normalized in the output context
        "start_date": root.attrib.get("StartTime"),
        "end_date": root.attrib.get("EndTime")
    }

    return metadata, log_data

def modify_existing_trend(
    input_file: str,
    range_start: str,
    range_end: str,
    step: str,
    calc: str | None = None,
    constant_value: float | None = None,
    output_file: str = f"./output/results/modified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
):
    if not calc and constant_value is None:
        raise ValueError("Either calc or constant_value must be provided")

    metadata, log_data = _load_existing_trend(f"{input_file}")
    start = parser.parse(range_start)
    end = parser.parse(range_end)

    delta_map = {
        "second": timedelta(seconds=1), # Adicionado
        "minute": timedelta(minutes=1),
        "hour": timedelta(hours=1),
        "day": timedelta(days=1)
    }
    
    if step not in delta_map:
        raise ValueError("step must be: minute, hour, or day")
    delta = delta_map[step]

    # Generate NEW range of data
    calc_fn = CALC_METHODS.get(calc) if calc else None
    new_entries = {}
    current_time = start
    idx = 0
    
    while current_time <= end:
        val = constant_value if constant_value is not None else round(calc_fn(idx), 5)
        # Store using the datetime object as the key to avoid string mismatch issues
        new_entries[current_time] = {"time": current_time, "value": val}
        current_time += delta
        idx += 1

    # Merge: existing log_data keys are already datetime objects from _load_existing_trend
    combined_data_dict = {entry["time"]: entry for entry in log_data}
    combined_data_dict.update(new_entries)

    # Sort and Format for Output
    sorted_log_data = sorted(combined_data_dict.values(), key=lambda x: x["time"])
    
    formatted_log = []
    values = []
    for entry in sorted_log_data:
        values.append(entry["value"])
        formatted_log.append({
            "time": entry["time"].strftime(DATE_FORMAT),
            "value": entry["value"]
        })

    context = {
        "name": metadata["name"],
        "description": metadata["description"],
        "unit": metadata["unit"],
        "start_date": sorted_log_data[0]["time"].strftime(DATE_FORMAT),
        "end_date": sorted_log_data[-1]["time"].strftime(DATE_FORMAT),
        "log_data": formatted_log,
        "metadata": {
            "max": max(values),
            "min": min(values),
            "average": sum(values) / len(values)
        }
    }

    _render_xml(context, output_file)
    return output_file

def delete_existing_trend(
    input_file: str,
    range_start: str,
    range_end: str,
    output_file: str = f"./output/results/deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
):
    metadata, log_data = _load_existing_trend(f"{input_file}")
    start = parser.parse(range_start)
    end = parser.parse(range_end)

    formatted_log = []
    values = []

    for entry in log_data:
        ts = entry["time"] # Already a datetime object
        if not (start <= ts <= end):
            values.append(entry["value"])
            formatted_log.append({
                "time": ts.strftime(DATE_FORMAT),
                "value": entry["value"]
            })

    if not formatted_log:
        raise ValueError("Resulting trend is empty after deletion")

    context = {
        "name": metadata["name"],
        "description": metadata["description"],
        "unit": metadata["unit"],
        "start_date": formatted_log[0]["time"],
        "end_date": formatted_log[-1]["time"],
        "log_data": formatted_log,
        "metadata": {
            "max": max(values),
            "min": min(values),
            "average": sum(values) / len(values)
        }
    }
    _render_xml(context, output_file)
    return output_file

def generate_xml(
    start_date: str,
    end_date: str,
    step: str,
    calc: str,
    file_path: str = f"./output/results/{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
):
    if calc not in CALC_METHODS:
        raise ValueError(f"Invalid calc method. Choose one of: {list(CALC_METHODS.keys())}")

    start = parser.parse(start_date)
    end = parser.parse(end_date)

    freq_map = {
        "second": "S", # Adicionado (S é o código do pandas para segundos)
        "minute": "T",
        "hour": "H",
        "day": "D"
    }
    if step not in freq_map:
        raise ValueError("step must be: minute, hour, or day")

    timestamps = pd.date_range(start=start, end=end, freq=freq_map[step])
    log_data = []
    values = []
    calc_fn = CALC_METHODS[calc]

    for i, ts in enumerate(timestamps):
        value = round(calc_fn(i), 5)
        values.append(value)
        log_data.append({
            "time": ts.strftime(DATE_FORMAT),
            "value": value
        })

    context = {
        "name": f"Generated Trend ({calc})",
        "description": f"Generated using '{calc}' calculation",
        "unit": "unit",
        "start_date": start.strftime(DATE_FORMAT),
        "end_date": end.strftime(DATE_FORMAT),
        "log_data": log_data,
        "metadata": {
            "max": max(values),
            "min": min(values),
            "average": sum(values) / len(values)
        }
    }
    _render_xml(context, file_path)
    return file_path

# Note: validate_excel_trend and convert_to_xml updated to use DATE_FORMAT similarly
def convert_to_xml(excel_path: str, output_file: str, **kwargs):
    df = pd.read_excel(excel_path)
    parsed_timestamps = validate_excel_trend(df)

    log_data = []
    values = []
    for dt, val in zip(parsed_timestamps, df["value"]):
        log_data.append({"time": dt.strftime(DATE_FORMAT), "value": float(val)})
        values.append(float(val))

    context = {
        "name": kwargs.get("name", "ExcelImportedTrend"),
        "description": kwargs.get("description", "Trend imported from Excel"),
        "unit": kwargs.get("unit", ""),
        "start_date": log_data[0]["time"],
        "end_date": log_data[-1]["time"],
        "log_data": log_data,
        "metadata": {"max": max(values), "min": min(values), "average": sum(values)/len(values)}
    }
    _render_xml(context, output_file)
    return output_file


def validate_excel_trend(df):
    # ----------------------------
    # Columns (order + names)
    # ----------------------------
    if list(df.columns) != ["timestamp", "value"]:
        raise ValueError(
            "Excel must have exactly two columns named: timestamp, value"
        )

    # ----------------------------
    # Empty cells
    # ----------------------------
    if df.isnull().any().any():
        raise ValueError("Excel contains empty cells")

    parsed_timestamps = []

    # ----------------------------
    # Timestamp validation (Excel-safe)
    # ----------------------------
    for i, raw in enumerate(df["timestamp"], start=2):
        try:
            if isinstance(raw, (pd.Timestamp, datetime)):
                dt = raw.to_pydatetime() if isinstance(raw, pd.Timestamp) else raw
            else:
                dt = parser.parse(str(raw))

            parsed_timestamps.append(dt)

        except Exception:
            raise ValueError(
                f"Invalid timestamp at row {i}: {raw}"
            )

    # ----------------------------
    # Sorted check
    # ----------------------------
    if parsed_timestamps != sorted(parsed_timestamps):
        raise ValueError("Timestamps must be in ascending order")

    # ----------------------------
    # Numeric values
    # ----------------------------
    if not pd.api.types.is_numeric_dtype(df["value"]):
        raise ValueError("Column 'value' must be numeric")

    return parsed_timestamps