"""
Seed one post per subway station (355 stations), rotating through 30 fake users.
Clears all existing posts first, then writes fresh data.
"""
import json
import random
import time
from datetime import datetime, timedelta, timezone

import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
STATIONS_JSON_PATH = "src/json/Subway_Stations.json"

# ── 30 fake users ────────────────────────────────────────────────────────────
USERS = [
    {"name": "Marcus Thompson",   "id": "user_001"},
    {"name": "Priya Patel",       "id": "user_002"},
    {"name": "Jordan Lee",        "id": "user_003"},
    {"name": "Sofia Reyes",       "id": "user_004"},
    {"name": "Daniel Park",       "id": "user_005"},
    {"name": "Amara Osei",        "id": "user_006"},
    {"name": "Tyler Brooks",      "id": "user_007"},
    {"name": "Mei-Lin Chen",      "id": "user_008"},
    {"name": "Isabella Russo",    "id": "user_009"},
    {"name": "Kwame Asante",      "id": "user_010"},
    {"name": "Rachel Goldstein",  "id": "user_011"},
    {"name": "Javier Morales",    "id": "user_012"},
    {"name": "Aisha Williams",    "id": "user_013"},
    {"name": "Ethan Nguyen",      "id": "user_014"},
    {"name": "Camille Dubois",    "id": "user_015"},
    {"name": "Omar Hassan",       "id": "user_016"},
    {"name": "Natalie Kim",       "id": "user_017"},
    {"name": "Carlos Mendoza",    "id": "user_018"},
    {"name": "Leah Shapiro",      "id": "user_019"},
    {"name": "Tariq Johnson",     "id": "user_020"},
    {"name": "Yuki Tanaka",       "id": "user_021"},
    {"name": "Brianna Scott",     "id": "user_022"},
    {"name": "Aleksei Volkov",    "id": "user_023"},
    {"name": "Fatima Al-Amin",    "id": "user_024"},
    {"name": "Noah Rodriguez",    "id": "user_025"},
    {"name": "Zoe Andersen",      "id": "user_026"},
    {"name": "DeShawn Harris",    "id": "user_027"},
    {"name": "Layla Mahmoud",     "id": "user_028"},
    {"name": "Ryan Fitzgerald",   "id": "user_029"},
    {"name": "Simone Tran",       "id": "user_030"},
]

# ── Food trucks / carts (pool to rotate through) ─────────────────────────────
TRUCKS = [
    "Wafels & Dinges",
    "The Halal Guys",
    "Birria-Landia",
    "Cinnamon Snail",
    "NY Dosas",
    "Mexicue",
    "Nuchas Empanadas",
    "Kogi NYC",
    "Frites 'N' Meats",
    "Patacon Pisao",
    "Eddie's Pizza Truck",
    "Van Leeuwen Ice Cream",
    "Gordo's Tacos",
    "Jamaican Dutchy",
    "Calexico",
    "Red Hook Lobster Pound",
    "Adele's Louisiana Kitchen",
    "Desi Truck NYC",
    "Kimchi Taco Truck",
    "Tacos Morales",
    "LIC Arepas Cart",
    "Gyro Corner Cart",
    "Patty King Jamaican Cart",
    "Mani in Pasta",
    "Seasoned Vegan",
    "Lam Zhou Noodle Cart",
    "Wooly's Ice Cream",
    "Tacos El Bronco",
    "Banh Mi Saigon Cart",
    "Empanada Guy",
    "Roti Roll",
    "Schnitzel & Things",
    "Aangan Indian Street Food",
    "Big Mozz",
    "Luke's Lobster Truck",
]

# ── Review sentence fragments to randomize ────────────────────────────────────
OPENERS = [
    "Finally tried {truck} near {station} and it did not disappoint.",
    "Spotted {truck} parked right by the {station} exit and had to stop.",
    "{truck} showed up near {station} this week and the line was worth it.",
    "Been meaning to try {truck} near {station} for months — finally did it.",
    "Caught {truck} on my commute through {station} and grabbed lunch.",
    "{truck} has been parking near {station} regularly and I'm not complaining.",
    "Quick lunch break from {station} led me to {truck} and I'm glad it did.",
    "Recommended {truck} near {station} by a coworker and they were absolutely right.",
]

FOOD_LINES = [
    "The food was fresh, hot, and way better than anything you'd expect from a street cart.",
    "Portions were generous and everything tasted made-to-order, not sitting under a lamp.",
    "The flavors were bold and well-balanced — clearly someone back there knows how to cook.",
    "Super fresh ingredients, nothing felt pre-packaged or reheated.",
    "Everything came out fast without feeling rushed — they clearly have the workflow dialed in.",
    "The seasoning was on point and each bite had real depth of flavor.",
    "Simple menu done really well — no gimmicks, just quality street food.",
    "Way more flavor than you'd expect for the price. Left completely satisfied.",
    "The cook clearly cares — every dish had a personal touch you can taste.",
    "Authentic flavors, not the watered-down version you get at tourist spots.",
]

PRICE_LINES = [
    "Lunch for under $12 in this city feels like a miracle — this truck delivers.",
    "Priced fairly for NYC, especially given the portion sizes.",
    "A little on the pricier side but the quality justifies every dollar.",
    "Great value — I walked away full and still had change from a $15 bill.",
    "Cash only so bring small bills, but the prices are very reasonable.",
    "Probably the best dollar-per-calorie ratio near this station.",
    "Not the cheapest option in the area but absolutely worth the premium.",
    "Solid value — two items and a drink came to about $14.",
]

CLOSERS = [
    "Will definitely be back next time I'm passing through {station}.",
    "Already told three people at my office to check it out. Highly recommend.",
    "One of the best quick lunches I've had near any subway stop in the city.",
    "If you commute through {station}, do yourself a favor and find this truck.",
    "Goes on my short list of go-to spots near the {station} area.",
    "Can't believe it took me this long to try it. Don't make my mistake.",
    "A regular stop for me now whenever I come through {station}.",
    "Exactly what you want when you need a fast, satisfying meal on a commute day.",
]


def pick_line_group(line_str: str) -> str:
    l = (line_str or "").upper()
    if ("A" in l) or ("C" in l) or ("E" in l):
        return "A"
    if ("B" in l) or ("D" in l) or ("F" in l) or ("M" in l):
        return "B"
    if "G" in l:
        return "G"
    if ("J" in l) or ("Z" in l):
        return "J"
    if "L" in l:
        return "L"
    if ("N" in l) or ("Q" in l) or ("W" in l) or ("R" in l):
        return "N"
    if "S" in l:
        return "S"
    if ("1" in l) or ("2" in l) or ("3" in l):
        return "one"
    if ("4" in l) or ("5" in l) or ("6" in l):
        return "four"
    if "7" in l:
        return "seven"
    return "A"


# ── Borough guessing from coordinates ─────────────────────────────────────────
def guess_borough(lon: float, lat: float) -> str:
    # Very rough bounding boxes
    if lat > 40.796 and lon < -73.91:
        return "Bronx"
    if lon < -74.04:
        return "Staten Island"
    if lon > -73.88 and lat < 40.74:
        return "Queens"
    if lon < -73.94 and lat < 40.72:
        return "Brooklyn"
    return "New York"  # Manhattan


def borough_zip(borough: str) -> str:
    return {
        "Bronx": random.choice(["10451", "10452", "10453", "10456", "10458", "10460"]),
        "Brooklyn": random.choice(["11201", "11205", "11206", "11211", "11215", "11217", "11220", "11238"]),
        "Queens": random.choice(["11101", "11354", "11355", "11372", "11373", "11374", "11375"]),
        "Staten Island": random.choice(["10301", "10302", "10303"]),
        "New York": random.choice(["10001", "10002", "10003", "10007", "10010", "10013", "10014", "10023", "10027", "10036"]),
    }.get(borough, "10001")


def make_address(station_name: str, lon: float, lat: float) -> str:
    """Generate a plausible street address near the station."""
    borough = guess_borough(lon, lat)
    zip_code = borough_zip(borough)

    # Try to extract a street reference from the station name
    name = station_name
    # Remove parenthetical suffixes
    for sep in [" - ", " – "]:
        if sep in name:
            name = name.split(sep)[0]

    # Common cross-street patterns
    cross_streets = {
        "Manhattan": ["Broadway", "Park Ave", "Lexington Ave", "7th Ave", "8th Ave", "Madison Ave", "Amsterdam Ave"],
        "Brooklyn": ["Flatbush Ave", "Atlantic Ave", "Bedford Ave", "Court St", "4th Ave", "5th Ave"],
        "Queens": ["Queens Blvd", "Northern Blvd", "Jamaica Ave", "Hillside Ave", "Roosevelt Ave"],
        "Bronx": ["Grand Concourse", "Jerome Ave", "Fordham Rd", "Boston Rd"],
        "Staten Island": ["Victory Blvd", "Richmond Ave", "Forest Ave"],
    }

    if borough == "New York":
        cross = random.choice(cross_streets["Manhattan"])
    elif borough == "Brooklyn":
        cross = random.choice(cross_streets["Brooklyn"])
    elif borough == "Queens":
        cross = random.choice(cross_streets["Queens"])
    elif borough == "Bronx":
        cross = random.choice(cross_streets["Bronx"])
    else:
        cross = random.choice(cross_streets["Staten Island"])

    # If station name has a street number, use it
    import re
    # Match patterns like "125th St", "42nd St", "34th St"
    m = re.search(r"(\d+)(st|nd|rd|th)\s+St", station_name, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        return f"{station_name.split(' -')[0].strip()} & {cross}, {borough if borough != 'New York' else 'New York'}, NY {zip_code}"

    # Use a house number derived loosely from coordinates (just for variety)
    house_num = abs(int((lon * 1000) % 500)) + 100
    return f"{house_num} {name.split(' -')[0].strip()}, {borough if borough != 'New York' else 'New York'}, NY {zip_code}"


def make_review(truck: str, station: str) -> str:
    opener = random.choice(OPENERS).format(truck=truck, station=station)
    food = random.choice(FOOD_LINES)
    price = random.choice(PRICE_LINES)
    closer = random.choice(CLOSERS).format(station=station)
    return f"{opener} {food} {price} {closer}"


def commit_batch_with_retry(batch, retries=3, delay=10):
    for attempt in range(retries):
        try:
            batch.commit()
            return
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "Quota" in str(e):
                print(f"  Rate limited. Waiting {delay}s before retry {attempt + 1}/{retries}...")
                time.sleep(delay)
                delay *= 2
            else:
                raise
    raise RuntimeError("Failed to commit batch after retries.")


# Stations already seeded by seed_realistic.py — skip these to avoid duplicates
ALREADY_SEEDED = {
    "Grand Central - 42nd St", "Times Sq - 42nd St", "Union Sq - 14th St",
    "59th St - Columbus Circle", "Herald Sq - 34th St", "34th St - Penn Station",
    "Wall St", "Jay St - MetroTech", "Borough Hall", "Canal St", "Spring St",
    "Chambers St", "Houston St", "Christopher St - Sheridan Sq", "Bleecker St",
    "Astor Pl", "23rd St", "28th St", "Lexington Ave - 59th St", "86th St",
    "125th St", "Bedford Ave", "Atlantic Av - Barclay's Center", "DeKalb Ave",
    "Flushing - Main St", "Astoria - Ditmars Blvd", "Forest Hills - 71st Av",
    "Flushing Ave", "Myrtle-Willoughby Aves", "Vernon Blvd - Jackson Ave",
}


def main():
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    posts_coll = db.collection("posts")

    # ── Step 1: Load stations ─────────────────────────────────────────────────
    with open(STATIONS_JSON_PATH) as f:
        geo = json.load(f)

    # Deduplicate by name, keep first occurrence (for coordinates)
    seen = {}
    for feat in geo["features"]:
        name = feat["properties"]["name"]
        if name not in seen:
            seen[name] = feat

    all_stations = sorted(seen.values(), key=lambda f: f["properties"]["name"])

    # Skip stations that already have a post
    stations = [s for s in all_stations if s["properties"]["name"] not in ALREADY_SEEDED]
    print(f"Total unique stations: {len(all_stations)}")
    print(f"Already seeded: {len(ALREADY_SEEDED)}")
    print(f"Stations to seed now: {len(stations)}\n")

    # ── Step 2: Seed one post per remaining station ───────────────────────────
    now = datetime.now(timezone.utc)
    random.seed(42)

    batch = db.batch()
    ops = 0
    total = 0
    MAX_BATCH = 400

    for i, feat in enumerate(stations, start=len(ALREADY_SEEDED)):
        props = feat["properties"]
        station_name = props["name"]
        line_str = props.get("line", "")
        lon, lat = feat["geometry"]["coordinates"]

        user = USERS[i % len(USERS)]
        truck = TRUCKS[i % len(TRUCKS)]
        line_group = pick_line_group(line_str)
        address = make_address(station_name, lon, lat)
        review = make_review(truck, station_name)
        title = f"{truck} near {station_name}"
        date_value = now - timedelta(hours=random.randint(1, 168), minutes=random.randint(0, 59))

        doc_ref = posts_coll.document()
        batch.set(doc_ref, {
            "title": title,
            "date": date_value,
            "line": line_group,
            "station": station_name,
            "address": address,
            "postText": review,
            "imagesURL": [],
            "author": user,
        })
        ops += 1
        total += 1

        if ops >= MAX_BATCH:
            commit_batch_with_retry(batch)
            print(f"  Written {total} posts so far...")
            time.sleep(1)
            batch = db.batch()
            ops = 0

    if ops > 0:
        commit_batch_with_retry(batch)

    print(f"\nDone. Seeded {total} posts across {total} stations.")


if __name__ == "__main__":
    main()
