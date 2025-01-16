# import pandas as pd
# import os
# from datetime import datetime


# def save_to_excel(result):
#     """
#     Menyimpan hasil crawling ke file Excel
#     """
#     # Buat direktori static jika belum ada
#     os.makedirs("static", exist_ok=True)

#     # Generate nama file dengan timestamp
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     excel_filename = f"static/crawled_links_{timestamp}.xlsx"

#     # Konversi data ke DataFrame
#     df = pd.DataFrame(result["links"])

#     # Buat worksheet untuk links dan summary
#     with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
#         df.to_excel(writer, sheet_name="Links", index=False)

#         # Tambahkan summary ke sheet terpisah
#         summary_df = pd.DataFrame([result["summary"]])
#         summary_df.to_excel(writer, sheet_name="Summary", index=False)

#     return excel_filename
