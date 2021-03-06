# Python Utils

This is a python utils package consists of the following packages. A sample project using these modules can be seen at https://github.com/emreisikligil/lambda-flask-template

## flaskjwt

flaskjwt adds jwt authorization support to flask views. All you have to do is to decorate authenticated views and flask jwt handles the rest. It passes extracted claims to the view function for further processing.

```python
from pyutils.auth.flaskjwt import FlaskJWT, Claims

app = Flask()
auth = FlaskJWT("key", ["RS256"])

@app.route('/user/<user_id>', methods=['GET'])
@auth.authenticated
def get_user(user_id: str, claims: Claims):
    pass
```

## modeltodict

When an SQLAlchemy model is decorated with @model2dict, todict() method is added to the model class which returns attributes as dict. Only mapped attributes are added to the dict. unmapped parameter can be set to add unmapped attributes to the final dict. 

This method is needed to get proper attribute dict of the model object. \__dict__ includes some additional attributes that are added by SQLAlchemy. That's why it cannot be used directly.

```python
from pyutils.model2dict import model2dict

db = SQlAlchemy(app)

@model2dict(exclude=["meta"])
class MyTable(db.Model):
    __table_name__ = "my_table"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1024), nullable=False)
    meta = db.Column(db.String(1024), nullable=False)

row = MyTable.query.get(5)
d = row.todict()
print(d) # prints {"id": 5, "data": "..."}
```

## schema_validation

Validates flask request body against a swagger (JSON) definition. Then it passes the body as a dict to the annotated function. If validation fails 422 - Unprocessable Entity exception is raised. The object that will be used to validate against should be defined under *definitions* of swagger spec. It does not follow references in the schema. To be able to use it all *#ref* keys should be dereferenced. You can use the following npm package for this purpose.

https://www.npmjs.com/package/swagger-cli

Dereferencing:
```sh
swagger-cli bundle -r -o swagger-flat.yml -t yaml swagger.yml
```

Usage:
```python
from pyutils.schema_validation import SchemaValidation

schema = SchemaValidation("spec/swagger-flat.yml")

@app.route("/pets", methods=["POST"])
@schema.validate("AddPetRequest")
def add_pet(body): 
    # body is validated and contains the input as dict. 
    # No need to validate it again.

```