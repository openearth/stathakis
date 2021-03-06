FROM continuumio/miniconda3
MAINTAINER Fedor Baart <fedor.baart@deltares.nl>
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
# update system and install wget
RUN \
    apt-get install -y apt-utils && \
    echo "deb http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    echo "deb-src http://httpredir.debian.org/debian jessie-backports main non-free" >> /etc/apt/sources.list && \
    apt-get update --fix-missing && \
    apt-get install -y wget unzip build-essential
# switch to python 3.5 (no gdal in 3.6)
RUN conda create -y -n py35 python=3.5  jpeg=8d libgdal netcdf4 pandas gdal shapely
COPY ./ app/
ENV PATH /opt/conda/envs/py35/bin:$PATH
ENV GDAL_DATA /opt/conda/envs/py35/share/gdal
RUN find /opt/conda/envs/py35
RUN cd /app && pip install -r requirements.txt && pip install -e .
VOLUME /data
# Create a run directory with
WORKDIR app
EXPOSE 8080
# not sure what this is
ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "stathakis" ]
