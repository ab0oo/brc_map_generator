import geopy.distance
import fiona
import math

# this will change every year for BM
# this LAT/LON is for the 2022 Golden Spike
goldenSpike = [40.787030, -119.202740]
# 2018 goldenSpike
#goldenSpike = [40.78634966315868, -119.20651954500156]
streetDepths = [2500,440,290,290,290,290,490,290,290,290,190,195]
fivePoints = [ (40.783341, -119.233011),
               (40.807777, -119.216715),
               (40.803538, -119.181098),
               (40.776488, -119.175400),
               (40.764008, -119.207478)]
distToCenterCamp = 3026
manRingRadius = 250
templeRingRadius = 125
centerCampPlazaRadius = 340
rodsRingRadius = 783
scale = 2

# nothing below here should normally change.
degOffset=45
streets = { 'Esplanade': 2500,
            'A': 2940,
            'B': 3230,
            'C': 3520,
            'D': 3810,
            'E': 4100,
            'F': 4590,
            'G': 4880,
            'H': 5170,
            'I': 5460,
            'J': 5650,
            'K': 5845 }

radials = { '2:00': 60.0,
            '2:15': 67.5,
            '2:30': 75.0,
            '2:45': 82.5,
            '3:00': 90.0,
            '3:15': 97.5,
            '3:30': 105.0,
            '3:45': 112.5,
            '4:00': 120.0,
            '4:!5': 127.5,
            '4:30': 135.0,
            '4:45': 142.5,
            '5:00': 150.0,
            '5:15': 157.5,
            '5:30': 165.0,
            '5:45': 172.5,
            '6:00': 180.0,
            '6:15': 187.5,
            '6:30': 195.0,
            '6:45': 202.5,
            '7:00': 210.0,
            '7:15': 217.5,
            '7:30': 225.0,
            '7:45': 232.5,
            '8:00': 240.0,
            '8:15': 247.5,
            '8:30': 255.0,
            '8:45': 262.5,
            '9:00': 270.0,
            '9:15': 277.5,
            '9:30': 285.0,
            '9:45': 292.5,
            '10:00': 300 }

def getStreetByDeg( deg:int ) -> str:
    for k,v in radials.items():
        if deg==v:
            return k

cc = geopy.distance.distance(feet=distToCenterCamp).destination(goldenSpike, bearing=degOffset+180)
centerCamp = [cc.latitude,cc.longitude]
tm = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=degOffset)
temple = [tm.latitude,tm.longitude]

                
# define schema
schema = {
    'geometry':'LineString',
    'properties':[('Name','str')]
}

#open a fiona object
lineShp = fiona.open('bm_2019.shp', mode='w', driver='ESRI Shapefile',
          schema = schema, crs = "EPSG:4326")

# annular streets
idx=0
for name,distance in streets.items():
    annular = []
    for d in range((degOffset+60)*scale,(degOffset+300)*scale+1,1):
        foo = geopy.distance.distance(feet=distance).destination(goldenSpike, bearing=d/scale)
        if geopy.distance.distance(foo,centerCamp).feet >= rodsRingRadius: 
            annular.append((foo.longitude,foo.latitude))
        else:
            rowDict = {
                    'geometry': {'type':'LineString',
                                'coordinates':annular},
                    'properties': {'Name': name,
                        }
                    }
            lineShp.write(rowDict)
            annular = []
    
    rowDict = {
            'geometry': {'type':'LineString',
                        'coordinates':annular},
            'properties': {'Name': name,
                }
            }
    lineShp.write(rowDict)

# radial streets
for name,r in radials.items():
    # 3:00 plaza from man to esplanade
    if name == '3:00':
        street = []
        foo = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=r+degOffset)
        street.append((foo.longitude,foo.latitude))
        foo = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=r+degOffset)
        street.append((foo.longitude,foo.latitude))
        rowDict = {
            'geometry': {'type':'LineString',
                'coordinates':street},
            'properties': {'Name': name,
                }
            }
        lineShp.write(rowDict)
    # 9:00 plaza from man to esplanade
    if name == '9:00':
        street = []
        foo = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=r+degOffset)
        street.append((foo.longitude,foo.latitude))
        foo = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=r+degOffset)
        street.append((foo.longitude,foo.latitude))
        rowDict = {
            'geometry': {'type':'LineString',
                'coordinates':street},
            'properties': {'Name': name,
                }
            }
        lineShp.write(rowDict)
    # special rules for the 6:00 radial
    if name == '6:00':
        street = []
        # road from Man Ring to Center Camp Plaza
        foo = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=r+degOffset)
        street.append((foo.longitude,foo.latitude))
        foo = geopy.distance.distance(feet=distToCenterCamp-centerCampPlazaRadius).destination(goldenSpike, bearing=r+degOffset)
        street.append((foo.longitude,foo.latitude))
        rowDict = {
            'geometry': {'type':'LineString',
                'coordinates':street},
            'properties': {'Name': name,
                }
            }
        lineShp.write(rowDict)
        # road from Center Camp Plaza to K
        street = []
        foo = geopy.distance.distance(feet=distToCenterCamp+centerCampPlazaRadius).destination(goldenSpike, bearing=r+degOffset)
        street.append((foo.longitude,foo.latitude))
        foo = geopy.distance.distance(feet=streets['K']).destination(goldenSpike, bearing=r+degOffset)
        street.append((foo.longitude,foo.latitude))
        rowDict = ({
            'geometry': {'type':'LineString',
                'coordinates':street},
            'properties': {'Name': name,
                }
            })
        lineShp.write(rowDict)
    else:
        # these are for "normal" Esplanade-to-K streets
        if r % 5 == 0:
            start = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=r+degOffset)
            # we do this to provide a different segment for each block.  this is important for anyone
            # using this map to do routing
            for steetName,distance in streets.items():
                street = []
                street.append((start.longitude,start.latitude))
                end = geopy.distance.distance(feet=distance).destination(goldenSpike, bearing=r+degOffset)
                street.append((end.longitude,end.latitude))
                rowDict = {
                    'geometry': {'type':'LineString',
                        'coordinates':street},
                    'properties': {'Name': name,
                        }
                    }
                lineShp.write(rowDict)
                start = end
        # these are for the :15/:45 short streets on the outer half of the city, F-K
        else:
            start = geopy.distance.distance(feet=streets['F']).destination(goldenSpike, bearing=r+degOffset)
            for streetName in ['G','H','I','J','K']:
                street = []
                street.append((start.longitude,start.latitude))
                end = geopy.distance.distance(feet=streets[streetName]).destination(goldenSpike, bearing=r+degOffset)
                street.append((end.longitude,end.latitude))
                rowDict = {
                    'geometry': {'type':'LineString',
                        'coordinates':street},
                    'properties': {'Name': name,
                        }
                    }
                lineShp.write(rowDict)
                start = end

street = []
# special rules for the 12:00 radial
foo = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=degOffset)
street.append((foo.longitude,foo.latitude))
foo = geopy.distance.distance(feet=streets['Esplanade']-templeRingRadius).destination(goldenSpike, bearing=degOffset)
street.append((foo.longitude,foo.latitude))
rowDict = {
    'geometry': {'type':'LineString',
        'coordinates':street},
    'properties': {'Name': '12:00',
        }
    }
lineShp.write(rowDict)

# center camp ring
manring = []
ring = []
ring2 = []
templeRing = []
radialThree = []
radialNine = []
for r in range((degOffset+0)*scale,(degOffset+360)*scale+1,1):
    foo = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=r/scale)
    manring.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=centerCampPlazaRadius).destination(centerCamp, bearing=r/scale)
    ring.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=rodsRingRadius).destination(centerCamp, bearing=r)
    ring2.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=templeRingRadius).destination(temple, bearing=r)
    templeRing.append((foo.longitude,foo.latitude))
    if r==90:
        foo = geopy.distance.distance(feet=centerCampPlazaRadius).destination(centerCamp, bearing=r+degOffset)
        radialThree.append((foo.longitude,foo.latitude))
        foo = geopy.distance.distance(feet=streets['A']).destination(goldenSpike, bearing=radials['5:30']+degOffset)
        radialThree.append((foo.longitude,foo.latitude))
    if r==270:
        foo = geopy.distance.distance(feet=centerCampPlazaRadius).destination(centerCamp, bearing=r+degOffset)
        radialNine.append((foo.longitude,foo.latitude))
        foo = geopy.distance.distance(feet=streets['A']).destination(goldenSpike, bearing=radials['6:30']+degOffset)
        radialNine.append((foo.longitude,foo.latitude))
        

mrDict = {
  'geometry': {'type':'LineString',
      'coordinates':manring},
  'properties': {'Name': 'Man Ring',
    }
}
lineShp.write(mrDict)

ccDict = {
  'geometry': {'type':'LineString',
      'coordinates':ring},
  'properties': {'Name': 'Center Camp Plaza',
    }
}
lineShp.write(ccDict)

rrDict = {
  'geometry': {'type':'LineString',
      'coordinates':ring2},
  'properties': {'Name': 'Rod\'s Ring Road',
    }
}
lineShp.write(rrDict)

rrDict = {
  'geometry': {'type':'LineString',
      'coordinates':templeRing},
  'properties': {'Name': 'Temple Ring Road',
    }
}
lineShp.write(rrDict)

rrDict = {
  'geometry': {'type':'LineString',
      'coordinates':radialThree},
  'properties': {'Name': 'Center Camp 3:00 Road',
    }
}
lineShp.write(rrDict)
rrDict = {
  'geometry': {'type':'LineString',
      'coordinates':radialNine},
  'properties': {'Name': 'Center Camp 9:00 Road',
    }
}
lineShp.write(rrDict)

tf = []
for lat, lon in fivePoints:
    tf.append((lon,lat))

# finally, build the trash fence.
tf.append((fivePoints[0][1], fivePoints[0][0]))
trashFence = { 
  'geometry': {'type':'LineString',
      'coordinates':tf},
  'properties': {'Name': 'Trash Fence',
    }
}

lineShp.write(trashFence)

lineShp.close()


