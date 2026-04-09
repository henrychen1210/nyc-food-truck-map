import json
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, firestore


# Update this to the path of your downloaded Firebase service account key JSON.
# IMPORTANT: Do not commit the service account key to git.
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"

STATIONS_JSON_PATH = "src/json/Subway_Stations.json"

POSTS_PER_STATION = 1  # exactly 1 post per station per your request


VENDORS = [
    "Street Taco Co.",
    "Late-Night Noodles",
    "Coffee & Pastries",
]


def pick_line_group(line_str: str) -> str:
    """
    Your UI expects `line` to be one of:
    A, B, G, J, L, N, S, one, four, seven
    """
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

    # Fallback (should be rare)
    return "A"


def main() -> None:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    posts_coll = db.collection("posts")

    with open(STATIONS_JSON_PATH, "r") as f:
        stops = json.load(f)

    features = stops.get("features", [])
    unique_stations = sorted({feat["properties"]["name"] for feat in features})

    # Determine a compatible `line` category for each station, so
    # the Edit UI's station dropdown options match the stored `line`.
    station_to_line = {}
    for feat in features:
        props = feat.get("properties", {})
        name = props.get("name")
        if not name or name in station_to_line:
            continue
        station_to_line[name] = pick_line_group(props.get("line"))

    # Seed posts
    author = {"name": "Seeder Bot", "id": "seeder-bot"}

    now = datetime.utcnow()
    MAX_BATCH = 400  # stay under Firestore batch limits (<= 500)
    batch = db.batch()
    ops_in_batch = 0
    total_written = 0

    for station_idx, station in enumerate(unique_stations, start=1):
        line_group = station_to_line.get(station, "A")

        for k in range(1, 1 + POSTS_PER_STATION):
            # Deterministic-ish vendor choice so content is varied across stations.
            vendor = VENDORS[(station_idx - 1) % len(VENDORS)]

            # Unique-ish content: station + post index + vendor.
            title = f"{vendor} at {station}"
            post_text = (
                f"Unique seed post #{k} for {station} (vendor: {vendor}). "
                "A great stop for a quick bite during the commute."
            )

            # Firestore Timestamp-friendly value; Admin SDK converts datetime to Timestamp.
            date_value = now + timedelta(minutes=station_idx, seconds=k)

            doc_ref = posts_coll.document()  # one-time seed, random IDs are fine
            batch.set(
                doc_ref,
                {
                    "title": title,
                    "date": date_value,
                    "line": line_group,
                    "station": station,
                    "address": "Seeded address (edit me)",
                    "postText": post_text,
                    "imagesURL": [],
                    "author": author,
                },
            )
            ops_in_batch += 1
            total_written += 1

            if ops_in_batch >= MAX_BATCH:
                batch.commit()
                print(f"Committed batch. Total written so far: {total_written}")
                batch = db.batch()
                ops_in_batch = 0

    if ops_in_batch > 0:
        batch.commit()

    print(f"Done. Total posts written: {total_written}")


if __name__ == "__main__":
    main()

