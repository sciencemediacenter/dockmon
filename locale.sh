#/bin/bash

pybabel extract . -o src/locale/base.pot
pybabel update -i src/locale/base.pot -d src/locale/
pybabel compile -d src/locale
