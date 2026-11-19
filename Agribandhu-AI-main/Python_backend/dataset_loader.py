# api/dataset_loader.py
"""
Dataset loader and parser for crop timetables and weather rules.
Cleans raw CSV task prefixes ('Day1:', etc.) and provides crop-specific rules.
"""

import pandas as pd
import os
import re

file_path = os.path.join(os.path.dirname(__file__), "data", "crop_timetable_dataset.csv")
crop_dataset = pd.read_csv(file_path)

# Normalize crop names alias mapping
CROP_ALIASES = {
    "gehu": "wheat",
    "chawal": "rice",
    "dhan": "rice",
    "paddy": "rice",
    "tamatar": "tomato",
    "tomatoes": "tomato",
    "aloo": "potato",
    "alu": "potato",
    "potatoes": "potato",
    "pyaz": "onion",
    "kanda": "onion",
    "onions": "onion",
    "mirch": "chilli",
    "mirchi": "chilli",
    "chillies": "chilli",
    "chilli pepper": "chilli",
    "chili": "chilli",
    "chilis": "chilli",
    "baingan": "brinjal",
    "brinjals": "brinjal",
    "eggplant": "brinjal",
    "eggplants": "brinjal",
    "aubergine": "brinjal",
    "makka": "maize",
    "makai": "maize",
    "corn": "maize",
    "sweetcorn": "maize",
    "soyabean": "soybean",
    "soybeans": "soybean",
    "soya": "soybean",
    "mungfali": "groundnut",
    "groundnuts": "groundnut",
    "peanut": "groundnut",
    "peanuts": "groundnut",
    "ganna": "sugarcane",
    "cane": "sugarcane",
    "sugar cane": "sugarcane",
    "kapas": "cotton"
}

# Rich crop-specific weather adjustments
CROP_WEATHER_RULES = {
    "wheat": {
        "hot": [
            "High temperature: Monitor soil moisture and irrigate in early morning to prevent terminal heat stress",
            "High temperature: Light irrigation in evening; avoid daytime fertilization",
            "High temperature: Check for moisture stress in root zone and mulch exposed soil"
        ],
        "rain": [
            "Rainy day: Ensure field drainage; suspend chemical spraying and irrigation",
            "Post-rain: Inspect for rust and root rot; do not allow standing water",
            "Rainy day: Delay nitrogen top-dressing until field drains"
        ],
        "cold": [
            "Cold spell: Frost risk warning — give light night irrigation to raise soil temperature",
            "Cold weather: Monitor for yellow rust symptoms on leaves",
            "Cold weather: Protect young tillers; postpone weedicide spraying"
        ]
    },
    "rice": {
        "hot": [
            "High temperature: Maintain 3-5 cm standing water to cool root zone",
            "Hot weather: Top dress urea only in late evening hours",
            "High temperature: Monitor water level twice daily to prevent drying"
        ],
        "rain": [
            "Rainy day: Drain excess water if submergence exceeds 7 cm",
            "Heavy rain: Check field bunds to prevent overflow and nutrient loss",
            "Post-rain: Check for bacterial leaf blight and blast symptoms"
        ],
        "cold": [
            "Cold weather: Maintain shallow water depth to preserve temperature",
            "Cold spell: Delay transplantation if seedlings are young",
            "Cold weather: Protect nursery with polythene covering at night"
        ]
    },
    "tomato": {
        "hot": [
            "High temperature: Water early morning; apply straw mulch to conserve moisture",
            "Hot day: Provide partial shade if possible; avoid chemical sprays above 32°C",
            "High temperature: Prevent blossom drop by maintaining consistent soil moisture"
        ],
        "rain": [
            "Rainy day: Delay transplanting/seeding; ensure rapid furrow drainage",
            "Post-rain: High fungal risk — spray copper oxychloride or systemic fungicide",
            "Rainy day: Avoid handling wet plants to prevent spreading bacterial wilt"
        ],
        "cold": [
            "Cold weather: Protect seedlings with mulch or plastic covers against frost",
            "Cold spell: Reduce watering frequency; cold wet soil induces damping off",
            "Cold weather: Delay pruning and fertilizer application"
        ]
    },
    "potato": {
        "hot": [
            "High temperature: Avoid midday irrigation to prevent tuber boiling",
            "Hot weather: Ensure ridges are well-covered with soil to shield tubers",
            "High temperature: Irrigate in cool night hours only"
        ],
        "rain": [
            "Rainy day: Ensure furrow drainage; waterlogged soil causes tuber rot",
            "Post-rain: High risk of late blight — prophylactic fungicide spray needed",
            "Rainy day: Postpone mounding and weeding tasks"
        ],
        "cold": [
            "Cold weather: Frost protection — give light irrigation before severe frost",
            "Cold spell: Earth up soil tightly around plant stems",
            "Cold weather: Check canopy for early frost damage"
        ]
    },
    "onion": {
        "hot": [
            "High temperature: Mulch beds lightly; water in cool evening hours",
            "Hot weather: Avoid over-fertilization to prevent bulb splitting",
            "High temperature: Keep soil consistently moist during bulb enlargement"
        ],
        "rain": [
            "Rainy day: Halt irrigation; ensure raised beds drain freely",
            "Post-rain: Spray Mancozeb for purple blotch disease prevention",
            "Rainy day: Never allow stagnant water near onion bulbs"
        ],
        "cold": [
            "Cold weather: Protect young seedlings from chilly winds",
            "Cold spell: Moderate watering; cold damp soil causes fungal neck rot",
            "Cold weather: Delay bulb harvesting until dry weather returns"
        ]
    },
    "chilli": {
        "hot": [
            "High temperature: Irrigate twice weekly; check for flower drop",
            "Hot weather: Mulch with organic matter; spray micronutrients in evening",
            "High temperature: Inspect for mites and thrips under leaves"
        ],
        "rain": [
            "Rainy day: High anthracnose and fruit rot risk — ensure full drainage",
            "Post-rain: Apply preventive fungicide spray on stems and fruits",
            "Rainy day: Suspend fertilizer application until soil dries"
        ],
        "cold": [
            "Cold weather: Growth slows below 18°C; reduce irrigation volume",
            "Cold spell: Protect nursery seedlings with temporary plastic cover",
            "Cold weather: Postpone transplanting until temperature stabilizes"
        ]
    },
    "cotton": {
        "hot": [
            "High temperature: Increase irrigation during square and boll formation",
            "Hot weather: Monitor for whitefly and jassid infestation",
            "High temperature: Avoid water stress to prevent boll shedding"
        ],
        "rain": [
            "Rainy day: Harmful during early seedling and boll opening stages",
            "Heavy rain: Clear drainage channels immediately",
            "Post-rain: Spray against boll rot if humidity remains high"
        ],
        "cold": [
            "Cold weather: Low temperatures delay boll maturation and opening",
            "Cold spell: Delay late-season picking until dew dries completely",
            "Cold weather: Terminate irrigation to encourage boll maturity"
        ]
    },
    "maize": {
        "hot": [
            "High temperature: Critical water need during silking/tasseling stage",
            "Hot weather: Irrigate immediately if leaves show morning rolling",
            "High temperature: Avoid drought stress during pollination"
        ],
        "rain": [
            "Rainy day: Suspend irrigation; waterlogging causes rapid lodging",
            "Heavy rain: Drain waterlogged rows within 24 hours",
            "Post-rain: Apply remaining nitrogen dose once soil is workable"
        ],
        "cold": [
            "Cold weather: Slows seed emergence and early vegetative growth",
            "Cold spell: Ensure seeds were sown at correct depth (3-5 cm)",
            "Cold weather: Delay intercultural operations until temperature rises"
        ]
    },
    "sugarcane": {
        "hot": [
            "High temperature: Increase irrigation frequency; water every 7-10 days",
            "Hot weather: Mulch cane trash in furrows to conserve soil moisture",
            "High temperature: Evening irrigation recommended to lower field temp"
        ],
        "rain": [
            "Rainy day: Beneficial during tillering; avoid prolonged waterlogging",
            "Heavy rain: Provide surface drainage in low-lying cane fields",
            "Post-rain: Earth up canes to prevent wind lodging"
        ],
        "cold": [
            "Cold weather: Low temp slows cane elongation and sugar accumulation",
            "Cold spell: Irrigate lightly to prevent frost injury in northern zones",
            "Cold weather: Delay harvesting if frost has affected leaves"
        ]
    },
    "soybean": {
        "hot": [
            "High temperature: Irrigate during flowering and pod filling stages",
            "Hot weather: Watch for pod shattering if harvest is near",
            "High temperature: Mulch soil to preserve moisture"
        ],
        "rain": [
            "Rainy day: High fungal risk — drain fields to prevent collar rot",
            "Post-rain: Spray fungicide if yellow mosaic or rust appears",
            "Rainy day: Delay pod harvest until foliage and pods dry"
        ],
        "cold": [
            "Cold weather: Protect seedlings; germination drops significantly below 15°C",
            "Cold spell: Reduce watering volume",
            "Cold weather: Postpone sowing until soil temperature is adequate"
        ]
    },
    "groundnut": {
        "hot": [
            "High temperature: Keep soil moist during peg penetration and pod development",
            "Hot weather: Mulch with crop residue; light frequent irrigation",
            "High temperature: Avoid gypsum application on dry soil"
        ],
        "rain": [
            "Rainy day: Excess water causes aflatoxin and pod rot; drain immediately",
            "Post-rain: Inspect for tikka disease; spray carbendazim if spots appear",
            "Rainy day: Never allow flood water to stagnate in pod zone"
        ],
        "cold": [
            "Cold weather: Germination and pegging severely affected below 20°C",
            "Cold spell: Delay sowing until warm weather sets in",
            "Cold weather: Protect young foliage from night frost"
        ]
    },
    "brinjal": {
        "hot": [
            "High temperature: Provide shade net for young plants; water twice weekly",
            "Hot weather: Inspect for shoot and fruit borer infestation",
            "High temperature: Apply balanced NPK with evening irrigation"
        ],
        "rain": [
            "Rainy day: High damping-off risk; raise planting beds",
            "Post-rain: Apply preventive copper fungicide spray",
            "Rainy day: Drain excess water promptly to avoid bacterial wilt"
        ],
        "cold": [
            "Cold weather: Growth slows down; reduce irrigation frequency",
            "Cold spell: Cover plants with plastic tunnels in frost-prone areas",
            "Cold weather: Postpone fertilizer top-dressing until weather warms"
        ]
    }
}


def clean_task_text(task: str) -> str:
    """Removes 'Day1:', 'Day 1 :', or 'Day10 -' prefixes from timetable tasks."""
    if not isinstance(task, str):
        return ""
    cleaned = re.sub(r"^Day\s*\d+\s*[:\-]\s*", "", task.strip(), flags=re.IGNORECASE)
    return cleaned.strip()


def parse_normal_timetable(value: str):
    """Convert 'Day1:Task|Day2:Task' into clean ['Task 1', 'Task 2'] list."""
    if isinstance(value, str):
        tasks = []
        for v in value.split("|"):
            cleaned = clean_task_text(v)
            if cleaned:
                tasks.append(cleaned)
        return tasks
    return []


def parse_weather_rules(rules: str):
    """
    Convert 'Rainy: x; Hot: y; Cold: z' into cleaned lists: rain, hot, cold
    """
    rain = []
    hot = []
    cold = []

    if isinstance(rules, str):
        rule_list = [r.strip() for r in rules.split(";")]
        for r in rule_list:
            lower = r.lower()
            cleaned = re.sub(r"^(rainy|rain|hot|cold)\s*[:\-]\s*", "", r.strip(), flags=re.IGNORECASE).strip()
            if not cleaned:
                continue

            if "rain" in lower:
                rain.append(cleaned)
            elif "hot" in lower:
                hot.append(cleaned)
            elif "cold" in lower:
                cold.append(cleaned)

    return rain, hot, cold


def normalize_crop_name(crop_name: str) -> str:
    """Normalize input crop name handling aliases and lowercase."""
    name = crop_name.strip().lower()
    return CROP_ALIASES.get(name, name)


def get_supported_crops() -> list:
    """Returns list of all supported canonical crop names."""
    return sorted(crop_dataset['crop'].str.lower().tolist())


def get_crop_rules(crop_name: str):
    """
    Returns rules dictionary for the specified crop:
    { 'normal': [...], 'rain': [...], 'hot': [...], 'cold': [...] }
    """
    canonical_crop = normalize_crop_name(crop_name)
    crop = crop_dataset[crop_dataset['crop'].str.lower() == canonical_crop]

    if crop.empty:
        c_title = canonical_crop.capitalize()
        return {
            "crop": c_title,
            "normal": [
                f"Seedbed preparation, soil aerating, and organic compost mixing for {c_title}",
                f"Sowing or transplanting {c_title} with basal fertilizer application",
                f"First scheduled irrigation check and seedling emergence inspection",
                f"Light weeding, soil loosening around root zone, and mulching",
                f"Bio-fertilizer booster or micronutrient foliar spray application",
                f"Pest and fungal scout: inspect underside of {c_title} leaves",
                f"Root zone moisture monitoring and secondary scheduled irrigation"
            ],
            "rain": [
                f"Rainy day: ensure field drainage channels are clear for {c_title}; suspend watering",
                f"Post-rain: inspect {c_title} for standing water, root rot, and fungal spots",
                f"High humidity after rain: delay pesticide spray until foliage dries"
            ],
            "hot": [
                f"High temperature: irrigate {c_title} during early morning or evening; mulch soil",
                f"Heat alert: monitor midday wilting and maintain uniform soil moisture for {c_title}",
                f"Hot weather: avoid midday foliar sprays to prevent chemical burn"
            ],
            "cold": [
                f"Cold weather: give light evening irrigation to protect {c_title} roots from frost",
                f"Chilly morning: inspect {c_title} for cold stress; delay foliar sprays until noon",
                f"Cold spell: protect young seedlings with temporary shelter or mulch"
            ]
        }

    row = crop.iloc[0].to_dict()

    normal_list = parse_normal_timetable(row.get("normal_timetable", ""))
    rain_list, hot_list, cold_list = parse_weather_rules(row.get("weather_rules", ""))

    # Enrich with specialized crop-specific weather rules if available
    specialized = CROP_WEATHER_RULES.get(canonical_crop, {})
    if specialized.get("hot"):
        hot_list = specialized["hot"]
    if specialized.get("rain"):
        rain_list = specialized["rain"]
    if specialized.get("cold"):
        cold_list = specialized["cold"]

    # Fallbacks if still empty
    if not rain_list:
        rain_list = [f"Rainy day: ensure field drainage and avoid fertilizer application for {canonical_crop}"]
    if not hot_list:
        hot_list = [f"Hot day: water {canonical_crop} early in the morning and monitor soil moisture"]
    if not cold_list:
        cold_list = [f"Cold weather: protect young {canonical_crop} plants and reduce excessive watering"]

    return {
        "crop": canonical_crop.capitalize(),
        "normal": normal_list,
        "rain": rain_list,
        "hot": hot_list,
        "cold": cold_list
    }
