import json
import re

import requests
from bs4 import BeautifulSoup


def extract_website_text(url):
    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = ""
        if soup.title and soup.title.get_text(strip=True):
            title = soup.title.get_text(strip=True)

        meta_title = soup.find("meta", attrs={"property": "og:title"}) or soup.find(
            "meta", attrs={"name": "twitter:title"}
        )
        if meta_title and meta_title.get("content"):
            title = meta_title["content"]

        description = ""
        meta_description = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        ) or soup.find("meta", attrs={"name": "twitter:description"})
        if meta_description and meta_description.get("content"):
            description = meta_description["content"]

        if "youtube.com/watch" in url or "youtu.be" in url:
            patterns = [
                r"ytInitialPlayerResponse\s*=\s*(\{.*?\});",
                r"ytInitialData\s*=\s*(\{.*?\});",
                r"\"videoDetails\"\s*:\s*(\{.*?\})\s*,",
            ]
            for pattern in patterns:
                match = re.search(pattern, response.text, re.S)
                if match:
                    try:
                        data_text = match.group(1)
                        player_data = json.loads(data_text)
                        if isinstance(player_data, dict):
                            video_details = player_data.get("videoDetails", {})
                            if isinstance(video_details, dict):
                                title = video_details.get("title") or title
                                description = video_details.get("shortDescription") or description
                            if not description:
                                description = player_data.get("microformat", {}).get("playerMicroformatRenderer", {}).get("description", "")
                    except json.JSONDecodeError:
                        continue
                    break

        text_parts = []
        if title:
            text_parts.append(title)
        if description:
            text_parts.append(description)

        for tag in soup(["script", "style", "nav", "footer", "header", "form", "button", "svg", "img"]):
            tag.decompose()

        content_container = None
        for selector in ["article", "main", "[role='main']", ".content", ".post-content", ".entry-content", "#content"]:
            candidate = soup.select_one(selector)
            if candidate and candidate.get_text(strip=True):
                content_container = candidate
                break

        if content_container is None:
            content_container = soup.body or soup

        body_text = content_container.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        body_text = "\n".join(lines)

        if body_text:
            text_parts.append(body_text)

        text = "\n\n".join(part for part in text_parts if part)
        return text if text else "No readable text found on the website."

    except Exception as e:
        return f"Error: {e}"