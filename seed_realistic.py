import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import random

SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"


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

# Each entry: (station_name, line_str, address, truck_name, review)
POSTS = [
    (
        "Grand Central - 42nd St",
        "4-5-6-6 Express",
        "89 E 42nd St, New York, NY 10017",
        "Wafels & Dinges",
        "Stumbled onto Wafels & Dinges parked right on Vanderbilt Ave between 42nd and 43rd. Got the Brussels wafel with cookie butter and speculoos crumble — honestly one of the best $9 I've ever spent. The wafel was perfectly crispy outside, soft inside, and the topping combo was insane. Lines move fast even at lunch rush. Highly recommend if you're commuting through Grand Central.",
    ),
    (
        "Times Sq - 42nd St",
        "N-Q-R-W",
        "236 W 42nd St, New York, NY 10036",
        "Mexicue",
        "Mexicue's truck was parked on 42nd between 7th and 8th. Had the brisket taco with chipotle BBQ sauce and pickled jalapeños — the fusion is real and it works. Portion size is generous for NYC prices. The truck was super clean and the staff was friendly even with the Times Square tourist chaos around them. Perfect quick lunch before hopping back on the N.",
    ),
    (
        "Union Sq - 14th St",
        "4-5-6-6 Express",
        "1 Union Square W, New York, NY 10003",
        "Cinnamon Snail",
        "Cinnamon Snail is parked on the north side of Union Square and it is worth every minute of the wait. I got the maple glazed donut and the smoked apple BBQ seitan sandwich — vegan and absolutely incredible. Don't let the plant-based label fool you, this is some of the most satisfying food I've had from a truck. Regulars here for a reason. Cash and card both accepted.",
    ),
    (
        "59th St - Columbus Circle",
        "1-2",
        "10 Columbus Circle, New York, NY 10019",
        "Patacon Pisao",
        "Found Patacon Pisao tucked on Broadway just south of Columbus Circle. Ordered the patacon sandwich stuffed with shredded chicken, avocado, and black beans — the fried plantain bun makes the whole thing work in a way regular bread never could. Super filling for under $12. The truck shows up around 11am and sells out quickly, so plan accordingly if you're coming from the 1 or 2.",
    ),
    (
        "Herald Sq - 34th St",
        "N-Q-R-W",
        "1 Herald Sq, New York, NY 10001",
        "Nuchas Empanadas",
        "Nuchas has a truck right by the 34th St Herald Sq entrance and it's my go-to when I have a layover at the station. The spinach and cheese empanada is perfectly flaky with a rich filling, and the spicy chicken one has just the right kick. Two empanadas and a lemonade for under $10 is a great deal in Midtown. Staff is fast, never a long wait even during peak hours.",
    ),
    (
        "34th St - Penn Station",
        "1-2-3",
        "371 7th Ave, New York, NY 10001",
        "Birria-Landia",
        "Birria-Landia has a truck on 31st St between 7th and 8th and it's a game changer near Penn. The birria tacos come with a rich consommé for dipping and the cheese is perfectly melted. Got 3 tacos and was completely full. The truck can get busy around 1pm but the line moves quick. Arrive early if you want them still crispy. One of the best birria spots in the city, truck or restaurant.",
    ),
    (
        "Wall St",
        "4-5",
        "23 Wall St, New York, NY 10005",
        "The Halal Guys",
        "The Halal Guys cart on Broadway and Wall is a financial district institution. The chicken and rice platter is exactly what you want at 12:30pm when you've been staring at spreadsheets all morning. White sauce and hot sauce combo is non-negotiable. Portions are massive — easily could share. Always a line but it wraps around fast. Cash only, so come prepared.",
    ),
    (
        "Jay St - MetroTech",
        "A-C-F",
        "333 Jay St, Brooklyn, NY 11201",
        "Gordo's Tacos",
        "Gordo's Tacos parks near Jay St and Willoughby, right by the MetroTech Commons. Their al pastor tacos have a proper char on the meat and the pineapple topping balances it perfectly. Three tacos for $12 is fair for the quality. Great spot for a lunch break if you work in the area. The truck is usually there Monday through Friday and occasionally Saturdays. Definitely worth the detour.",
    ),
    (
        "Borough Hall",
        "4-5",
        "209 Joralemon St, Brooklyn, NY 11201",
        "Red Hook Lobster Pound",
        "Red Hook Lobster Pound had their truck parked on Court St near Borough Hall on a Friday afternoon. Got the Maine-style lobster roll — cold, with just a touch of mayo, on a toasted split-top bun. It's expensive at $20+ but the quality is undeniable. Fresh lobster, generous filling, bread is always perfectly toasted. Worth the splurge on a nice day when you can eat outside on the steps.",
    ),
    (
        "Canal St",
        "4-6-6 Express",
        "277 Canal St, New York, NY 10013",
        "NY Dosas",
        "NY Dosas is a legendary cart at the entrance to Canal St and it did not disappoint. The masala dosa was massive — crispy crepe stuffed with perfectly spiced potato and served with coconut chutney and sambar. All for $9. The vendor is incredibly fast even when the line is long. This is authentic South Indian street food at its best. Go before 2pm, they run out.",
    ),
    (
        "Spring St",
        "A-C-E",
        "508 6th Ave, New York, NY 10011",
        "Van Leeuwen Ice Cream",
        "Van Leeuwen had their bright yellow truck on 6th Ave near Spring St on a warm afternoon. Got the honeycomb ice cream in a waffle cone — the ice cream is dense and rich without being overly sweet. Also tried a scoop of their earl grey flavor and it's genuinely unique. Not the cheapest soft serve in the city but the quality is real artisan-level. Great post-lunch treat before jumping back on the A/C/E.",
    ),
    (
        "Chambers St",
        "A-C",
        "111 Church St, New York, NY 10007",
        "Jamaican Dutchy",
        "Jamaican Dutchy parks on Chambers near Church St and the jerk chicken is fragrant from half a block away. The chicken is smoky, tender, and comes with rice and peas and a side of plantains. Full plate is $14 and very filling. The oxtail stew they had as a special that day was worth every penny extra. Authentic Jamaican flavors, not watered down for a non-Jamaican crowd. Will definitely be back.",
    ),
    (
        "Houston St",
        "1-2",
        "Houston St & Varick St, New York, NY 10013",
        "Calexico",
        "Calexico's truck is usually on Varick near Houston and the California-Mexican food hits differently. Had the carne asada burrito — well-seasoned meat, proper guacamole, and rice and beans that weren't afterthoughts. The truck is run efficiently and the staff clearly takes pride in what they serve. Great value for the area. Pairs well with a walk across to the Hudson River Park after.",
    ),
    (
        "Christopher St - Sheridan Sq",
        "1-2",
        "1 Sheridan Square, New York, NY 10014",
        "Frites 'N' Meats",
        "Frites 'N' Meats was parked on 7th Ave South near Sheridan Square and the burgers are genuinely excellent truck fare. Went with the house burger — smash-style patty, american cheese, pickles, special sauce on a brioche bun. The fries are thick-cut and come well-salted. Everything was hot and fresh. The staff is chatty and fun. Waited about 8 minutes at noon which is totally reasonable for this quality.",
    ),
    (
        "Bleecker St",
        "4-6-6 Express",
        "274 Bleecker St, New York, NY 10014",
        "Tacos El Bronco",
        "Tacos El Bronco has a truck that sometimes rolls through Bleecker St on weekends and the suadero tacos are the reason to track them down. Slow-cooked beef, double corn tortilla, onion, cilantro — simple and perfect. They also have the freshest agua fresca I've had in the city. Cash only, but there's a bodega with an ATM nearby. Follow their Instagram to know when they're in this neighborhood.",
    ),
    (
        "Astor Pl",
        "4-6-6 Express",
        "432 Lafayette St, New York, NY 10003",
        "Kogi NYC",
        "Kogi NYC — the Korean BBQ taco truck — was on Lafayette near Astor and the hype is completely warranted. Tried the short rib taco and the spicy pork taco. Both had incredible depth of flavor from the Korean marinade with the taco format working seamlessly. The kimchi slaw on top adds crunch and brightness. Line was long but the truck has a solid system going. Follow them on social to catch their location.",
    ),
    (
        "23rd St",
        "4-6-6 Express",
        "235 Park Ave S, New York, NY 10003",
        "Mani in Pasta",
        "Mani in Pasta parks near 23rd and Park Ave S and serves proper Italian street food from a tiny but busy truck. Had the truffle mac and cheese and a supplì (fried risotto ball with mozzarella center). Both were genuinely delicious — the pasta was al dente and the truffle not overpowering. For NYC truck food this is a cut above. Gets crowded fast at lunch so arrive before 12:30.",
    ),
    (
        "28th St",
        "N-Q-R-W",
        "28th St & Broadway, New York, NY 10001",
        "Eddie's Pizza Truck",
        "Eddie's Pizza Truck is parked on Broadway near 28th and the NY-style slices are legit. Grabbed two slices — plain cheese and the white with spinach — and both were properly crispy on the bottom with the right amount of char. The cheese-to-sauce ratio on the plain is perfect. $3.50 a slice is fair. Ate it right there standing on the sidewalk like a real New Yorker. Quick service, good vibe.",
    ),
    (
        "Lexington Ave - 59th St",
        "4-5-6-6 Express",
        "135 E 59th St, New York, NY 10022",
        "Adele's Louisiana Kitchen",
        "Adele's Louisiana Kitchen had their truck on 59th near Lex and the shrimp po'boy was outstanding. Perfectly fried shrimp, dressed with lettuce, tomato, pickles and remoulade on a proper French roll. Also tried the red beans and rice as a side — well-seasoned with andouille sausage running through it. Portions are big, prices are reasonable for this neighborhood. Brought me right back to New Orleans. Highly recommend.",
    ),
    (
        "86th St",
        "1-2",
        "201 W 86th St, New York, NY 10024",
        "Desi Truck NYC",
        "Desi Truck NYC rolls up near 86th and Broadway and the butter chicken wrap is comfort food perfection. Tender chicken in a rich, not-too-spicy sauce wrapped in a warm paratha with pickled onions and mint chutney. The samosa they had as a side was crisp and well-spiced too. Really solid South Asian street food in the Upper West Side where options can be limited. $11 for the wrap is fair. Don't skip the mango lassi.",
    ),
    (
        "125th St",
        "2-3",
        "2880 Broadway, New York, NY 10025",
        "Seasoned Vegan",
        "Seasoned Vegan has a presence near 125th and Broadway and the jerk 'chicken' (jackfruit) wrap converted me into believing plant-based food can be genuinely satisfying. The seasoning is bold, the texture of the jackfruit is spot on, and the wrap holds together well. Also tried the mac and 'cheese' with cashew cream — surprisingly rich and tasty. Harlem needs more options like this. The staff is passionate about the food and it shows.",
    ),
    (
        "Bedford Ave",
        "L",
        "136 Bedford Ave, Brooklyn, NY 11211",
        "Wooly's Ice",
        "Wooly's Ice cream truck is a staple on Bedford Ave in Williamsburg and they do seasonal flavors that are genuinely creative. Had the black sesame soft serve with mochi pieces — the nuttiness of the sesame was beautifully balanced and the mochi added great chew. Also tried their matcha and it's properly bitter, not the sweet imitation you get elsewhere. Perfect treat after the farmers market on Saturday. Worth the line.",
    ),
    (
        "Atlantic Av - Barclay's Center",
        "2-3-4-5",
        "620 Atlantic Ave, Brooklyn, NY 11217",
        "Kimchi Taco Truck",
        "Kimchi Taco Truck is right near Barclays on Flatbush Ave and gets busy before and after events. The spicy pork kimchi taco is their best — funky from the kimchi, rich from the pork, and the corn tortilla holds up. Also had the tofu version and it works surprisingly well. Prices are fair at $4 per taco. Even with the event-night crowds the line moved in about 12 minutes. Good fuel before a Nets game.",
    ),
    (
        "DeKalb Ave",
        "B-D-N-Q-R",
        "395 Flatbush Ave Ext, Brooklyn, NY 11201",
        "Nuchas Empanadas",
        "There's a Nuchas cart near the DeKalb Ave station entrance that I hit every time I'm in the area. The beef picadillo empanada is their best in my opinion — savory, slightly sweet with raisins, and really flaky pastry. Three empanadas is a full meal for around $12. They also had a Nutella dessert empanada that was dangerous. Quick service, always fresh. Great when you're transferring between the B/D and N/Q/R lines.",
    ),
    (
        "Flushing - Main St",
        "7-7 Express",
        "41-31 Main St, Flushing, NY 11355",
        "Golden Mall Food Stalls Cart",
        "Right outside the 7 train in Flushing there's a cluster of street carts and this one specializing in hand-pulled noodles is incredible. The beef noodle soup features thick, chewy hand-pulled noodles in a deeply savory broth with tender braised beef. A full bowl is $10. The scallion pancakes they sell as a side are crispy and layered properly. This is some of the best Chinese street food in the five boroughs. Go hungry.",
    ),
    (
        "Astoria - Ditmars Blvd",
        "N-W",
        "31-15 Ditmars Blvd, Astoria, NY 11105",
        "Gyro Corner Cart",
        "There's a Greek gyro cart near the Ditmars Blvd terminal and it's exactly what you want after a long commute. The lamb and beef gyro is packed into a thick warm pita with tzatziki, tomato, and onion — classic and done right. The meat is properly seasoned and carved fresh off the spit. $8 for a full gyro is a steal in 2024. The guy running it has been there for years and knows his regulars by name. A true neighborhood spot.",
    ),
    (
        "Forest Hills - 71st Av",
        "E-F-M-R",
        "108-50 Queens Blvd, Forest Hills, NY 11375",
        "Lam Zhou Handmade Noodles Cart",
        "There's a small handmade noodle cart near the Forest Hills 71st Ave station that is worth finding. The dan dan noodles had a great balance of peanut, sesame, and chili with properly springy hand-pulled noodles. Also tried the soup dumplings (they somehow manage them from a cart) and they were juicy and delicate. Everything is made fresh so there can be a short wait but it's worth it. Cash only, bring small bills.",
    ),
    (
        "Flushing Ave",
        "G",
        "Flushing Ave & Clermont Ave, Brooklyn, NY 11205",
        "Patty King Jamaican Cart",
        "Patty King is a cart that sets up near the Flushing Ave G stop and the beef patties are the best I've found outside of Flatbush. The pastry is golden, flaky, and buttery, and the spiced beef filling is perfectly seasoned with scotch bonnet heat that builds slowly. Two patties for $5 is an incredible deal. They also sell coco bread and the combo is classic. A no-frills cart run by a no-nonsense crew who know what they're doing.",
    ),
    (
        "Myrtle-Willoughby Aves",
        "G",
        "Myrtle Ave & Willoughby Ave, Brooklyn, NY 11205",
        "Tacos Morales",
        "Tacos Morales is a family-run taco truck that parks near Myrtle and Willoughby on weekends. The barbacoa tacos are slow-cooked and fall apart in the best way. Cilantro, onion, salsa verde — no frills, just proper technique. Four tacos for $10 is the best deal on the G line. The horchata is house-made and ice cold. This is the kind of truck that locals fight to keep a secret. Definitely worth the trip out to Bed-Stuy.",
    ),
    (
        "Vernon Blvd - Jackson Ave",
        "7-7 Express",
        "46-01 Vernon Blvd, Long Island City, NY 11101",
        "LIC Arepas Cart",
        "LIC Arepas is a cart near the Vernon Blvd-Jackson Ave 7 train stop and it's a gem in the Long Island City food scene. The reina pepiada arepa — shredded chicken with avocado and mayo inside a grilled corn cake — is rich and satisfying. The pabellón arepa with black beans, shredded beef, and sweet plantains is equally excellent. Both around $9. The owner is from Venezuela and the authenticity shows in every bite. Cash preferred.",
    ),
]


def main():
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    posts_coll = db.collection("posts")

    now = datetime.utcnow()
    batch = db.batch()
    ops = 0
    total = 0

    for i, (station, line_str, address, truck_name, review) in enumerate(POSTS):
        user = USERS[i]
        line_group = pick_line_group(line_str)
        title = f"{truck_name} near {station}"
        date_value = now - timedelta(hours=random.randint(1, 72), minutes=random.randint(0, 59))

        doc_ref = posts_coll.document()
        batch.set(doc_ref, {
            "title": title,
            "date": date_value,
            "line": line_group,
            "station": station,
            "address": address,
            "postText": review,
            "imagesURL": [],
            "author": user,
        })
        ops += 1
        total += 1

        if ops >= 400:
            batch.commit()
            print(f"Committed batch. Total so far: {total}")
            batch = db.batch()
            ops = 0

    if ops > 0:
        batch.commit()

    print(f"Done. Seeded {total} posts from {total} unique fake users.")


if __name__ == "__main__":
    main()
