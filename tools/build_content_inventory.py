from __future__ import annotations

import csv
import datetime as dt
import html
import os
import re
import textwrap
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DOWNLOADS = Path.home() / "Downloads"
BASE_URL = "https://www.aaaimpressions.com"
THREAD_ID = os.environ.get("CODEX_THREAD_ID", "local")
OUTPUT_DIR = ROOT / "outputs" / THREAD_ID
OUTPUT_XLSX = OUTPUT_DIR / "aaaimpressions_content_inventory_pillars_clusters.xlsx"


PAGE_TITLE_CSV = DOWNLOADS / "page_titles_all.csv"
RESPONSE_CODES_CSV = DOWNLOADS / "response_codes_all.csv"
CRAWL_OVERVIEW_CSV = DOWNLOADS / "crawl_overview.csv"
REDIRECT_CHAINS_CSV = DOWNLOADS / "redirect_chains.csv"


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return list(csv.DictReader(handle))
        except UnicodeDecodeError:
            continue
    with path.open("r", errors="replace", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_crawl_overview(path: Path) -> dict[str, str]:
    overview: dict[str, str] = {}
    if not path.exists():
        return overview
    for row in csv.reader(read_text(path).splitlines()):
        if len(row) >= 2 and row[0]:
            overview[row[0]] = row[1]
    return overview


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith("local-only:"):
        return url
    url = url.split("#", 1)[0]
    if url.endswith("/index.html"):
        url = url[: -len("index.html")]
    if url == BASE_URL:
        return BASE_URL + "/"
    return url


def page_url_from_source(path: Path) -> str:
    rel = path.relative_to(SRC).as_posix()
    if rel == "index.njk":
        return BASE_URL + "/"
    if rel.endswith("/index.njk"):
        url_path = "/" + rel[: -len("index.njk")]
    else:
        url_path = "/" + rel.rsplit(".", 1)[0] + "/"
    url_path = re.sub(r"/+", "/", url_path)
    return BASE_URL + url_path


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", raw, flags=re.S)
    if not match:
        return {}, raw
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        meta[key.strip()] = value
    return meta, raw[match.end() :]


def clean_visible_text(fragment: str) -> str:
    fragment = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", fragment, flags=re.I | re.S)
    fragment = re.sub(r"\{#[\s\S]*?#\}", " ", fragment)
    fragment = re.sub(r"\{[%{][\s\S]*?[%}]\}", " ", fragment)
    fragment = re.sub(r"<!--[\s\S]*?-->", " ", fragment)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    fragment = html.unescape(fragment)
    fragment = re.sub(r"\s+", " ", fragment).strip()
    return fragment


def extract_tag_text(raw: str, tag: str) -> list[str]:
    results = []
    for match in re.finditer(rf"<{tag}\b[^>]*>(.*?)</{tag}>", raw, flags=re.I | re.S):
        text = clean_visible_text(match.group(1))
        if text:
            results.append(text)
    return results


def extract_meta_description_from_html(raw: str) -> str:
    match = re.search(
        r"<meta\s+[^>]*name=[\"']description[\"'][^>]*content=[\"']([^\"']*)[\"'][^>]*>",
        raw,
        flags=re.I,
    )
    if match:
        return html.unescape(match.group(1)).strip()
    return ""


def extract_title_from_html(raw: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", raw, flags=re.I | re.S)
    if match:
        return clean_visible_text(match.group(1))
    return ""


def page_type_for_url(url: str, source_path: str = "") -> str:
    lower = url.lower() + " " + source_path.lower()
    if lower.startswith("local-only:"):
        return "Archivo local"
    if lower in (BASE_URL.lower() + "/", BASE_URL.lower() + "/index.html"):
        return "Redirect/Home raiz"
    if "/servicios/" in lower or "/services/" in lower:
        return "Servicio"
    if "/ubicaciones/" in lower or "/locations/" in lower:
        return "Ubicacion"
    if "/blog/" in lower:
        return "Blog"
    if "/paquetes/" in lower or "/packages/" in lower:
        return "Paquetes"
    if "/contacto/" in lower or "/contact/" in lower:
        return "Contacto"
    if "/sobre-nosotros/" in lower or "/about/" in lower:
        return "Sobre nosotros"
    if "/gracias/" in lower or "/thank-you/" in lower:
        return "Gracias"
    if lower.endswith("/es/ ") or lower.endswith("/en/ "):
        return "Home"
    return "Pagina"


def language_for_url(url: str) -> str:
    if "/es/" in url or url.endswith("/es/"):
        return "ES"
    if "/en/" in url or url.endswith("/en/"):
        return "EN"
    if url.startswith("local-only:"):
        return "ES/local"
    return "Neutral"


SERVICE_KEYWORDS = {
    "google-business-profile": (
        "Google Business Profile Treasure Coast",
        "Google Maps; perfil de negocio de Google; SEO local; aparecer en Google Maps",
        "Presencia local y SEO",
        "Google Business Profile",
    ),
    "google-ads": (
        "Google Ads Treasure Coast",
        "publicidad en Google; anuncios de busqueda; leads locales; campanas PPC",
        "Publicidad pagada",
        "Google Ads",
    ),
    "facebook-instagram": (
        "publicidad Facebook Instagram Treasure Coast",
        "Meta Ads; anuncios en Facebook; anuncios en Instagram; publicidad local",
        "Publicidad pagada",
        "Meta Ads",
    ),
    "publicidad-facebook-instagram": (
        "publicidad Facebook Instagram Treasure Coast",
        "Meta Ads; anuncios en Facebook; anuncios en Instagram; publicidad local",
        "Publicidad pagada",
        "Meta Ads",
    ),
    "web-design": (
        "web design Treasure Coast",
        "sitios web para negocios; diseno web local; landing pages; conversion web",
        "Diseno web y conversion",
        "Diseno web",
    ),
    "diseno-web": (
        "diseno web Treasure Coast",
        "sitios web para negocios; pagina web profesional; landing pages; conversion web",
        "Diseno web y conversion",
        "Diseno web",
    ),
    "branding-logo": (
        "branding y diseno de logo Treasure Coast",
        "logo para negocios; identidad visual; marca local; branding profesional",
        "Branding y materiales",
        "Branding y logo",
    ),
    "branding-diseno-logo": (
        "branding y diseno de logo Treasure Coast",
        "logo para negocios; identidad visual; marca local; branding profesional",
        "Branding y materiales",
        "Branding y logo",
    ),
    "social-media": (
        "social media management Treasure Coast",
        "manejo de redes sociales; contenido para redes; publicaciones locales; community management",
        "Contenido y redes sociales",
        "Redes sociales",
    ),
    "manejo-redes-sociales": (
        "manejo de redes sociales Treasure Coast",
        "contenido para redes; publicaciones locales; calendario de contenido; community management",
        "Contenido y redes sociales",
        "Redes sociales",
    ),
    "print-materials": (
        "print materials Treasure Coast",
        "flyers; business cards; banners; materiales promocionales",
        "Branding y materiales",
        "Materiales impresos",
    ),
    "materiales-impresos": (
        "materiales impresos Treasure Coast",
        "flyers; tarjetas de presentacion; banners; materiales promocionales",
        "Branding y materiales",
        "Materiales impresos",
    ),
}


BLOG_KEYWORDS = {
    "chatgpt": (
        "como usar ChatGPT o Claude para marketing",
        "IA para marketing; prompts para negocios; automatizacion de contenido; marketing diario",
        "Contenido y redes sociales",
        "IA para marketing",
    ),
    "claude": (
        "como usar ChatGPT o Claude para marketing",
        "IA para marketing; prompts para negocios; automatizacion de contenido; marketing diario",
        "Contenido y redes sociales",
        "IA para marketing",
    ),
    "email-marketing": (
        "campanas de email marketing para negocios",
        "newsletter local; seguimiento a clientes; email para promociones; retencion",
        "Contenido y redes sociales",
        "Email marketing",
    ),
    "internet-marketing-consultant": (
        "internet marketing consultant SEO",
        "consultor SEO; estrategia digital; consultoria de marketing; auditoria SEO",
        "Marketing digital para negocios locales",
        "Consultoria SEO",
    ),
    "consultor-de-internet": (
        "consultor de internet marketing y SEO",
        "consultor SEO; estrategia digital; consultoria de marketing; auditoria SEO",
        "Marketing digital para negocios locales",
        "Consultoria SEO",
    ),
    "internet-marketing-services": (
        "servicios de internet marketing para pequenos negocios",
        "marketing digital para pequenas empresas; servicios online; crecimiento local",
        "Marketing digital para negocios locales",
        "Servicios de marketing digital",
    ),
    "servicios-de-internet": (
        "servicios de internet marketing para pequenos negocios",
        "marketing digital para pequenas empresas; servicios online; crecimiento local",
        "Marketing digital para negocios locales",
        "Servicios de marketing digital",
    ),
    "internet-health-test": (
        "test de salud online para negocio",
        "auditoria web; revision de presencia digital; diagnostico marketing; checklist online",
        "Marketing digital para negocios locales",
        "Auditoria de presencia online",
    ),
    "test-de-salud-online": (
        "test de salud online para negocio",
        "auditoria web; revision de presencia digital; diagnostico marketing; checklist online",
        "Marketing digital para negocios locales",
        "Auditoria de presencia online",
    ),
    "what-businesses-need": (
        "what businesses need to grow online presence",
        "online presence; local business growth; website and SEO; digital checklist",
        "Marketing digital para negocios locales",
        "Presencia online",
    ),
    "que-necesita": (
        "que necesita un negocio para aumentar presencia online",
        "presencia online; crecer negocio local; sitio web y SEO; checklist digital",
        "Marketing digital para negocios locales",
        "Presencia online",
    ),
    "internet-marketing-agency-near-me": (
        "internet marketing agency near me",
        "agencia de marketing cerca de mi; marketing local; elegir agencia; Treasure Coast",
        "Marketing digital para negocios locales",
        "Agencia local",
    ),
    "agencia-de-internet": (
        "agencia de internet marketing cerca de mi",
        "agencia de marketing cerca de mi; marketing local; elegir agencia; Treasure Coast",
        "Marketing digital para negocios locales",
        "Agencia local",
    ),
}


CITY_MAP = {
    "port-st-lucie": "Port St. Lucie",
    "fort-pierce": "Fort Pierce",
    "stuart": "Stuart",
    "vero-beach": "Vero Beach",
}


def keyword_plan(url: str, page_type: str, title: str, h1: str) -> tuple[str, str, str, str]:
    lower = url.lower()
    if page_type == "Archivo local":
        return (
            "marketing digital para negocios locales",
            "Google Business; Meta Ads; Google Ads; diseno web; branding",
            "Marketing digital para negocios locales",
            "Home/landing local",
        )
    if page_type == "Redirect/Home raiz":
        return (
            "AAA Impressions",
            "marketing digital Treasure Coast; pagina de idioma; redireccion homepage",
            "Tecnico SEO",
            "Home raiz",
        )
    if lower.endswith("/es/"):
        return (
            "marketing digital Treasure Coast",
            "agencia de marketing digital; negocios locales; Port St. Lucie; Fort Pierce; Stuart; Vero Beach",
            "Marketing digital para negocios locales",
            "Home ES",
        )
    if lower.endswith("/en/"):
        return (
            "digital marketing Treasure Coast",
            "digital marketing agency; local businesses; Port St. Lucie; Fort Pierce; Stuart; Vero Beach",
            "Marketing digital para negocios locales",
            "Home EN",
        )
    if lower.endswith("/servicios/"):
        return (
            "servicios de marketing digital Treasure Coast",
            "Google Business Profile; Meta Ads; Google Ads; diseno web; branding; redes sociales",
            "Marketing digital para negocios locales",
            "Servicios",
        )
    if lower.endswith("/services/"):
        return (
            "digital marketing services Treasure Coast",
            "Google Business Profile; Meta Ads; Google Ads; web design; branding; social media",
            "Marketing digital para negocios locales",
            "Services",
        )
    if lower.endswith("/ubicaciones/") or lower.endswith("/locations/"):
        return (
            "marketing digital Treasure Coast Florida",
            "Port St. Lucie; Fort Pierce; Stuart; Vero Beach; agencia local",
            "SEO local por ciudad",
            "Ubicaciones",
        )
    if lower.endswith("/blog/"):
        return (
            "blog de marketing digital para negocios locales",
            "SEO; anuncios; IA; email marketing; presencia online",
            "Marketing digital para negocios locales",
            "Blog hub",
        )
    if "/paquetes/" in lower or "/packages/" in lower:
        return (
            "paquetes de marketing digital",
            "planes de marketing; paquetes para negocios locales; presencia digital; anuncios",
            "Conversion y paquetes",
            "Paquetes",
        )
    if "/contact" in lower or "/contacto" in lower:
        return (
            "consulta de marketing digital Treasure Coast",
            "contactar agencia; cotizacion marketing; WhatsApp marketing digital",
            "Conversion y contacto",
            "Contacto",
        )
    if "/about" in lower or "/sobre-nosotros" in lower:
        return (
            "agencia de marketing digital bilingue Treasure Coast",
            "AAA Impressions; equipo local; marketing bilingue; agencia local",
            "Marca y confianza",
            "Sobre nosotros",
        )
    for city_slug, city in CITY_MAP.items():
        if city_slug in lower and page_type == "Ubicacion":
            base = "marketing digital" if "/es/" in lower else "digital marketing"
            return (
                f"{base} {city}",
                f"agencia local {city}; Google Business {city}; Google Ads {city}; diseno web {city}",
                "SEO local por ciudad",
                city,
            )
    for slug, values in SERVICE_KEYWORDS.items():
        if slug in lower:
            return values
    for slug, values in BLOG_KEYWORDS.items():
        if slug in lower:
            return values
    fallback = clean_visible_text(h1 or title)
    fallback = fallback[:80] if fallback else "marketing digital para negocios locales"
    return (
        fallback,
        "negocios locales; Treasure Coast; SEO local; presencia digital",
        "Marketing digital para negocios locales",
        "General",
    )


def role_for(page_type: str, url: str) -> str:
    lower = url.lower()
    if page_type in {"Home", "Pagina"} or lower.endswith("/servicios/") or lower.endswith("/services/"):
        return "Pillar"
    if page_type in {"Servicio", "Ubicacion"}:
        return "Cluster comercial"
    if page_type == "Blog":
        if lower.endswith("/blog/"):
            return "Hub editorial"
        return "Cluster informativo"
    if page_type in {"Contacto", "Paquetes"}:
        return "Conversion"
    if page_type == "Redirect/Home raiz":
        return "Tecnico"
    if page_type == "Archivo local":
        return "Revisar"
    return "Soporte"


def intent_and_funnel(page_type: str, url: str) -> tuple[str, str]:
    if page_type in {"Servicio", "Ubicacion", "Paquetes"}:
        return "Comercial", "Bottom"
    if page_type == "Blog":
        return "Informativa", "Top/Mid"
    if page_type == "Contacto":
        return "Transaccional", "Bottom"
    if page_type in {"Home", "Pagina"}:
        return "Comercial/Navegacional", "Mid/Bottom"
    if page_type == "Redirect/Home raiz":
        return "Tecnica", "SEO"
    return "Soporte", "Soporte"


def action_for(page_type: str, issues: list[str], cluster: str) -> str:
    issue_text = " ".join(issues).lower()
    if "fuera de flujo" in issue_text:
        return "Decidir si este HTML local se migra a src/ o se archiva."
    if "redirect" in issue_text or page_type == "Redirect/Home raiz":
        return "Revisar redireccion raiz: preferir 301/canonical claro si aplica."
    if "no encontrado en crawl" in issue_text:
        return "Agregar enlaces internos o revisar si debe indexarse."
    if page_type == "Servicio":
        return f"Crear 2-4 articulos soporte sobre {cluster} y enlazarlos a esta pagina."
    if page_type == "Ubicacion":
        return "Crear clusters servicio + ciudad y enlazar servicios principales."
    if page_type == "Blog":
        return "Agregar CTA y enlaces internos hacia el servicio/pillar relacionado."
    if page_type == "Paquetes":
        return "Conectar paquetes desde servicios y posts con intencion comercial."
    if page_type == "Contacto":
        return "Revisar tracking de formularios/WhatsApp y CTAs desde paginas clave."
    return "Revisar contenido, keyword y enlaces internos."


def link_suggestions(page_type: str, url: str, pillar: str, cluster: str) -> str:
    lang = "en" if "/en/" in url else "es"
    prefix = f"/{lang}"
    if page_type == "Servicio":
        return f"{prefix}/paquetes/; {prefix}/contacto/; paginas de ubicacion relevantes; posts sobre {cluster}"
    if page_type == "Ubicacion":
        if lang == "en":
            return "/en/services/; /en/contact/; service pages for Google Ads, web design, GBP"
        return "/es/servicios/; /es/contacto/; paginas de Google Ads, diseno web y GBP"
    if page_type == "Blog":
        if "IA" in cluster or "Email" in cluster or "Redes" in cluster:
            return f"{prefix}/servicios/manejo-redes-sociales-treasure-coast/; {prefix}/servicios/diseno-web-treasure-coast/; {prefix}/paquetes/"
        return f"{prefix}/servicios/; {prefix}/paquetes/; posts relacionados del blog"
    if page_type == "Paquetes":
        return f"{prefix}/servicios/; {prefix}/contacto/; servicios de anuncios y presencia local"
    if page_type == "Contacto":
        return f"{prefix}/servicios/; {prefix}/paquetes/; paginas de alta intencion"
    return "Servicios principales; ubicaciones; blog hub; contacto"


def build_source_pages() -> dict[str, dict[str, Any]]:
    pages: dict[str, dict[str, Any]] = {}
    for path in sorted(SRC.rglob("*.njk")):
        rel = path.relative_to(ROOT).as_posix()
        if "/_includes/" in f"/{rel}" or "/_data/" in f"/{rel}":
            continue
        if path.name == "sitemap.njk":
            continue
        raw = read_text(path)
        meta, body = parse_frontmatter(raw)
        url = normalize_url(page_url_from_source(path))
        h1s = extract_tag_text(body, "h1")
        h2s = extract_tag_text(body, "h2")
        visible = clean_visible_text(body)
        title = meta.get("title") or extract_title_from_html(body)
        description = meta.get("metaDescription") or extract_meta_description_from_html(body)
        pages[url] = {
            "url": url,
            "source_file": rel,
            "title_source": title,
            "meta_description": description,
            "h1": h1s[0] if h1s else "",
            "h2s": "; ".join(h2s[:6]),
            "word_count": len(re.findall(r"\b[\w'-]+\b", visible)),
            "summary": textwrap.shorten(visible, width=320, placeholder="...") if visible else "",
            "hreflang_es": meta.get("hreflangEs", ""),
            "hreflang_en": meta.get("hreflangEn", ""),
        }

    # The repo has a root index.html that is outside the current Eleventy source flow.
    local_index = ROOT / "index.html"
    if local_index.exists():
        raw = read_text(local_index)
        h1s = extract_tag_text(raw, "h1")
        h2s = extract_tag_text(raw, "h2")
        visible = clean_visible_text(raw)
        pages["local-only:index.html"] = {
            "url": "local-only:index.html",
            "source_file": "index.html",
            "title_source": extract_title_from_html(raw),
            "meta_description": extract_meta_description_from_html(raw),
            "h1": h1s[0] if h1s else "",
            "h2s": "; ".join(h2s[:6]),
            "word_count": len(re.findall(r"\b[\w'-]+\b", visible)),
            "summary": textwrap.shorten(visible, width=320, placeholder="...") if visible else "",
            "hreflang_es": "",
            "hreflang_en": "",
        }
    return pages


def build_crawl_maps() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], list[dict[str, str]], dict[str, str]]:
    responses = {}
    for row in read_csv(RESPONSE_CODES_CSV):
        address = normalize_url(row.get("Address", ""))
        if not address:
            continue
        responses[address] = row

    titles = {}
    for row in read_csv(PAGE_TITLE_CSV):
        address = normalize_url(row.get("Address", ""))
        if not address:
            continue
        titles[address] = row

    crawl_source = []
    for address, row in responses.items():
        content_type = row.get("Content Type", "")
        if address.startswith(BASE_URL) and "text/html" in content_type:
            title_row = titles.get(address, {})
            crawl_source.append(
                {
                    "Address": address,
                    "Status Code": row.get("Status Code", ""),
                    "Status": row.get("Status", ""),
                    "Indexability": row.get("Indexability", ""),
                    "Indexability Status": row.get("Indexability Status", ""),
                    "Inlinks": row.get("Inlinks", ""),
                    "Response Time": row.get("Response Time", ""),
                    "Redirect URL": row.get("Redirect URL", ""),
                    "Redirect Type": row.get("Redirect Type", ""),
                    "Title": title_row.get("Title 1", ""),
                    "Title Length": title_row.get("Title 1 Length", ""),
                }
            )
    overview = parse_crawl_overview(CRAWL_OVERVIEW_CSV)
    return responses, titles, crawl_source, overview


def build_inventory() -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, str]]:
    source_pages = build_source_pages()
    responses, titles, crawl_source, overview = build_crawl_maps()
    urls = set(source_pages.keys())
    for row in crawl_source:
        urls.add(normalize_url(row["Address"]))

    rows: list[dict[str, Any]] = []
    for url in sorted(urls, key=lambda value: (value.startswith("local-only:"), value)):
        source = source_pages.get(url, {})
        crawl = responses.get(url, {})
        title_row = titles.get(url, {})
        page_type = page_type_for_url(url, source.get("source_file", ""))
        lang = language_for_url(url)
        crawl_title = title_row.get("Title 1", "")
        title_source = source.get("title_source", "")
        effective_title = crawl_title or title_source
        h1 = source.get("h1", "")
        keyword, secondaries, pillar, cluster = keyword_plan(url, page_type, effective_title, h1)
        role = role_for(page_type, url)
        intent, funnel = intent_and_funnel(page_type, url)

        issues: list[str] = []
        if crawl.get("Indexability") and crawl.get("Indexability") != "Indexable":
            issues.append(f"Non-indexable: {crawl.get('Indexability Status') or crawl.get('Indexability')}")
        if crawl.get("Redirect URL") or "Redirect" in crawl.get("Indexability Status", ""):
            issues.append("Redirect detectado")
        if not source and not url.startswith("local-only:"):
            issues.append("URL en crawl sin fuente src encontrada")
        if source and not crawl and not url.startswith("local-only:"):
            issues.append("No encontrado en crawl")
        if source and not h1 and page_type not in {"Redirect/Home raiz"}:
            issues.append("H1 faltante")
        if source and not source.get("meta_description") and page_type not in {"Redirect/Home raiz"}:
            issues.append("Meta description faltante")
        if url.startswith("local-only:"):
            issues.append("Fuera de flujo Eleventy/live crawl")

        title_len = len(effective_title)
        if title_len > 65:
            issues.append("Titulo largo")
        elif 0 < title_len < 25:
            issues.append("Titulo corto")

        priority = "Media"
        if page_type in {"Servicio", "Ubicacion", "Home", "Paquetes", "Contacto"}:
            priority = "Alta"
        if page_type in {"Gracias"}:
            priority = "Baja"
        if page_type in {"Redirect/Home raiz", "Archivo local"} or issues:
            priority = "Revisar" if page_type == "Archivo local" else "Alta"

        rows.append(
            {
                "URL": url,
                "Idioma": lang,
                "Tipo pagina": page_type,
                "Estado HTTP": crawl.get("Status Code", ""),
                "Indexabilidad": crawl.get("Indexability", ""),
                "Inlinks": crawl.get("Inlinks", ""),
                "Titulo crawl": crawl_title,
                "Titulo source": title_source,
                "H1": h1,
                "H2 principales": source.get("h2s", ""),
                "Palabras": source.get("word_count", ""),
                "Resumen contenido": source.get("summary", ""),
                "Palabra clave principal": keyword,
                "Keywords secundarias": secondaries,
                "Pillar recomendado": pillar,
                "Cluster recomendado": cluster,
                "Rol": role,
                "Intencion": intent,
                "Funnel": funnel,
                "Prioridad": priority,
                "Oportunidad": action_for(page_type, issues, cluster),
                "Enlaces internos sugeridos": link_suggestions(page_type, url, pillar, cluster),
                "Accion siguiente": action_for(page_type, issues, cluster),
                "Archivo fuente": source.get("source_file", ""),
                "Fuente datos": "Repo src + Screaming Frog CSV" if crawl else "Repo src/local",
                "Issues SEO": "; ".join(issues),
                "Hreflang ES": source.get("hreflang_es", ""),
                "Hreflang EN": source.get("hreflang_en", ""),
            }
        )

    title_counts = Counter((row["Titulo crawl"] or row["Titulo source"]).strip() for row in rows if (row["Titulo crawl"] or row["Titulo source"]).strip())
    for row in rows:
        title = (row["Titulo crawl"] or row["Titulo source"]).strip()
        if title and title_counts[title] > 1 and "Titulo duplicado" not in row["Issues SEO"]:
            row["Issues SEO"] = (row["Issues SEO"] + "; " if row["Issues SEO"] else "") + "Titulo duplicado"
            if row["Prioridad"] != "Baja":
                row["Prioridad"] = "Alta"
    return rows, crawl_source, overview


def build_pillars(inventory: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_pillar: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in inventory:
        if not row["URL"].startswith("local-only:"):
            by_pillar[row["Pillar recomendado"]].append(row)

    ordered = [
        "Marketing digital para negocios locales",
        "Presencia local y SEO",
        "Publicidad pagada",
        "Diseno web y conversion",
        "Contenido y redes sociales",
        "Branding y materiales",
        "SEO local por ciudad",
        "Conversion y paquetes",
        "Conversion y contacto",
        "Marca y confianza",
        "Tecnico SEO",
    ]
    gap_map = {
        "Marketing digital para negocios locales": "Crear hub/guia: estrategia de marketing digital para negocios locales en Treasure Coast; conectar servicios, ubicaciones y paquetes.",
        "Presencia local y SEO": "Clusters faltantes: Google Maps SEO, manejo de resenas, posts de Google Business, checklist de perfil local.",
        "Publicidad pagada": "Clusters faltantes: costo de Google Ads, Meta Ads vs Google Ads, landing pages para anuncios, seguimiento de leads.",
        "Diseno web y conversion": "Clusters faltantes: checklist de sitio web local, landing pages por servicio, velocidad web, formularios y conversiones.",
        "Contenido y redes sociales": "Clusters faltantes: calendario mensual, prompts de IA por industria, ideas de reels, email + social para retencion.",
        "Branding y materiales": "Clusters faltantes: logo para negocios locales, material impreso para promociones, coherencia marca digital/fisica.",
        "SEO local por ciudad": "Clusters faltantes: servicio + ciudad para PSL/Fort Pierce/Stuart/Vero, guias locales por industria.",
        "Conversion y paquetes": "Crear comparador simple de paquetes y enlazar desde servicios con casos de uso por etapa del negocio.",
        "Conversion y contacto": "Revisar tracking de WhatsApp/formulario y conectar todas las paginas de alta intencion.",
        "Marca y confianza": "Agregar pruebas de confianza: casos, proceso, industrias y diferenciadores bilingues/locales.",
        "Tecnico SEO": "Resolver redireccion raiz, sitemaps y consistencia canonical/hreflang.",
    }
    rows = []
    for pillar in ordered:
        pages = by_pillar.get(pillar, [])
        if not pages and pillar not in gap_map:
            continue
        es_pages = [r["URL"] for r in pages if r["Idioma"].startswith("ES")][:5]
        en_pages = [r["URL"] for r in pages if r["Idioma"].startswith("EN")][:5]
        clusters = sorted({r["Cluster recomendado"] for r in pages if r["Cluster recomendado"]})
        rows.append(
            {
                "Pillar": pillar,
                "Estado": "Existente" if pages else "Gap",
                "URL principal ES": es_pages[0] if es_pages else "",
                "URL principal EN": en_pages[0] if en_pages else "",
                "Clusters existentes": "; ".join(clusters[:10]),
                "Paginas actuales": "; ".join((es_pages + en_pages)[:10]),
                "Ideas/gaps": gap_map.get(pillar, ""),
                "Enlaces internos sugeridos": "Hub -> cluster pages -> servicio/contacto; agregar enlaces contextuales desde blogs a servicios.",
                "Siguiente accion": "Elegir 1 pillar prioritario y crear 3 clusters soporte con enlaces internos claros.",
            }
        )
    return rows


def build_keyword_bank(inventory: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    seen = set()
    for item in inventory:
        primary = item["Palabra clave principal"]
        if primary:
            key = (primary.lower(), item["URL"])
            if key not in seen:
                seen.add(key)
                rows.append(
                    {
                        "Keyword": primary,
                        "Tipo": "Principal",
                        "URL actual": item["URL"],
                        "Pillar": item["Pillar recomendado"],
                        "Cluster": item["Cluster recomendado"],
                        "Intencion": item["Intencion"],
                        "Prioridad": item["Prioridad"],
                        "Notas": "Keyword asignada desde pagina actual.",
                    }
                )
        for secondary in [part.strip() for part in str(item["Keywords secundarias"]).split(";") if part.strip()]:
            key = (secondary.lower(), item["URL"])
            if key not in seen:
                seen.add(key)
                rows.append(
                    {
                        "Keyword": secondary,
                        "Tipo": "Secundaria",
                        "URL actual": item["URL"],
                        "Pillar": item["Pillar recomendado"],
                        "Cluster": item["Cluster recomendado"],
                        "Intencion": item["Intencion"],
                        "Prioridad": item["Prioridad"],
                        "Notas": "Usar en H2s, FAQs, anchors internos o articulo soporte.",
                    }
                )
    return rows


def xml_escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=False)


def attr_escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def col_name(index: int) -> str:
    name = ""
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def cell_ref(row: int, col: int) -> str:
    return f"{col_name(col)}{row}"


def sheet_xml(
    rows: list[list[Any]],
    col_widths: list[float],
    *,
    freeze_rows: int = 0,
    autofilter: bool = False,
    merges: list[str] | None = None,
    validations: list[tuple[str, list[str]]] | None = None,
    styled_rows: dict[int, int] | None = None,
    styled_cols: dict[int, int] | None = None,
    styled_cells: dict[tuple[int, int], int] | None = None,
) -> str:
    merges = merges or []
    validations = validations or []
    styled_rows = styled_rows or {}
    styled_cols = styled_cols or {}
    styled_cells = styled_cells or {}
    max_cols = max((len(row) for row in rows), default=1)
    dimension = f"A1:{cell_ref(max(len(rows), 1), max(max_cols, 1))}"
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        f'<dimension ref="{dimension}"/>',
        '<sheetViews><sheetView showGridLines="0" workbookViewId="0">',
    ]
    if freeze_rows:
        top_left = f"A{freeze_rows + 1}"
        parts.append(f'<pane ySplit="{freeze_rows}" topLeftCell="{top_left}" activePane="bottomLeft" state="frozen"/>')
        parts.append('<selection pane="bottomLeft"/>')
    parts.append("</sheetView></sheetViews>")
    if col_widths:
        parts.append("<cols>")
        for idx, width in enumerate(col_widths, start=1):
            parts.append(f'<col min="{idx}" max="{idx}" width="{width}" customWidth="1"/>')
        parts.append("</cols>")
    parts.append("<sheetData>")
    for r_idx, row in enumerate(rows, start=1):
        height = 24 if r_idx in styled_rows else 42 if r_idx > 1 else 22
        parts.append(f'<row r="{r_idx}" ht="{height}" customHeight="1">')
        for c_idx, value in enumerate(row, start=1):
            if value is None:
                continue
            ref = cell_ref(r_idx, c_idx)
            style = styled_cells.get((r_idx, c_idx), styled_rows.get(r_idx, styled_cols.get(c_idx, 5)))
            if isinstance(value, dict) and "formula" in value:
                formula = str(value["formula"]).lstrip("=")
                cached = value.get("value", "")
                if isinstance(cached, (int, float)):
                    parts.append(f'<c r="{ref}" s="{style}"><f>{xml_escape(formula)}</f><v>{cached}</v></c>')
                else:
                    parts.append(
                        f'<c r="{ref}" s="{style}" t="str"><f>{xml_escape(formula)}</f><v>{xml_escape(cached)}</v></c>'
                    )
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                parts.append(f'<c r="{ref}" s="{style}"><v>{value}</v></c>')
            else:
                text = str(value)
                if len(text) > 32000:
                    text = text[:31997] + "..."
                parts.append(
                    f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{xml_escape(text)}</t></is></c>'
                )
        parts.append("</row>")
    parts.append("</sheetData>")
    if autofilter and rows:
        parts.append(f'<autoFilter ref="A1:{cell_ref(1, max_cols)}"/>')
    if validations:
        parts.append(f'<dataValidations count="{len(validations)}">')
        for sqref, values in validations:
            list_value = ",".join(values)
            parts.append(
                f'<dataValidation type="list" allowBlank="1" showErrorMessage="1" sqref="{attr_escape(sqref)}">'
                f'<formula1>"{xml_escape(list_value)}"</formula1></dataValidation>'
            )
        parts.append("</dataValidations>")
    if merges:
        parts.append(f'<mergeCells count="{len(merges)}">')
        for merge in merges:
            parts.append(f'<mergeCell ref="{attr_escape(merge)}"/>')
        parts.append("</mergeCells>")
    parts.append("</worksheet>")
    return "".join(parts)


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="6">
    <font><sz val="10"/><color rgb="FF111827"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="16"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FF111827"/><name val="Calibri"/></font>
    <font><u/><sz val="10"/><color rgb="FF0B57D0"/><name val="Calibri"/></font>
    <font><sz val="9"/><color rgb="FF4B5563"/><name val="Calibri"/></font>
  </fonts>
  <fills count="10">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF09162E"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF0057E7"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFEAF1FF"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFFF7CC"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFEAF7EA"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFFE8E8"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF3F4F6"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFFF0E8"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border><left style="thin"><color rgb="FFE5E7EB"/></left><right style="thin"><color rgb="FFE5E7EB"/></right><top style="thin"><color rgb="FFE5E7EB"/></top><bottom style="thin"><color rgb="FFE5E7EB"/></bottom><diagonal/></border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="16">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="2" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="4" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="6" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="5" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="7" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="5" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="3" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="3" fillId="8" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="5" fillId="8" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="9" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


def content_types_xml(sheet_count: int) -> str:
    sheet_overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for i in range(1, sheet_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  {sheet_overrides}
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""


def workbook_xml(sheet_names: list[str]) -> str:
    sheets = "".join(
        f'<sheet name="{attr_escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, name in enumerate(sheet_names, start=1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <workbookPr date1904="false"/>
  <sheets>{sheets}</sheets>
  <calcPr calcMode="auto"/>
</workbook>"""


def workbook_rels_xml(sheet_count: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
        for i in range(1, sheet_count + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{sheet_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels)
        + "</Relationships>"
    )


def root_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def doc_props_core_xml() -> str:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>AAA Impressions Content Inventory and Pillar Cluster Planner</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def doc_props_app_xml(sheet_names: list[str]) -> str:
    titles = "".join(f"<vt:lpstr>{xml_escape(name)}</vt:lpstr>" for name in sheet_names)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <HeadingPairs>
    <vt:vector size="2" baseType="variant">
      <vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>
      <vt:variant><vt:i4>{len(sheet_names)}</vt:i4></vt:variant>
    </vt:vector>
  </HeadingPairs>
  <TitlesOfParts>
    <vt:vector size="{len(sheet_names)}" baseType="lpstr">{titles}</vt:vector>
  </TitlesOfParts>
</Properties>"""


def make_dashboard_rows(inventory: list[dict[str, Any]], overview: dict[str, str]) -> list[list[Any]]:
    last = len(inventory) + 1
    counts = Counter(row["Tipo pagina"] for row in inventory)
    priority_counts = Counter(row["Prioridad"] for row in inventory)
    indexable = sum(1 for row in inventory if row["Indexabilidad"] == "Indexable")
    issue_count = sum(1 for row in inventory if row["Issues SEO"])
    crawl_date = overview.get("Report Date") or overview.get("Start Date") or ""
    return [
        ["Mapa de Contenido SEO - AAA Impressions", None, None, None, None, None, None, None],
        [f"Inventario generado desde repo + crawl. Reporte crawl: {crawl_date}", None, None, None, None, None, None, None],
        [],
        ["Metrica", "Valor", "Nota", None, "Primeras acciones recomendadas", None, None, None],
        ["Paginas en inventario", {"formula": f"COUNTA(Inventario!A2:A{last})", "value": len(inventory)}, "Fuente: src/ + HTML crawl + local index.html", None, "1", "Resolver/confirmar la redireccion raiz y canonical.", None, None],
        ["Paginas indexables", {"formula": f'COUNTIF(Inventario!E2:E{last},"Indexable")', "value": indexable}, "Segun Screaming Frog", None, "2", "Usar /es/ y /en/ como pillars principales y enlazar servicios/ubicaciones/blog.", None, None],
        ["Servicios", {"formula": f'COUNTIF(Inventario!C2:C{last},"Servicio")', "value": counts["Servicio"]}, "Paginas comerciales", None, "3", "Crear clusters de soporte para Google Business, Google Ads, Meta Ads, web, redes y branding.", None, None],
        ["Blog posts", {"formula": f'COUNTIF(Inventario!C2:C{last},"Blog")', "value": counts["Blog"]}, "Contenido informativo/hub", None, "4", "Desde cada blog, enlazar al servicio/pillar y a una pagina de conversion.", None, None],
        ["Ubicaciones", {"formula": f'COUNTIF(Inventario!C2:C{last},"Ubicacion")', "value": counts["Ubicacion"]}, "SEO local por ciudad", None, "5", "Planear servicio + ciudad como clusters futuros para Treasure Coast.", None, None],
        ["Prioridad alta/revisar", {"formula": f'COUNTIF(Inventario!T2:T{last},"Alta")+COUNTIF(Inventario!T2:T{last},"Revisar")', "value": priority_counts["Alta"] + priority_counts["Revisar"]}, "Filtrar Inventario por Prioridad", None, "6", "Decidir si index.html raiz local se migra a src/ o se archiva.", None, None],
        ["Filas con issues SEO", {"formula": f'COUNTIF(Inventario!Z2:Z{last},"*?*")', "value": issue_count}, "Ver columna Issues SEO", None, "", "", None, None],
        [],
        ["Como usar esta hoja", None, None, None, None, None, None, None],
        ["Filtra Inventario por Prioridad = Alta/Revisar, luego por Pillar recomendado. Llena Owner/Status si la subes a Google Sheets y convierte las oportunidades en tareas editoriales.", None, None, None, None, None, None, None],
    ]


def rows_from_dicts(data: list[dict[str, Any]], headers: list[str]) -> list[list[Any]]:
    return [headers] + [[row.get(header, "") for header in headers] for row in data]


def build_workbook() -> None:
    inventory, crawl_source, overview = build_inventory()
    pillars = build_pillars(inventory)
    keywords = build_keyword_bank(inventory)

    inventory_headers = [
        "URL",
        "Idioma",
        "Tipo pagina",
        "Estado HTTP",
        "Indexabilidad",
        "Inlinks",
        "Titulo crawl",
        "Titulo source",
        "H1",
        "H2 principales",
        "Palabras",
        "Resumen contenido",
        "Palabra clave principal",
        "Keywords secundarias",
        "Pillar recomendado",
        "Cluster recomendado",
        "Rol",
        "Intencion",
        "Funnel",
        "Prioridad",
        "Oportunidad",
        "Enlaces internos sugeridos",
        "Accion siguiente",
        "Archivo fuente",
        "Fuente datos",
        "Issues SEO",
        "Hreflang ES",
        "Hreflang EN",
    ]
    pillar_headers = [
        "Pillar",
        "Estado",
        "URL principal ES",
        "URL principal EN",
        "Clusters existentes",
        "Paginas actuales",
        "Ideas/gaps",
        "Enlaces internos sugeridos",
        "Siguiente accion",
    ]
    keyword_headers = ["Keyword", "Tipo", "URL actual", "Pillar", "Cluster", "Intencion", "Prioridad", "Notas"]
    crawl_headers = [
        "Address",
        "Status Code",
        "Status",
        "Indexability",
        "Indexability Status",
        "Inlinks",
        "Response Time",
        "Redirect URL",
        "Redirect Type",
        "Title",
        "Title Length",
    ]

    notes_rows = [
        ["Nota", "Detalle"],
        ["Objetivo", "Ver que paginas y contenido existen para planear pillars and clusters en el website."],
        ["Fuentes", f"Repo: {ROOT}; Crawl CSVs: {DOWNLOADS}"],
        ["Crawl report date", overview.get("Report Date", "")],
        ["Root index.html", "Hay un index.html local en la raiz fuera del flujo src/ de Eleventy; se marco como local-only para revisar."],
        ["Uso sugerido", "Sube este XLSX a Google Sheets. Luego filtra Inventario por Prioridad, Pillar y Cluster para planear contenido."],
        ["Campos editables", "Puedes agregar Owner, Status, Fecha objetivo y URL final en Google Sheets despues de importar."],
    ]

    sheets: list[tuple[str, str]] = []
    dashboard = make_dashboard_rows(inventory, overview)
    sheets.append(
        (
            "Dashboard",
            sheet_xml(
                dashboard,
                [28, 14, 44, 4, 12, 70, 8, 8],
                merges=["A1:H1", "A2:H2", "A13:H13", "A14:H14"],
                styled_rows={1: 1, 2: 11, 4: 4, 13: 3, 14: 11},
                styled_cols={2: 12},
                styled_cells={(r, 2): 12 for r in range(5, 12)},
            ),
        )
    )

    inv_rows = rows_from_dicts(inventory, inventory_headers)
    inv_styles = {}
    for r_idx, row in enumerate(inventory, start=2):
        priority = row.get("Prioridad", "")
        if priority == "Alta":
            inv_styles[(r_idx, 20)] = 9
        elif priority == "Revisar":
            inv_styles[(r_idx, 20)] = 8
        elif priority == "Baja":
            inv_styles[(r_idx, 20)] = 14
        else:
            inv_styles[(r_idx, 20)] = 11
        if row.get("Indexabilidad") == "Indexable":
            inv_styles[(r_idx, 5)] = 7
        elif row.get("Indexabilidad"):
            inv_styles[(r_idx, 5)] = 9
        if row.get("URL", "").startswith("local-only:"):
            inv_styles[(r_idx, 1)] = 15

    sheets.append(
        (
            "Inventario",
            sheet_xml(
                inv_rows,
                [42, 10, 16, 10, 15, 10, 34, 34, 36, 48, 10, 58, 30, 44, 30, 24, 18, 18, 14, 14, 50, 50, 50, 34, 22, 40, 20, 20],
                freeze_rows=1,
                autofilter=True,
                validations=[
                    (f"Q2:Q{len(inv_rows)}", ["Pillar", "Cluster comercial", "Cluster informativo", "Hub editorial", "Conversion", "Tecnico", "Revisar"]),
                    (f"T2:T{len(inv_rows)}", ["Alta", "Media", "Baja", "Revisar"]),
                    (f"R2:R{len(inv_rows)}", ["Informativa", "Comercial", "Transaccional", "Tecnica", "Soporte", "Comercial/Navegacional"]),
                ],
                styled_rows={1: 4},
                styled_cols={1: 6},
                styled_cells=inv_styles,
            ),
        )
    )

    sheets.append(
        (
            "Pillars_Clusters",
            sheet_xml(
                rows_from_dicts(pillars, pillar_headers),
                [30, 14, 42, 42, 42, 58, 62, 55, 46],
                freeze_rows=1,
                autofilter=True,
                styled_rows={1: 4},
                styled_cols={3: 6, 4: 6},
            ),
        )
    )

    kw_rows = rows_from_dicts(keywords, keyword_headers)
    kw_styles = {}
    for r_idx, row in enumerate(keywords, start=2):
        if row.get("Tipo") == "Principal":
            kw_styles[(r_idx, 2)] = 11
    sheets.append(
        (
            "Keyword_Bank",
            sheet_xml(
                kw_rows,
                [34, 14, 50, 30, 26, 18, 14, 48],
                freeze_rows=1,
                autofilter=True,
                styled_rows={1: 4},
                styled_cols={3: 6},
                styled_cells=kw_styles,
            ),
        )
    )

    sheets.append(
        (
            "Crawl_Source",
            sheet_xml(
                rows_from_dicts(crawl_source, crawl_headers),
                [52, 12, 12, 16, 22, 10, 14, 46, 20, 48, 12],
                freeze_rows=1,
                autofilter=True,
                styled_rows={1: 4},
                styled_cols={1: 6, 8: 6},
            ),
        )
    )

    sheets.append(
        (
            "Notas",
            sheet_xml(
                notes_rows,
                [24, 90],
                freeze_rows=1,
                styled_rows={1: 4},
                styled_cols={2: 5},
            ),
        )
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sheet_names = [name for name, _ in sheets]
    with zipfile.ZipFile(OUTPUT_XLSX, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml(len(sheets)))
        zf.writestr("_rels/.rels", root_rels_xml())
        zf.writestr("docProps/core.xml", doc_props_core_xml())
        zf.writestr("docProps/app.xml", doc_props_app_xml(sheet_names))
        zf.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(len(sheets)))
        zf.writestr("xl/styles.xml", styles_xml())
        for idx, (_, xml) in enumerate(sheets, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", xml)

    validate_xlsx(OUTPUT_XLSX)
    print(f"Wrote {OUTPUT_XLSX}")
    print(f"Inventory rows: {len(inventory)}")
    print(f"Keyword rows: {len(keywords)}")
    print(f"Crawl HTML rows: {len(crawl_source)}")


def validate_xlsx(path: Path) -> None:
    with zipfile.ZipFile(path, "r") as zf:
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f"Corrupt zip member: {bad}")
        required = [
            "[Content_Types].xml",
            "xl/workbook.xml",
            "xl/styles.xml",
            "xl/worksheets/sheet1.xml",
            "xl/worksheets/sheet2.xml",
        ]
        for name in required:
            if name not in zf.namelist():
                raise RuntimeError(f"Missing XLSX part: {name}")
        for name in zf.namelist():
            if name.endswith(".xml"):
                ElementTree.fromstring(zf.read(name))


if __name__ == "__main__":
    build_workbook()
