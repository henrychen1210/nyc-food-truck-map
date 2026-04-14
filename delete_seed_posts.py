import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"

def main() -> None:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    posts_coll = db.collection("posts")

    # Seed posts all have author.id == "seeder-bot"
    query = posts_coll.where("author.id", "==", "seeder-bot")
    docs = query.get()

    total = len(docs)
    print(f"Found {total} seed posts to delete.")

    MAX_BATCH = 400
    batch = db.batch()
    ops = 0
    deleted = 0

    for doc in docs:
        batch.delete(doc.reference)
        ops += 1
        deleted += 1
        if ops >= MAX_BATCH:
            batch.commit()
            print(f"Deleted {deleted} so far...")
            batch = db.batch()
            ops = 0

    if ops > 0:
        batch.commit()

    print(f"Done. Deleted {deleted} seed posts.")

if __name__ == "__main__":
    main()
