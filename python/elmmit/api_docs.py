import json

def make_docs(route_descriptor):
    "Auto-generate documentation from the API descriptor given in server.py"

    docs = []

    docs.append("API endpoints for Elmmit")
    docs.append('='*len(docs[-1]))
    docs.append("")

    return_types = set()

    for path, route in sorted(route_descriptor.items()):
        docs.append("%s" % (path,))
        docs.append('-'*len(docs[-1]))
        docs.append("Path: %s" % (path,))
        docs.append("Description: %s" % (route.doc,))
        docs.append("Method: %s" % (route.method,))
        docs.append("Arguments:")

        for name, field in sorted(route.fields.items()):
            docs.append("\t* %s: %s" % (name, field.description))
            docs.append("\t\t- type: %s" % field.type.__name__)
            docs.append("\t\t- required: %s" % field.required)
            if not field.required:
                if field.default is not None:
                    docs.append("\t\t- default: %s" % field.default)

        docs.append("Return type: %s" % (route.returns.__name__))
        return_types.add(route.returns)

        docs.append('')
        docs.append('')

    docs.append("Return types")
    docs.append('='*len(docs[-1]))
    docs.append('')

    for return_type in sorted(return_types, key=lambda rt: rt.__name__.lower()):
        docs.append("%s" % (return_type.__name__,))
        docs.append('-'*len(docs[-1]))
        docs.append("Fields:")
        for field in return_type.fields:
            docs.append("\t* %s" % (field,))

        docs.append('')

    docs.append('')

    return '\n'.join(docs)

if __name__ == '__main__':
    from api import api_routes
    print make_docs(api_routes)

