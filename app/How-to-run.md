## Frontend: ..\frontend>
npm i
npm run
npm start

## Backend: ..\backedn>


# Set-up python venev, flask

Note: You may need to use 'python3' instead of 'python'.

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
pip install flask flask-cors
python save_links.py


#Java Backend Setup

Pre-requisite: maven
install dependencies : mvn install
Starting server: mvn spring-boot:run

#commands to run after dockerization 
Pre-requisite: docker
cd app
docker-compose build --no-cache
docker-compose up
