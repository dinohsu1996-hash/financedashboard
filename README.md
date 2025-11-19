## Windows Setup
✅ Step 1: Create and Activate a Virtual Environment

Open PowerShell and run:

cd "C:\Users\User\Documents\GitHub\financedashboard"
python -m venv .venv
.\.venv\Scripts\activate
pip install streamlit streamlit-option-menu pandas yfinance plotly sqlalchemy pymysql

✅ Step 2: Install Dolt on Windows

Go to: https://github.com/dolthub/dolt/releases

Download the latest dolt-windows-amd64.zip

Extract it to a folder, for example:

C:\Users\User\Dolt\dolt-windows-amd64


Add this folder to your system PATH:

C:\Users\User\Dolt\dolt-windows-amd64\bin


To add it:

Open Start → Search for Environment Variables

Click Edit the system environment variables

Click Environment Variables

Under User Variables, find Path, click Edit, then New, and paste the folder path.

Restart PowerShell and confirm installation:

dolt version


You should see something like: dolt version 1.25.0

✅ Step 3: Clone the Dolt Earnings Database
dolt clone post-no-preference/earnings


This will create a folder called earnings inside your current directory.

✅ Step 4: Start Dolt SQL Server
cd C:\Users\User\Documents\GitHub\financedashboard\earnings
dolt sql-server --port 3307

✅ Step 5: Launch the Streamlit App
cd ..
cd "C:\Users\User\Documents\GitHub\financedashboard"
.venv\Scripts\activate
streamlit run finance_dashboard.py

## 🍎 macOS Setup
✅ Step 1: Create and Activate a Virtual Environment
cd ~/Desktop/FinanceDashboard
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit streamlit-option-menu pandas yfinance plotly sqlalchemy pymysql

✅ Step 2: Install Dolt on macOS
brew install dolt

✅ Step 3: Clone the Dolt Earnings Database
dolt clone post-no-preference/earnings

✅ Step 4: Start Dolt SQL Server
cd ~/Desktop/FinanceDashboard/earnings
dolt sql-server --port 3307

✅ Step 5: Launch the Streamlit App
cd ~/Desktop/FinanceDashboard
source .venv/bin/activate
streamlit run finance_dashboard.py

💡 Tips

dolt pull — update the database with latest changes

cd .. — move up one directory

cd earnings — enter the earnings DB folder