import argparse
import json
import pprint

from elmmit import api
from elmmit import db
from elmmit import models
from elmmit import server

def main():
    parser = argparse.ArgumentParser('elmmit')

    parser.add_argument('-f',
                        help='path to sqlite database',
                        required=True,
                        type=db.connect_db)

    subparsers = parser.add_subparsers()

    server_subparser = subparsers.add_parser("server")
    server_subparser.add_argument('--port', '-p', default=8080, type=int)
    server_subparser.set_defaults(func='server')

    # autogenerate command-line versions of all API functions.  we autogenerate
    # the parser out of the API description given by server.py.  this lets us
    # have a nice command-line interface without having to write individual
    # handlers for every API call, but it does restrict how complicated our
    # arguments can be
    for route_path, route in sorted(api.api_routes.items()):
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

    if hasattr(arguments, 'route'):
        # it was an auto-generated command. construct the call to the
        # underlying DB command
        conn = arguments.f
        route = arguments.route
        args = {name: getattr(arguments, name)
                for name in route.fields}
        print "%s %s:" % (route.basename, args)
        result = route.db_call(conn, **args)
        pprint.pprint(result.to_json())

    elif arguments.func == 'server':
        server.server(conn=arguments.f, port=arguments.port)


if __name__ == '__main__':
    main()

