FROM osgeo/gdal:latest

ENV BUILD_PACKAGES="build-essential git python3-dev python3-pip"
ENV DEBIAN_FRONTEND=noninteractive

COPY ["gen_brc_shapefile.py","requirements.txt","LICENSE.txt","/srv/brc_map_generator/"]

RUN ls -l /srv/brc_map_generator \
  && apt-get update \
  && apt-get upgrade -y \ 
     --no-install-recommends --no-install-suggests \
  && apt-get install -y \
     --no-install-recommends --no-install-suggests \
     ${BUILD_PACKAGES} \
  && cd /srv/brc_map_generator \
  && pip install -r requirements.txt \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir /output 

# Where the files will be placed.
WORKDIR /output

CMD ["/usr/bin/python", "/srv/brc_map_generator/gen_brc_shapefile.py"]
