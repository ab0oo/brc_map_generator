import geopy.distance
import fiona

degOffset=45
streetNames = ['Esplanade','A','B','C','D','E','F','G','H','I','J','K' ]
streetDepths = [2500,440,290,290,290,290,490,290,290,290,190,190]
radialNames = ['2:00','2:30','3:00','3:30','4:00','4:30','5:00','5:30','6:00', \
               '6:30','7:00','7:30','8:00','8:30','9:00','9:30','10:00' ]
shortRadialNames = ['2:15','2:45','3:15','3:45','4:15','4:45','5:15','5:45','6:15', \
                    '6:45','7:15','7:45','8:15','8:45','9:15','9:45' ]
                
currDist = 0;

maxDistance = sum(streetDepths)

# define schema
schema = {
    'geometry':'LineString',
    'properties':[('Name','str')]
}
goldenSpike = [40.78634966315868, -119.20651954500156]
cc = geopy.distance.distance(feet=2925).destination(goldenSpike, bearing=degOffset+180)
centerCamp = [cc.latitude,cc.longitude]

#open a fiona object
lineShp = fiona.open('bm_2019.shp', mode='w', driver='ESRI Shapefile',
          schema = schema, crs = "EPSG:4326")

# annular streets
idx=0
for s in streetDepths:
    currDist = currDist+s
    print(f"Distance for center of {streetNames[idx]} is {currDist}")
    radial = []
    for d in range(degOffset+60,degOffset+301,5):
        foo = geopy.distance.distance(feet=currDist).destination(goldenSpike, bearing=d)
        radial.append((foo.longitude,foo.latitude))
    
    rowDict = {
            'geometry': {'type':'LineString',
                        'coordinates':radial},
            'properties': {'Name': streetNames[idx],
                }
            }
    lineShp.write(rowDict)
    idx=idx+1

# radial streets
idx=0
for r in range(degOffset+60,degOffset+301,15):
    street = []
    foo = geopy.distance.distance(feet=2500).destination(goldenSpike, bearing=r)
    street.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=maxDistance).destination(goldenSpike, bearing=r)
    street.append((foo.longitude,foo.latitude))
    rowDict = {
        'geometry': {'type':'LineString',
            'coordinates':street},
        'properties': {'Name': radialNames[idx],
            }
        }
    lineShp.write(rowDict)
    idx=idx+1

# short radial streets at :15's
idx=0
shortRadial = degOffset+67.5
while shortRadial < degOffset+300:
    street = []
    foo = geopy.distance.distance(feet=4590).destination(goldenSpike, bearing=shortRadial)
    street.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=maxDistance).destination(goldenSpike, bearing=shortRadial)
    street.append((foo.longitude,foo.latitude))
    rowDict = {
        'geometry': {'type':'LineString',
            'coordinates':street},
        'properties': {'Name': shortRadialNames[idx],
            }
        }
    lineShp.write(rowDict)
    shortRadial = shortRadial + 15
    idx=idx+1

# center camp ring
manring = []
ring = []
ring2 = []
for r in range(0,361,5):
    foo = geopy.distance.distance(feet=250).destination(goldenSpike, bearing=r)
    manring.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=320).destination(centerCamp, bearing=r)
    ring.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=784).destination(centerCamp, bearing=r)
    ring2.append((foo.longitude,foo.latitude))

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

lineShp.close()
