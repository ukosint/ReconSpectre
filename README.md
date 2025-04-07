# 👁️‍🗨️ ReconSpectre

**ReconSpectre** is a focused, lightweight OSINT tool for identifying usernames across a wide range of platforms — combining smart scanning, metadata scraping, and clean reporting.

Ideal for cybersecurity analysts, investigators, and digital researchers.

---

### 🚀 Features

- 🔍 Scans for usernames across platforms like GitHub, Reddit, Instagram, GitLab, Telegram, Facebook, Behance, and more
- 🧠 Smart username matching (e.g. `user`, `user_`, `user_official`)
- 🛡️ False-positive filtering via platform-specific fingerprinting
- 📂 Saves results to `results.txt`
- 📄 Exports clean, shareable PDF reports
- 🧬 Scrapes detailed GitHub metadata (bio, repos, followers, creation date, etc.)

---

### 📦 Installation

```bash
git clone https://github.com/ukosint/ReconSpectre.git
cd ReconSpectre
pip install -r requirements.txt
