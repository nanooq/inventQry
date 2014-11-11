#!/usr/bin/env python
from flask import *
import sqlite3

class Storage:
    def __init__(self):
        self.data_file = "inventory.db"
        self.db_conn = sqlite3.connect(self.data_file, check_same_thread=False)
        cursor = self.db_conn.cursor()

        things_table = """CREATE TABLE IF NOT EXISTS things (
                              id         INTEGER       PRIMARY KEY AUTOINCREMENT,
                              name       INTEGER       KEY NOT NULL,
                              owner      INTEGER       KEY NOT NULL,
                              contact    INTEGER       KEY NOT NULL,
                              usage_rule INTEGER       KEY NOT NULL,
                              url        VARCHAR(1024)
                          );"""
        persons_table = """CREATE TABLE IF NOT EXISTS persons (
                               id        INTEGER       PRIMARY KEY AUTOINCREMENT,
                               pseudonym VARCHAR(8192) NOT NULL,
                               email VARCHAR(8192) NOT NULL
                           );"""
        usage_rules_table = """CREATE TABLE IF NOT EXISTS usage_rules (
                                   id   INTEGER       PRIMARY KEY AUTOINCREMENT,
                                   rule VARCHAR(8192) NOT NULL
                               );"""
        cursor.execute(things_table)
        cursor.execute(persons_table)
        cursor.execute(usage_rules_table)

        cursor.close()

    def __del__(self): 
        self.db_conn.close()

    def write(self, query, values = None):
        cursor = self.db_conn.cursor()

        if values != None:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        self.db_conn.commit()

        return cursor

    def read(self, query, values = None):
        cursor = self.db_conn.cursor()

        if values != None:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        return cursor

app = Flask(__name__)
storage = Storage()

# get
def db_get_things():
    c = storage.read("SELECT * FROM things ORDER BY id DESC;")
    things = [dict(id=row[0], owner=row[1], contact=row[2], usage_rule=row[2], url=row[3]) for row in c.fetchall()]

    return things

def db_get_persons():
    c = storage.read("SELECT * FROM persons ORDER BY id DESC;")
    persons = [dict(id=row[0], pseudonym=row[1], email=row[2]) for row in c.fetchall()]

    return persons

def db_get_usage_rules():
    c = storage.read("SELECT * FROM usage_rules ORDER BY id DESC;")
    usage_rules = [dict(id=row[0], rule=row[1]) for row in c.fetchall()]

    return usage_rules

# get by id
def db_get_thing_by_id(id):
    c = storage.read("SELECT * FROM things WHERE id=?;", [id])
    things = [dict(id=row[0], name=row[1], owner=row[2], contact=row[3], usage_rule=row[4], url=row[5]) for row in c.fetchall()]

    return things[0] if len(things) > 0 else None

def db_get_person_by_id(id):
    c = storage.read("SELECT * FROM persons WHERE id=?;", [id])
    persons = [dict(id=row[0], pseudonym=row[1], email=row[2]) for row in c.fetchall()]

    return persons[0] if len(persons) > 0 else None

def db_get_usage_rule_by_id(id):
    c = storage.read("SELECT * FROM usage_rules WHERE id=?;", [id])
    usage_rules = [dict(id=row[0], rule=row[1]) for row in c.fetchall()]

    return usage_rules[0] if len(usage_rules) > 0 else None

# add
def db_add_thing(name, owner, contact, usage_rule, url):
    c = storage.write("INSERT INTO things (name, owner, contact, usage_rule, url) VALUES (?, ?, ?, ?, ?);", [name, owner, contact, usage_rule, url])

def db_add_person(pseudonym, email):
    # TODO prevent sql injections
    c = storage.write("INSERT INTO persons (pseudonym, email) VALUES (?, ?);", [pseudonym, email])

def db_add_usage_rule(rule):
    # TODO prevent sql injections
    c = storage.write("INSERT INTO usage_rules (rule) VALUES (?);", [rule])

# modify
def db_modify_thing(id, name, owner, contact, usage_rule, url):
    # TODO prevent sql injections
    c = storage.read("UPDATE things SET name=?, owner=?, contact=?, usage_rule=?, url=? WHERE id=?;", [name, owner, contact, usage_rule, url, id])

def db_modify_person(id, pseudonym, email):
    # TODO prevent sql injections
    c = storage.read("UPDATE persons SET pseudonym=?, email=? WHERE id=?;", [pseudonym, email, id])

def db_modify_usage_rule(id, rule):
    # TODO prevent sql injections
    c = storage.read("UPDATE usage_rules SET rule=? WHERE id=?;", [rule, id])

# routes
@app.route("/")
def hello():
    return show_inventory()

@app.route("/show_inventory")
def show_inventory():
    c = storage.read('SELECT * FROM inventory ORDER BY id DESC;')
    inventory = [dict(id=row[0], owner=row[1], contact=row[2], usage_rule=row[2], url=row[3]) for row in c.fetchall()]

    return render_template("show_inventory.html", inventory=inventory)

@app.route("/add_thing", methods=["GET", "POST"])
@app.route("/modify_thing", methods=["GET", "POST"])
def thing():
    inventory = db_get_things()
    persons = db_get_persons()
    usage_rules = db_get_usage_rules()

    if request.path[1:len("modify_thing") + 1] == "modify_thing":
        if request.method == "POST":
            db_modify_thing(request.form["id"], request.form["name"], request.form["owner"], request.form["contact"], request.form["usage_rule"], request.form["url"])

        id = request.args.get("id")

        if id == None:
            return render_template("error.html")

        thing = db_get_thing_by_id(int(id))

        if thing == None:
            return render_template("error.html")

        return render_template("thing.html", modify=True, inventory=inventory, persons=persons, usage_rules=usage_rules, thing=thing)
    else:
        if request.method == "POST":
            db_add_thing(request.form["name"], request.form["owner"], request.form["contact"], request.form["usage_rule"], request.form["url"])

        return render_template("thing.html", modify=False, inventory=inventory, persons=persons, usage_rules=usage_rules)

@app.route("/add_person", methods=["GET", "POST"])
@app.route("/modify_person", methods=["GET", "POST"])
def person():
    if request.path[1:len("modify_person") + 1] == "modify_person":
        if request.method == "POST":
            db_modify_person(request.form["id"], request.form["pseudonym"], request.form["email"])

        id = request.args.get("id")

        if id == None:
            return render_template("error.html")

        person = db_get_person_by_id(int(id))

        if person == None:
            return render_template("error.html")

        return render_template("person.html", modify=True, person=person)
    else:
        if request.method == "POST":
            db_add_person(request.form["pseudonym"], request.form["email"])

        return render_template("person.html", modify=False)

@app.route("/add_usage_rule", methods=["GET", "POST"])
@app.route("/modify_usage_rule", methods=["GET", "POST"])
def usage_rule():
    if request.path[1:len("modify_usage_rule") + 1] == "modify_usage_rule":
        if request.method == "POST":
            db_modify_usage_rule(request.form["id"], request.form["rule"])

        id = request.args.get("id")

        if id == None:
            return render_template("error.html")

        usage_rule = db_get_usage_rule_by_id(int(id))

        if usage_rule == None:
            return render_template("error.html")

        return render_template("usage_rule.html", modify=True, usage_rule=usage_rule)
    else:
        if request.method == "POST":
            db_add_usage_rule(request.form["rule"])

        return render_template("usage_rule.html", modify=False)

if  __name__ == "__main__":
    app.run(debug=True)
