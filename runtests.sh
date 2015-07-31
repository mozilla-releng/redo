rm -rf test
virtualenv test
source test/bin/activate
pip install pep8 pyflakes nose
pep8 --config=./pep8rc .
pyflakes .
nosetests --with-doctest
