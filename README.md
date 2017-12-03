elmmit is a starter repo for writing a reddit clone in [elm](http://elm-lang.org/)

Included is a small API server in Python and some scripts to get elm installed
and running in a Vagrant VM

To get started, install [Vagrant](https://www.vagrantup.com/) and run:

```bash
vagrant up
```

Go and get some coffee, and when you get back in that same shell run

```bash
./scripts/elm-reactor.sh
```

And in a web browser open both of:

* http://localhost:8000 (a nice UI to the elm compiler and environment)
* http://localhost:8080/docs (the docs for the simple API implemented by the Python server)

And you're set! Happy hacking
