# start from base
FROM ubuntu:latest

RUN apt-get -yqq update
RUN apt-get -yqq install python-pip python-dev curl gnupg

ADD web /web
WORKDIR /web

# fetch app specific deps
#RUN npm install
# RUN npm run build
RUN pip install -r requirements.txt

# expose port
EXPOSE 5000

# start app
CMD [ "python", "./app.py" ]
