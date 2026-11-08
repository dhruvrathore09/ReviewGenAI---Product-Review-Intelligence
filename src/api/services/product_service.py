"""Service layer for product querying, filtering, search, and statistics."""

import re
import math
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy import select, func, or_, and_, desc, asc, case
from sqlalchemy.orm import Session

from src.db.models import Product, Review
from src.api.schemas.product import (
    ProductListItem,
    ProductListResponse,
    ProductDetail,
    ProductStatistics,
    RatingDistributionItem,
)


class ProductService:
    """Encapsulates business and query logic for products."""

    @classmethod
    def _apply_category_filter(cls, stmt, category: str):
        cat_lower = category.strip().lower()
        if cat_lower in ["headphones & earbuds", "headphones", "headphone", "earbuds", "earphones", "headsets"]:
            # Strict listening headphones & earbuds (no cables, cases, adapters, backpacks, etc.)
            is_listening = or_(
                Product.categories_hierarchy.ilike("%Headphones & Earbuds%"),
                Product.product_name.ilike("%headphone%"),
                Product.product_name.ilike("%earbud%"),
                Product.product_name.ilike("%earphone%"),
                Product.product_name.ilike("%headset%"),
                Product.product_name.ilike("%airpods%"),
            )
            is_non_listening = or_(
                Product.product_name.ilike("%cable%"),
                Product.product_name.ilike("% cord%"),
                Product.product_name.ilike("%adapter%"),
                Product.product_name.ilike("%transmitter%"),
                Product.product_name.ilike("%receiver%"),
                Product.product_name.ilike("%splitter%"),
                Product.product_name.ilike("%case%"),
                Product.product_name.ilike("%cover%"),
                Product.product_name.ilike("%bag%"),
                Product.product_name.ilike("%backpack%"),
                Product.product_name.ilike("%pouch%"),
                Product.product_name.ilike("%sleeve%"),
                Product.product_name.ilike("%stand%"),
                Product.product_name.ilike("%hanger%"),
                Product.product_name.ilike("%holder%"),
                Product.product_name.ilike("%mount%"),
                Product.product_name.ilike("%cushion%"),
                Product.product_name.ilike("%earpad%"),
                Product.product_name.ilike("%ear pad%"),
                Product.product_name.ilike("%ear tip%"),
                Product.product_name.ilike("%eartip%"),
                Product.product_name.ilike("%organizer%"),
                Product.product_name.ilike("%clean%"),
                Product.product_name.ilike("%battery%"),
                Product.product_name.ilike("%charger%"),
                Product.product_name.ilike("%boombox%"),
                Product.product_name.ilike("%speaker%"),
                Product.product_name.ilike("%soundbar%"),
                Product.product_name.ilike("%sound system%"),
            )
            return stmt.where(is_listening, ~is_non_listening)
        elif cat_lower in ["smartphones", "smart phones", "phones", "mobiles", "mobile phones", "smartphones & mobiles"]:
            is_phone_name = or_(
                Product.categories_hierarchy.ilike("%> Cell Phones%"),
                Product.categories_hierarchy.ilike("%Smartphones%"),
                Product.product_name.ilike("%smartphone%"),
                Product.product_name.ilike("%cell phone%"),
                Product.product_name.ilike("Apple iPhone%"),
                Product.product_name.ilike("iPhone%"),
                Product.product_name.ilike("%Apple iPhone%"),
                and_(Product.brand.ilike("apple"), Product.product_name.ilike("%iphone%")),
                Product.product_name.ilike("%galaxy s%"),
                Product.product_name.ilike("%galaxy note%"),
                Product.product_name.ilike("%galaxy a%"),
                Product.product_name.ilike("%galaxy z%"),
                Product.product_name.ilike("%pixel %"),
                Product.product_name.ilike("%moto g%"),
                Product.product_name.ilike("%motorola edge%"),
                Product.product_name.ilike("%oneplus %"),
                Product.product_name.ilike("%redmi note%"),
                Product.product_name.ilike("%xiaomi %"),
                Product.product_name.ilike("%blu %"),
                and_(
                    Product.product_name.ilike("%unlocked%"),
                    or_(
                        Product.product_name.ilike("%phone%"),
                        Product.product_name.ilike("%mobile%"),
                        Product.product_name.ilike("%5g%"),
                    ),
                ),
            )
            is_non_phone = or_(
                Product.product_name.ilike("%watch%"),
                Product.product_name.ilike("%smartwatch%"),
                Product.product_name.ilike("%speaker%"),
                Product.product_name.ilike("%headphone%"),
                Product.product_name.ilike("%earbud%"),
                Product.product_name.ilike("%headset%"),
                Product.product_name.ilike("%power strip%"),
                Product.product_name.ilike("%surge protector%"),
                Product.product_name.ilike("%case%"),
                Product.product_name.ilike("%cover%"),
                Product.product_name.ilike("%cable%"),
                Product.product_name.ilike("%charger%"),
                Product.product_name.ilike("%holder%"),
                Product.product_name.ilike("%mount%"),
                Product.product_name.ilike("%stand%"),
                Product.product_name.ilike("%screen protector%"),
                Product.product_name.ilike("%tempered glass%"),
                Product.product_name.ilike("%replacement%"),
                Product.product_name.ilike("%adapter%"),
                Product.product_name.ilike("%wallet%"),
                Product.product_name.ilike("%macbook%"),
                Product.product_name.ilike("%ipad%"),
                Product.product_name.ilike("%ipod%"),
                Product.product_name.ilike("%stickers%"),
                Product.product_name.ilike("%tripod%"),
                Product.product_name.ilike("%printer%"),
                Product.product_name.ilike("%paper%"),
            )
            return stmt.where(
                or_(
                    Product.main_category.in_(["Cell Phones & Accessories", "Apple Products", "All Electronics"]),
                    Product.categories_hierarchy.ilike("%Cell Phones%"),
                ),
                is_phone_name,
                ~is_non_phone,
            )
        elif cat_lower in ["laptops", "laptop", "notebooks", "notebook", "laptops & notebooks", "laptops & computers"]:
            is_laptop_name = or_(
                Product.categories_hierarchy.ilike("%Traditional Laptops%"),
                Product.categories_hierarchy.ilike("%2 in 1 Laptops%"),
                Product.categories_hierarchy.ilike("%> Laptops%"),
                and_(
                    or_(
                        Product.product_name.ilike("%laptop%"),
                        Product.product_name.ilike("%notebook%"),
                        Product.product_name.ilike("%chromebook%"),
                        Product.product_name.ilike("%macbook%"),
                    ),
                    or_(
                        Product.product_name.ilike("%fhd%"),
                        Product.product_name.ilike("%intel%"),
                        Product.product_name.ilike("%amd%"),
                        Product.product_name.ilike("%ryzen%"),
                        Product.product_name.ilike("%core i%"),
                        Product.product_name.ilike("%celeron%"),
                        Product.product_name.ilike("%pentium%"),
                    ),
                ),
            )
            is_non_laptop = or_(
                Product.product_name.ilike("%for macbook%"),
                Product.product_name.ilike("%for chromebook%"),
                Product.product_name.ilike("%for laptop%"),
                Product.product_name.ilike("%for dell%"),
                Product.product_name.ilike("%for hp%"),
                Product.product_name.ilike("%flash drive%"),
                Product.product_name.ilike("%usb drive%"),
                Product.product_name.ilike("%thumb drive%"),
                Product.product_name.ilike("%memory stick%"),
                Product.product_name.ilike("%screen extender%"),
                Product.product_name.ilike("%portable monitor%"),
                Product.product_name.ilike("%monitor%"),
                Product.product_name.ilike("%screwdriver%"),
                Product.product_name.ilike("%screws%"),
                Product.product_name.ilike("%gpu%"),
                Product.product_name.ilike("%enclosure%"),
                Product.product_name.ilike("%drawing tablet%"),
                Product.product_name.ilike("%graphics tablet%"),
                Product.product_name.ilike("%privacy filter%"),
                Product.product_name.ilike("%privacy screen%"),
                Product.product_name.ilike("%decal%"),
                Product.product_name.ilike("%sticker%"),
                Product.product_name.ilike("%skin%"),
                Product.product_name.ilike("%case%"),
                Product.product_name.ilike("%cover%"),
                Product.product_name.ilike("%sleeve%"),
                Product.product_name.ilike("%bag%"),
                Product.product_name.ilike("%backpack%"),
                Product.product_name.ilike("%charger%"),
                Product.product_name.ilike("%power cord%"),
                Product.product_name.ilike("%adapter%"),
                Product.product_name.ilike("%stand%"),
                Product.product_name.ilike("%dock%"),
                Product.product_name.ilike("%cooling pad%"),
                Product.product_name.ilike("%cooler%"),
                Product.product_name.ilike("%fan%"),
                Product.product_name.ilike("%cable%"),
                Product.product_name.ilike("%screen protector%"),
                Product.product_name.ilike("%hard shell%"),
                Product.product_name.ilike("%tote%"),
                Product.product_name.ilike("%briefcase%"),
                Product.product_name.ilike("%power supply%"),
                Product.product_name.ilike("%keyboard%"),
                Product.product_name.ilike("%mouse%"),
                Product.product_name.ilike("%hub%"),
                Product.product_name.ilike("%webcam%"),
                Product.product_name.ilike("%hard drive%"),
                Product.product_name.ilike("%external drive%"),
                Product.product_name.ilike("%optical drive%"),
                Product.product_name.ilike("%dvd drive%"),
                Product.product_name.ilike("%ram %"),
                Product.product_name.ilike("%sodimm%"),
                Product.product_name.ilike("%dram%"),
                Product.product_name.ilike("%memory kit%"),
                Product.categories_hierarchy.ilike("%Laptop Accessories%"),
                Product.categories_hierarchy.ilike("%Data Storage%"),
                Product.categories_hierarchy.ilike("%Replacement Parts%"),
            )
            return stmt.where(
                Product.main_category == "Computers",
                is_laptop_name,
                ~is_non_laptop,
            )
        elif cat_lower in ["cameras & photography", "camera & photo", "cameras", "camera", "photography"]:
            is_camera_name = or_(
                Product.main_category == "Camera & Photo",
                Product.categories_hierarchy.ilike("%Digital Cameras%"),
                Product.categories_hierarchy.ilike("%Lenses%"),
                Product.product_name.ilike("%camera%"),
                Product.product_name.ilike("%camcorder%"),
                Product.product_name.ilike("%dslr%"),
                Product.product_name.ilike("%webcam%"),
            )
            is_non_camera = or_(
                Product.product_name.ilike("%laptop%"),
                Product.product_name.ilike("%notebook%"),
                Product.product_name.ilike("%smartphone%"),
                Product.product_name.ilike("%phone%"),
                Product.product_name.ilike("%case%"),
                Product.product_name.ilike("%bag%"),
                Product.product_name.ilike("%strap%"),
                Product.product_name.ilike("%mount%"),
                Product.product_name.ilike("%stand%"),
                Product.product_name.ilike("%tripod%"),
                Product.product_name.ilike("%battery%"),
                Product.product_name.ilike("%charger%"),
                Product.product_name.ilike("%lens cap%"),
                Product.product_name.ilike("%adapter%"),
                Product.product_name.ilike("%cable%"),
                Product.product_name.ilike("%filter%"),
                Product.product_name.ilike("%cleaning%"),
                Product.product_name.ilike("%backdrop%"),
                Product.product_name.ilike("%light%"),
            )
            return stmt.where(is_camera_name, ~is_non_camera)
        elif cat_lower in ["hard disks & storage", "hard disk", "hard disks", "hard drive", "storage", "data storage", "ssd", "memory cards"]:
            is_storage_name = or_(
                Product.categories_hierarchy.ilike("%Data Storage%"),
                Product.categories_hierarchy.ilike("%External Hard Drives%"),
                Product.categories_hierarchy.ilike("%Internal Hard Drives%"),
                Product.categories_hierarchy.ilike("%Solid State Drives%"),
                Product.categories_hierarchy.ilike("%USB Flash Drives%"),
                Product.product_name.ilike("%hard drive%"),
                Product.product_name.ilike("%external hard drive%"),
                Product.product_name.ilike("%SSD%"),
                Product.product_name.ilike("%flash drive%"),
                Product.product_name.ilike("%thumb drive%"),
                Product.product_name.ilike("%microSD%"),
                Product.product_name.ilike("%memory card%"),
                Product.product_name.ilike("%portable hard drive%"),
                Product.product_name.ilike("%NVMe%"),
            )
            is_non_storage = or_(
                Product.product_name.ilike("%laptop%"),
                Product.product_name.ilike("%notebook%"),
                Product.product_name.ilike("%player%"),
                Product.product_name.ilike("%mini pc%"),
                Product.product_name.ilike("%desktop pc%"),
                Product.product_name.ilike("%case%"),
                Product.product_name.ilike("%enclosure%"),
                Product.product_name.ilike("%caddy%"),
                Product.product_name.ilike("%cable%"),
                Product.product_name.ilike("%bag%"),
                Product.product_name.ilike("%dock%"),
                Product.product_name.ilike("%adapter%"),
                Product.product_name.ilike("%holder%"),
                Product.product_name.ilike("%wallet%"),
            )
            return stmt.where(is_storage_name, ~is_non_storage)
        elif cat_lower in ["home audio & speakers", "home audio & theater", "speakers", "speaker", "audio", "home theater"]:
            is_audio_name = or_(
                Product.main_category == "Home Audio & Theater",
                Product.categories_hierarchy.ilike("%Home Audio%"),
                Product.categories_hierarchy.ilike("%Speakers%"),
                Product.product_name.ilike("%speaker%"),
                Product.product_name.ilike("%soundbar%"),
                Product.product_name.ilike("%subwoofer%"),
                Product.product_name.ilike("%home theater%"),
            )
            is_non_audio = or_(
                Product.product_name.ilike("%headphone%"),
                Product.product_name.ilike("%earbud%"),
                Product.product_name.ilike("%earphone%"),
                Product.product_name.ilike("%cable%"),
                Product.product_name.ilike("%wall mount%"),
                Product.product_name.ilike("%bracket%"),
                Product.product_name.ilike("%stand%"),
                Product.product_name.ilike("%cover%"),
                Product.product_name.ilike("%strap%"),
            )
            return stmt.where(is_audio_name, ~is_non_audio)
        elif cat_lower in ["smart home & devices", "amazon devices", "smart home", "streaming devices", "smart devices"]:
            is_smarthome_name = or_(
                Product.main_category == "Amazon Devices",
                Product.categories_hierarchy.ilike("%Amazon Devices%"),
                Product.product_name.ilike("%echo dot%"),
                Product.product_name.ilike("%echo show%"),
                Product.product_name.ilike("%fire tv%"),
                Product.product_name.ilike("%kindle%"),
                Product.product_name.ilike("%fire tablet%"),
            )
            is_non_smarthome = or_(
                Product.product_name.ilike("%case%"),
                Product.product_name.ilike("%cover%"),
                Product.product_name.ilike("%remote cover%"),
                Product.product_name.ilike("%wall mount%"),
                Product.product_name.ilike("%stand%"),
            )
            return stmt.where(is_smarthome_name, ~is_non_smarthome)
        elif cat_lower in ["cables & power accessories", "cables & accessories", "cables", "cable", "chargers", "accessories"]:
            is_cables_name = or_(
                Product.product_name.ilike("%hdmi cable%"),
                Product.product_name.ilike("%usb-c cable%"),
                Product.product_name.ilike("%charging cable%"),
                Product.product_name.ilike("%power adapter%"),
                Product.product_name.ilike("%surge protector%"),
                Product.product_name.ilike("%power strip%"),
                Product.product_name.ilike("%extension cord%"),
                Product.product_name.ilike("%usb hub%"),
                Product.product_name.ilike("%ethernet cable%"),
                Product.product_name.ilike("%lightning cable%"),
                Product.product_name.ilike("%audio cable%"),
                Product.product_name.ilike("%aux cable%"),
            )
            is_non_cables = or_(
                Product.product_name.ilike("%laptop%"),
                Product.product_name.ilike("%smartphone%"),
                Product.product_name.ilike("%headphone%"),
            )
            return stmt.where(is_cables_name, ~is_non_cables)
        else:
            return stmt.where(func.lower(Product.main_category) == cat_lower)

    CATEGORY_PATTERNS = [
        (
            "Laptops & Notebooks",
            [
                r"\blaptops?\b",
                r"\bnotebooks?\b",
                r"\bchromebooks?\b",
                r"\bmacbooks?\b",
                r"\bultrabooks?\b",
            ],
            {"macbook", "macbooks", "chromebook", "chromebooks", "thinkpad", "ideapad", "inspiron", "aspire", "pavilion", "zenbook", "latitude", "xps", "surface pro"},
        ),
        (
            "Smartphones & Mobiles",
            [
                r"\bsmartphones?\b",
                r"\bmobiles?\b",
                r"\bcell\s*phones?\b",
                r"\bphones?\b",
            ],
            {"iphone", "iphones", "galaxy", "pixel", "oneplus", "motorola edge", "moto g"},
        ),
        (
            "Headphones & Earbuds",
            [
                r"\bheadphones?\b",
                r"\bearbuds?\b",
                r"\bearphones?\b",
                r"\bheadsets?\b",
                r"\bear\s*buds?\b",
                r"\bear\s*phones?\b",
            ],
            {"airpods", "galaxy buds", "wh-1000xm4", "wh-1000xm5"},
        ),
        (
            "Cameras & Photography",
            [
                r"\bcameras?\b",
                r"\bcamcorders?\b",
                r"\bdslrs?\b",
                r"\bwebcams?\b",
                r"\bphotography\b",
            ],
            {"gopro", "powershot", "eos", "rebel", "cyber-shot", "lumix"},
        ),
        (
            "Hard Disks & Storage",
            [
                r"\bhard\s*disks?\b",
                r"\bhard\s*drives?\b",
                r"\bssds?\b",
                r"\bflash\s*drives?\b",
                r"\bthumb\s*drives?\b",
                r"\bmemory\s*cards?\b",
                r"\bmicrosd\b",
                r"\bexternal\s*storage\b",
            ],
            {"evo", "sandisk extreme", "passport", "elements", "barracuda"},
        ),
        (
            "Home Audio & Speakers",
            [
                r"\bspeakers?\b",
                r"\bsoundbars?\b",
                r"\bsubwoofers?\b",
                r"\bhome\s*audio\b",
                r"\bhome\s*theater\b",
                r"\bbluetooth\s*speakers?\b",
            ],
            {"soundlink", "flip", "charge", "boombox"},
        ),
        (
            "Smart Home & Devices",
            [
                r"\bsmart\s*homes?\b",
                r"\bamazon\s*devices?\b",
                r"\becho\b",
                r"\bfire\s*tv\b",
                r"\bkindles?\b",
            ],
            {"echo dot", "echo show", "fire stick", "paperwhite"},
        ),
        (
            "Cables & Power Accessories",
            [
                r"\bcables?\b",
                r"\bhdmi\b",
                r"\bchargers?\b",
                r"\bpower\s*adapters?\b",
                r"\bpower\s*strips?\b",
                r"\bextension\s*cords?\b",
                r"\busb\s*hubs?\b",
            ],
            set(),
        ),
    ]

    @classmethod
    def _resolve_smart_category(cls, query: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Intelligently resolves whether a search query refers to a specific product category
        and extracts any remaining specific brand/model keywords.
        Returns (detected_category, remaining_query).
        """
        if not query or not query.strip():
            return None, None

        q_clean = query.strip()
        q_lower = q_clean.lower()

        for cat_name, patterns, retain_keywords in cls.CATEGORY_PATTERNS:
            for pat in patterns:
                match = re.search(pat, q_lower)
                if match:
                    # Check if query contains retain keywords (e.g. "MacBook", "iPhone", "Kindle")
                    # If it's a specific model name, we keep the query as search term while enforcing category
                    if any(kw in q_lower for kw in retain_keywords):
                        return cat_name, q_clean

                    # Strip the generic category word (e.g., "laptop", "phones", "headphones")
                    rem = re.sub(pat, "", q_clean, flags=re.IGNORECASE).strip()
                    rem = re.sub(r"\s+", " ", rem).strip()
                    return cat_name, rem if rem else None

        return None, q_clean

    @classmethod
    def get_canonical_brand(cls, product_name: Optional[str], raw_brand: Optional[str]) -> str:
        """Derive genuine brand from product title and manufacturer metadata."""
        name_lower = (product_name or "").lower()
        brand_lower = (raw_brand or "").strip().lower()

        # Apple (iPhones, MacBooks, iPads, AirPods)
        if any(w in name_lower for w in ["iphone", "ipad", "macbook", "airpods", "apple watch"]) or brand_lower == "apple" or name_lower.startswith("apple "):
            return "Apple"

        # Samsung
        if "galaxy " in name_lower or "samsung" in brand_lower or name_lower.startswith("samsung "):
            return "Samsung"

        # Google
        if ("pixel " in name_lower or "google" in brand_lower or name_lower.startswith("google ")) and "trackr" not in name_lower:
            return "Google"

        # Motorola
        if any(w in name_lower for w in ["moto g", "moto z", "moto e", "motorola edge"]) or "motorola" in brand_lower or name_lower.startswith("motorola "):
            return "Motorola"

        # OnePlus
        if "oneplus" in name_lower or "oneplus" in brand_lower:
            return "OnePlus"

        # Dell
        if any(w in name_lower for w in ["inspiron", "latitude", "vostro", "xps"]) or brand_lower == "dell" or name_lower.startswith("dell "):
            return "Dell"

        # HP
        if any(w in name_lower for w in ["pavilion", "probook", "elitebook", "spectre", "envy", "omen", "stream laptop"]) or brand_lower == "hp" or name_lower.startswith("hp "):
            return "HP"

        # Lenovo
        if any(w in name_lower for w in ["thinkpad", "ideapad", "legion"]) or brand_lower == "lenovo" or name_lower.startswith("lenovo "):
            return "Lenovo"

        # ASUS
        if any(w in name_lower for w in ["zenbook", "vivobook", "rog ", "tuf "]) or brand_lower == "asus" or name_lower.startswith("asus "):
            return "ASUS"

        # Acer
        if any(w in name_lower for w in ["aspire", "predator", "swift", "nitro"]) or brand_lower == "acer" or name_lower.startswith("acer "):
            return "Acer"

        # Sony
        if "wh-1000xm" in name_lower or "playstation" in name_lower or brand_lower == "sony" or name_lower.startswith("sony "):
            return "Sony"

        # Bose
        if "quietcomfort" in name_lower or brand_lower == "bose" or name_lower.startswith("bose "):
            return "Bose"

        # Beats
        if "powerbeats" in name_lower or "beats solo" in name_lower or "beats studio" in name_lower or brand_lower == "beats" or name_lower.startswith("beats "):
            return "Beats"

        # JBL
        if brand_lower == "jbl" or name_lower.startswith("jbl "):
            return "JBL"

        # SanDisk
        if "sandisk" in brand_lower or "sandisk" in name_lower:
            return "SanDisk"

        # Western Digital
        if "western digital" in brand_lower or "wd " in name_lower or "wd_" in name_lower or brand_lower == "wd":
            return "Western Digital"

        # Crucial
        if "crucial" in brand_lower or "crucial" in name_lower:
            return "Crucial"

        # Seagate
        if "seagate" in brand_lower or "seagate" in name_lower:
            return "Seagate"

        # Kingston
        if "kingston" in brand_lower or "kingston" in name_lower:
            return "Kingston"

        # Canon
        if brand_lower == "canon" or name_lower.startswith("canon "):
            return "Canon"

        # Nikon
        if brand_lower == "nikon" or name_lower.startswith("nikon "):
            return "Nikon"

        # BLU
        if brand_lower == "blu" or name_lower.startswith("blu ") or " blu " in name_lower:
            return "BLU"

        # Xiaomi
        if "xiaomi" in brand_lower or "redmi" in name_lower or "xiaomi" in name_lower or "poco" in name_lower:
            return "Xiaomi"

        # LG
        if brand_lower == "lg" or name_lower.startswith("lg ") or " lg " in name_lower:
            return "LG"

        # MSI
        if brand_lower == "msi" or name_lower.startswith("msi "):
            return "MSI"

        # Toshiba
        if brand_lower == "toshiba" or name_lower.startswith("toshiba ") or "satellite" in name_lower:
            return "Toshiba"

        # Microsoft
        if "surface" in name_lower or brand_lower == "microsoft" or name_lower.startswith("microsoft "):
            return "Microsoft"

        # Gateway
        if brand_lower == "gateway" or name_lower.startswith("gateway "):
            return "Gateway"

        # Fallback to cleaned raw brand if present
        if raw_brand and raw_brand.strip():
            clean_b = raw_brand.strip()
            if clean_b.lower() not in ["amazon renewed", "unknown"]:
                return clean_b

        return "Generic"

    @classmethod
    def get_canonical_brand(cls, product_name: Optional[str], raw_brand: Optional[str]) -> str:
        """Derive genuine brand from product title and manufacturer metadata."""
        name_lower = (product_name or "").lower()
        brand_lower = (raw_brand or "").strip().lower()

        # Apple (iPhones, MacBooks, iPads, AirPods)
        if any(w in name_lower for w in ["iphone", "ipad", "macbook", "airpods", "apple watch"]) or brand_lower == "apple" or name_lower.startswith("apple "):
            return "Apple"

        # Samsung
        if "galaxy " in name_lower or "samsung" in brand_lower or name_lower.startswith("samsung "):
            return "Samsung"

        # Google
        if ("pixel " in name_lower or "google" in brand_lower or name_lower.startswith("google ")) and "trackr" not in name_lower:
            return "Google"

        # Motorola
        if any(w in name_lower for w in ["moto g", "moto z", "moto e", "motorola edge"]) or "motorola" in brand_lower or name_lower.startswith("motorola "):
            return "Motorola"

        # OnePlus
        if "oneplus" in name_lower or "oneplus" in brand_lower:
            return "OnePlus"

        # Dell
        if any(w in name_lower for w in ["inspiron", "latitude", "vostro", "xps"]) or brand_lower == "dell" or name_lower.startswith("dell "):
            return "Dell"

        # HP
        if any(w in name_lower for w in ["pavilion", "probook", "elitebook", "spectre", "envy", "omen", "stream laptop"]) or brand_lower == "hp" or name_lower.startswith("hp "):
            return "HP"

        # Lenovo
        if any(w in name_lower for w in ["thinkpad", "ideapad", "legion"]) or brand_lower == "lenovo" or name_lower.startswith("lenovo "):
            return "Lenovo"

        # ASUS
        if any(w in name_lower for w in ["zenbook", "vivobook", "rog ", "tuf "]) or brand_lower == "asus" or name_lower.startswith("asus "):
            return "ASUS"

        # Acer
        if any(w in name_lower for w in ["aspire", "predator", "swift", "nitro"]) or brand_lower == "acer" or name_lower.startswith("acer "):
            return "Acer"

        # Sony
        if "wh-1000xm" in name_lower or "playstation" in name_lower or brand_lower == "sony" or name_lower.startswith("sony "):
            return "Sony"

        # Bose
        if "quietcomfort" in name_lower or brand_lower == "bose" or name_lower.startswith("bose "):
            return "Bose"

        # Beats
        if "powerbeats" in name_lower or "beats solo" in name_lower or "beats studio" in name_lower or brand_lower == "beats" or name_lower.startswith("beats "):
            return "Beats"

        # JBL
        if brand_lower == "jbl" or name_lower.startswith("jbl "):
            return "JBL"

        # SanDisk
        if "sandisk" in brand_lower or "sandisk" in name_lower:
            return "SanDisk"

        # Western Digital
        if "western digital" in brand_lower or "wd " in name_lower or "wd_" in name_lower or brand_lower == "wd":
            return "Western Digital"

        # Crucial
        if "crucial" in brand_lower or "crucial" in name_lower:
            return "Crucial"

        # Seagate
        if "seagate" in brand_lower or "seagate" in name_lower:
            return "Seagate"

        # Kingston
        if "kingston" in brand_lower or "kingston" in name_lower:
            return "Kingston"

        # Canon
        if brand_lower == "canon" or name_lower.startswith("canon "):
            return "Canon"

        # Nikon
        if brand_lower == "nikon" or name_lower.startswith("nikon "):
            return "Nikon"

        # BLU
        if brand_lower == "blu" or name_lower.startswith("blu ") or " blu " in name_lower:
            return "BLU"

        # Xiaomi
        if "xiaomi" in brand_lower or "redmi" in name_lower or "xiaomi" in name_lower or "poco" in name_lower:
            return "Xiaomi"

        # LG
        if brand_lower == "lg" or name_lower.startswith("lg ") or " lg " in name_lower:
            return "LG"

        # MSI
        if brand_lower == "msi" or name_lower.startswith("msi "):
            return "MSI"

        # Toshiba
        if brand_lower == "toshiba" or name_lower.startswith("toshiba ") or "satellite" in name_lower:
            return "Toshiba"

        # Microsoft
        if "surface" in name_lower or brand_lower == "microsoft" or name_lower.startswith("microsoft "):
            return "Microsoft"

        # Gateway
        if brand_lower == "gateway" or name_lower.startswith("gateway "):
            return "Gateway"

        # Fallback to cleaned raw brand if present
        if raw_brand and raw_brand.strip():
            clean_b = raw_brand.strip()
            if clean_b.lower() not in ["amazon renewed", "unknown"]:
                return clean_b

        return "Generic"

    @classmethod
    def _apply_brand_filter(cls, stmt, brand: str):
        b_clean = brand.strip().lower()
        if b_clean in ["amazon", "amazon basics"]:
            return stmt.where(func.lower(Product.brand) == b_clean)
        elif b_clean == "apple":
            return stmt.where(
                or_(
                    func.lower(Product.brand) == "apple",
                    Product.brand.ilike("%apple%"),
                    Product.product_name.ilike("Apple %"),
                    Product.product_name.ilike("% Apple %"),
                    Product.product_name.ilike("%iPhone%"),
                    Product.product_name.ilike("%MacBook%"),
                    Product.product_name.ilike("%iPad%"),
                )
            )
        elif b_clean == "samsung":
            return stmt.where(
                or_(
                    func.lower(Product.brand) == "samsung",
                    Product.brand.ilike("%samsung%"),
                    Product.product_name.ilike("Samsung %"),
                    Product.product_name.ilike("% Samsung %"),
                    Product.product_name.ilike("%Galaxy %"),
                )
            )
        elif b_clean in ["motorola", "moto"]:
            return stmt.where(
                or_(
                    func.lower(Product.brand) == "motorola",
                    Product.brand.ilike("%motorola%"),
                    Product.product_name.ilike("Motorola %"),
                    Product.product_name.ilike("% Motorola %"),
                    Product.product_name.ilike("%Moto %"),
                )
            )
        elif b_clean in ["google", "pixel"]:
            return stmt.where(
                or_(
                    func.lower(Product.brand) == "google",
                    Product.brand.ilike("%google%"),
                    Product.product_name.ilike("Google %"),
                    and_(
                        Product.product_name.ilike("%Pixel %"),
                        ~Product.product_name.ilike("%trackr%"),
                    ),
                )
            )
        elif b_clean == "hp":
            return stmt.where(
                or_(
                    func.lower(Product.brand) == "hp",
                    Product.brand.ilike("%hp%"),
                    Product.product_name.ilike("HP %"),
                    Product.product_name.ilike("% HP %"),
                )
            )
        elif b_clean == "microsoft":
            return stmt.where(
                or_(
                    func.lower(Product.brand) == "microsoft",
                    Product.brand.ilike("%microsoft%"),
                    Product.product_name.ilike("Microsoft %"),
                    Product.product_name.ilike("% Surface %"),
                    Product.product_name.ilike("Surface %"),
                )
            )
        elif b_clean == "blu":
            return stmt.where(
                or_(
                    func.lower(Product.brand) == "blu",
                    Product.brand.ilike("blu%"),
                    Product.brand.ilike("% blu"),
                    Product.product_name.ilike("BLU %"),
                    Product.product_name.ilike("% BLU %"),
                )
            )
        elif b_clean in ["lenovo", "dell", "asus", "acer", "sony", "bose", "msi", "toshiba", "gateway", "xiaomi", "sandisk", "kingston", "seagate", "crucial", "canon", "nikon", "fujifilm", "panasonic", "gopro", "jbl", "beats"]:
            return stmt.where(
                or_(
                    func.lower(Product.brand) == b_clean,
                    Product.brand.ilike(f"%{b_clean}%"),
                    Product.product_name.ilike(f"{b_clean} %"),
                    Product.product_name.ilike(f"% {b_clean} %"),
                )
            )
        else:
            return stmt.where(
                or_(
                    func.lower(Product.brand) == b_clean,
                    Product.brand.ilike(f"%{b_clean}%"),
                )
            )

    @classmethod
    def _apply_search_filter(cls, stmt, query: str):
        cleaned_query = query.strip()
        search_pattern = f"%{cleaned_query}%"
        return stmt.where(
            or_(
                Product.product_name.ilike(search_pattern),
                Product.brand.ilike(search_pattern),
            )
        )

    @classmethod
    def list_products(
        cls,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        sort_by: str = "rating_number",
        order: str = "desc",
        q: Optional[str] = None,
    ) -> ProductListResponse:
        """Fetch paginated, filtered, and sorted products with stored review counts."""
        # Subquery to aggregate review count per product in our database
        review_count_subq = (
            select(
                Review.product_id,
                func.count(Review.review_id).label("db_review_count"),
            )
            .group_by(Review.product_id)
            .subquery()
        )

        db_review_count_col = func.coalesce(review_count_subq.c.db_review_count, 0)

        # Base query
        stmt = (
            select(
                Product,
                db_review_count_col.label("db_review_count"),
            )
            .outerjoin(review_count_subq, Product.product_id == review_count_subq.c.product_id)
        )

        # Smart Category Resolution: Detect category intent when category not explicitly passed
        effective_category = category
        effective_q = q

        if not effective_category and effective_q and effective_q.strip():
            smart_cat, rem_q = cls._resolve_smart_category(effective_q)
            if smart_cat:
                effective_category = smart_cat
                effective_q = rem_q

        # Apply filters
        if brand and brand.strip():
            stmt = cls._apply_brand_filter(stmt, brand)
        if effective_category and effective_category.strip():
            stmt = cls._apply_category_filter(stmt, effective_category)
        if effective_q and effective_q.strip():
            stmt = cls._apply_search_filter(stmt, effective_q)
        if min_rating is not None:
            stmt = stmt.where(Product.average_rating >= min_rating)
        if max_rating is not None:
            stmt = stmt.where(Product.average_rating <= max_rating)

        # Count total matching records
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        # Sorting
        sort_column_map = {
            "rating": Product.average_rating,
            "rating_number": Product.rating_number,
            "price": Product.price,
            "name": Product.product_name,
            "review_count": db_review_count_col,
        }
        target_sort_col = sort_column_map.get(sort_by, Product.rating_number)

        # Null handling for sorting (e.g. products with null prices)
        if order.lower() == "asc":
            order_clause = asc(target_sort_col).nulls_last()
        else:
            order_clause = desc(target_sort_col).nulls_last()

        stmt = stmt.order_by(order_clause, asc(Product.product_id))

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        rows = db.execute(stmt).all()

        items = []
        for product_obj, db_rev_cnt in rows:
            raw_rating = float(product_obj.average_rating) if product_obj.average_rating is not None else 4.2
            honest_rat = round(max(2.5, min(4.4, raw_rating - 0.45)), 1)

            items.append(
                ProductListItem(
                    product_id=product_obj.product_id,
                    product_name=product_obj.product_name,
                    brand=cls.get_canonical_brand(product_obj.product_name, product_obj.brand),
                    main_category=product_obj.main_category,
                    price=float(product_obj.price) if product_obj.price is not None else None,
                    image_url=product_obj.image_url,
                    average_rating=float(product_obj.average_rating) if product_obj.average_rating is not None else None,
                    rating_number=product_obj.rating_number,
                    honest_rating=honest_rat,
                    flaw_tag=None,
                    db_review_count=int(db_rev_cnt),
                )
            )

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return ProductListResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=items,
        )

    @classmethod
    def search_products(
        cls,
        db: Session,
        query: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ProductListResponse:
        """Search products matching name or brand keywords, optionally scoped to a category/brand."""
        return cls.list_products(
            db=db,
            page=page,
            page_size=page_size,
            brand=brand,
            category=category,
            q=query,
            sort_by="rating_number",
            order="desc",
        )

    @classmethod
    def get_product_by_id(cls, db: Session, product_id: str) -> Optional[ProductDetail]:
        """Retrieve full product details along with stored review stats."""
        product_obj = db.get(Product, product_id)
        if not product_obj:
            return None

        # Aggregate reviews for this product
        rev_stats = db.execute(
            select(
                func.count(Review.review_id).label("rev_cnt"),
                func.avg(Review.star_rating).label("avg_rating"),
            ).where(Review.product_id == product_id)
        ).one()

        db_rev_count = rev_stats.rev_cnt or 0
        db_avg_rating = round(float(rev_stats.avg_rating), 2) if rev_stats.avg_rating is not None else None

        return ProductDetail(
            product_id=product_obj.product_id,
            product_name=product_obj.product_name,
            brand=cls.get_canonical_brand(product_obj.product_name, product_obj.brand),
            main_category=product_obj.main_category,
            categories_hierarchy=product_obj.categories_hierarchy,
            price=float(product_obj.price) if product_obj.price is not None else None,
            image_url=product_obj.image_url,
            average_rating=float(product_obj.average_rating) if product_obj.average_rating is not None else None,
            rating_number=product_obj.rating_number,
            db_review_count=db_rev_count,
            db_average_review_rating=db_avg_rating,
        )

    @staticmethod
    def get_product_statistics(db: Session, product_id: str) -> Optional[ProductStatistics]:
        """Compute rating breakdown, verified purchase ratio, and averages from stored reviews."""
        product_obj = db.get(Product, product_id)
        if not product_obj:
            return None

        # Overall review stats for product
        overall = db.execute(
            select(
                func.count(Review.review_id).label("total_revs"),
                func.avg(Review.star_rating).label("avg_rating"),
                func.min(Review.star_rating).label("min_rating"),
                func.max(Review.star_rating).label("max_rating"),
                func.count(case((Review.verified_purchase == True, 1))).label("verified_count"),
            ).where(Review.product_id == product_id)
        ).one()

        total_revs = overall.total_revs or 0
        avg_rating = round(float(overall.avg_rating), 2) if overall.avg_rating is not None else None
        min_rating = float(overall.min_rating) if overall.min_rating is not None else None
        max_rating = float(overall.max_rating) if overall.max_rating is not None else None
        verified_count = overall.verified_count or 0
        verified_pct = round((verified_count * 100.0) / total_revs, 2) if total_revs > 0 else 0.0

        # Star rating frequency distribution (5.0, 4.0, 3.0, 2.0, 1.0)
        dist_rows = db.execute(
            select(
                Review.star_rating,
                func.count(Review.review_id).label("star_count"),
            )
            .where(Review.product_id == product_id)
            .group_by(Review.star_rating)
            .order_by(desc(Review.star_rating))
        ).all()

        counts_dict = {float(row.star_rating): row.star_count for row in dist_rows}

        distribution_items = []
        for star in [5.0, 4.0, 3.0, 2.0, 1.0]:
            count = counts_dict.get(star, 0)
            pct = round((count * 100.0) / total_revs, 2) if total_revs > 0 else 0.0
            distribution_items.append(
                RatingDistributionItem(
                    star_rating=star,
                    count=count,
                    percentage=pct,
                )
            )

        return ProductStatistics(
            product_id=product_obj.product_id,
            product_name=product_obj.product_name,
            total_reviews=total_revs,
            average_review_rating=avg_rating,
            min_rating=min_rating,
            max_rating=max_rating,
            verified_purchases_count=verified_count,
            verified_purchases_percentage=verified_pct,
            star_distribution=distribution_items,
        )

