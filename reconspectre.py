import requests
import json
import time
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from colorama import Fore, Style, init
from collections import defaultdict
from io import BytesIO
from bs4 import BeautifulSoup
from pyfiglet import Figlet
from github_scraper import scrape_github_metadata

init(autoreset=True)

# ─── Banner ───

def print_banner():
    f = Figlet(font='slant')
    print(Fore.LIGHTRED_EX + f.renderText('ReconSpectre') + Style.RESET_ALL)

def print_signature():
    sig = r"""
________/
_______/\ 
______/\ \ 
_____/\ \ \ 
____/\ \ \ \ 
___/\ \ \ \ \ 
__/\ \ \ \ \ \ 
_/\ \ \ \ \ \ \ 
/\ \ \ \ \ \ \ \ 
\/-/-/-/-/-/-/-/-------------------------------------------
_\/ / / / / / /  Profile. Parse. Print.            
__\/ / / / / /                                   \(|)/
___\/ / / / /                                   --(")--
____\/ / / /                                      /`\   ukosint
"""
    print(Fore.LIGHTRED_EX + sig + Style.RESET_ALL)

# ─── Boot-Up Animation ───

def boot_up_sequence():
    lines = [
        "[BOOT] Initializing ReconSpectre subsystem...",
        "[SYS] Loading threat database...",
        "[OK]  Terminal interface online.",
        "[OK]  Cryptographic module... verified.",
        "[READY] Awaiting input.\n"
    ]
    for line in lines:
        print(Fore.LIGHTBLACK_EX + line + Style.RESET_ALL)
        time.sleep(0.5)

# ─── Core Functions ───

def load_sites():
    with open('sites.json', 'r') as f:
        return json.load(f)

def save_result(username_variant, site_name, url):
    with open('results.txt', 'a') as f:
        f.write(f"{username_variant} | {site_name}: {url}\n")

def generate_permutations(username):
    return list(set([
        username,
        username + "_",
        username + "_official"
    ]))

def is_false_positive(site_name, response_text):
    site = site_name.lower()
    text = response_text.lower()

    if site == "reddit":
        return "sorry, nobody on reddit goes by that name." in text
    elif site == "instagram":
        return (
            "sorry, this page isn't available." in text or
            "the link may be broken or the profile may have been removed" in text or
            '"alternatename"' not in text
        )
    elif site == "pinterest":
        return (
            "oops! that page can't be found." in text or
            "explore pinterest" in text or
            "/user/" not in text
        )
    elif site == "hackernews":
        return "no such user." in text
    elif site == "medium":
        return "page not found" in text or "out of nothing, something." in text
    elif site == "tiktok":
        return "couldn't find this account" in text or "try browsing our trending creators" in text
    elif site == "behance":
        return "sorry, that page isn’t here anymore." in text
    elif site == "dribbble":
        return "page not found" in text
    elif site == "pastebin":
        return "maximum number of unregistered user pastes" in text or "pastebin.com" not in text
    elif site == "telegram":
        return (
            "contact this user" not in text and
            '<div class="tgme_page_title"' not in response_text
        )
    elif site == "about.me":
        return "the page you're looking for doesn't exist" in text or "about.me" not in text
    elif site == "facebook":
        soup = BeautifulSoup(response_text, "lxml")
        title = soup.title.string.strip().lower() if soup.title else ""
        og_title = soup.find("meta", property="og:title")
        og_image = soup.find("meta", property="og:image")

        if (
            "this content isn't available right now" in text or
            "go to news feed" in text or
            "the link you followed may be broken" in text or
            "page not found" in text or
            not og_title or
            not og_image or
            ("facebook" in title and "profile" not in title)
        ):
            print(Fore.BLUE + "[debug] Facebook profile likely false positive (parsed HTML)")
            return True
        return False

    return False

def export_to_pdf(results, base_username, sites):
    filename = f"{base_username}_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    grouped_results = defaultdict(list)
    site_lookup = {site["name"]: site for site in sites}

    for uname, site_name, url in results:
        site_meta = site_lookup.get(site_name, {})
        category = site_meta.get("category", "other")
        icon_url = site_meta.get("icon")
        grouped_results[category].append((uname, site_name, url, icon_url))

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"ReconSpectre Report for: {base_username}")
    y = height - 80

    for category, entries in grouped_results.items():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Category: {category.capitalize()}")
        y -= 20

        for uname, site_name, url, icon_url in entries:
            if y < 60:
                c.showPage()
                c.setFont("Helvetica-Bold", 14)
                y = height - 50
                c.drawString(50, y, f"Category: {category.capitalize()}")
                y -= 20

            if icon_url:
                try:
                    response = requests.get(icon_url, timeout=3)
                    if response.status_code == 200:
                        image = ImageReader(BytesIO(response.content))
                        c.drawImage(image, 50, y - 5, width=16, height=16, preserveAspectRatio=True, mask='auto')
                except:
                    pass

            c.setFont("Helvetica", 11)
            c.drawString(70, y, f"[{uname}] → [{site_name}]  {url}")
            y -= 20

    c.save()
    print(Fore.CYAN + f"[+] PDF report saved to {filename}")

def check_username_variants(base_username, sites):
    permutations = generate_permutations(base_username)
    total_sites = len(sites)
    total_variants = len(permutations)

    print(Fore.CYAN + f"\n[!] Starting ReconSpectre smart scan for: {base_username}")
    print(Fore.CYAN + f"[i] {total_sites} platforms × {total_variants} variants = {total_sites * total_variants} total checks\n")

    found_results = []

    for uname in permutations:
        print(Fore.YELLOW + f"\n🔍 Scanning variation: {uname}")
        for site in sites:
            site_name = site['name']
            site_url = site['url'].format(username=uname)

            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(site_url, headers=headers, timeout=5)

                if response.status_code == 200:
                    if is_false_positive(site_name, response.text):
                        print(Fore.RED + f"[-] Not found on {site_name} (filtered by content)")
                        continue

                    print(Fore.GREEN + f"[+] Found on {site_name}: {site_url}")
                    save_result(uname, site_name, site_url)
                    found_results.append((uname, site_name, site_url))

                    if site_name.lower() == "github":
                        meta = scrape_github_metadata(uname)
                        if "error" not in meta:
                            print(Fore.MAGENTA + "\n[+] GitHub Metadata:")
                            print(f"Name: {meta['name']}")
                            print(f"Bio: {meta['bio']}")
                            print(f"Location: {meta['location']}")
                            print(f"Repos: {meta['public_repos']}, Followers: {meta['followers']}, Following: {meta['following']}")
                            print(f"Account Created: {meta['created_at']}")
                            print(f"Profile Image: {meta['profile_image']}")
                else:
                    print(Fore.RED + f"[-] Not found on {site_name} (status: {response.status_code})")
            except requests.RequestException:
                print(Fore.YELLOW + f"[!] Error checking {site_name}")
            except Exception as e:
                print(Fore.YELLOW + f"[!] Unexpected error on {site_name}: {e}")

    export_to_pdf(found_results, base_username, sites)
    print_signature()
    print(Fore.CYAN + "\n[!] Smart scan complete. PDF and results.txt saved.\n")

# ─── Entry Point ───

if __name__ == "__main__":
    print_banner()
    boot_up_sequence()
    print_signature()
    username = input(Fore.CYAN + "\nEnter a username to check: ").strip()
    sites = load_sites()
    check_username_variants(username, sites)
