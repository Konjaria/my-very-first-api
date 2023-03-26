from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


api_keys = {'Client1': "mySpecificApiKey"}


# Café TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        cafe_dict = {}
        for column in self.__table__.columns:
            cafe_dict[column.name] = getattr(self, column.name)
        return cafe_dict



## HTTP GET - Read Record
@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/random')
def random_cafe_generator():
    cafes = db.session.query(Cafe).all()
    random_cafe = choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def all_cafe_fetcher():
    cafes = db.session.query(Cafe).order_by(Cafe.coffee_price).all()
    return jsonify([cafe.to_dict() for cafe in cafes])


@app.route('/find')
def search():
    location_provided = request.args.get('loc')
    cafe = db.session.query(Cafe).filter_by(location=location_provided).all()
    if len(cafe) > 0:
        return jsonify([great_deal.to_dict() for great_deal in cafe])
    else:
        return jsonify({'error': 'Cafe at provided location hasn\'t been found. '})


# HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def add_a_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("has_sockets")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-cafe/<int:cafe_id>", methods=["GET", "PUT", "PATCH"])
def update_whole_cafe_data(cafe_id):
    cafe_found = db.session.query(Cafe).get(cafe_id)
    if cafe_found:
        cafe_found.name = request.form.get("name")
        cafe_found.map_url = request.form.get("map_url")
        cafe_found.img_url = request.form.get("img_url")
        cafe_found.location = request.form.get("location")
        cafe_found.has_sockets = bool(request.form.get("has_sockets"))
        cafe_found.has_toilet = bool(request.form.get("has_toilet"))
        cafe_found.has_wifi = bool(request.form.get("has_wifi"))
        cafe_found.can_take_calls = bool(request.form.get("can_take_calls"))
        cafe_found.seats = request.form.get("seats")
        cafe_found.coffee_price = request.form.get("coffee_price")
        db.session.commit()
        return jsonify([{"result": "Successfully Updated."}, cafe_found.to_dict()])
    else:
        return jsonify({'error': 'Cafe is not presented yet in our database do you wanna add it? if yes please make '
                                 'sure to use proper URL. '})


@app.route("/update-price/<int:cafe_id>", methods=["GET", "PATCH"])
def update_price(cafe_id):
    cafe_found = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe_found:
        cafe_found.coffee_price = request.args.get('coffee_price')
        db.session.commit()
        return jsonify({"result": "Successfully Updated."}), 200
    else:
        return jsonify({'error': 'Cafe is not presented yet in our database do you wanna add it? if yes please make '
                                 'sure to use proper URL. '}), 400


# HTTP DELETE - Delete Record
@app.route('/delete-cafe/<int:cafe_id>', methods=['GET', 'DELETE'])
def delete_cafe(cafe_id):
    # Check api key that the client brought to us
    api_key_provided = request.args.get('api-key')

    if api_key_provided in api_keys.values():
        # Since we have checked whether if the api-key was okay or not, we should
        # be aware about cafe_id for this particular moment
        cafe_found = db.session.query(Cafe).filter_by(id=cafe_id).first()
        if cafe_found:
            # delete specific instance
            db.session.delete(cafe_found)
            db.session.commit()
            return jsonify({"success": "Cafe Deleted Successfully"}), 200
    return jsonify({"error": "Please make sure that API key is correct as well "
                             "as id of a cafe you asked to delete"}), 400


if __name__ == "__main__":
    app.run(debug=True)
