# Python Utils

This is a python utils package consists of the following packages.

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

This method is needed to get proper attribute dict of the model object. __dict__ includes some additional attributes that are added by SQLAlchemy. That's why it cannot be used directly.

```python

@model2dict()
class MyTable(db.Model):
    __table_name__ = "my_table"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1024), nullable=False)

row = MyTable.query.get(5)
d = row.todict()
print(d) # prints {"id": 5, "data": "..."}
```