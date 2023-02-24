# FROM val01:5000/python-base-image:dev-base
FROM ddnirvana/python-base-image:dev-base-3.6

COPY src/setup.py /
COPY src/ol.c /

RUN python3 setup.py build_ext --inplace && mv ol.*.so ol.so
RUN pip3 install flask

COPY src/daemon.py /
COPY src/daemon-loop.py /

CMD ["python3", "daemon-loop.py"]
