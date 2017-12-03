import argparse
import json
import pprint

from . import db
from . import models
from . import server

def main():
    parser = argparse.ArgumentParser('Elmmit: reddit for the dendrophiliac')

    parser.add_argument('-f',
                        help='path to sqlite database',
                        required=True,
                        type=db.connect_db)

    subparsers = parser.add_subparsers()

    # autogenerate command-line versions of all API functions
    for route_path, route in sorted(server.api_routes.items()):
        subparser = subparsers.add_parser(route.basename,
                                          help=route.doc)
        for field_name, field in route.fields.items():
            subparser.add_argument(
                '--' + field_name,
                help="%s (default: %%(default)s)" % (field.description,),
                type=field.type,
                required=field.required,
                default=field.default)
            subparser.set_defaults(route=route)

    arguments = parser.parse_args()

    # construct the call to the underlying DB command
    conn = arguments.f
    route = arguments.route
    args = {name: getattr(arguments, name)
            for name in route.fields}
    print "%s %s:" % (route.basename, args)
    result = route.db_call(conn, **args)

    pprint.pprint(result.to_json())

if __name__ == '__main__':
    main()

