## Unit Testing Instructions to perform Locally:

### 1.Clone the repository and "cd" to fan_out_service:
git clone https://github.com/Mrunal2148/ser516-group-26
cd ser516-group-26/app/backend/python-backend/fan-in-fan-out/fan_in_service

### 2.Setup and activate a python virtual environment: 
python -m venv venv
source venv/bin/activate (for macOS)
venv/Scripts/activate (for Windows) 

### 3.Install dependencies using the requirements.txt file: 
pip install -r requirements.txt 

### 4.Check if $JAVA_HOME environment variable is setup
  echo $JAVA_HOME

  If not set, do the following:
- FOR macOS:
 1. /usr/libexec/java_home -V
 2. export JAVA_HOME=$(/usr/libexec/java_home -v 17)
- FOR Windows:
 1. Go to your system environment variables.
 2. Find JAVA_HOME Path (example): C:\Program Files\Java\jdk-17
 3. Then, find the Path variable under System Variables → click Edit →
 4. Add: %JAVA_HOME%\bin 

### 5.Run the Fan-Out FastAPI service: 
cd src

uvicorn main:app --port 8000 --reload

### 6.Run Unit Tests: 
cd ../ 

pytest -v