# import time
# import requests
# from bs4 import BeautifulSoup
# import certifi
# from app.utils.url_utils import is_valid_url, get_domain, urljoin
# from app.config import Config


# def get_all_links(url):
#     try:
#         response = requests.get(
#             url, headers=Config.HEADERS, verify=certifi.where(), timeout=30
#         )
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")

#         links_data = []

#         # Mengambil semua elemen <a>
#         for link in soup.find_all("a", href=True):
#             href = link["href"]
#             full_url = urljoin(url, href)

#             if is_valid_url(full_url):
#                 link_data = {
#                     "url": full_url,
#                     "text": link.get_text(strip=True) or "[No Text]",
#                     "title": link.get("title", ""),
#                     "type": "Internal" if get_domain(url) in full_url else "External",
#                 }
#                 links_data.append(link_data)

#         # Mengambil semua elemen yang memiliki atribut src
#         for element in soup.find_all(src=True):
#             src = element["src"]
#             full_url = urljoin(url, src)

#             if is_valid_url(full_url):
#                 link_data = {
#                     "url": full_url,
#                     "text": element.get("alt", "[No Text]"),
#                     "title": element.get("title", ""),
#                     "type": f"{element.name.upper()} Source",
#                 }
#                 links_data.append(link_data)

#         return links_data
#     except Exception as e:
#         print(f"Error fetching {url}: {e}")
#         return []


# def crawl_website(start_url):
#     if not is_valid_url(start_url):
#         return {"status": "error", "message": "URL tidak valid"}

#     start_time = time.time()
#     base_domain = get_domain(start_url)
#     visited = set()
#     to_visit = {start_url}
#     all_links = []
#     internal_count = 0
#     external_count = 0
#     media_count = 0

#     try:
#         while (
#             to_visit
#             and len(visited) < Config.MAX_PAGES
#             and (time.time() - start_time) < Config.MAX_TIME
#         ):
#             current_url = to_visit.pop()

#             if current_url not in visited and base_domain in current_url:
#                 print(f"Mengunjungi: {current_url}")
#                 visited.add(current_url)

#                 links_data = get_all_links(current_url)

#                 for link_data in links_data:
#                     if link_data["url"] not in [l["url"] for l in all_links]:
#                         all_links.append(link_data)

#                         if link_data["type"] == "Internal":
#                             internal_count += 1
#                             if link_data["url"] not in visited:
#                                 to_visit.add(link_data["url"])
#                         elif link_data["type"] == "External":
#                             external_count += 1
#                         else:
#                             media_count += 1

#                 time.sleep(Config.SLEEP_TIME)

#         summary = {
#             "total_links": len(all_links),
#             "internal_links": internal_count,
#             "external_links": external_count,
#             "media_links": media_count,
#             "pages_crawled": len(visited),
#             "time_taken": f"{time.time() - start_time:.2f} seconds",
#         }

#         return {"status": "success", "links": all_links, "summary": summary}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}
