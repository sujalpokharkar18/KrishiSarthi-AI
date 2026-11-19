import pandas as pd
import random
import os
from sklearn.model_selection import train_test_split
import math

os.makedirs("data", exist_ok=True)

crops_en = ["wheat", "rice", "tomato", "cotton", "sugarcane", "potato", "onion", "maize", "soybean", "groundnut", "chilli", "brinjal", "millet", "grapes", "banana", "mango"]
crops_hi = ["gehu", "chawal", "tamatar", "kapas", "ganna", "aloo", "pyaz", "makka", "soyabean", "mungfali", "mirch", "baingan", "bajra", "angoor", "kela", "aam"]
all_crops = crops_en + crops_hi

seasons = ["summer", "winter", "monsoon", "kharif", "rabi", "zaid", "garmi", "sardi", "baarish"]
soils = ["sandy", "clay", "loamy", "black", "red", "alluvial", "chikni", "kali", "lal"]

intent_templates = {
    "CROP_DISEASE": [
        "what is wrong with my {crop}", "why is my {crop} dying", "disease in {crop}", "{crop} rog",
        "{crop} me bimari", "how to treat disease in {crop}", "what disease attacks {crop}",
        "how to cure {crop}", "leaves turning yellow in {crop}", "white spots on {crop}",
        "my {crop} looks sick", "fungus on {crop}", "{crop} ki bimari ka ilaj", "rog in {crop}",
        "what are common diseases of {crop}", "how to prevent {crop} diseases", "{crop} disease control",
        "why {crop} is not growing well", "{crop} me fungus", "black spots on {crop} leaves"
    ],
    "FERTILIZER_SUGGESTION": [
        "what fertilizer for {crop}", "fertilizer for {crop}", "{crop} ke liye fertilizer", 
        "which khad for {crop}", "best fertilizer to use for {crop}", "how much urea for {crop}",
        "DAP requirement for {crop}", "{crop} ko kitna khad chahiye", "organic fertilizer for {crop}",
        "NPK ratio for {crop}", "when to apply fertilizer to {crop}", "{crop} fertilizer schedule",
        "khad in {crop}", "which nutrient is best for {crop}", "top dressing in {crop}",
        "{crop} poshak tatva", "{crop} ki paidaish badhane ke liye konsi khad dale", "fertiliser {crop}"
    ],
    "IRRIGATION_GUIDE": [
        "how to irrigate {crop}", "how to water {crop}", "how much water for {crop}", "when to water {crop}", "{crop} me pani kab de",
        "irrigation for {crop}", "{crop} irrigation schedule", "sinchai for {crop}",
        "{crop} ki sinchai kaise kare", "does {crop} need a lot of water", "drip irrigation for {crop}",
        "sprinkler for {crop}", "water requirement of {crop}", "how many times to water {crop}",
        "is {crop} drought tolerant", "{crop} me sinchai", "paani for {crop}",
        "how often to irrigate {crop}", "best irrigation method for {crop}", "water stress in {crop}"
    ],
    "WEATHER_QUERY": [
        "weather forecast", "will it rain tomorrow", "barish kab hogi", "mausam kaisa hai",
        "today's weather", "is it going to rain", "temperature today", "rain prediction",
        "aaj ka mausam", "kal ka mausam", "weather update", "humidity level", "wind speed",
        "is it good weather for spraying", "frost risk today", "baarish prediction",
        "kya aaj barish aayegi", "sunshine duration", "weather over the next week", "climate right now"
    ],
    "SOIL_HEALTH": [
        "how to improve {soil} soil", "{soil} soil suitable crops", "what to grow in {soil} soil",
        "soil testing", "how to check soil ph", "mitti ki janch", "soil health card",
        "how to increase soil fertility", "mitti ko upjau kaise banaye", "soil preparation for farming",
        "{soil} mitti me kya ugaye", "benefits of soil testing", "ph level of soil",
        "organic matter in soil", "preventing soil erosion", "soil moisture", 
        "improving soil structure", "mitti ki quality", "zamin ki upjau shamta", "is my soil healthy"
    ],
    "STORAGE_GUIDE": [
        "how to store {crop}", "{crop} storage", "storing {crop}", "{crop} ko kaise store kare",
        "post harvest storage of {crop}", "how to keep {crop} fresh", "preventing pests in stored {crop}",
        "cold storage for {crop}", "{crop} bhandaran", "{crop} safe storage",
        "what is the shelf life of {crop}", "moisture content for storing {crop}",
        "protect {crop} from rats", "grain bins for {crop}", "gunny bags for {crop}",
        "{crop} storage temperature", "store {crop} long term", "bhandar grah",
        "{crop} sadasya kaise rakhe", "godaam me {crop} rakhaav"
    ],
    "SEED_GUIDE": [
        "which seed is best for {crop}", "{crop} seeds", "best variety of {crop}",
        "{crop} ke beej", "hybrid seeds for {crop}", "how many seeds per acre for {crop}",
        "seed rate of {crop}", "{crop} seed treatment", "beej upchar of {crop}",
        "where to buy {crop} seeds", "germination of {crop} seed", "high yielding variety of {crop}",
        "{crop} beej ki matra", "certified seeds of {crop}", "desi vs hybrid {crop}",
        "how to sow {crop} seeds", "{crop} seeds availability", "seed quality of {crop}",
        "how to select seeds for {crop}", "which brand seed for {crop}"
    ],
    "CROP_GROWTH_GUIDE": [
        "how to grow {crop}", "{crop} cultivation tips", "steps for growing {crop}",
        "{crop} ki kheti kaise kare", "how to cultivate {crop}", "farming of {crop}",
        "{crop} ugagane ka tarika", "guide to growing {crop}", "how to increase {crop} yield",
        "tips for better {crop} growth", "{crop} crop cycle", "{crop} ki kheti",
        "best practices for {crop} cultivation", "{crop} management", "how to plant {crop}",
        "growing {crop} in fields", "complete guide for {crop}", "{crop} production technology",
        "how long does {crop} take to grow", "stages of {crop} growth"
    ],
    "PEST_CONTROL": [
        "how to control pests in {crop}", "pest management for {crop}", "{crop} me kide kaise hataye",
        "insect attack on {crop} what to do", "{crop} pest control", "bugs in my {crop}",
        "which insecticide for {crop}", "caterpillar on {crop}", "aphids on {crop}",
        "how to get rid of insects in {crop}", "organic pest control for {crop}", "spray for {crop} pests",
        "{crop} me keet niyantran", "how to save {crop} from pests", "common pests of {crop}",
        "termites in {crop}", "whitefly on {crop}", "neem oil for {crop} pests",
        "pest attack on {crop}", "what is eating my {crop}"
    ],
    "PLANTING_SEASON": [
        "best season to plant {crop}", "when to sow {crop}", "{crop} ki buwai kab kare",
        "what month to plant {crop}", "planting time for {crop}", "{season} season crops",
        "can I grow {crop} in {season}", "sowing schedule for {crop}", "right time to plant {crop}",
        "{crop} planting calendar", "{crop} kab ugaye", "is it too late to plant {crop}",
        "when is the {season} for {crop}", "{crop} sowing date", "ideal time for {crop}",
        "month to start {crop}", "{crop} lagaane ka sahi samay", "{season} mela",
        "{crop} season in india", "should i plant {crop} now"
    ],
    "HARVEST_GUIDE": [
        "when to harvest {crop}", "how to know if {crop} is ready for harvest", "best time to pick {crop}",
        "{crop} ki katai kab kare", "harvesting {crop}", "signs {crop} is ready",
        "how to harvest {crop}", "{crop} harvest time", "maturity signs of {crop}",
        "{crop} yield per acre", "post harvest management of {crop}", "{crop} chunai",
        "at what stage to harvest {crop}", "is my {crop} ready", "harvesting machinery for {crop}",
        "days to harvest {crop}", "{crop} todne ka samay", "manual harvesting of {crop}",
        "how to cut {crop}", "harvest index of {crop}"
    ],
    "ORGANIC_FARMING": [
        "what is organic farming", "organic kheti kaise kare", "how to do natural farming",
        "benefits of organic agriculture", "zero budget natural farming", "how to make compost",
        "organic fertilizer preparation", "jeevamrutha kaise banaye", "organic certification",
        "is organic farming profitable", "natural pest control", "jaivik kheti",
        "organic farming vs conventional", "how to switch to organic", "organic manure",
        "vermicompost benefits", "how to start organic farming", "organic principles",
        "desi cow benefits in farming", "no chemical farming"
    ],
    "CROP_SELECTION": [
        "which crop is best for {soil} soil", "what to grow in {season} season", "best crop for my region",
        "konsi fasal ugaye", "profitable crops", "cash crops to grow", "short duration crops",
        "what crop gives maximum profit", "which crop requires less water", "crop rotation advice",
        "intercropping ideas", "what should I plant next", "alternative crops",
        "suggest a crop for {season}", "best crop for {soil} land", "high value crops",
        "commercial farming crops", "sabse jyada munafa konsi fasal me hai", "multi cropping",
        "crop planning"
    ],
    "MARKET_GUIDE": [
        "where to sell my {crop}", "current price of {crop}", "mandi me best rate kaise mile",
        "how to get best price for produce", "{crop} mandi bhav", "e-nam platform",
        "MSP of {crop}", "who will buy my {crop}", "how to export {crop}",
        "market trends for {crop}", "today {crop} price", "how to sell directly to consumers",
        "where is the nearest mandi", "bhav of {crop}", "{crop} ka rate",
        "agricultural marketing", "value addition for {crop}", "contract farming for {crop}",
        "FPO benefits", "selling crop online"
    ],
    "GENERAL_AGRICULTURE": [
        "tell me about farming", "agriculture tips", "kheti ke baare me bataiye",
        "general farming advice", "what is agriculture", "types of farming",
        "modern farming techniques", "agriculture news", "government schemes for farmers",
        "kisan credit card", "PM kisan yojana", "tractor subsidy", "how to start farming",
        "agriculture loan", "farming subsidies", "agri startup ideas", "smart farming",
        "precision agriculture", "future of farming", "krishi darshan", "how to get loan for farming"
    ],
    "UNKNOWN": [
        "hello", "xyz123", "what is the meaning of life", "tell me a joke", "random gibberish",
        "who is the president", "how to code in python", "what is machine learning",
        "good morning", "hi", "bye", "thank you", "asdfghjkl", "12345",
        "can you help me with my math homework", "what is the capital of india",
        "play a song", "movie review", "cricket score", "how to cook pasta",
        "who won the match", "what is the time", "where am i", "tell me a story",
        "do aliens exist", "how to fix a car", "best restaurants near me", "what is ai"
    ]
}

ANSWERS = {
    "CROP_DISEASE": "Crop diseases can be caused by fungi, bacteria, or viruses. Please provide a picture or describe the symptoms (like spots, wilting) for specific treatment advice.",
    "FERTILIZER_SUGGESTION": "The right fertilizer depends on the crop and soil testing. Generally, a balanced NPK ratio is needed. Consider a soil test for precise recommendations.",
    "IRRIGATION_GUIDE": "Irrigation depends on the crop, soil type, and weather. Use methods like drip irrigation to save water. Water your crops when the topsoil feels dry.",
    "WEATHER_QUERY": "I cannot provide real-time weather updates yet, but you can check local weather forecasts on weather apps or news channels to plan your farming activities.",
    "SOIL_HEALTH": "Healthy soil is crucial. Get your soil tested regularly. Add organic compost, maintain proper pH, and practice crop rotation to keep your soil healthy.",
    "STORAGE_GUIDE": "Proper storage prevents post-harvest losses. Dry the produce well, store in a cool, dry place, and protect from pests and rodents. Use hermetic bags if possible.",
    "SEED_GUIDE": "Always use certified and high-quality seeds. Choose varieties suitable for your region's climate and soil. Treat seeds before sowing to prevent diseases.",
    "CROP_GROWTH_GUIDE": "Good crop growth requires proper sunlight, soil prep, timely irrigation, and nutrient management. Follow a recommended crop calendar for best results.",
    "PEST_CONTROL": "Identify the pest first. Use Integrated Pest Management (IPM), including biological controls like neem oil, and only use chemical pesticides as a last resort.",
    "PLANTING_SEASON": "Planting at the right time ensures good yield. The ideal season depends on the crop (Kharif for monsoon, Rabi for winter). Check local agricultural guidelines.",
    "HARVEST_GUIDE": "Harvest when the crop reaches full maturity. Harvesting too early or too late can affect quality. Look for typical maturity signs like color change or grain hardness.",
    "ORGANIC_FARMING": "Organic farming relies on natural inputs like compost, manure, and bio-pesticides. It avoids synthetic chemicals, improving long-term soil and human health.",
    "CROP_SELECTION": "Choose crops based on your soil type, water availability, local climate, and market demand. Crop rotation can also help decide what to plant next.",
    "MARKET_GUIDE": "You can sell your produce at local mandis, directly to consumers, or via e-NAM. Always check current market prices (Mandi Bhav) before selling.",
    "GENERAL_AGRICULTURE": "Agriculture encompasses growing crops and raising livestock. It's best to combine modern techniques with traditional knowledge for sustainable farming.",
    "UNKNOWN": "I am an agriculture assistant. I can help you with crop diseases, fertilizers, farming tips, and other agriculture-related queries. Please ask me about farming!"
}

def expand_templates(templates):
    expanded = []
    for t in templates:
        if "{crop}" in t:
            for c in all_crops:
                expanded.append(t.replace("{crop}", c))
        elif "{season}" in t:
            for s in seasons:
                expanded.append(t.replace("{season}", s))
        elif "{soil}" in t:
            for s in soils:
                expanded.append(t.replace("{soil}", s))
        else:
            # We want to have enough diverse samples for items without placeholders too.
            # We will append the template itself multiple times so it can be sampled later
            for _ in range(50):
                expanded.append(t)
    return expanded

# Generate dataset
dataset = []
target_per_category = 1200

for intent, templates in intent_templates.items():
    expanded = expand_templates(templates)
    
    # Randomly sample to reach exactly target_per_category (if we have more, downsample. If less, upsample with replacement)
    sampled = random.choices(expanded, k=target_per_category)
    
    for q in sampled:
        # Occasionally add some random noise or spelling variations to make it more robust
        if random.random() < 0.1:
            q = q.replace(" a ", " ") # random deletion
        dataset.append({
            "question": q,
            "label": intent,
            "answer": ANSWERS[intent]
        })

df = pd.DataFrame(dataset)

# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Split 80/20
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])

# Save to csv
train_df.to_csv("data/train_expanded.csv", index=False)
test_df.to_csv("data/test_expanded.csv", index=False)

# Print summary
print("Dataset Generation Complete!")
print("-" * 30)
print(f"Total rows: {len(df)}")
print(f"Train size: {len(train_df)}")
print(f"Test size: {len(test_df)}")
print("\nRows per category:")
print(df['label'].value_counts())
