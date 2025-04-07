import requests
import json
from colorama import Fore, Style, init
from github_scraper import scrape_github_metadata

init(autoreset=True)  # Initialize colorama for colored terminal output

def load_sites():
    with open('sites.json', 'r') as f:
        return json.load(f)

def save_result(site_name, url):
    with open('results.txt', 'a') as f:
        f.write(f"{site_name}: {url}\n")

def check_username(username, sites):
    print(Fore.CYAN + f"\n[!] Starting ReconSpectre OSINT scan for: {username}\n")
    for site in sites:
        url = site['url'].format(username=username)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(Fore.GREEN + f"[+] Found on {site['name']}: {url}")
                save_result(site['name'], url)

                # Scrape metadata if it's GitHub
                if site['name'].lower() == "github":
                    meta = scrape_github_metadata(username)
                    if "error" not in meta:
                        print(Fore.MAGENTA + "\n[+] GitHub Metadata:")
                        print(f"Name: {meta['name']}")
                        print(f"Bio: {meta['bio']}")
                        print(f"Location: {meta['location']}")
                        print(f"Repos: {meta['public_repos']}, Followers: {meta['followers']}, Following: {meta['following']}")
                        print(f"Account Created: {meta['created_at']}")
                        print(f"Profile Image: {meta['profile_image']}")
                    else:
                        print(Fore.YELLOW + f"[-] GitHub metadata error: {meta['error']}")
            else:
                print(Fore.RED + f"[-] Not found on {site['name']}")
        except requests.RequestException:
            print(Fore.YELLOW + f"[!] Error checking {site['name']}")

    print(Fore.CYAN + "\n[!] Scan complete. Check results.txt for saved links.\n")

if __name__ == "__main__":
    username = input("Enter a username to check: ").strip()
    sites = load_sites()
    check_username(username, sites)
