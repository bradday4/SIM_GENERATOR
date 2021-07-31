
echo Building venv
python3 -m venv .venv
source ".venv/bin/activate"
echo Upgrading pip
python3 -m pip install --upgrade pip
echo Upgrading setuptools
python3 -m pip install --upgrade setuptools

echo Building program
if [ $1 = "dev" ]; then
echo Installing dev requirements
python -m pip install -e ".[dev]"
pre-commit install
elif [ $1 = "test" ]; then
echo Installing test requirements
python -m pip install -e ".[test]"
else
echo Installing requirements
python -m pip install -e "."
fi
