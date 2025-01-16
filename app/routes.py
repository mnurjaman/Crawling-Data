# import templates
# from flask import Blueprint, render_template, request, jsonify
# from app.crawler.crawler import crawl_website
# from app.utils.excel_utils import save_to_excel

# # Membuat blueprint untuk routing
# main_bp = Blueprint("main", __name__)


# @main_bp.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         url = request.form.get("url")

#         # Memeriksa apakah URL kosong
#         if not url:
#             return jsonify({"status": "error", "message": "URL tidak boleh kosong"})

#         # Melakukan crawling pada website yang diberikan
#         result = crawl_website(url)

#         # Memeriksa status hasil crawling
#         if result["status"] == "success":
#             try:
#                 # Menyimpan hasil crawling ke file Excel
#                 excel_filename = save_to_excel(result)

#                 # Mengembalikan respons sukses
#                 return jsonify(
#                     {
#                         "status": "success",
#                         "message": "Crawling berhasil",
#                         "links": result["links"],
#                         "summary": result["summary"],
#                         "excel_file": excel_filename,
#                     }
#                 )
#             except Exception as e:
#                 # Menangani kesalahan saat menyimpan file Excel
#                 return jsonify(
#                     {
#                         "status": "error",
#                         "message": f"Error saat menyimpan file: {str(e)}",
#                     }
#                 )
#         else:
#             # Mengembalikan respons error jika crawling gagal
#             return jsonify(result)

#     # Menampilkan halaman utama
#     return render_template("index.html")
