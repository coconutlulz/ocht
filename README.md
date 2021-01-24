This is a basic KeyDB/Redis ORM and command-line interface for managing sports, events and selections.

Everything here (except standard libs and named third-party libraries) been written from scratch over a weekend.

The KeyDB library is only used to send raw commands to the database. Its ORM functionality is not used.

# Environment
Create a virtualenv using Python 3.9.1:
```
python -m venv env
source env/bin/activate
```

# Nodes
## Testing
```
python -m unittest
```

# CRUD 
## Preparation
To get the CRUD application working (from this directory):
```
cd crud
docker-compose -f docker-compose.yml up -d
pip install --upgrade -r requirements.txt
```

Generate a test DB with:
```
python -m test.utils generate_test_db
```

## Testing
```
python -m unittest
```

## Usage
```
python cmdline.py
```

### get

Retrieve an object from the database.

```shell
python cmdline.py get <type> <id>
```
```shell
> python cmdline.py get event 1473986426286838251
Event(id=1473986426286838251, name='Event 2', type=1, sport=1470842810873876971, status=0, scheduled_start=datetime.datetime(2705, 7, 18, 21, 25, 36, 132439), actual_start=None, selections=[], slug='event-2', active=False)
```

### create

Create a new object with a dictionary representation of its attributes. Do not include an ID.

```shell
> python cmdline.py create <type> <dict>
```

```shell
> python cmdline.py create sport '{"name": "SomeSport", "active": True}'
Sport(id=7664868525736202731, name='SomeSport', events=[], active=True, slug='somesport')
```

### update

Update the specified object with a dictionary representation of the new attributes.

```shell
> python cmdline.py update <type> <id> <dict>
```
```shell
> python cmdline.py update selection 1479965450259599851 "{'name': 'A New Selection'}"
Selection(id=1479965450259599851, name='A New Selection', event=1473641712211661291, price=1.0, outcome=1, active=False)
```

### deactivate

```shell
> python cmdline.py deactivate <id>
```
```shell
> python cmdline.py deactivate sport 1472831939077673451                                                                                                                                                   ✘ 130 main ✱ ◼
Sport(id=1472831939077673451, name='Sport 10', events=[], active=False, slug='sport-10')
```

### filter

Use regexes and comparison operators chained in any combination with ` AND ` to 
retrieve all objects in the database and filter them.

```shell
> python cmdline.py filter <type> <filter_pattern>
```

Warning: the character ":" is not supported in filter patterns.

Get all sports:
```shell
> python cmdline.py filter sport "regex:^(.*)$"
[Sport(id=1471280510991012331, name='Sport 3', events=[], active=False, slug='sport-3'), Sport(id=1472145302656061931, name='Sport 7', events=[], active=False, slug='sport-7'), Sport(id=1471057988735406571, name='Sport 2', events=[], active=False, slug='sport-2'), Sport(id=1472603446817526251, name='Sport 9', events=[], active=False, slug='sport-9'), Sport(id=1471916166150820331, name='Sport 6', events=[], active=False, slug='sport-6'), Sport(id=1471487442515333611, name='Sport 4', events=[], active=False, slug='sport-4'), Sport(id=1470842810873876971, name='Sport 1', events=[], active=False, slug='sport-1'), Sport(id=1471707989085983211, name='Sport 5', events=[], active=False, slug='sport-5'), Sport(id=1472372892973076971, name='Sport 8', events=[], active=False, slug='sport-8'), Sport(id=1470313155506934251, name='Sport 0', events=[], active=False, slug='sport-0'), Sport(id=1472831939077673451, name='Sport 10', events=[], active=False, slug='sport-10')]
```

Get sports whose names begin with `Sport 1` and which have less than two events.
```shell
> python cmdline.py filter sport "regex:^Sport 1(.*) AND events:<<2"
[Sport(id=1470842810873876971, name='Sport 1', events=[], active=False, slug='sport-1'), Sport(id=1472831939077673451, name='Sport 10', events=[], active=False, slug='sport-10')]
```

Supported operators:
```
<< (less than)
<= (less than or equal)
== (equal)
>= (greater than or equal)
>> (greater than)
```

## Errors
If a database entry does not exist, you may see an unhelpful error such as:
```
TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'
```

Other errors are found in `crud.errors` and should be relatively self-explanatory.

## Caveats
* The only tests are integration tests.
* SQL is not used as I am more comfortable with key-value stores and felt it would take too much time to re-familiarise myself with SQl.
* This is largely experimental, as instead of opting for raw commands I've built a bare-bones ORM.
* The application does **NOT** support transactions. You will see in `crud.database` that I initially
opted for a transactional approach but this was taking too long to debug. As a single-user program, a lack of atomicity should be alright for a first verison.
  
## TODO
* Expand test coverage.
* Add more comments and more helpful log messages.

# Author
```
David Ó Laigheanáin
davidlynam071@gmail.com
```