# 0 or 1 and 2 or 3 or 4
attribute = ['attr1', 'attr2', 'attr3', 'attr4', 'attr5']
condition = ['cond1', 'cond2', 'cond3', 'cond4', 'cond5']
query = ['query1', 'query2', 'query3', 'query4', 'query5']
operator = ['or', 'and', 'or', 'or']


filters = []
ors = []

for i in xrange(0, len(attribute)):
    filters.append( Q( **{ "%s__%s" % (attribute[i], condition[i]) : query } ))

for i in xrange(0, len(operator)):
    if operator[i] == 'or':
        ors.append(filters.pop(0))
    elif operator[i] == 'and':
        q1 = filters.pop(0)
        q2 = filters.pop(0)
        filters.insert(0, q1 & q2)

filter = filters[0]
for i in xrange(0, len(ors)):
    filter = filter | ors[i]

return contacts.filter(filter)






filters = []
union = []
intersection = []

for i in xrange(0,len(attribute)):
    filters.append( [ attribute[i], condition[i], query[i] ] )

def reducesearch(filters, operators, contacts):
    if operators == []:
        # perform filter and return it
        newcontacts = contacts.filter(something)
        return newcontacts
    if operator[0] == "and":
        # filter the queryset with these two and return it
        left = filters[0]
        right = filters[1]
        qsleft = contacts.filter(something)
        qsright = contacts.filter(something)
    elif operator[0] == "or":
        o = operator[0]
        left = filters[0]
        qsright = reducesearch(filters[1:], operators[1:], contacts)
        # filter with left, union that with right by id__in = [c.id for c in right]
        qsleft = contacts.filter(something)
        ids = [c.id for c in qsleft]
        ids = ids + [c.id for c in qsright]
        return contacts.filter(id__in = ids)


def performfilter(filter, contacts):
    (attr, cond, query) = filter
    if cond == "contains":
        
    elif cond == "doesn't contain":
    elif cond == "is":
    elif cond == "is empty":
