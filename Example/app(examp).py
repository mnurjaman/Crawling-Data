from flask import Flask, render_template, request, send_file, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import pandas as pd
import os
import certifi
from datetime import datetime

app = Flask(__name__)


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_domain(url):
    parsed_uri = urlparse(url)
    return "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)


def get_all_links(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(
            url, headers=headers, verify=certifi.where(), timeout=30
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        links_data = []

        # Mengambil semua elemen <a>
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(url, href)

            if is_valid_url(full_url):
                link_data = {
                    "url": full_url,
                    "text": link.get_text(strip=True) or "[No Text]",
                    "title": link.get("title", ""),
                    "type": "Internal" if get_domain(url) in full_url else "External",
                }
                links_data.append(link_data)

        # Mengambil semua elemen yang memiliki atribut src
        for element in soup.find_all(src=True):
            src = element["src"]
            full_url = urljoin(url, src)

            if is_valid_url(full_url):
                link_data = {
                    "url": full_url,
                    "text": element.get("alt", "[No Text]"),
                    "title": element.get("title", ""),
                    "type": f"{element.name.upper()} Source",
                }
                links_data.append(link_data)

        return links_data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []


def crawl_website(start_url, max_pages=100, max_time=600):  # 10 menit maksimum
    if not is_valid_url(start_url):
        return {"status": "error", "message": "URL tidak valid"}

    start_time = time.time()
    base_domain = get_domain(start_url)
    visited = set()
    to_visit = {start_url}
    all_links = []
    internal_count = 0
    external_count = 0
    media_count = 0

    try:
        while (
            to_visit
            and len(visited) < max_pages
            and (time.time() - start_time) < max_time
        ):
            current_url = to_visit.pop()

            if current_url not in visited and base_domain in current_url:
                print(f"Mengunjungi: {current_url}")
                visited.add(current_url)

                links_data = get_all_links(current_url)

                for link_data in links_data:
                    if link_data["url"] not in [l["url"] for l in all_links]:
                        all_links.append(link_data)

                        if link_data["type"] == "Internal":
                            internal_count += 1
                            if link_data["url"] not in visited:
                                to_visit.add(link_data["url"])
                        elif link_data["type"] == "External":
                            external_count += 1
                        else:
                            media_count += 1

                time.sleep(1)

        summary = {
            "total_links": len(all_links),
            "internal_links": internal_count,
            "external_links": external_count,
            "media_links": media_count,
            "pages_crawled": len(visited),
            "time_taken": f"{time.time() - start_time:.2f} seconds",
        }

        return {"status": "success", "links": all_links, "summary": summary}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return jsonify({"status": "error", "message": "URL tidak boleh kosong"})

        result = crawl_website(url)

        if result["status"] == "success":
            try:
                # Buat direktori static jika belum ada
                os.makedirs("static", exist_ok=True)

                # Generate nama file dengan timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                excel_filename = f"static/crawled_links_{timestamp}.xlsx"

                # Konversi data ke DataFrame
                df = pd.DataFrame(result["links"])

                # Buat worksheet untuk links dan summary
                with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name="Links", index=False)

                    # Tambahkan summary ke sheet terpisah
                    summary_df = pd.DataFrame([result["summary"]])
                    summary_df.to_excel(writer, sheet_name="Summary", index=False)

                return jsonify(
                    {
                        "status": "success",
                        "message": "Crawling berhasil",
                        "links": result["links"],
                        "summary": result["summary"],
                        "excel_file": excel_filename,
                    }
                )
            except Exception as e:
                return jsonify(
                    {
                        "status": "error",
                        "message": f"Error saat menyimpan file: {str(e)}",
                    }
                )
        else:
            return jsonify(result)

    return render_template("index.html")


@app.route("/download/<filename>")
def download_file(filename):
    try:
        file_path = os.path.join("static", filename)
        if os.path.exists(file_path):
            return send_file(
                file_path,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            return jsonify({"status": "error", "message": "File tidak ditemukan"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(debug=True)


app.py

from flask import Flask, render_template, request, send_file, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import pandas as pd
import os
import certifi
from datetime import datetime

app = Flask(__name__)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def get_domain(url):
    parsed_uri = urlparse(url)
    return "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)

def extract_page_content(soup):
    """Mengekstrak konten dari halaman"""
    content = {
        "title": "",
        "meta_description": "",
        "meta_keywords": "",
        "main_content": "",
        "headings": [],
        "date_posted": "",  # Tambahkan untuk menyimpan tanggal
        "image": ""         # Tambahkan untuk menyimpan gambar
    }

    # Mengambil judul
    if soup.title:
        content["title"] = soup.title.string.strip() if soup.title.string else ""

    # Mengambil meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        content["meta_description"] = meta_desc.get("content", "")

    # Mengambil meta keywords
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    if meta_keywords:
        content["meta_keywords"] = meta_keywords.get("content", "")

    # Mengambil semua heading (h1-h6)
    headings = []
    for i in range(1, 7):
        for heading in soup.find_all(f"h{i}"):
            if heading.text.strip():
                headings.append({"level": i, "text": heading.text.strip()})
    content["headings"] = headings

    # Mengambil konten utama
    # Mencoba mencari elemen konten utama
    main_content = ""
    content_elements = soup.find_all(
        ["article", "main", "div"],
        class_=["content", "main-content", "article-content"],
    )

    if content_elements:
        # Menggunakan elemen konten yang ditemukan
        main_content = content_elements[0].get_text(separator="\n", strip=True)
    else:
        # Jika tidak menemukan elemen khusus, ambil semua paragraf
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
        main_content = "\n".join(paragraphs)

    content["main_content"] = main_content

    # Mengambil tanggal dan gambar (misalnya dari elemen tertentu)
    date_meta = soup.find("meta", attrs={"property": "article:published_time"})
    if date_meta:
        content["date_posted"] = date_meta.get("content", "")

    image_meta = soup.find("meta", attrs={"property": "og:image"})
    if image_meta:
        content["image"] = image_meta.get("content", "")

    return content

def get_all_links(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(
            url, headers=headers, verify=certifi.where(), timeout=30
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Ekstrak konten halaman
        page_content = extract_page_content(soup)

        links_data = []

        # Mengambil semua elemen <a>
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(url, href)

            if is_valid_url(full_url):
                link_data = {
                    "url": full_url,
                    "text": link.get_text(strip=True) or "[No Text]",
                    "title": link.get("title", ""),
                    "type": "Internal" if get_domain(url) in full_url else "External",
                    "page_title": page_content["title"],
                    "meta_description": page_content["meta_description"],
                    "meta_keywords": page_content["meta_keywords"],
                    "headings": str(page_content["headings"]),
                    "main_content": (
                        page_content["main_content"][:1000]
                        if page_content["main_content"]
                        else ""
                    ),  # Membatasi konten untuk tampilan
                    "date_posted": page_content["date_posted"],  # Tambahkan tanggal
                    "image": page_content["image"]  # Tambahkan gambar
                }
                links_data.append(link_data)

        # Mengambil semua elemen yang memiliki atribut src
        for element in soup.find_all(src=True):
            src = element["src"]
            full_url = urljoin(url, src)

            if is_valid_url(full_url):
                link_data = {
                    "url": full_url,
                    "text": element.get("alt", "[No Text]"),
                    "title": element.get("title", ""),
                    "type": f"{element.name.upper()} Source",
                    "page_title": page_content["title"],
                    "meta_description": page_content["meta_description"],
                    "meta_keywords": page_content["meta_keywords"],
                    "headings": str(page_content["headings"]),
                    "main_content": (
                        page_content["main_content"][:1000]
                        if page_content["main_content"]
                        else ""
                    ),
                    "date_posted": page_content["date_posted"],  # Tambahkan tanggal
                    "image": page_content["image"]  # Tambahkan gambar
                }
                links_data.append(link_data)

        return links_data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def crawl_website(start_url, max_pages=100, max_time=600):
    if not is_valid_url(start_url):
        return {"status": "error", "message": "URL tidak valid"}

    start_time = time.time()
    base_domain = get_domain(start_url)
    visited = set()
    to_visit = {start_url}
    all_links = []
    internal_count = 0
    external_count = 0
    media_count = 0

    try:
        while (
            to_visit
            and len(visited) < max_pages
            and (time.time() - start_time) < max_time
        ):
            current_url = to_visit.pop()

            if current_url not in visited and base_domain in current_url:
                print(f"Mengunjungi: {current_url}")
                visited.add(current_url)

                links_data = get_all_links(current_url)

                for link_data in links_data:
                    if link_data["url"] not in [l["url"] for l in all_links]:
                        all_links.append(link_data)

                        if link_data["type"] == "Internal":
                            internal_count += 1
                            if link_data["url"] not in visited:
                                to_visit.add(link_data["url"])
                        elif link_data["type"] == "External":
                            external_count += 1
                        else:
                            media_count += 1

                time.sleep(1)

        summary = {
            "total_links": len(all_links),
            "internal_links": internal_count,
            "external_links": external_count,
            "media_links": media_count,
            "pages_crawled": len(visited),
            "time_taken": f"{time.time() - start_time:.2f} seconds",
        }

        return {"status": "success", "links": all_links, "summary": summary}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return jsonify({"status": "error", "message": "URL tidak boleh kosong"})

        result = crawl_website(url)

        if result["status"] == "success":
            try:
                os.makedirs("static", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                excel_filename = f"static/crawled_links_{timestamp}.xlsx"

                # Format hasil sesuai permintaan
                formatted_links = []
                for link in result["links"]:
                    formatted_links.append({
                        "description": link["meta_description"],
                        "title": link["title"] if link["title"] else link["page_title"],
                        "datePosted": link["date_posted"] if link["date_posted"] else "",
                        "image": link["image"],
                        "link": link["url"]
                    })

                df = pd.DataFrame(formatted_links)

                with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name="Links", index=False)
                    summary_df = pd.DataFrame([result["summary"]])
                    summary_df.to_excel(writer, sheet_name="Summary", index=False)

                return jsonify(
                    {
                        "status": "success",
                        "message": "Crawling berhasil",
                        "links": formatted_links,
                        "summary": result["summary"],
                        "excel_file": excel_filename,
                    }
                )
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})

        return jsonify(result)

    return render_template("index.html")


@app.route("/download/<filename>")
def download_file(filename):
    try:
        return send_file(os.path.join("static", filename), as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# if __name__ == "__main__":
#     app.run(debug=True)

# from flask import Flask


# def create_app():
#     app = Flask(__name__)

#     # Initialize config
#     from app.config import Config

#     app.config.from_object(Config)

#     # Register blueprints
#     from app.routes import main_bp

#     app.register_blueprint(main_bp)

#     return app
