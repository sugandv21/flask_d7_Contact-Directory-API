from flask import Flask, request, redirect, url_for
from flask_restful import Api, Resource
from models import db, Contact

app = Flask(__name__)

# SQLite config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
api = Api(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for("contacts"))

# ------------------ Validation ------------------
def validate_contact(name, phone):
    if not name:
        return False, "Name is required"
    if not phone or len(phone) != 10 or not phone.isdigit():
        return False, "Phone must be exactly 10 digits"
    return True, None

# ------------------ Resources ------------------
class ContactListResource(Resource):
    def get(self):
        contacts = Contact.query.all()
        return {"status": "success", "contacts": [c.to_dict() for c in contacts]}, 200

    def post(self):
        data = request.get_json()
        if not data:
            return {"status": "error", "message": "Missing JSON body"}, 400

        name = data.get("name")
        phone = data.get("phone")
        email = data.get("email")

        valid, error = validate_contact(name, phone)
        if not valid:
            return {"status": "error", "message": error}, 400

        new_contact = Contact(name=name, phone=phone, email=email)
        db.session.add(new_contact)
        db.session.commit()

        return {"status": "success", "contact": new_contact.to_dict()}, 201


class ContactResource(Resource):
    def get(self, id):
        contact = Contact.query.get_or_404(id)
        return {"status": "success", "contact": contact.to_dict()}, 200

    def put(self, id):
        contact = Contact.query.get_or_404(id)
        data = request.get_json()

        if "name" in data:
            contact.name = data["name"]
        if "phone" in data:
            valid, error = validate_contact(data.get("name", contact.name), data["phone"])
            if not valid:
                return {"status": "error", "message": error}, 400
            contact.phone = data["phone"]
        if "email" in data:
            contact.email = data["email"]

        db.session.commit()
        return {"status": "success", "contact": contact.to_dict()}, 200

    def delete(self, id):
        contact = Contact.query.get_or_404(id)
        db.session.delete(contact)
        db.session.commit()
        return {"status": "success", "message": "Contact deleted"}, 200

# Register endpoints
api.add_resource(ContactListResource, "/contacts", endpoint="contacts")
api.add_resource(ContactResource, "/contacts/<int:id>", endpoint="contact")

if __name__ == "__main__":
    app.run(debug=True)
