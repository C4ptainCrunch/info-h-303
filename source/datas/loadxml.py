from bs4 import BeautifulSoup
from psycopg2 import connect, IntegrityError
import datetime

con = connect("dbname=horeca")
con.autocommit = True
cursor = con.cursor()

def createUser(username, admin=False):
    email = username + "@ulb.ac.be"
    password = username
    created = datetime.datetime.now()
    sql = """INSERT INTO "user" (username,email,password,created,is_admin) VALUES (%s,%s,%s,%s,%s) RETURNING id"""
    cursor.execute("""SELECT * FROM "user" WHERE username=%s""", [username])
    res = cursor.fetchone()
    if res:
        if admin:
            cursor.execute("""UPDATE "user" SET is_admin=%s WHERE id=%s""", [True, res[0]])
        return res[0]
    cursor.execute(sql,[username, email, password, created, admin])
    res = cursor.fetchone()[0]
    return res

def createLabel(label):
    sql = """INSERT INTO "label" (name) VALUES (%s) RETURNING id"""
    cursor.execute("""SELECT * FROM "label" WHERE name=%s""", [label])
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(sql,[label])
    res = cursor.fetchone()[0]
    return res

def tag(tags, etablissement_id):
    sql = """INSERT INTO "etablissement_label" (etablissement_id,user_id,label_id) VALUES (%s,%s,%s)"""
    for t in tags:
        label_id = createLabel(t["name"])
        for user in t.findAll("User"):
            user_id = createUser(user["nickname"])
            try:
                cursor.execute(sql, [etablissement_id, user_id, label_id])
            except IntegrityError as e:
                print("Erreur à l'ajout de label: ", e)

def comment(comments, etablissement_id):
    sql = """INSERT INTO "comment" (user_id,etablissement_id,date,score,text) VALUES (%s,%s,%s,%s,%s)"""
    for c in comments:
        user_id = createUser(c["nickname"])
        date = datetime.date(*map(int,reversed(c["date"].split('/'))))
        score = int(c["score"])
        text = c.get_text()
        cursor.execute(sql,[user_id, etablissement_id, date, score, text])

def createEtablissement(xmlEntity, type):
    name = xmlEntity.Informations.Name.get_text()
    phone = xmlEntity.Informations.Tel.get_text()
    url = xmlEntity.Informations.Site
    if url:
        url = url["link"]
    address = xmlEntity.Informations.Address
    address_street = address.Street.get_text()
    address_number = address.Num.get_text()
    address_zip = address.Zip.get_text()
    address_city = address.City.get_text()
    latitude = address.Latitude.get_text()
    longitude = address.Longitude.get_text()
    created = datetime.date(*map(int,reversed(xmlEntity["creationDate"].split('/'))))
    user_id = createUser(xmlEntity["nickname"], True)

    sql = """INSERT INTO "etablissement"
            (name, phone, url, address_street, address_number, address_zip, address_city, latitude, longitude,  created, user_id, type)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id"""
    cursor.execute(sql,[name, phone, url, address_street, address_number, address_zip, address_city, latitude, longitude, created, user_id, type])
    res = cursor.fetchone()[0]

    if xmlEntity.Comments:
        comment(xmlEntity.Comments.findAll("Comment"), res)
    if xmlEntity.Tags:
        tag(xmlEntity.Tags.findAll("Tag"), res)

    return res

def createCafe(cafe):
    etablissement_id = createEtablissement(cafe, "bar")
    smoker = cafe.Informations.Smoking is not None
    food = cafe.Informations.Snack is not None

    sql = """INSERT INTO "bar" (etablissement_id,smoker,food) VALUES (%s,%s,%s) RETURNING etablissement_id"""
    cursor.execute(sql, [etablissement_id, smoker, food])
    res = cursor.fetchone()[0]
    return res

def createRestaurant(resto):
    sql = """INSERT INTO "restaurant"
            (etablissement_id,price_range,max_seats,takeaway,delivery,openings)
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING etablissement_id"""
    etablissement_id = createEtablissement(resto, "restaurant")
    price_range = int(resto.Informations.PriceRange.get_text())
    max_seats = int(resto.Informations.Banquet["capacity"])
    takeaway = resto.TakeAway is not None
    delivery = resto.Delivery is not None
    openings = [True] * 14
    if resto.Informations.Closed:
        for close in resto.Informations.Closed.findAll("On"):
            am = False
            pm = False
            if close.get("hour") == "am":
                pm = True
            elif close.get("hour") == "pm":
                am = True
            day = int(close["day"])
            openings[2*day] = am
            openings[2*day + 1] = pm
    cursor.execute(sql, [etablissement_id, price_range, max_seats, takeaway, delivery, openings])
    res = cursor.fetchone()[0]
    return res

# Resto
f = open("Restaurants.xml", "r")
xml = f.read()
soup = BeautifulSoup(xml, "lxml-xml")
for resto in soup.findAll("Restaurant"):
    createRestaurant(resto)

# Bar
f = open("Cafes.xml", "r")
xml = f.read()
soup = BeautifulSoup(xml, "lxml-xml")
for cafe in soup.findAll("Cafe"):
    createCafe(cafe)

con.commit()
con.close()
