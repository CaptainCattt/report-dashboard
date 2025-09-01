import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io


# --- Hàm xử lý dữ liệu TikTok ---
def process_tiktok_data(df_new, ngay_bat_dau, ngay_ket_thuc):
    df_new.columns = df_new.columns.str.strip()  # chuẩn hóa tên cột

    # Bắt đầu bằng copy Seller SKU
    df_new["SKU Category"] = df_new["Seller SKU"].copy()

    # Danh sách các mẫu thay thế
    replacements = {
        r"^(COMBO-SC-ANHDUC|COMBO-SC-NGOCTRINH|COMBO-SC-MIX|SC_COMBO_MIX|SC_COMBO_MIX_LIVESTREAM|COMBO-SC_LIVESTREAM|SC_COMBO_MIX_01)$": "COMBO-SC",
        r"^SC_X1$": "SC-450g",
        r"^SC_X2$": "SC-x2-450g",
        r"^(SC_COMBO_X1|COMBO-CAYVUA-X1|SC_COMBO_X1_LIVESTREAM|COMBO-SCX1|COMBO-SCX1_LIVESTREAM)$": "COMBO-SCX1",
        r"^(SC_COMBO_X2|COMBO-SIEUCAY-X2|SC_COMBO_X2_LIVESTREAM|COMBO-SCX2|COMBO-SCX2_LIVESTREAM)$": "COMBO-SCX2",
        r"^(BTHP-Cay-200gr|BTHP_Cay)$": "BTHP-CAY",
        r"^(BTHP-200gr|BTHP_KhongCay)$": "BTHP-0CAY",
        r"^(BTHP_COMBO_MIX|BTHP003_combo_mix)$": "BTHP-COMBO",
        r"^(BTHP_COMBO_KhongCay|BTHP003_combo_kocay)$": "BTHP-COMBO-0CAY",
        r"^(BTHP_COMBO_Cay|BTHP003_combo_cay)$": "BTHP-COMBO-CAY",
        r"^BTHP-COMBO\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP-COMBO\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^BTHP_COMBO_MIX\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP_COMBO_MIX\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^(BTHP-2Cay-2KhongCay)": "COMBO_4BTHP",
        r"^(BTHP-4Hu-KhongCay)$": "4BTHP_0CAY",
        r"^(BTHP-4Hu-Cay)$": "4BTHP_CAY",
    }

    for pattern, replacement in replacements.items():
        df_new["SKU Category"] = df_new["SKU Category"].str.replace(
            pattern, replacement, regex=True
        )

    for pattern, replacement in replacements.items():
        df_new["SKU Category"] = df_new["SKU Category"].str.replace(
            pattern, replacement, regex=True
        )

    date_columns = [
        "Created Time",
        "Paid Time",
        "RTS Time",
        "Shipped Time",
        "Delivered Time",
        "Cancelled Time",
    ]

    # Ép kiểu về datetime
    df_new[date_columns] = df_new[date_columns].apply(
        lambda col: pd.to_datetime(col, errors="coerce", format="%d/%m/%Y %H:%M:%S")
    )

    # Loại bỏ giờ, giữ lại phần ngày (vẫn là kiểu datetime)
    for col in date_columns:
        df_new[col] = df_new[col].dt.normalize()

    don_hoan_thanh_tiktok = df_new[
        (df_new["Order Substatus"] == "Completed")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
    ]

    don_hoan_thanh_tiktok_unique = don_hoan_thanh_tiktok["Order ID"].drop_duplicates()
    so_don_hoan_thanh_tiktok = len(don_hoan_thanh_tiktok_unique)

    don_da_giao_tiktok = df_new[
        (df_new["Order Substatus"] == "Delivered")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
    ]
    don_da_giao_tiktok_unique = don_da_giao_tiktok["Order ID"].drop_duplicates()
    so_don_da_giao_tiktok = len(don_da_giao_tiktok_unique)
    #

    don_cloud_tiktok = df_new[
        (
            (df_new["Order Substatus"] != "Canceled")
            & (
                (df_new["Delivered Time"] > ngay_ket_thuc)
                | (df_new["Delivered Time"].isna())
            )
        )
    ]
    don_cloud_tiktok_unique = don_cloud_tiktok["Order ID"].drop_duplicates()
    so_don_cloud_tiktok = len(don_cloud_tiktok_unique)

    SCx1_tiktok_hoan_thanh = df_new[
        (df_new["SKU Category"] == "SC-450g")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    SCx2_tiktok_hoan_thanh = df_new[
        (df_new["SKU Category"] == "SC-x2-450g")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    SC_Combo_tiktok_hoan_thanh = df_new[
        (df_new["SKU Category"] == "COMBO-SC")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    Combo_Scx1_tiktok_hoan_thanh = df_new[
        (df_new["SKU Category"] == "COMBO-SCX1")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    Combo_Scx2_tiktok_hoan_thanh = df_new[
        (df_new["SKU Category"] == "COMBO-SCX2")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    so_luong_SCx1_tiktok_hoan_thanh = SCx1_tiktok_hoan_thanh["Quantity"].sum()
    so_luong_SCx2_tiktok_hoan_thanh = SCx2_tiktok_hoan_thanh["Quantity"].sum()
    so_luong_SC_Combo_tiktok_hoan_thanh = SC_Combo_tiktok_hoan_thanh["Quantity"].sum()

    so_luong_Combo_Scx1_tiktok_hoan_thanh = Combo_Scx1_tiktok_hoan_thanh[
        "Quantity"
    ].sum()
    so_luong_Combo_Scx2_tiktok_hoan_thanh = Combo_Scx2_tiktok_hoan_thanh[
        "Quantity"
    ].sum()

    tong_san_pham_tiktok_hoan_thanh = (
        so_luong_SCx1_tiktok_hoan_thanh
        + so_luong_Combo_Scx1_tiktok_hoan_thanh * 2
        + so_luong_SCx2_tiktok_hoan_thanh
        + so_luong_Combo_Scx2_tiktok_hoan_thanh * 2
        + so_luong_SC_Combo_tiktok_hoan_thanh * 2
    )

    SCx1_tiktok_da_giao = df_new[
        (df_new["SKU Category"] == "SC-450g")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    SCx2_tiktok_da_giao = df_new[
        (df_new["SKU Category"] == "SC-x2-450g")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    SC_Combo_tiktok_da_giao = df_new[
        (df_new["SKU Category"] == "COMBO-SC")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    Combo_Scx1_tiktok_da_giao = df_new[
        (df_new["SKU Category"] == "COMBO-SCX1")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    Combo_Scx2_tiktok_da_giao = df_new[
        (df_new["SKU Category"] == "COMBO-SCX2")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    so_luong_SCx1_tiktok_da_giao = SCx1_tiktok_da_giao["Quantity"].sum()
    so_luong_SCx2_tiktok_da_giao = SCx2_tiktok_da_giao["Quantity"].sum()
    so_luong_SC_Combo_tiktok_da_giao = SC_Combo_tiktok_da_giao["Quantity"].sum()

    so_luong_Combo_Scx1_tiktok_da_giao = Combo_Scx1_tiktok_da_giao["Quantity"].sum()
    so_luong_Combo_Scx2_tiktok_da_giao = Combo_Scx2_tiktok_da_giao["Quantity"].sum()

    tong_san_pham_tiktok_da_giao = (
        so_luong_SCx1_tiktok_da_giao
        + so_luong_Combo_Scx1_tiktok_da_giao * 2
        + so_luong_SCx2_tiktok_da_giao
        + so_luong_Combo_Scx2_tiktok_da_giao * 2
        + so_luong_SC_Combo_tiktok_da_giao * 2
    )

    SCx1_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "SC-450g")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    SCx2_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "SC-x2-450g")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    SC_Combo_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "COMBO-SC")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    CB_SCx1_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "COMBO-SCX1")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    CB_SCx2_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "COMBO-SCX2")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    so_luong_SCx1_tiktok_hoan_tra = SCx1_tiktok_hoan_tra["Quantity"].sum()
    so_luong_SCx2_tiktok_hoan_tra = SCx2_tiktok_hoan_tra["Quantity"].sum()
    so_luong_SC_Combo_tiktok_hoan_tra = SC_Combo_tiktok_hoan_tra["Quantity"].sum()
    so_luong_CB_SCx1_tiktok_hoan_tra = CB_SCx1_tiktok_hoan_tra["Quantity"].sum()
    so_luong_CB_SCx2_tiktok_hoan_tra = CB_SCx2_tiktok_hoan_tra["Quantity"].sum()

    tong_san_pham_tiktok_hoan_tra = (
        so_luong_SCx1_tiktok_hoan_tra
        + so_luong_SCx2_tiktok_hoan_tra
        + so_luong_SC_Combo_tiktok_hoan_tra * 2
    )

    # BÁNH TRÁNG

    # Hoàn thành
    BTHP_0CAY_hoan_thanh = df_new[
        (df_new["SKU Category"] == "BTHP-0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    BTHP_CAY_hoan_thanh = df_new[
        (df_new["SKU Category"] == "BTHP-CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    BTHP_Combo_hoan_thanh = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    BTHP_Combo_0CAY_hoan_thanh = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO-0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    BTHP_Combo_CAY_hoan_thanh = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO-CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    so_luong_BTHP_0CAY_hoan_thanh = BTHP_0CAY_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_CAY_hoan_thanh = BTHP_CAY_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_Combo_hoan_thanh = BTHP_Combo_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_Combo_0CAY_hoan_thanh = BTHP_Combo_0CAY_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_Combo_CAY_hoan_thanh = BTHP_Combo_CAY_hoan_thanh["Quantity"].sum()

    # Đã giao
    BTHP_0CAY_da_giao = df_new[
        (df_new["SKU Category"] == "BTHP-0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    BTHP_CAY_da_giao = df_new[
        (df_new["SKU Category"] == "BTHP-CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    BTHP_Combo_da_giao = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    BTHP_Combo_0CAY_da_giao = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO-0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    BTHP_Combo_CAY_da_giao = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO-CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    so_luong_BTHP_0CAY_da_giao = BTHP_0CAY_da_giao["Quantity"].sum()
    so_luong_BTHP_CAY_da_giao = BTHP_CAY_da_giao["Quantity"].sum()
    so_luong_BTHP_Combo_da_giao = BTHP_Combo_da_giao["Quantity"].sum()
    so_luong_BTHP_Combo_0CAY_da_giao = BTHP_Combo_0CAY_da_giao["Quantity"].sum()
    so_luong_BTHP_Combo_CAY_da_giao = BTHP_Combo_CAY_da_giao["Quantity"].sum()

    # Combo BTHP + SC

    BTHP_SCx1_hoan_thanh = df_new[
        (df_new["SKU Category"] == "COMBO_BTHP_SCx1")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    BTHP_SCx2_hoan_thanh = df_new[
        (df_new["SKU Category"] == "COMBO_BTHP_SCx2")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    BTHP_SCx1_da_giao = df_new[
        (df_new["SKU Category"] == "COMBO_BTHP_SCx1")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    BTHP_SCx2_da_giao = df_new[
        (df_new["SKU Category"] == "COMBO_BTHP_SCx2")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    BTHP_COMBO4_hoan_thanh_tiktok = df_new[
        (df_new["SKU Category"] == "COMBO_4BTHP")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    BTHP_COMBO4_da_giao_tiktok = df_new[
        (df_new["SKU Category"] == "COMBO_4BTHP")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    so_luong_BTHP_COMBO4_hoan_thanh_tiktok = BTHP_COMBO4_hoan_thanh_tiktok[
        "Quantity"
    ].sum()
    so_luong_BTHP_COMBO4_da_giao_tiktok = BTHP_COMBO4_da_giao_tiktok["Quantity"].sum()

    so_luong_BTHP_SCx1_hoan_thanh = BTHP_SCx1_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_SCx2_hoan_thanh = BTHP_SCx2_hoan_thanh["Quantity"].sum()
    so_luong_BTHP_SCx1_da_giao = BTHP_SCx1_da_giao["Quantity"].sum()
    so_luong_BTHP_SCx2_da_giao = BTHP_SCx2_da_giao["Quantity"].sum()

    COMBO_4_BTHP_0CAY_hoan_thanh_tiktok = df_new[
        (df_new["SKU Category"] == "4BTHP_0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    COMBO_4_BTHP_CAY_hoan_thanh_tiktok = df_new[
        (df_new["SKU Category"] == "4BTHP_CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Completed")
    ]

    COMBO_4_BTHP_0CAY_da_giao_tiktok = df_new[
        (df_new["SKU Category"] == "4BTHP_0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    COMBO_4_BTHP_CAY_da_giao_tiktok = df_new[
        (df_new["SKU Category"] == "4BTHP_CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Order Substatus"] == "Delivered")
    ]

    soluong_COMBO_4_BTHP_0CAY_hoan_thanh_tiktok = COMBO_4_BTHP_0CAY_hoan_thanh_tiktok[
        "Quantity"
    ].sum()
    soluong_COMBO_4_BTHP_CAY_hoan_thanh_tiktok = COMBO_4_BTHP_CAY_hoan_thanh_tiktok[
        "Quantity"
    ].sum()

    soluong_COMBO_4_BTHP_0CAY_da_giao_tiktok = COMBO_4_BTHP_0CAY_da_giao_tiktok[
        "Quantity"
    ].sum()
    soluong_COMBO_4_BTHP_CAY_da_giao_tiktok = COMBO_4_BTHP_CAY_da_giao_tiktok[
        "Quantity"
    ].sum()

    # Hoàn trả
    BTHP_0CAY_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "BTHP-0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    BTHP_CAY_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "BTHP-CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    BTHP_Combo_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    BTHP_Combo_0CAY_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO-0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    BTHP_Combo_CAY_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "BTHP-COMBO-CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    BTHP_SCx1_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "COMBO_BTHP_SCx1")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    BTHP_SCx2_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "COMBO_BTHP_SCx2")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    BTHP_COMBO4_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "COMBO_4BTHP")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    COMBO_4_BTHP_0CAY_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "4BTHP_0CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    COMBO_4_BTHP_CAY_tiktok_hoan_tra = df_new[
        (df_new["SKU Category"] == "4BTHP_CAY")
        & (df_new["Delivered Time"] >= ngay_bat_dau)
        & (df_new["Delivered Time"] <= ngay_ket_thuc)
        & (df_new["Sku Quantity of return"] != 0)
    ]

    so_luong_BTHP_0CAY_tiktok_hoan_tra = BTHP_0CAY_tiktok_hoan_tra["Quantity"].sum()
    so_luong_BTHP_CAY_tiktok_hoan_tra = BTHP_CAY_tiktok_hoan_tra["Quantity"].sum()
    so_luong_BTHP_Combo_tiktok_hoan_tra = BTHP_Combo_tiktok_hoan_tra["Quantity"].sum()
    so_luong_BTHP_Combo_0CAY_tiktok_hoan_tra = BTHP_Combo_0CAY_tiktok_hoan_tra[
        "Quantity"
    ].sum()
    so_luong_BTHP_Combo_CAY_tiktok_hoan_tra = BTHP_Combo_CAY_tiktok_hoan_tra[
        "Quantity"
    ].sum()
    so_luong_BTHP_SCx1_tiktok_hoan_tra = BTHP_SCx1_tiktok_hoan_tra["Quantity"].sum()
    so_luong_BTHP_SCx2_tiktok_hoan_tra = BTHP_SCx2_tiktok_hoan_tra["Quantity"].sum()
    so_luong_BTHP_COMBO4_tiktok_hoan_tra = BTHP_COMBO4_tiktok_hoan_tra["Quantity"].sum()
    soluong_COMBO_4_BTHP_0CAY_tiktok_hoan_tra = COMBO_4_BTHP_0CAY_tiktok_hoan_tra[
        "Quantity"
    ].sum()
    soluong_COMBO_4_BTHP_CAY_tiktok_hoan_tra = COMBO_4_BTHP_CAY_tiktok_hoan_tra[
        "Quantity"
    ].sum()

    # CLOUD
    SCx1_tiktok_cloud = don_cloud_tiktok[don_cloud_tiktok["SKU Category"] == "SC-450g"]
    SCx2_tiktok_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "SC-x2-450g"
    ]
    SC_Combo_tiktok_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "COMBO-SC"
    ]
    Combo_Scx1_tiktok_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "COMBO-SCX1"
    ]
    Combo_Scx2_tiktok_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "COMBO-SCX2"
    ]
    BTHP_0CAY_cloud = don_cloud_tiktok[don_cloud_tiktok["SKU Category"] == "BTHP-0CAY"]
    BTHP_CAY_cloud = don_cloud_tiktok[don_cloud_tiktok["SKU Category"] == "BTHP-CAY"]
    BTHP_Combo_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "BTHP-COMBO"
    ]
    BTHP_Combo_0CAY_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "BTHP-COMBO-0CAY"
    ]
    BTHP_Combo_CAY_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "BTHP-COMBO-CAY"
    ]
    BTHP_SCx1_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "COMBO_BTHP_SCx1"
    ]
    BTHP_SCx2_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "COMBO_BTHP_SCx2"
    ]
    BTHP_COMBO4_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "COMBO_4BTHP"
    ]
    COMBO_4_BTHP_0CAY_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "4BTHP_0CAY"
    ]
    COMBO_4_BTHP_CAY_cloud = don_cloud_tiktok[
        don_cloud_tiktok["SKU Category"] == "4BTHP_CAY"
    ]
    so_luong_SCx1_tiktok_cloud = SCx1_tiktok_cloud["Quantity"].sum()
    so_luong_SCx2_tiktok_cloud = SCx2_tiktok_cloud["Quantity"].sum()
    so_luong_SC_Combo_tiktok_cloud = SC_Combo_tiktok_cloud["Quantity"].sum()
    so_luong_Combo_Scx1_tiktok_cloud = Combo_Scx1_tiktok_cloud["Quantity"].sum()
    so_luong_Combo_Scx2_tiktok_cloud = Combo_Scx2_tiktok_cloud["Quantity"].sum()
    so_luong_BTHP_0CAY_tiktok_cloud = BTHP_0CAY_cloud["Quantity"].sum()
    so_luong_BTHP_CAY_tiktok_cloud = BTHP_CAY_cloud["Quantity"].sum()
    so_luong_BTHP_Combo_tiktok_cloud = BTHP_Combo_cloud["Quantity"].sum()
    so_luong_BTHP_Combo_0CAY_tiktok_cloud = BTHP_Combo_0CAY_cloud["Quantity"].sum()
    so_luong_BTHP_Combo_CAY_tiktok_cloud = BTHP_Combo_CAY_cloud["Quantity"].sum()
    so_luong_BTHP_SCx1_tiktok_cloud = BTHP_SCx1_cloud["Quantity"].sum()
    so_luong_BTHP_SCx2_tiktok_cloud = BTHP_SCx2_cloud["Quantity"].sum()
    so_luong_BTHP_COMBO4_tiktok_cloud = BTHP_COMBO4_cloud["Quantity"].sum()
    soluong_COMBO_4_BTHP_0CAY_tiktok_cloud = COMBO_4_BTHP_0CAY_cloud["Quantity"].sum()
    soluong_COMBO_4_BTHP_CAY_tiktok_cloud = COMBO_4_BTHP_CAY_cloud["Quantity"].sum()

    tong_so_luong_BTHP_hoan_thanh = (
        so_luong_BTHP_0CAY_hoan_thanh
        + so_luong_BTHP_CAY_hoan_thanh
        + so_luong_BTHP_Combo_hoan_thanh * 2
        + so_luong_BTHP_Combo_0CAY_hoan_thanh * 2
        + so_luong_BTHP_Combo_CAY_hoan_thanh * 2
        + so_luong_BTHP_SCx1_hoan_thanh * 2
        + so_luong_BTHP_SCx2_hoan_thanh * 2
        + so_luong_BTHP_COMBO4_hoan_thanh_tiktok * 4
        + soluong_COMBO_4_BTHP_0CAY_hoan_thanh_tiktok * 4
        + soluong_COMBO_4_BTHP_CAY_hoan_thanh_tiktok * 4
    )

    tong_so_luong_BTHP_da_giao = (
        so_luong_BTHP_0CAY_da_giao
        + so_luong_BTHP_CAY_da_giao
        + so_luong_BTHP_Combo_da_giao * 2
        + so_luong_BTHP_Combo_0CAY_da_giao * 2
        + so_luong_BTHP_Combo_CAY_da_giao * 2
        + so_luong_BTHP_SCx1_da_giao * 2
        + so_luong_BTHP_SCx2_da_giao * 2
        + so_luong_BTHP_COMBO4_da_giao_tiktok * 4
        + soluong_COMBO_4_BTHP_0CAY_da_giao_tiktok * 4
        + soluong_COMBO_4_BTHP_CAY_da_giao_tiktok * 4
    )

    Tong_soluong_SCx1_tiktok = (
        so_luong_SCx1_tiktok_hoan_thanh
        + so_luong_SCx1_tiktok_da_giao
        + so_luong_Combo_Scx1_tiktok_da_giao * 2
        + so_luong_Combo_Scx1_tiktok_hoan_thanh * 2
        + so_luong_BTHP_SCx1_hoan_thanh
        + so_luong_BTHP_SCx1_da_giao
    )

    Tong_soluong_SCx2_tiktok = (
        so_luong_SCx2_tiktok_hoan_thanh
        + so_luong_SCx2_tiktok_da_giao
        + so_luong_Combo_Scx2_tiktok_da_giao * 2
        + so_luong_Combo_Scx2_tiktok_hoan_thanh * 2
        + so_luong_BTHP_SCx2_hoan_thanh
        + so_luong_BTHP_SCx2_da_giao
    )

    Tong_soluong_SCxCombo_tiktok = (
        so_luong_SC_Combo_tiktok_hoan_thanh + so_luong_SC_Combo_tiktok_da_giao
    ) * 2

    Tong_soluong_BTHP_0CAY_tiktok = (
        so_luong_BTHP_0CAY_hoan_thanh
        + so_luong_BTHP_0CAY_da_giao
        #
        + so_luong_BTHP_Combo_0CAY_hoan_thanh * 2
        + so_luong_BTHP_Combo_0CAY_da_giao * 2
        #
        + soluong_COMBO_4_BTHP_0CAY_hoan_thanh_tiktok * 4
        + soluong_COMBO_4_BTHP_0CAY_da_giao_tiktok * 4
    )

    Tong_soluong_BTHP_CAY_tiktok = (
        so_luong_BTHP_CAY_hoan_thanh
        + so_luong_BTHP_CAY_da_giao
        #
        + so_luong_BTHP_Combo_CAY_hoan_thanh * 2
        + so_luong_BTHP_Combo_CAY_da_giao * 2
        #
        + soluong_COMBO_4_BTHP_CAY_hoan_thanh_tiktok * 4
        + soluong_COMBO_4_BTHP_CAY_da_giao_tiktok * 4
    )

    Tong_soluong_BTHP_COMBO_tiktok = (
        (so_luong_BTHP_Combo_hoan_thanh + so_luong_BTHP_Combo_da_giao) * 2
        + (so_luong_BTHP_SCx1_hoan_thanh + so_luong_BTHP_SCx1_da_giao) * 2
        + (so_luong_BTHP_SCx2_hoan_thanh + so_luong_BTHP_SCx2_da_giao) * 2
        + (so_luong_BTHP_COMBO4_hoan_thanh_tiktok + so_luong_BTHP_COMBO4_da_giao_tiktok)
        * 4
    )

    return (
        # cloud
        so_don_cloud_tiktok,
        so_luong_SCx1_tiktok_cloud,
        so_luong_SCx2_tiktok_cloud,
        so_luong_SC_Combo_tiktok_cloud,
        so_luong_Combo_Scx1_tiktok_cloud,
        so_luong_Combo_Scx2_tiktok_cloud,
        so_luong_BTHP_0CAY_tiktok_cloud,
        so_luong_BTHP_CAY_tiktok_cloud,
        so_luong_BTHP_Combo_tiktok_cloud,
        so_luong_BTHP_Combo_0CAY_tiktok_cloud,
        so_luong_BTHP_Combo_CAY_tiktok_cloud,
        so_luong_BTHP_SCx1_tiktok_cloud,
        so_luong_BTHP_SCx2_tiktok_cloud,
        so_luong_BTHP_COMBO4_tiktok_cloud,
        soluong_COMBO_4_BTHP_0CAY_tiktok_cloud,
        soluong_COMBO_4_BTHP_CAY_tiktok_cloud,
        ###Hoan tra
        so_luong_SCx1_tiktok_hoan_tra,
        so_luong_SCx2_tiktok_hoan_tra,
        so_luong_SC_Combo_tiktok_hoan_tra,
        so_luong_CB_SCx1_tiktok_hoan_tra,
        so_luong_CB_SCx2_tiktok_hoan_tra,
        tong_san_pham_tiktok_hoan_tra,
        so_luong_BTHP_0CAY_tiktok_hoan_tra,
        so_luong_BTHP_CAY_tiktok_hoan_tra,
        so_luong_BTHP_Combo_tiktok_hoan_tra,
        so_luong_BTHP_Combo_0CAY_tiktok_hoan_tra,
        so_luong_BTHP_Combo_CAY_tiktok_hoan_tra,
        so_luong_BTHP_SCx1_tiktok_hoan_tra,
        so_luong_BTHP_SCx2_tiktok_hoan_tra,
        so_luong_BTHP_COMBO4_tiktok_hoan_tra,
        soluong_COMBO_4_BTHP_0CAY_tiktok_hoan_tra,
        soluong_COMBO_4_BTHP_CAY_tiktok_hoan_tra,
        ###
        Tong_soluong_SCx1_tiktok,
        Tong_soluong_SCx2_tiktok,
        Tong_soluong_SCxCombo_tiktok,
        Tong_soluong_BTHP_0CAY_tiktok,
        Tong_soluong_BTHP_CAY_tiktok,
        Tong_soluong_BTHP_COMBO_tiktok,
        ####
        soluong_COMBO_4_BTHP_0CAY_hoan_thanh_tiktok,
        soluong_COMBO_4_BTHP_CAY_hoan_thanh_tiktok,
        soluong_COMBO_4_BTHP_0CAY_da_giao_tiktok,
        soluong_COMBO_4_BTHP_CAY_da_giao_tiktok,
        ###
        so_luong_BTHP_COMBO4_hoan_thanh_tiktok,
        so_luong_BTHP_COMBO4_da_giao_tiktok,
        ###
        tong_san_pham_tiktok_hoan_thanh,
        tong_san_pham_tiktok_da_giao,
        so_luong_SC_Combo_tiktok_hoan_thanh,
        so_luong_SC_Combo_tiktok_da_giao,
        so_luong_SCx1_tiktok_hoan_thanh,
        so_luong_SCx1_tiktok_da_giao,
        so_luong_SCx2_tiktok_hoan_thanh,
        so_luong_SCx2_tiktok_da_giao,
        so_don_da_giao_tiktok,
        so_don_hoan_thanh_tiktok,
        so_luong_Combo_Scx1_tiktok_hoan_thanh,
        so_luong_Combo_Scx2_tiktok_hoan_thanh,
        so_luong_Combo_Scx1_tiktok_da_giao,
        so_luong_Combo_Scx2_tiktok_da_giao,
        # Bánh tráng
        so_luong_BTHP_0CAY_hoan_thanh,
        so_luong_BTHP_CAY_hoan_thanh,
        so_luong_BTHP_Combo_hoan_thanh,
        so_luong_BTHP_Combo_0CAY_hoan_thanh,
        so_luong_BTHP_Combo_CAY_hoan_thanh,
        so_luong_BTHP_0CAY_da_giao,
        so_luong_BTHP_CAY_da_giao,
        so_luong_BTHP_Combo_da_giao,
        so_luong_BTHP_Combo_0CAY_da_giao,
        so_luong_BTHP_Combo_CAY_da_giao,
        tong_so_luong_BTHP_da_giao,
        tong_so_luong_BTHP_hoan_thanh,
        # Combo BTHP + SC
        so_luong_BTHP_SCx1_hoan_thanh,
        so_luong_BTHP_SCx2_hoan_thanh,
        so_luong_BTHP_SCx1_da_giao,
        so_luong_BTHP_SCx2_da_giao,
    )


# --- Hàm xử lý dữ liệu Shopee ---
def process_shopee_data(df_shopee, ngay_bat_dau, ngay_ket_thuc):
    df_shopee.columns = df_shopee.columns.str.strip()

    df_shopee["Acctually type"] = df_shopee["Trạng Thái Đơn Hàng"]

    df_shopee["Acctually type"] = df_shopee["Acctually type"].apply(
        lambda x: (
            "Đơn hàng đã đến User"
            if isinstance(x, str) and "Người mua xác nhận đã nhận được hàng" in x
            else x
        )
    )

    df_shopee["SKU Category"] = df_shopee["SKU phân loại hàng"].copy()

    # Danh sách các mẫu thay thế
    replacements = {
        r"^(COMBO-SC-ANHDUC|COMBO-SC-NGOCTRINH|COMBO-SC-MIX|SC_COMBO_MIX|SC_COMBO_MIX_LIVESTREAM|COMBO-SC_LIVESTREAM|SC_COMBO_MIX_01)$": "COMBO-SC",
        r"^SC_X1$": "SC-450g",
        r"^SC_X2$": "SC-x2-450g",
        r"^(SC_COMBO_X1|COMBO-CAYVUA-X1|SC_COMBO_X1_LIVESTREAM|COMBO-SCX1|COMBO-SCX1_LIVESTREAM)$": "COMBO-SCX1",
        r"^(SC_COMBO_X2|COMBO-SIEUCAY-X2|SC_COMBO_X2_LIVESTREAM|COMBO-SCX2|COMBO-SCX2_LIVESTREAM)$": "COMBO-SCX2",
        r"^(BTHP-Cay-200gr|BTHP_Cay)$": "BTHP-CAY",
        r"^(BTHP-200gr|BTHP_KhongCay)$": "BTHP-0CAY",
        r"^(BTHP_COMBO_MIX|BTHP003_combo_mix)$": "BTHP-COMBO",
        r"^(BTHP_COMBO_KhongCay|BTHP003_combo_kocay)$": "BTHP-COMBO-0CAY",
        r"^(BTHP_COMBO_Cay|BTHP003_combo_cay)$": "BTHP-COMBO-CAY",
        r"^BTHP-COMBO\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP-COMBO\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^BTHP_COMBO_MIX\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP_COMBO_MIX\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^(BTHP-2Cay-2KhongCay)": "COMBO_4BTHP",
        r"^(BTHP-4Hu-KhongCay)$": "4BTHP_0CAY",
        r"^(BTHP-4Hu-Cay)$": "4BTHP_CAY",
    }

    for pattern, replacement in replacements.items():
        df_shopee["SKU Category"] = df_shopee["SKU Category"].str.replace(
            pattern, replacement, regex=True
        )

    date_columns_shopee = [
        "Ngày đặt hàng",
        "Ngày giao hàng dự kiến",
        "Ngày gửi hàng",
        "Thời gian giao hàng",
    ]

    # Ép kiểu về datetime với định dạng đúng
    df_shopee[date_columns_shopee] = df_shopee[date_columns_shopee].apply(
        lambda col: pd.to_datetime(col, errors="coerce", format="%Y-%m-%d %H:%M")
    )

    # Loại bỏ giờ, giữ lại phần ngày
    for col in date_columns_shopee:
        df_shopee[col] = df_shopee[col].dt.normalize()

    don_hoan_thanh_shopee = df_shopee[
        (df_shopee["Acctually type"].isin(["Hoàn thành"]))
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
    ]

    don_hoan_thanh_shopee_unique = don_hoan_thanh_shopee[
        "Mã đơn hàng"
    ].drop_duplicates()
    so_don_hoan_thanh_shopee = len(don_hoan_thanh_shopee_unique)

    don_da_giao_shopee = df_shopee[
        (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    don_da_giao_shopee_unique = don_da_giao_shopee["Mã đơn hàng"].drop_duplicates()
    so_don_da_giao_shopee = len(don_da_giao_shopee_unique)

    don_dang_giao_shopee = df_shopee[
        (df_shopee["Acctually type"] == "Đang giao")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
    ]
    don_dang_giao_shopee_unique = don_dang_giao_shopee["Mã đơn hàng"].drop_duplicates()
    so_don_dang_giao_shopee = len(don_dang_giao_shopee_unique)

    don_hoan_tra_shopee = df_shopee[
        (df_shopee["Trạng thái Trả hàng/Hoàn tiền"] == "Đã Chấp Thuận Yêu Cầu")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
    ]
    don_hoan_tra_shopee_unique = don_hoan_tra_shopee["Mã đơn hàng"].drop_duplicates()
    so_don_hoan_tra_shopee = len(don_hoan_tra_shopee_unique)

    don_cloud_shopee = df_shopee[
        (df_shopee["Acctually type"] != "Đã hủy")
        & (
            (df_shopee["Thời gian giao hàng"] > ngay_ket_thuc)
            | (df_shopee["Thời gian giao hàng"].isna())
        )
    ]
    don_cloud_shopee_unique = don_cloud_shopee["Mã đơn hàng"].drop_duplicates()
    so_don_cloud_shopee = len(don_cloud_shopee_unique)

    # HOÀN THÀNH
    SCx1_shopee_hoanh_thanh = df_shopee[
        (df_shopee["SKU Category"] == "SC-450g")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    SCx2_shopee_hoanh_thanh = df_shopee[
        (df_shopee["SKU Category"] == "SC-x2-450g")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    SC_Combo_shopee_hoanh_thanh = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SC")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    so_luong_SCx1_shopee_hoanh_thanh = SCx1_shopee_hoanh_thanh["Số lượng"].sum()
    so_luong_SCx2_shopee_hoanh_thanh = SCx2_shopee_hoanh_thanh["Số lượng"].sum()
    so_luong_SC_Combo_shopee_hoanh_thanh = SC_Combo_shopee_hoanh_thanh["Số lượng"].sum()

    SCx1_shopee_da_giao = df_shopee[
        (df_shopee["SKU Category"] == "SC-450g")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    SCx2_shopee_da_giao = df_shopee[
        (df_shopee["SKU Category"] == "SC-x2-450g")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    SC_Combo_shopee_da_giao = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SC")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    so_luong_SCx1_shopee_da_giao = SCx1_shopee_da_giao["Số lượng"].sum()
    so_luong_SCx2_shopee_da_giao = SCx2_shopee_da_giao["Số lượng"].sum()
    so_luong_SC_Combo_shopee_da_giao = SC_Combo_shopee_da_giao["Số lượng"].sum()

    SCx1_shopee_hoan_tra = df_shopee[
        (df_shopee["SKU Category"] == "SC-450g")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    SCx2_shopee_hoan_tra = df_shopee[
        (df_shopee["SKU Category"] == "SC-x2-450g")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    SC_Combo_shopee_hoan_tra = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SC")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    CB_SCx1_shopee_hoan_tra = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SCX1")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    CB_SCx2_shopee_hoan_tra = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SCX2")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    so_luong_SCx1_shopee_hoan_tra = SCx1_shopee_hoan_tra["Số lượng"].sum()
    so_luong_SCx2_shopee_hoan_tra = SCx2_shopee_hoan_tra["Số lượng"].sum()
    so_luong_SC_Combo_shopee_hoan_tra = SC_Combo_shopee_hoan_tra["Số lượng"].sum()
    so_luong_CB_SCx1_shopee_hoan_tra = CB_SCx1_shopee_hoan_tra["Số lượng"].sum()
    so_luong_CB_SCx2_shopee_hoan_tra = CB_SCx2_shopee_hoan_tra["Số lượng"].sum()

    tong_san_pham_shopee_hoan_tra = (
        so_luong_SCx1_shopee_hoan_tra
        + so_luong_SCx2_shopee_hoan_tra
        + so_luong_SC_Combo_shopee_hoan_tra * 2
    )

    # COMBO mới

    COMBO_SCx1_shopee_hoan_thanh = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SCX1")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    COMBO_SCx2_shopee_hoan_thanh = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SCX2")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    so_luong_COMBO_SCx1_shopee_hoan_thanh = COMBO_SCx1_shopee_hoan_thanh[
        "Số lượng"
    ].sum()
    so_luong_COMBO_SCx2_shopee_hoan_thanh = COMBO_SCx2_shopee_hoan_thanh[
        "Số lượng"
    ].sum()

    COMBO_SCx1_shopee_da_giao = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SCX1")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    COMBO_SCx2_shopee_da_giao = df_shopee[
        (df_shopee["SKU Category"] == "COMBO-SCX2")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    so_luong_COMBO_SCx1_shopee_da_giao = COMBO_SCx1_shopee_da_giao["Số lượng"].sum()
    so_luong_COMBO_SCx2_shopee_da_giao = COMBO_SCx2_shopee_da_giao["Số lượng"].sum()

    # BTHP CAY & 0CAY

    BTHP_0CAY_hoan_thanh_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_CAY_hoan_thanh_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_COMBO_hoan_thanh_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_COMBO_0CAY_hoan_thanh_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO-0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_COMBO_CAY_hoan_thanh_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO-CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    so_luong_BTHP_0CAY_hoan_thanh_sp = BTHP_0CAY_hoan_thanh_sp["Số lượng"].sum()
    so_luong_BTHP_CAY_hoan_thanh_sp = BTHP_CAY_hoan_thanh_sp["Số lượng"].sum()
    so_luong_BTHP_COMBO_hoan_thanh_sp = BTHP_COMBO_hoan_thanh_sp["Số lượng"].sum()
    so_luong_BTHP_COMBO_0CAY_hoan_thanh_sp = BTHP_COMBO_0CAY_hoan_thanh_sp[
        "Số lượng"
    ].sum()
    so_luong_BTHP_COMBO_CAY_hoan_thanh_sp = BTHP_COMBO_CAY_hoan_thanh_sp[
        "Số lượng"
    ].sum()

    ### BTHP

    BTHP_0CAY_da_giao_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    BTHP_CAY_da_giao_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    BTHP_COMBO_da_giao_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    BTHP_COMBO_0CAY_da_giao_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO-0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    BTHP_COMBO_CAY_da_giao_sp = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO-CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    so_luong_BTHP_0CAY_da_giao_sp = BTHP_0CAY_da_giao_sp["Số lượng"].sum()
    so_luong_BTHP_CAY_da_giao_sp = BTHP_CAY_da_giao_sp["Số lượng"].sum()
    so_luong_BTHP_COMBO_da_giao_sp = BTHP_COMBO_da_giao_sp["Số lượng"].sum()
    so_luong_BTHP_COMBO_0CAY_da_giao_sp = BTHP_COMBO_0CAY_da_giao_sp["Số lượng"].sum()
    so_luong_BTHP_COMBO_CAY_da_giao_sp = BTHP_COMBO_CAY_da_giao_sp["Số lượng"].sum()

    BTHP_SCx1_shopee_hoan_thanh = df_shopee[
        (df_shopee["SKU Category"] == "COMBO_BTHP_SCx1")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_SCx2_shopee_hoan_thanh = df_shopee[
        (df_shopee["SKU Category"] == "COMBO_BTHP_SCx2")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_SCx1_shopee_da_giao = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO_BTHP_SCx1")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    BTHP_SCx2_shopee_da_giao = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO_BTHP_SCx2")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]
    so_luong_BTHP_SCx1_shopee_hoan_thanh = BTHP_SCx1_shopee_hoan_thanh["Số lượng"].sum()
    so_luong_BTHP_SCx2_shopee_hoan_thanh = BTHP_SCx2_shopee_hoan_thanh["Số lượng"].sum()
    so_luong_BTHP_SCx1_shopee_da_giao = BTHP_SCx1_shopee_da_giao["Số lượng"].sum()
    so_luong_BTHP_SCx2_shopee_da_giao = BTHP_SCx2_shopee_da_giao["Số lượng"].sum()

    ###COMBO4

    BTHP_COMBO4_hoan_thanh_sp = df_shopee[
        (df_shopee["SKU Category"] == "COMBO_4BTHP")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_COMBO4_da_giao_sp = df_shopee[
        (df_shopee["SKU Category"] == "COMBO_4BTHP")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    so_luong_BTHP_COMBO4_hoan_thanh_sp = BTHP_COMBO4_hoan_thanh_sp["Số lượng"].sum()
    so_luong_BTHP_COMBO4_da_giao_sp = BTHP_COMBO4_da_giao_sp["Số lượng"].sum()

    BTHP_COMBO4_0CAY_hoan_thanh_sp = df_shopee[
        (df_shopee["SKU Category"] == "4BTHP_0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_COMBO4_0CAY_da_giao_sp = df_shopee[
        (df_shopee["SKU Category"] == "4BTHP_0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    soluong_BTHP_COMBO4_0CAY_hoan_thanh_sp = BTHP_COMBO4_0CAY_hoan_thanh_sp[
        "Số lượng"
    ].sum()
    soluong_BTHP_COMBO4_0CAY_da_giao_sp = BTHP_COMBO4_0CAY_da_giao_sp["Số lượng"].sum()

    BTHP_COMBO4_CAY_hoan_thanh_sp = df_shopee[
        (df_shopee["SKU Category"] == "4BTHP_CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Acctually type"] == "Hoàn thành")
    ]

    BTHP_COMBO4_CAY_da_giao_sp = df_shopee[
        (df_shopee["SKU Category"] == "4BTHP_CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (
            df_shopee["Acctually type"].isin(
                ["Đã giao", "Đơn hàng đã đến User", "Đã nhận được hàng"]
            )
        )
    ]

    soluong_BTHP_COMBO4_CAY_hoan_thanh_sp = BTHP_COMBO4_CAY_hoan_thanh_sp[
        "Số lượng"
    ].sum()
    soluong_BTHP_COMBO4_CAY_da_giao_sp = BTHP_COMBO4_CAY_da_giao_sp["Số lượng"].sum()

    # Hoan tra
    BTHP_0CAY_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_CAY_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_COMBO_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_COMBO_0CAY_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO-0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_COMBO_CAY_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "BTHP-COMBO-CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_SCx1_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "COMBO_BTHP_SCx1")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_SCx2_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "COMBO_BTHP_SCx2")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_COMBO4_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "COMBO_4BTHP")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_COMBO4_0CAY_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "4BTHP_0CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    BTHP_COMBO4_CAY_hoan_tra_shopee = df_shopee[
        (df_shopee["SKU Category"] == "4BTHP_CAY")
        & (df_shopee["Thời gian giao hàng"] >= ngay_bat_dau)
        & (df_shopee["Thời gian giao hàng"] <= ngay_ket_thuc)
        & (df_shopee["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    so_luong_BTHP_0CAY_hoan_tra_shopee = BTHP_0CAY_hoan_tra_shopee["Số lượng"].sum()
    so_luong_BTHP_CAY_hoan_tra_shopee = BTHP_CAY_hoan_tra_shopee["Số lượng"].sum()
    so_luong_BTHP_COMBO_hoan_tra_shopee = BTHP_COMBO_hoan_tra_shopee["Số lượng"].sum()
    so_luong_BTHP_COMBO_0CAY_hoan_tra_shopee = BTHP_COMBO_0CAY_hoan_tra_shopee[
        "Số lượng"
    ].sum()
    so_luong_BTHP_COMBO_CAY_hoan_tra_shopee = BTHP_COMBO_CAY_hoan_tra_shopee[
        "Số lượng"
    ].sum()
    so_luong_BTHP_SCx1_hoan_tra_shopee = BTHP_SCx1_hoan_tra_shopee["Số lượng"].sum()
    so_luong_BTHP_SCx2_hoan_tra_shopee = BTHP_SCx2_hoan_tra_shopee["Số lượng"].sum()
    so_luong_BTHP_COMBO4_hoan_tra_shopee = BTHP_COMBO4_hoan_tra_shopee["Số lượng"].sum()
    so_luong_BTHP_COMBO4_0CAY_hoan_tra_shopee = BTHP_COMBO4_0CAY_hoan_tra_shopee[
        "Số lượng"
    ].sum()
    so_luong_BTHP_COMBO4_CAY_hoan_tra_shopee = BTHP_COMBO4_CAY_hoan_tra_shopee[
        "Số lượng"
    ].sum()

    # CLOUD
    SCx1_shopee_cloud = don_cloud_shopee[don_cloud_shopee["SKU Category"] == "SC-450g"]
    SCx2_shopee_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "SC-x2-450g"
    ]
    SC_Combo_shopee_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "COMBO-SC"
    ]
    COMBO_SCx1_shopee_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "COMBO-SCX1"
    ]
    COMBO_SCx2_shopee_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "COMBO-SCX2"
    ]
    BTHP_SCx1_shopee_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "COMBO_BTHP_SCx1"
    ]
    BTHP_SCx2_shopee_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "COMBO_BTHP_SCx2"
    ]
    BTHP_0CAY_cloud = don_cloud_shopee[don_cloud_shopee["SKU Category"] == "BTHP-0CAY"]
    BTHP_CAY_cloud = don_cloud_shopee[don_cloud_shopee["SKU Category"] == "BTHP-CAY"]
    BTHP_COMBO_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "BTHP-COMBO"
    ]
    BTHP_COMBO_0CAY_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "BTHP-COMBO-0CAY"
    ]
    BTHP_COMBO_CAY_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "BTHP-COMBO-CAY"
    ]
    BTHP_COMBO4_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "COMBO_4BTHP"
    ]
    BTHP_COMBO4_0CAY_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "4BTHP_0CAY"
    ]
    BTHP_COMBO4_CAY_cloud = don_cloud_shopee[
        don_cloud_shopee["SKU Category"] == "4BTHP_CAY"
    ]

    so_luong_SCx1_shopee_cloud = SCx1_shopee_cloud["Số lượng"].sum()
    so_luong_SCx2_shopee_cloud = SCx2_shopee_cloud["Số lượng"].sum()
    so_luong_SC_Combo_shopee_cloud = SC_Combo_shopee_cloud["Số lượng"].sum()
    so_luong_COMBO_SCx1_shopee_cloud = COMBO_SCx1_shopee_cloud["Số lượng"].sum()
    so_luong_COMBO_SCx2_shopee_cloud = COMBO_SCx2_shopee_cloud["Số lượng"].sum()
    so_luong_BTHP_SCx1_shopee_cloud = BTHP_SCx1_shopee_cloud["Số lượng"].sum()
    so_luong_BTHP_SCx2_shopee_cloud = BTHP_SCx2_shopee_cloud["Số lượng"].sum()
    so_luong_BTHP_0CAY_shopee_cloud = BTHP_0CAY_cloud["Số lượng"].sum()
    so_luong_BTHP_CAY_shopee_cloud = BTHP_CAY_cloud["Số lượng"].sum()
    so_luong_BTHP_COMBO_shopee_cloud = BTHP_COMBO_cloud["Số lượng"].sum()
    so_luong_BTHP_COMBO_0CAY_shopee_cloud = BTHP_COMBO_0CAY_cloud["Số lượng"].sum()
    so_luong_BTHP_COMBO_CAY_shopee_cloud = BTHP_COMBO_CAY_cloud["Số lượng"].sum()
    so_luong_BTHP_COMBO4_shopee_cloud = BTHP_COMBO4_cloud["Số lượng"].sum()
    so_luong_BTHP_COMBO4_0CAY_shopee_cloud = BTHP_COMBO4_0CAY_cloud["Số lượng"].sum()
    so_luong_BTHP_COMBO4_CAY_shopee_cloud = BTHP_COMBO4_CAY_cloud["Số lượng"].sum()

    tong_san_pham_shopee_hoanh_thanh = (
        so_luong_SCx1_shopee_hoanh_thanh
        + so_luong_SCx2_shopee_hoanh_thanh
        + so_luong_SC_Combo_shopee_hoanh_thanh * 2
        + so_luong_COMBO_SCx1_shopee_hoan_thanh * 2
        + so_luong_COMBO_SCx2_shopee_hoan_thanh * 2
    )

    tong_san_pham_shopee_da_giao = (
        so_luong_SCx1_shopee_da_giao
        + so_luong_SCx2_shopee_da_giao
        + so_luong_SC_Combo_shopee_da_giao * 2
        + so_luong_COMBO_SCx1_shopee_da_giao * 2
        + so_luong_COMBO_SCx2_shopee_da_giao * 2
    )

    Tong_soluong_SCx1_sp = (
        so_luong_SCx1_shopee_hoanh_thanh
        + so_luong_SCx1_shopee_da_giao
        #
        + so_luong_COMBO_SCx1_shopee_hoan_thanh * 2
        + so_luong_COMBO_SCx1_shopee_da_giao * 2
        + so_luong_BTHP_SCx1_shopee_hoan_thanh
    )

    Tong_soluong_SCx2_sp = (
        so_luong_SCx2_shopee_hoanh_thanh
        + so_luong_SCx2_shopee_da_giao
        #
        + so_luong_COMBO_SCx2_shopee_hoan_thanh * 2
        + so_luong_COMBO_SCx2_shopee_da_giao * 2
        + so_luong_BTHP_SCx2_shopee_hoan_thanh
    )

    Tong_soluong_SCxCombo_sp = (
        so_luong_SC_Combo_shopee_hoanh_thanh + so_luong_SC_Combo_shopee_da_giao
    ) * 2

    Tong_soluong_BTHP_0CAY_sp = (
        so_luong_BTHP_0CAY_hoan_thanh_sp
        + so_luong_BTHP_0CAY_da_giao_sp
        #
        + so_luong_BTHP_COMBO_0CAY_hoan_thanh_sp * 2
        + so_luong_BTHP_COMBO_0CAY_da_giao_sp * 2
        #
        + soluong_BTHP_COMBO4_0CAY_da_giao_sp * 4
        + soluong_BTHP_COMBO4_0CAY_hoan_thanh_sp * 4
    )

    Tong_soluong_BTHP_CAY_sp = (
        so_luong_BTHP_CAY_hoan_thanh_sp
        + so_luong_BTHP_CAY_da_giao_sp
        #
        + so_luong_BTHP_COMBO_CAY_hoan_thanh_sp * 2
        + so_luong_BTHP_COMBO_CAY_da_giao_sp * 2
        #
        + soluong_BTHP_COMBO4_CAY_da_giao_sp * 4
        + soluong_BTHP_COMBO4_CAY_hoan_thanh_sp * 4
    )

    Tong_soluong_BTHP_COMBO_sp = (
        so_luong_BTHP_COMBO_hoan_thanh_sp * 2
        + so_luong_BTHP_COMBO_da_giao_sp * 2
        + (so_luong_BTHP_SCx1_shopee_hoan_thanh + so_luong_BTHP_SCx1_shopee_da_giao) * 2
        + (so_luong_BTHP_SCx2_shopee_hoan_thanh + so_luong_BTHP_SCx2_shopee_da_giao) * 2
        + (so_luong_BTHP_COMBO4_hoan_thanh_sp + so_luong_BTHP_COMBO4_da_giao_sp) * 4
    )

    return (
        # Cloud
        so_don_cloud_shopee,
        so_luong_SCx1_shopee_cloud,
        so_luong_SCx2_shopee_cloud,
        so_luong_SC_Combo_shopee_cloud,
        so_luong_COMBO_SCx1_shopee_cloud,
        so_luong_COMBO_SCx2_shopee_cloud,
        so_luong_BTHP_SCx1_shopee_cloud,
        so_luong_BTHP_SCx2_shopee_cloud,
        so_luong_BTHP_0CAY_shopee_cloud,
        so_luong_BTHP_CAY_shopee_cloud,
        so_luong_BTHP_COMBO_shopee_cloud,
        so_luong_BTHP_COMBO_0CAY_shopee_cloud,
        so_luong_BTHP_COMBO_CAY_shopee_cloud,
        so_luong_BTHP_COMBO4_shopee_cloud,
        so_luong_BTHP_COMBO4_0CAY_shopee_cloud,
        so_luong_BTHP_COMBO4_CAY_shopee_cloud,
        # Hoan tra
        so_luong_SCx1_shopee_hoan_tra,
        so_luong_SCx2_shopee_hoan_tra,
        so_luong_SC_Combo_shopee_hoan_tra,
        so_luong_CB_SCx1_shopee_hoan_tra,
        so_luong_CB_SCx2_shopee_hoan_tra,
        so_luong_BTHP_0CAY_hoan_tra_shopee,
        so_luong_BTHP_CAY_hoan_tra_shopee,
        so_luong_BTHP_COMBO_hoan_tra_shopee,
        so_luong_BTHP_COMBO_0CAY_hoan_tra_shopee,
        so_luong_BTHP_COMBO_CAY_hoan_tra_shopee,
        so_luong_BTHP_SCx1_hoan_tra_shopee,
        so_luong_BTHP_SCx2_hoan_tra_shopee,
        so_luong_BTHP_COMBO4_hoan_tra_shopee,
        so_luong_BTHP_COMBO4_0CAY_hoan_tra_shopee,
        so_luong_BTHP_COMBO4_CAY_hoan_tra_shopee,
        ###
        Tong_soluong_SCx1_sp,
        Tong_soluong_SCx2_sp,
        Tong_soluong_SCxCombo_sp,
        Tong_soluong_BTHP_0CAY_sp,
        Tong_soluong_BTHP_CAY_sp,
        Tong_soluong_BTHP_COMBO_sp,
        #
        soluong_BTHP_COMBO4_0CAY_hoan_thanh_sp,
        soluong_BTHP_COMBO4_0CAY_da_giao_sp,
        soluong_BTHP_COMBO4_CAY_hoan_thanh_sp,
        soluong_BTHP_COMBO4_CAY_da_giao_sp,
        ###
        so_luong_BTHP_COMBO4_hoan_thanh_sp,
        so_luong_BTHP_COMBO4_da_giao_sp,
        ###
        so_luong_BTHP_SCx1_shopee_hoan_thanh,
        so_luong_BTHP_SCx2_shopee_hoan_thanh,
        so_luong_BTHP_SCx1_shopee_da_giao,
        so_luong_BTHP_SCx2_shopee_da_giao,
        ###
        so_luong_BTHP_0CAY_hoan_thanh_sp,
        so_luong_BTHP_CAY_hoan_thanh_sp,
        so_luong_BTHP_COMBO_hoan_thanh_sp,
        so_luong_BTHP_COMBO_0CAY_hoan_thanh_sp,
        so_luong_BTHP_COMBO_CAY_hoan_thanh_sp,
        so_luong_BTHP_0CAY_da_giao_sp,
        so_luong_BTHP_CAY_da_giao_sp,
        so_luong_BTHP_COMBO_da_giao_sp,
        so_luong_BTHP_COMBO_0CAY_da_giao_sp,
        so_luong_BTHP_COMBO_CAY_da_giao_sp,
        ###
        so_luong_COMBO_SCx1_shopee_hoan_thanh,
        so_luong_COMBO_SCx2_shopee_hoan_thanh,
        so_luong_COMBO_SCx1_shopee_da_giao,
        so_luong_COMBO_SCx2_shopee_da_giao,
        tong_san_pham_shopee_hoanh_thanh,
        tong_san_pham_shopee_da_giao,
        so_luong_SC_Combo_shopee_hoanh_thanh,
        so_luong_SC_Combo_shopee_da_giao,
        so_luong_SCx1_shopee_hoanh_thanh,
        so_luong_SCx1_shopee_da_giao,
        so_luong_SCx2_shopee_hoanh_thanh,
        so_luong_SCx2_shopee_da_giao,
        so_don_dang_giao_shopee,
        so_don_hoan_thanh_shopee,
        so_don_hoan_tra_shopee,
        tong_san_pham_shopee_hoan_tra,
        so_don_da_giao_shopee,
    )


# --- Giao diện Streamlit ---
st.set_page_config(page_title="Báo Cáo Đơn Hàng", layout="wide")

st.markdown(
    """
    <div style='top: 60px; left: 40px; z-index: 1000;'>
        <img src='https://raw.githubusercontent.com/CaptainCattt/Report_of_shopee/main/logo-lamvlog.png' width='150'/>
    </div>
    <h1 style='text-align: center;'>📦 Báo Cáo Số Lượng Đơn Hàng Và Sản Phẩm TikTok & Shopee</h1>""",
    unsafe_allow_html=True,
)

st.markdown("<br><br>", unsafe_allow_html=True)  # Tạo khoảng cách sau tiêu đề

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        "<h3 style='text-align: center;'>📥 Upload file TikTok</h3>",
        unsafe_allow_html=True,
    )
    file_tiktok = st.file_uploader("", type=["xlsx", "xls"], key="tiktok_file")

with col2:
    st.markdown(
        "<h3 style='text-align: center;'>📥 Upload file Shopee</h3>",
        unsafe_allow_html=True,
    )
    file_shopee = st.file_uploader("", type=["xlsx", "xls"], key="shopee_file")


ngay_bat_dau = st.date_input("📅 Ngày bắt đầu", value=datetime.now().date())
ngay_ket_thuc = st.date_input("📅 Ngày kết thúc", value=datetime.now().date())

ngay_bat_dau = pd.to_datetime(ngay_bat_dau)
ngay_ket_thuc = pd.to_datetime(ngay_ket_thuc)

# Khởi tạo trạng thái nếu chưa có
if "processing" not in st.session_state:
    st.session_state.processing = False

# Nút xử lý
process_btn = st.button("🔍 Xử lý dữ liệu", disabled=st.session_state.processing)

if process_btn:
    if not file_tiktok or not file_shopee:
        st.warning("Vui lòng upload cả 2 file!")
    else:
        with st.spinner("⏳ Đang xử lý dữ liệu, vui lòng chờ..."):
            df_tiktok = pd.read_excel(file_tiktok)
            df_shopee = pd.read_excel(file_shopee)

            (
                # cloud
                so_don_cloud_tiktok,
                so_luong_SCx1_tiktok_cloud,
                so_luong_SCx2_tiktok_cloud,
                so_luong_SC_Combo_tiktok_cloud,
                so_luong_Combo_Scx1_tiktok_cloud,
                so_luong_Combo_Scx2_tiktok_cloud,
                so_luong_BTHP_0CAY_tiktok_cloud,
                so_luong_BTHP_CAY_tiktok_cloud,
                so_luong_BTHP_Combo_tiktok_cloud,
                so_luong_BTHP_Combo_0CAY_tiktok_cloud,
                so_luong_BTHP_Combo_CAY_tiktok_cloud,
                so_luong_BTHP_SCx1_tiktok_cloud,
                so_luong_BTHP_SCx2_tiktok_cloud,
                so_luong_BTHP_COMBO4_tiktok_cloud,
                soluong_COMBO_4_BTHP_0CAY_tiktok_cloud,
                soluong_COMBO_4_BTHP_CAY_tiktok_cloud,
                ###Hoan tra
                so_luong_SCx1_tiktok_hoan_tra,
                so_luong_SCx2_tiktok_hoan_tra,
                so_luong_SC_Combo_tiktok_hoan_tra,
                so_luong_CB_SCx1_tiktok_hoan_tra,
                so_luong_CB_SCx2_tiktok_hoan_tra,
                tong_san_pham_tiktok_hoan_tra,
                so_luong_BTHP_0CAY_tiktok_hoan_tra,
                so_luong_BTHP_CAY_tiktok_hoan_tra,
                so_luong_BTHP_Combo_tiktok_hoan_tra,
                so_luong_BTHP_Combo_0CAY_tiktok_hoan_tra,
                so_luong_BTHP_Combo_CAY_tiktok_hoan_tra,
                so_luong_BTHP_SCx1_tiktok_hoan_tra,
                so_luong_BTHP_SCx2_tiktok_hoan_tra,
                so_luong_BTHP_COMBO4_tiktok_hoan_tra,
                soluong_COMBO_4_BTHP_0CAY_tiktok_hoan_tra,
                soluong_COMBO_4_BTHP_CAY_tiktok_hoan_tra,
                ###
                Tong_soluong_SCx1_tiktok,
                Tong_soluong_SCx2_tiktok,
                Tong_soluong_SCxCombo_tiktok,
                Tong_soluong_BTHP_0CAY_tiktok,
                Tong_soluong_BTHP_CAY_tiktok,
                Tong_soluong_BTHP_COMBO_tiktok,
                ###
                soluong_COMBO_4_BTHP_0CAY_hoan_thanh_tiktok,
                soluong_COMBO_4_BTHP_CAY_hoan_thanh_tiktok,
                soluong_COMBO_4_BTHP_0CAY_da_giao_tiktok,
                soluong_COMBO_4_BTHP_CAY_da_giao_tiktok,
                ###
                so_luong_BTHP_COMBO4_hoan_thanh_tiktok,
                so_luong_BTHP_COMBO4_da_giao_tiktok,
                ###
                tong_san_pham_tiktok_hoan_thanh,
                tong_san_pham_tiktok_da_giao,
                so_luong_SC_Combo_tiktok_hoan_thanh,
                so_luong_SC_Combo_tiktok_da_giao,
                so_luong_SCx1_tiktok_hoan_thanh,
                so_luong_SCx1_tiktok_da_giao,
                so_luong_SCx2_tiktok_hoan_thanh,
                so_luong_SCx2_tiktok_da_giao,
                so_don_da_giao_tiktok,
                so_don_hoan_thanh_tiktok,
                so_luong_Combo_Scx1_tiktok_hoan_thanh,
                so_luong_Combo_Scx2_tiktok_hoan_thanh,
                so_luong_Combo_Scx1_tiktok_da_giao,
                so_luong_Combo_Scx2_tiktok_da_giao,
                # Bánh tráng
                so_luong_BTHP_0CAY_hoan_thanh,
                so_luong_BTHP_CAY_hoan_thanh,
                so_luong_BTHP_Combo_hoan_thanh,
                so_luong_BTHP_Combo_0CAY_hoan_thanh,
                so_luong_BTHP_Combo_CAY_hoan_thanh,
                so_luong_BTHP_0CAY_da_giao,
                so_luong_BTHP_CAY_da_giao,
                so_luong_BTHP_Combo_da_giao,
                so_luong_BTHP_Combo_0CAY_da_giao,
                so_luong_BTHP_Combo_CAY_da_giao,
                tong_so_luong_BTHP_da_giao,
                tong_so_luong_BTHP_hoan_thanh,
                # Combo BTHP + SC
                so_luong_BTHP_SCx1_hoan_thanh,
                so_luong_BTHP_SCx2_hoan_thanh,
                so_luong_BTHP_SCx1_da_giao,
                so_luong_BTHP_SCx2_da_giao,
            ) = process_tiktok_data(df_tiktok, ngay_bat_dau, ngay_ket_thuc)

            (
                # Cloud
                so_don_cloud_shopee,
                so_luong_SCx1_shopee_cloud,
                so_luong_SCx2_shopee_cloud,
                so_luong_SC_Combo_shopee_cloud,
                so_luong_COMBO_SCx1_shopee_cloud,
                so_luong_COMBO_SCx2_shopee_cloud,
                so_luong_BTHP_SCx1_shopee_cloud,
                so_luong_BTHP_SCx2_shopee_cloud,
                so_luong_BTHP_0CAY_shopee_cloud,
                so_luong_BTHP_CAY_shopee_cloud,
                so_luong_BTHP_COMBO_shopee_cloud,
                so_luong_BTHP_COMBO_0CAY_shopee_cloud,
                so_luong_BTHP_COMBO_CAY_shopee_cloud,
                so_luong_BTHP_COMBO4_shopee_cloud,
                so_luong_BTHP_COMBO4_0CAY_shopee_cloud,
                so_luong_BTHP_COMBO4_CAY_shopee_cloud,
                # Hoan tra
                so_luong_SCx1_shopee_hoan_tra,
                so_luong_SCx2_shopee_hoan_tra,
                so_luong_SC_Combo_shopee_hoan_tra,
                so_luong_CB_SCx1_shopee_hoan_tra,
                so_luong_CB_SCx2_shopee_hoan_tra,
                so_luong_BTHP_0CAY_hoan_tra_shopee,
                so_luong_BTHP_CAY_hoan_tra_shopee,
                so_luong_BTHP_COMBO_hoan_tra_shopee,
                so_luong_BTHP_COMBO_0CAY_hoan_tra_shopee,
                so_luong_BTHP_COMBO_CAY_hoan_tra_shopee,
                so_luong_BTHP_SCx1_hoan_tra_shopee,
                so_luong_BTHP_SCx2_hoan_tra_shopee,
                so_luong_BTHP_COMBO4_hoan_tra_shopee,
                so_luong_BTHP_COMBO4_0CAY_hoan_tra_shopee,
                so_luong_BTHP_COMBO4_CAY_hoan_tra_shopee,
                ###
                Tong_soluong_SCx1_sp,
                Tong_soluong_SCx2_sp,
                Tong_soluong_SCxCombo_sp,
                Tong_soluong_BTHP_0CAY_sp,
                Tong_soluong_BTHP_CAY_sp,
                Tong_soluong_BTHP_COMBO_sp,
                #
                soluong_BTHP_COMBO4_0CAY_hoan_thanh_sp,
                soluong_BTHP_COMBO4_0CAY_da_giao_sp,
                soluong_BTHP_COMBO4_CAY_hoan_thanh_sp,
                soluong_BTHP_COMBO4_CAY_da_giao_sp,
                ###
                so_luong_BTHP_COMBO4_hoan_thanh_sp,
                so_luong_BTHP_COMBO4_da_giao_sp,
                so_luong_BTHP_SCx1_shopee_hoan_thanh,
                so_luong_BTHP_SCx2_shopee_hoan_thanh,
                so_luong_BTHP_SCx1_shopee_da_giao,
                so_luong_BTHP_SCx2_shopee_da_giao,
                ###
                so_luong_BTHP_0CAY_hoan_thanh_sp,
                so_luong_BTHP_CAY_hoan_thanh_sp,
                so_luong_BTHP_COMBO_hoan_thanh_sp,
                so_luong_BTHP_COMBO_0CAY_hoan_thanh_sp,
                so_luong_BTHP_COMBO_CAY_hoan_thanh_sp,
                so_luong_BTHP_0CAY_da_giao_sp,
                so_luong_BTHP_CAY_da_giao_sp,
                so_luong_BTHP_COMBO_da_giao_sp,
                so_luong_BTHP_COMBO_0CAY_da_giao_sp,
                so_luong_BTHP_COMBO_CAY_da_giao_sp,
                ###
                so_luong_COMBO_SCx1_shopee_hoan_thanh,
                so_luong_COMBO_SCx2_shopee_hoan_thanh,
                so_luong_COMBO_SCx1_shopee_da_giao,
                so_luong_COMBO_SCx2_shopee_da_giao,
                tong_san_pham_shopee_hoanh_thanh,
                tong_san_pham_shopee_da_giao,
                so_luong_SC_Combo_shopee_hoanh_thanh,
                so_luong_SC_Combo_shopee_da_giao,
                so_luong_SCx1_shopee_hoanh_thanh,
                so_luong_SCx1_shopee_da_giao,
                so_luong_SCx2_shopee_hoanh_thanh,
                so_luong_SCx2_shopee_da_giao,
                so_don_dang_giao_shopee,
                so_don_hoan_thanh_shopee,
                so_don_hoan_tra_shopee,
                tong_san_pham_shopee_hoan_tra,
                so_don_da_giao_shopee,
            ) = process_shopee_data(df_shopee, ngay_bat_dau, ngay_ket_thuc)

            bang_thong_ke_don_hang = pd.DataFrame(
                {
                    "ĐƠN ĐÃ GIAO": [so_don_da_giao_tiktok, so_don_da_giao_shopee],
                    "ĐƠN HOÀN THÀNH": [
                        so_don_hoan_thanh_tiktok,
                        so_don_hoan_thanh_shopee,
                    ],
                    "TỔNG": [
                        so_don_da_giao_tiktok + so_don_hoan_thanh_tiktok,
                        so_don_da_giao_shopee + so_don_hoan_thanh_shopee,
                    ],
                },
                index=["Tiktok", "Shopee"],
            )

            bang_thong_ke_so_luong_tiktok = pd.DataFrame(
                {
                    "SC_Combo (x2)": [
                        (
                            so_luong_SC_Combo_tiktok_hoan_thanh
                            + so_luong_SC_Combo_tiktok_da_giao
                        )
                        * 2
                    ],
                    "SCx1": [
                        so_luong_SCx1_tiktok_hoan_thanh + so_luong_SCx1_tiktok_da_giao
                    ],
                    "Combo_SCx1 (x2)": [
                        +so_luong_Combo_Scx1_tiktok_da_giao * 2
                        + so_luong_Combo_Scx1_tiktok_hoan_thanh * 2
                    ],
                    "SCx2": [
                        so_luong_SCx2_tiktok_hoan_thanh + so_luong_SCx2_tiktok_da_giao
                    ],
                    "Combo_SCx2 (x2)": [
                        +so_luong_Combo_Scx2_tiktok_da_giao * 2
                        + so_luong_Combo_Scx2_tiktok_hoan_thanh * 2
                    ],
                    "BTHP_Combo (x2)": [
                        (so_luong_BTHP_Combo_hoan_thanh + so_luong_BTHP_Combo_da_giao)
                        * 2
                    ],
                    "BTHP 0Cay": [
                        so_luong_BTHP_0CAY_hoan_thanh + so_luong_BTHP_0CAY_da_giao
                    ],
                    "Combo BTHP 0Cay (x2)": [
                        +so_luong_BTHP_Combo_0CAY_hoan_thanh * 2
                        + so_luong_BTHP_Combo_0CAY_da_giao * 2
                    ],
                    "BTHP Cay": [
                        so_luong_BTHP_CAY_hoan_thanh + so_luong_BTHP_CAY_da_giao
                    ],
                    "Combo_BTHP Cay (x2)": [
                        +so_luong_BTHP_Combo_CAY_hoan_thanh * 2
                        + so_luong_BTHP_Combo_CAY_da_giao * 2
                    ],
                    "COMBO BTHP + SCx1": [
                        so_luong_BTHP_SCx1_hoan_thanh + so_luong_BTHP_SCx1_da_giao
                    ],
                    "COMBO BTHP + SCx2": [
                        so_luong_BTHP_SCx2_hoan_thanh + so_luong_BTHP_SCx2_da_giao
                    ],
                    "COMBO 4BTHP": [
                        so_luong_BTHP_COMBO4_hoan_thanh_tiktok
                        + so_luong_BTHP_COMBO4_da_giao_tiktok
                    ],
                    "COMBO 4BTHP 0CAY": [
                        soluong_COMBO_4_BTHP_0CAY_hoan_thanh_tiktok
                        + soluong_COMBO_4_BTHP_0CAY_da_giao_tiktok
                    ],
                    "COMBO 4BTHP CAY": [
                        soluong_COMBO_4_BTHP_CAY_hoan_thanh_tiktok
                        + soluong_COMBO_4_BTHP_CAY_da_giao_tiktok
                    ],
                    "TỔNG SẢN PHẨM": [
                        tong_san_pham_tiktok_hoan_thanh
                        + tong_san_pham_tiktok_da_giao
                        + tong_so_luong_BTHP_hoan_thanh
                        + tong_so_luong_BTHP_da_giao
                        + (so_luong_BTHP_SCx1_hoan_thanh + so_luong_BTHP_SCx1_da_giao)
                        + (so_luong_BTHP_SCx2_hoan_thanh + so_luong_BTHP_SCx2_da_giao)
                    ],
                },
                index=["Tiktok"],
            )

            bang_thong_ke_so_luong_shopee = pd.DataFrame(
                {
                    "SC_Combo (x2)": [
                        (
                            so_luong_SC_Combo_shopee_hoanh_thanh
                            + so_luong_SC_Combo_shopee_da_giao
                        )
                        * 2
                    ],
                    "SCx1": [
                        so_luong_SCx1_shopee_hoanh_thanh + so_luong_SCx1_shopee_da_giao
                    ],
                    "Combo_SCx1 (x2)": [
                        +so_luong_COMBO_SCx1_shopee_hoan_thanh * 2
                        + so_luong_COMBO_SCx1_shopee_da_giao * 2
                    ],
                    "SCx2": [
                        so_luong_SCx2_shopee_hoanh_thanh + so_luong_SCx2_shopee_da_giao
                    ],
                    "Combo_SCx2 (x2)": [
                        +so_luong_COMBO_SCx2_shopee_hoan_thanh * 2
                        + so_luong_COMBO_SCx2_shopee_da_giao * 2
                    ],
                    "BTHP_Combo (x2)": [
                        (
                            so_luong_BTHP_COMBO_hoan_thanh_sp
                            + so_luong_BTHP_COMBO_da_giao_sp
                        )
                        * 2
                    ],
                    "BTHP 0Cay": [
                        so_luong_BTHP_0CAY_hoan_thanh_sp + so_luong_BTHP_0CAY_da_giao_sp
                    ],
                    "Combo BTHP 0Cay (x2)": [
                        +so_luong_BTHP_COMBO_0CAY_hoan_thanh_sp * 2
                        + so_luong_BTHP_COMBO_0CAY_da_giao_sp * 2
                    ],
                    "BTHP Cay": [
                        so_luong_BTHP_CAY_hoan_thanh_sp + so_luong_BTHP_CAY_da_giao_sp
                    ],
                    "Combo_BTHP Cay (x2)": [
                        +so_luong_BTHP_COMBO_CAY_hoan_thanh_sp * 2
                        + so_luong_BTHP_COMBO_CAY_da_giao_sp * 2
                    ],
                    "COMBO BTHP + SCx1": [
                        so_luong_BTHP_SCx1_shopee_hoan_thanh
                        + so_luong_BTHP_SCx1_shopee_da_giao
                    ],
                    "COMBO BTHP + SCx2": [
                        so_luong_BTHP_SCx2_shopee_hoan_thanh
                        + so_luong_BTHP_SCx2_shopee_da_giao
                    ],
                    "COMBO 4BTHP": [
                        so_luong_BTHP_COMBO4_hoan_thanh_sp
                        + so_luong_BTHP_COMBO4_da_giao_sp
                    ],
                    "COMBO 4BTHP 0CAY": [
                        soluong_BTHP_COMBO4_0CAY_hoan_thanh_sp
                        + soluong_BTHP_COMBO4_0CAY_da_giao_sp
                    ],
                    "COMBO 4BTHP CAY": [
                        soluong_BTHP_COMBO4_CAY_hoan_thanh_sp
                        + soluong_BTHP_COMBO4_CAY_da_giao_sp
                    ],
                    "TỔNG SẢN PHẨM": [
                        tong_san_pham_shopee_hoanh_thanh
                        + tong_san_pham_shopee_da_giao
                        + so_luong_BTHP_0CAY_hoan_thanh_sp
                        + so_luong_BTHP_CAY_hoan_thanh_sp
                        + so_luong_BTHP_COMBO_hoan_thanh_sp * 2
                        + so_luong_BTHP_COMBO_0CAY_hoan_thanh_sp * 2
                        + so_luong_BTHP_COMBO_CAY_hoan_thanh_sp * 2
                        + so_luong_BTHP_CAY_da_giao_sp
                        + so_luong_BTHP_0CAY_da_giao_sp
                        + so_luong_BTHP_COMBO_da_giao_sp * 2
                        + so_luong_BTHP_COMBO_0CAY_da_giao_sp * 2
                        + so_luong_BTHP_COMBO_CAY_da_giao_sp * 2
                        + (
                            so_luong_BTHP_SCx1_shopee_hoan_thanh
                            + so_luong_BTHP_SCx1_shopee_da_giao
                        )
                        * 3
                        + (
                            so_luong_BTHP_SCx2_shopee_hoan_thanh
                            + so_luong_BTHP_SCx2_shopee_da_giao
                        )
                        * 3
                        + (
                            so_luong_BTHP_COMBO4_hoan_thanh_sp
                            + so_luong_BTHP_COMBO4_da_giao_sp
                        )
                        * 4
                        + (
                            soluong_BTHP_COMBO4_0CAY_hoan_thanh_sp
                            + soluong_BTHP_COMBO4_0CAY_da_giao_sp
                        )
                        * 4
                        + (
                            soluong_BTHP_COMBO4_CAY_hoan_thanh_sp
                            + soluong_BTHP_COMBO4_CAY_da_giao_sp
                        )
                        * 4
                    ],
                },
                index=["Shopee"],
            )

            bang_thong_ke_san_pham_tiktok = pd.DataFrame(
                {
                    "SL SP HOÀN THÀNH": [
                        so_luong_SC_Combo_tiktok_hoan_thanh * 2
                        + so_luong_SCx1_tiktok_hoan_thanh
                        + so_luong_SCx2_tiktok_hoan_thanh
                        + so_luong_Combo_Scx1_tiktok_hoan_thanh * 2
                        + so_luong_Combo_Scx2_tiktok_hoan_thanh * 2
                        + so_luong_BTHP_SCx1_hoan_thanh
                        + so_luong_BTHP_SCx2_hoan_thanh
                    ],
                    "SL SP ĐÃ GIAO": [
                        so_luong_SC_Combo_tiktok_da_giao * 2
                        + so_luong_SCx1_tiktok_da_giao
                        + so_luong_Combo_Scx1_tiktok_da_giao * 2
                        + +so_luong_SCx2_tiktok_da_giao
                        + so_luong_Combo_Scx2_tiktok_da_giao * 2
                        + so_luong_BTHP_SCx1_da_giao
                        + so_luong_BTHP_SCx2_da_giao
                    ],
                    "TỔNG SỐ LƯỢNG SP": [
                        Tong_soluong_SCx1_tiktok
                        + Tong_soluong_SCx2_tiktok
                        + Tong_soluong_SCxCombo_tiktok
                    ],
                },
                index=["Tiktok"],
            )
            bang_thong_ke_san_pham_shopee = pd.DataFrame(
                {
                    "SL SP HOÀN THÀNH": [
                        so_luong_SC_Combo_shopee_hoanh_thanh * 2
                        + so_luong_SCx1_shopee_hoanh_thanh
                        + so_luong_COMBO_SCx1_shopee_hoan_thanh * 2
                        + so_luong_SCx2_shopee_hoanh_thanh
                        + so_luong_COMBO_SCx2_shopee_hoan_thanh * 2
                        + so_luong_BTHP_SCx1_shopee_hoan_thanh
                        + so_luong_BTHP_SCx2_shopee_hoan_thanh
                    ],
                    "SL SP ĐÃ GIAO": [
                        so_luong_SC_Combo_shopee_da_giao * 2
                        + +so_luong_SCx1_shopee_da_giao
                        + so_luong_COMBO_SCx1_shopee_da_giao * 2
                        + so_luong_SCx2_shopee_da_giao
                        + so_luong_COMBO_SCx2_shopee_da_giao * 2
                        + so_luong_BTHP_SCx1_shopee_da_giao
                        + so_luong_BTHP_SCx2_shopee_da_giao
                    ],
                    "TỔNG SỐ LƯỢNG SP": [
                        Tong_soluong_SCx1_sp
                        + Tong_soluong_SCx2_sp
                        + Tong_soluong_SCxCombo_sp
                    ],
                },
                index=["Shopee"],
            )

            bang_thong_ke_san_pham_BTHP = pd.DataFrame(
                {
                    "SL SP HOÀN THÀNH": [
                        tong_so_luong_BTHP_hoan_thanh,
                        so_luong_BTHP_0CAY_hoan_thanh_sp
                        + so_luong_BTHP_CAY_hoan_thanh_sp
                        + so_luong_BTHP_COMBO_hoan_thanh_sp * 2
                        + so_luong_BTHP_COMBO_0CAY_hoan_thanh_sp * 2
                        + so_luong_BTHP_COMBO_CAY_hoan_thanh_sp * 2
                        + so_luong_BTHP_SCx1_shopee_hoan_thanh * 2
                        + so_luong_BTHP_SCx2_shopee_hoan_thanh * 2
                        + so_luong_BTHP_COMBO4_hoan_thanh_sp * 4
                        + soluong_BTHP_COMBO4_0CAY_hoan_thanh_sp * 4
                        + soluong_BTHP_COMBO4_CAY_hoan_thanh_sp * 4,
                    ],
                    "SL SP ĐÃ GIAO": [
                        tong_so_luong_BTHP_da_giao,
                        so_luong_BTHP_CAY_da_giao_sp
                        + so_luong_BTHP_0CAY_da_giao_sp
                        + so_luong_BTHP_COMBO_da_giao_sp * 2
                        + so_luong_BTHP_COMBO_0CAY_da_giao_sp * 2
                        + so_luong_BTHP_COMBO_CAY_da_giao_sp * 2
                        + so_luong_BTHP_SCx1_shopee_da_giao * 2
                        + so_luong_BTHP_SCx2_shopee_da_giao * 2
                        + so_luong_BTHP_COMBO4_da_giao_sp * 4
                        + soluong_BTHP_COMBO4_0CAY_da_giao_sp * 4
                        + soluong_BTHP_COMBO4_CAY_da_giao_sp * 4,
                    ],
                    "TỔNG SỐ LƯỢNG SP": [
                        Tong_soluong_BTHP_0CAY_tiktok
                        + Tong_soluong_BTHP_CAY_tiktok
                        + Tong_soluong_BTHP_COMBO_tiktok,
                        Tong_soluong_BTHP_0CAY_sp
                        + Tong_soluong_BTHP_CAY_sp
                        + Tong_soluong_BTHP_COMBO_sp,
                    ],
                },
                index=["Tiktok", "SHOPEE"],
            )

            bang_tong_so_luong_san_pham = pd.DataFrame(
                {
                    "SCx1": [Tong_soluong_SCx1_tiktok, Tong_soluong_SCx1_sp],
                    "SCx2": [Tong_soluong_SCx2_tiktok, Tong_soluong_SCx2_sp],
                    "SCxCombo": [
                        Tong_soluong_SCxCombo_tiktok,
                        Tong_soluong_SCxCombo_sp,
                    ],
                    "BTHP KHONG CAY": [
                        Tong_soluong_BTHP_0CAY_tiktok,
                        Tong_soluong_BTHP_0CAY_sp,
                    ],
                    "BTHP CAY": [
                        Tong_soluong_BTHP_CAY_tiktok,
                        Tong_soluong_BTHP_CAY_sp,
                    ],
                    "BTHP COMBO": [
                        Tong_soluong_BTHP_COMBO_tiktok,
                        Tong_soluong_BTHP_COMBO_sp,
                    ],
                    "TỔNG": [
                        Tong_soluong_SCx1_tiktok
                        + Tong_soluong_SCx2_tiktok
                        + Tong_soluong_SCxCombo_tiktok
                        + Tong_soluong_BTHP_0CAY_tiktok
                        + Tong_soluong_BTHP_CAY_tiktok
                        + Tong_soluong_BTHP_COMBO_tiktok,
                        Tong_soluong_SCx1_sp
                        + Tong_soluong_SCx2_sp
                        + Tong_soluong_SCxCombo_sp
                        + Tong_soluong_BTHP_0CAY_sp
                        + Tong_soluong_BTHP_CAY_sp
                        + Tong_soluong_BTHP_COMBO_sp,
                    ],
                },
                index=["Tiktok", "Shopee"],
            )

            bang_so_luong_san_pham_hoan_tra = pd.DataFrame(
                {
                    "SCx1": [
                        so_luong_SCx1_tiktok_hoan_tra,
                        so_luong_SCx1_shopee_hoan_tra,
                    ],
                    "SCx2": [
                        so_luong_SCx2_tiktok_hoan_tra,
                        so_luong_SCx2_shopee_hoan_tra,
                    ],
                    "SC_Combo": [
                        so_luong_SC_Combo_tiktok_hoan_tra,
                        so_luong_SC_Combo_shopee_hoan_tra,
                    ],
                    "Combo_SCx1": [
                        so_luong_CB_SCx1_tiktok_hoan_tra,
                        so_luong_CB_SCx1_shopee_hoan_tra,
                    ],
                    "Combo_SCx2": [
                        so_luong_CB_SCx2_tiktok_hoan_tra,
                        so_luong_CB_SCx2_shopee_hoan_tra,
                    ],
                    "BTHP 0Cay": [
                        so_luong_BTHP_0CAY_tiktok_hoan_tra,
                        so_luong_BTHP_0CAY_hoan_tra_shopee,
                    ],
                    "BTHP Cay": [
                        so_luong_BTHP_CAY_tiktok_hoan_tra,
                        so_luong_BTHP_CAY_hoan_tra_shopee,
                    ],
                    "BTHP_Combo": [
                        so_luong_BTHP_Combo_tiktok_hoan_tra,
                        so_luong_BTHP_COMBO_hoan_tra_shopee,
                    ],
                    "Combo BTHP 0Cay": [
                        so_luong_BTHP_Combo_0CAY_tiktok_hoan_tra,
                        so_luong_BTHP_COMBO_0CAY_hoan_tra_shopee,
                    ],
                    "Combo_BTHP Cay": [
                        so_luong_BTHP_Combo_CAY_tiktok_hoan_tra,
                        so_luong_BTHP_COMBO_CAY_hoan_tra_shopee,
                    ],
                    "COMBO BTHP + SCx1": [
                        so_luong_BTHP_SCx1_tiktok_hoan_tra,
                        so_luong_BTHP_SCx1_hoan_tra_shopee,
                    ],
                    "COMBO BTHP + SCx2": [
                        so_luong_BTHP_SCx2_tiktok_hoan_tra,
                        so_luong_BTHP_SCx2_hoan_tra_shopee,
                    ],
                    "COMBO 4BTHP": [
                        so_luong_BTHP_COMBO4_tiktok_hoan_tra,
                        so_luong_BTHP_COMBO4_hoan_tra_shopee,
                    ],
                    "COMBO 4BTHP 0CAY": [
                        soluong_COMBO_4_BTHP_0CAY_tiktok_hoan_tra,
                        so_luong_BTHP_COMBO4_0CAY_hoan_tra_shopee,
                    ],
                    "COMBO 4BTHP CAY": [
                        soluong_COMBO_4_BTHP_CAY_tiktok_hoan_tra,
                        so_luong_BTHP_COMBO4_CAY_hoan_tra_shopee,
                    ],
                },
                index=["Tiktok", "Shopee"],
            )

            bang_thong_ke_don_cloud = pd.DataFrame(
                {
                    "TỔNG": [so_don_cloud_tiktok, so_don_cloud_shopee],
                },
                index=["Tiktok", "Shopee"],
            )

            bang_so_luong_san_pham_cua_don_cloud = pd.DataFrame(
                {
                    "TỔNG ĐƠN": [so_don_cloud_tiktok, so_don_cloud_shopee],
                    "SCx1": [so_luong_SCx1_tiktok_cloud, so_luong_SCx1_shopee_cloud],
                    "SCx2": [so_luong_SCx2_tiktok_cloud, so_luong_SCx2_shopee_cloud],
                    "SC_Combo": [
                        so_luong_SC_Combo_tiktok_cloud,
                        so_luong_SC_Combo_shopee_cloud,
                    ],
                    "Combo_SCx1": [
                        so_luong_Combo_Scx1_tiktok_cloud,
                        so_luong_COMBO_SCx1_shopee_cloud,
                    ],
                    "Combo_SCx2": [
                        so_luong_Combo_Scx2_tiktok_cloud,
                        so_luong_COMBO_SCx2_shopee_cloud,
                    ],
                    "BTHP 0Cay": [
                        so_luong_BTHP_0CAY_tiktok_cloud,
                        so_luong_BTHP_0CAY_shopee_cloud,
                    ],
                    "BTHP Cay": [
                        so_luong_BTHP_CAY_tiktok_cloud,
                        so_luong_BTHP_CAY_shopee_cloud,
                    ],
                    "BTHP_Combo": [
                        so_luong_BTHP_Combo_tiktok_cloud,
                        so_luong_BTHP_COMBO_shopee_cloud,
                    ],
                    "Combo BTHP 0Cay": [
                        so_luong_BTHP_Combo_0CAY_tiktok_cloud,
                        so_luong_BTHP_COMBO_0CAY_shopee_cloud,
                    ],
                    "Combo_BTHP Cay": [
                        so_luong_BTHP_Combo_CAY_tiktok_cloud,
                        so_luong_BTHP_COMBO_CAY_shopee_cloud,
                    ],
                    "COMBO BTHP + SCx1": [
                        so_luong_BTHP_SCx1_tiktok_cloud,
                        so_luong_BTHP_SCx1_shopee_cloud,
                    ],
                    "COMBO BTHP + SCx2": [
                        so_luong_BTHP_SCx2_tiktok_cloud,
                        so_luong_BTHP_SCx2_shopee_cloud,
                    ],
                    "COMBO 4BTHP": [
                        so_luong_BTHP_COMBO4_tiktok_cloud,
                        so_luong_BTHP_COMBO4_shopee_cloud,
                    ],
                    "COMBO 4BTHP 0CAY": [
                        soluong_COMBO_4_BTHP_0CAY_tiktok_cloud,
                        so_luong_BTHP_COMBO4_0CAY_shopee_cloud,
                    ],
                    "COMBO 4BTHP CAY": [
                        soluong_COMBO_4_BTHP_CAY_tiktok_cloud,
                        so_luong_BTHP_COMBO4_CAY_shopee_cloud,
                    ],
                },
                index=["Tiktok", "Shopee"],
            )

            bang_thong_ke_so_luong = pd.concat(
                [bang_thong_ke_so_luong_tiktok, bang_thong_ke_so_luong_shopee]
            )

            bang_thong_ke_san_pham = pd.concat(
                [bang_thong_ke_san_pham_tiktok, bang_thong_ke_san_pham_shopee]
            )

            # Hiển thị bảng thống kê đơn hàng
            st.markdown("### 📊 Tổng Đơn Hàng Tiktok & Shopee")
            with st.container():
                st.markdown("#### 📋 Bảng Thống Kê")
                st.dataframe(bang_thong_ke_don_hang)

            st.markdown("### 📊 Tổng SỐ LƯỢNG Sản Phẩm Tiktok & Shopee")
            with st.container():
                st.markdown("#### 📋 Bảng Thống Kê")
                st.dataframe(bang_tong_so_luong_san_pham)

            st.markdown("### 📊 Chi Tiết Số Lượng Sản Phẩm Tiktok & Shopee")
            with st.container():
                st.markdown("#### 📋 Bảng Thống Kê")
                st.markdown("#### 📦 Chi Tiết Số Lượng Sản Phẩm")
                st.dataframe(bang_thong_ke_so_luong)

            st.markdown("### 📊 Sản Phẩm Sốt Chấm & BTHP Tiktok & Shopee")
            col6, col7 = st.columns(2)

            with col6:
                st.markdown("#### 📋 Bảng Thống Kê Sốt Chấm")
                st.dataframe(bang_thong_ke_san_pham)

            with col7:
                st.markdown("#### 📈 Bảng Thống Kê BTHP")
                st.dataframe(bang_thong_ke_san_pham_BTHP)

            st.markdown("### 📊 Số lượng hàng hoàn ")
            with st.container():
                st.markdown("#### 📋 Bảng Thống Kê")
                st.dataframe(bang_so_luong_san_pham_hoan_tra)

            st.markdown("### 📊 Số lượng chi tiết đơn Cloud ")
            with st.container():
                st.markdown("#### 📋 Bảng Thống Kê")
                st.dataframe(bang_so_luong_san_pham_cua_don_cloud)

            # col1, col2 = st.columns(2)

            # with col1:
            #     st.markdown("#### 📈 Biểu Đồ")
            #     st.plotly_chart(fig_pie_tiktok, use_container_width=True)

            # with col2:
            #     st.markdown("#### 📈 Biểu Đồ")
            #     st.plotly_chart(fig_pie_shopee, use_container_width=True)

            # --- Gộp Bảng và Biểu đồ Đơn Hàng Hoàn Trả ---

            # --- Gộp Bảng và Biểu đồ Đơn Hàng Hoàn Thành / Đã Giao ---

        st.success("✅ Xử lý dữ liệu thành công!")
