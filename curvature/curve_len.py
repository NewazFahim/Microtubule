import os
import numpy as np
import pandas as pd
import re
from collections import defaultdict
from scipy.optimize import leastsq


# =========================
# 🔴 SCALE (PIXEL → NM)
# =========================

NM_PER_PIXEL = 6.25   


# =========================
# FOLDER PATHS
# =========================

input_folder = r"Z:\Area\All_mask\WT"
output_folder = r"Z:\Area\All_mask\WT\Results"

os.makedirs(output_folder, exist_ok=True)

final_excel = os.path.join(output_folder, "ALL_length_curvature.xlsx")


# =========================
# PATH PARSER
# =========================

def parse_path_file(txt_file_path):
    path_points = {}
    with open(txt_file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if not line.strip():
            continue

        parts = line.strip().split(",")
        if len(parts) < 3:
            continue

        name, x, y = parts[:3]
        path_name = name.rsplit("_", 1)[0]
        point = (float(x), float(y))

        path_points.setdefault(path_name, []).append(point)

    return path_points


# =========================
# PATH LENGTH (nm)
# =========================

def calculate_path_length_linear_interp(points_nm, num_points=1000):
    points = np.array(points_nm)
    if len(points) < 2:
        return 0.0

    deltas = np.diff(points, axis=0)
    seg_lengths = np.hypot(deltas[:, 0], deltas[:, 1])
    distances = np.concatenate([[0], np.cumsum(seg_lengths)])
    total_length = distances[-1]

    if total_length == 0:
        return 0.0

    uniform_distances = np.linspace(0, total_length, num_points)
    x_interp = np.interp(uniform_distances, distances, points[:, 0])
    y_interp = np.interp(uniform_distances, distances, points[:, 1])

    interp_points = np.column_stack((x_interp, y_interp))
    deltas_interp = np.diff(interp_points, axis=0)

    return np.sum(np.hypot(deltas_interp[:, 0], deltas_interp[:, 1]))


# =========================
# CIRCLE FITTING
# =========================

def calc_R(xc, yc, x, y):
    return np.sqrt((x - xc)**2 + (y - yc)**2)

def f_2(c, x, y):
    Ri = calc_R(*c, x, y)
    return Ri - Ri.mean()

def fit_circle(x, y):
    center, _ = leastsq(f_2, (np.mean(x), np.mean(y)), args=(x, y))
    xc, yc = center
    Ri = calc_R(xc, yc, np.array(x), np.array(y))
    return xc, yc, Ri.mean()


# =========================
# PROCESS SINGLE FILE
# =========================

def process_file(txt_path):
    # ---- LENGTH ----
    path_data_px = parse_path_file(txt_path)

    # 🔴 convert px → nm for length
    path_data_nm = {
        k: [(x*NM_PER_PIXEL, y*NM_PER_PIXEL) for (x, y) in v]
        for k, v in path_data_px.items()
    }

    lengths = {k: calculate_path_length_linear_interp(v) for k, v in path_data_nm.items()}

    # ---- CURVATURE ----
    raw_data = pd.read_csv(txt_path, header=None)
    paths = defaultdict(list)

    for _, row in raw_data.iterrows():
        match = re.match(r"(seg_\d+path)", str(row[0]))
        if match:
            # 🔴 convert px → nm for curvature
            paths[match.group(1)].append(
                (float(row[1])*NM_PER_PIXEL, float(row[2])*NM_PER_PIXEL)
            )

    curvatures = {}
    for path, pts in paths.items():
        if len(pts) >= 3:
            x, y = zip(*pts)
            _, _, R = fit_circle(x, y)   # R is now in nm
            if R > 0:
                curvatures[path] = 1.0 / R   # curvature in 1/nm

    # ---- MERGE ----
    records = []
    for seg in lengths:
        L = lengths.get(seg, 0)
        if L == 0:
            continue
        C = curvatures.get(seg, None)
        records.append([seg, L, C])

    df = pd.DataFrame(records, columns=["Segment", "Length_nm", "Curvature_1_per_nm"])
    df["seg_num"] = df["Segment"].str.extract(r"seg_(\d+)").astype(int)
    df = df.sort_values("seg_num").drop(columns="seg_num")

    return df


# =========================
# FOLDER LOOP
# =========================

all_data = []
global_segment_index = 0

txt_files = sorted([f for f in os.listdir(input_folder) if f.endswith(".txt")])

for file in txt_files:
    txt_path = os.path.join(input_folder, file)
    print(f"📄 Processing: {file}")

    df = process_file(txt_path)

    # ---- Save individual excel ----
    excel_name = file.replace(".txt", "_length_curvature.xlsx")
    excel_path = os.path.join(output_folder, excel_name)
    df.to_excel(excel_path, index=False)
    print("   ✅ Saved:", excel_name)

    # ---- Renumber for final file ----
    new_segments = []
    for _ in range(len(df)):
        new_segments.append(f"seg_{global_segment_index}path")
        global_segment_index += 1

    df_final = df.copy()
    df_final["Segment"] = new_segments
    df_final["Source_File"] = file
    all_data.append(df_final)


# =========================
# SAVE FINAL MERGED FILE
# =========================

final_df = pd.concat(all_data, ignore_index=True)
final_df.to_excel(final_excel, index=False)

print("\n🎉 ALL FILES DONE!")
print("📦 Final combined file:", final_excel)
print("Total segments:", len(final_df))
