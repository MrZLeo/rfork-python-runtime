# FROM val01:5000/python-base-image:dev-base
FROM ddnirvana/python-base-image:dev-base-3.6
RUN mkdir /env && mkdir /code
COPY daemon-base.py /env
COPY daemon-loop.py /env
COPY img-convertor/ /code

