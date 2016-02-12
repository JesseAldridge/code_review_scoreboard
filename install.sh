echo "installing requirements..."
pip install -r requirements.txt --user
echo "setting up launchctl..."
python setup_launchctl.py
