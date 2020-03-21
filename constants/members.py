users = dict([
    (46535653, {"name": "Thomas", "top": 13}),
    (225652477, {"name": "Philipp", "top": 9}),
    (431332931, {"name": "Stephan", "top": 3}),
    (10243457, {"name": "Alexander", "top": 9}),
    (416387342, {"name": "Julian", "top": 14}),
    (491884854, {"name": "Tobias", "top": 9}),
    (495226626, {"name": "Daniel", "top": 3})
])


def getTOP(userid):
    try:
        top = users[userid]["top"]
        return top
    except KeyError:
        return "7 (pls no)"


def getName(userid):
    try:
        name = users[userid]["name"]
        return name
    except KeyError:
        return "Markus (pls no)"