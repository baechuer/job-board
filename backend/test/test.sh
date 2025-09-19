export DB_URL="sqlite:///:memory:"
python -m unittest test/models_test.py
python -m unittest test/security_test.py
python -m unittest test/routes_test.py
unset DB_URL