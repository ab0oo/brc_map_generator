import geopy.distance
from geopy.distance import geodesic as GD
import fiona
import math

# this will change every year for BM
# this LAT/LON is for the 2022 Golden Spike
#2023 goldenSpike
goldenSpike = [40.786400, -119.203500]
#2022 goldenSpike
#goldenSpike = [40.787030, -119.202740]
# 2018 goldenSpike
#goldenSpike = [40.78634966315868, -119.20651954500156]

fivePoints = [ (40.782814, -119.233566),
               (40.807028, -119.217274),
               (40.802722, -119.181931),
               (40.775857, -119.176407),
               (40.763558, -119.208301)]
distToCenterCamp = 3026
manRingRadius = 250
templeRingRadius = 125
centerCampPlazaRadius = 340
rodsRingRadius = 783
scale = 2
RAD_PER_DEG = 2 * math.pi / 360.0

# nothing below here should normally change.
cityOffsetAngle=45
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
            '4:15': 127.5,
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

cc = geopy.distance.distance(feet=distToCenterCamp).destination(goldenSpike, bearing=cityOffsetAngle+180)
centerCamp = [cc.latitude,cc.longitude]
tm = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=cityOffsetAngle)
temple = [tm.latitude,tm.longitude]

#open a fiona object
lineShp = fiona.open('bm_2023_lines.shp', 
                     mode='w', driver='ESRI Shapefile',
                     schema = {
                        'geometry':'LineString',
                        'properties':[('Name','str'),
                                      ('FID','str'),
                                      ('Length','float')]
                     },
                     crs = "EPSG:4326")

polyShp = fiona.open('bm_2023_poly.shp',
                     mode='w', driver='ESRI Shapefile',
                     schema = {
                        'geometry':'Polygon',
                        'properties':[('Name','str')]
                     },
                     crs = "EPSG:4326")

# annular streets
idx=0
fid= -1
for name,distance in streets.items():
    for clock,streetDegree in radials.items():
        if ( clock=="10:00" ):
            continue
        if ( clock in ('5:30', '5:45', '6:00','6:15') and name in ('B','C')):
            continue
        annular = []
        startAngle = streetDegree + cityOffsetAngle
        # this causes us to skip the :15 streets when inside F
        if ( distance < 4101 ):
            stepAngle = 15
            if streetDegree % 15 != 0:
               continue
        else:
            stepAngle = 7.5
        endAngle = startAngle + stepAngle
        streetLength = distance * ( ( endAngle - startAngle ) * RAD_PER_DEG )
        steps = math.floor(streetLength / 25 )
        stepDeg = 25 / distance / RAD_PER_DEG
        cc = False
        for d in range(0,steps+1):
            bearing = startAngle + d*stepDeg
            pt = geopy.distance.distance(feet=distance).destination(goldenSpike, bearing=bearing)
            if geopy.distance.distance(pt,centerCamp).feet < rodsRingRadius: 
                cc = True
            else:
                annular.append((pt.longitude,pt.latitude))
        # this pins the end of the segment at the terminous of the segment, unless it's inside Rod's Ring Road
        if ( cc == False ):
            pt = geopy.distance.distance(feet=distance).destination(goldenSpike, bearing=endAngle)
            annular.append((pt.longitude,pt.latitude))
        fid+=1
        rowDict = {
                'geometry': {'type':'LineString',
                            'coordinates':annular},
                'properties': {'Name': name,
                               'FID': fid,
                               'Length': streetLength,
                    }
                }
        lineShp.write(rowDict)

# radial streets
for name,r in radials.items():
    # 3:00 road from man to esplanade
    if name == '3:00':
        street = []
        #streetStart = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=r+cityOffsetAngle)
        streetStart = geopy.Point(goldenSpike[0], goldenSpike[1])
        street.append((streetStart.longitude,streetStart.latitude))
        streetEnd = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=r+cityOffsetAngle)
        street.append((streetEnd.longitude,streetEnd.latitude))
        streetLength = round(GD(streetStart,streetEnd).feet)
        fid+=1
        rowDict = {
            'geometry': {'type':'LineString',
                'coordinates':street},
            'properties': {'Name': name,
                           'FID': fid,
                           'Length': streetLength,
                }
            }
        lineShp.write(rowDict)
    # 9:00 road from man to esplanade
    if name == '9:00':
        street = []
        #streetStart = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=r+cityOffsetAngle)
        streetStart = geopy.Point(goldenSpike[0], goldenSpike[1])
        street.append((streetStart.longitude,streetStart.latitude))
        streetEnd = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=r+cityOffsetAngle)
        street.append((streetEnd.longitude,streetEnd.latitude))
        streetLength = round(GD(streetStart,streetEnd).feet)
        fid+=1
        rowDict = {
            'geometry': {'type':'LineString',
                'coordinates':street},
            'properties': {'Name': name,
                           'FID': fid,
                           'Length': streetLength,
                }
            }
        lineShp.write(rowDict)
    # special rules for the 6:00 radial
    if name == '6:00':
        street = []
        # road from Man Ring to Center Camp Plaza
        #streetStart = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=r+cityOffsetAngle)
        streetStart = geopy.Point(goldenSpike[0], goldenSpike[1])
        street.append((streetStart.longitude,streetStart.latitude))
        streetEnd = geopy.distance.distance(feet=distToCenterCamp-centerCampPlazaRadius).destination(goldenSpike, bearing=r+cityOffsetAngle)
        street.append((streetEnd.longitude,streetEnd.latitude))
        streetLength = round(GD(streetStart,streetEnd).feet)
        fid+=1
        rowDict = {
            'geometry': {'type':'LineString',
                'coordinates':street},
            'properties': {'Name': name,
                           'FID': fid,
                           'Length': streetLength,
                }
            }
        lineShp.write(rowDict)
        # road from Center Camp Plaza to K
        street = []
        streetStart = geopy.distance.distance(feet=distToCenterCamp+centerCampPlazaRadius).destination(goldenSpike, bearing=r+cityOffsetAngle)
        street.append((streetStart.longitude,streetStart.latitude))
        streetEnd = geopy.distance.distance(feet=streets['K']).destination(goldenSpike, bearing=r+cityOffsetAngle)
        street.append((streetEnd.longitude,streetEnd.latitude))
        streetLength = round(GD(streetStart,streetEnd).feet)
        fid+=1
        rowDict = ({
            'geometry': {'type':'LineString',
                'coordinates':street},
            'properties': {'Name': name,
                           'FID': fid,
                           'Length': streetLength,
                }
            })
        lineShp.write(rowDict)
    else:
        # these are for "normal" Esplanade-to-K streets
        if r % 5 == 0:
            start = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=r+cityOffsetAngle)
            # we do this to provide a different segment for each block.  this is important for anyone
            # using this map to do routing
            for steetName,distance in streets.items():
                street = []
                street.append((start.longitude,start.latitude))
                end = geopy.distance.distance(feet=distance).destination(goldenSpike, bearing=r+cityOffsetAngle)
                street.append((end.longitude,end.latitude))
                streetLength = round(GD(start,end).feet)
                fid+=1
                rowDict = {
                    'geometry': {'type':'LineString',
                        'coordinates':street},
                    'properties': {'Name': name,
                                   'FID': fid,
                                   'Length': streetLength,
                        }
                    }
                lineShp.write(rowDict)
                start = end
        # these are for the :15/:45 short streets on the outer half of the city, F-K
        else:
            start = geopy.distance.distance(feet=streets['F']).destination(goldenSpike, bearing=r+cityOffsetAngle)
            for streetName in ['G','H','I','J','K']:
                street = []
                street.append((start.longitude,start.latitude))
                end = geopy.distance.distance(feet=streets[streetName]).destination(goldenSpike, bearing=r+cityOffsetAngle)
                street.append((end.longitude,end.latitude))
                streetLength = round(GD(start,end).feet)
                fid+=1
                rowDict = {
                    'geometry': {'type':'LineString',
                        'coordinates':street},
                    'properties': {'Name': name,
                                   'FID': fid,
                                   'Length': streetLength,
                        }
                    }
                lineShp.write(rowDict)
                start = end

street = []
# special rules for the 12:00 radial
#streetStart = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=cityOffsetAngle)
streetStart = geopy.Point(goldenSpike[0], goldenSpike[1])
street.append((streetStart.longitude,streetStart.latitude))
streetEnd = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=cityOffsetAngle)
street.append((streetEnd.longitude,streetEnd.latitude))
streetLength = round(GD(streetStart,streetEnd).feet)
fid+=1
rowDict = {
    'geometry': {'type':'LineString',
        'coordinates':street},
    'properties': {'Name': '12:00',
                   'FID': fid,
                   'Length': streetLength,
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
for r in range(0,360*scale+1,1):
    foo = geopy.distance.distance(feet=manRingRadius).destination(goldenSpike, bearing=r/scale)
    manring.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=centerCampPlazaRadius).destination(centerCamp, bearing=r/scale)
    ring.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=rodsRingRadius).destination(centerCamp, bearing=r)
    ring2.append((foo.longitude,foo.latitude))
    foo = geopy.distance.distance(feet=templeRingRadius).destination(temple, bearing=r)
    templeRing.append((foo.longitude,foo.latitude))
    if r==90:
        radialThreeStart = geopy.distance.distance(feet=centerCampPlazaRadius).destination(centerCamp, bearing=r+cityOffsetAngle)
        radialThree.append((radialThreeStart.longitude,radialThreeStart.latitude))
        radialThreeEnd = geopy.distance.distance(feet=streets['A']).destination(goldenSpike, bearing=radials['5:30']+cityOffsetAngle)
        radialThree.append((radialThreeEnd.longitude,radialThreeEnd.latitude))
    if r==270:
        radialNineStart = geopy.distance.distance(feet=centerCampPlazaRadius).destination(centerCamp, bearing=r+cityOffsetAngle)
        radialNine.append((radialNineStart.longitude,radialNineStart.latitude))
        radialNineEnd = geopy.distance.distance(feet=streets['A']).destination(goldenSpike, bearing=radials['6:30']+cityOffsetAngle)
        radialNine.append((radialNineEnd.longitude,radialNineEnd.latitude))
        
fid+=1
mrDict = {
  'geometry': {'type':'LineString',
      'coordinates':manring},
  'properties': {'Name': 'Man Ring',
                 'FID': fid,
                 'Length': round(manRingRadius * 2 * math.pi),
    }
}
lineShp.write(mrDict)

fid+=1
ccDict = {
  'geometry': {'type':'LineString',
      'coordinates':ring},
  'properties': {'Name': 'Center Camp Plaza',
                 'FID': fid,
                 'Length': round(centerCampPlazaRadius * 2 * math.pi),
    }
}
lineShp.write(ccDict)

fid+=1
rrDict = {
  'geometry': {'type':'LineString',
      'coordinates':ring2},
  'properties': {'Name': 'Rod\'s Ring Road',
                 'FID': fid,
                 'Length': round(rodsRingRadius * 2 * math.pi),
    }
}
lineShp.write(rrDict)

fid+=1
rrDict = {
  'geometry': {'type':'LineString',
      'coordinates':templeRing},
  'properties': {'Name': 'Temple Ring Road',
                 'FID': fid,
                 'Length': round(templeRingRadius * 2 * math.pi),
    }
}
lineShp.write(rrDict)

streetLength = round(GD(radialThreeStart,radialThreeEnd).feet)
fid+=1
rrDict = {
  'geometry': {'type':'LineString',
      'coordinates':radialThree},
  'properties': {'Name': 'Center Camp 3:00 Road',
                 'FID': fid,
                 'Length': streetLength,
    }
}
lineShp.write(rrDict)

streetLength = round(GD(radialNineStart,radialNineEnd).feet)
fid+=1
rrDict = {
  'geometry': {'type':'LineString',
      'coordinates':radialNine},
  'properties': {'Name': 'Center Camp 9:00 Road',
                 'FID': fid,
                 'Length': streetLength,
    }
}
lineShp.write(rrDict)

for i in range(len(fivePoints)):
    tf = []
    fid+=1
    segmentStart = geopy.Point(fivePoints[i][0],fivePoints[i][1])
    tf.append((segmentStart.longitude, segmentStart.latitude))
    if ( i < len(fivePoints)-1 ):
        segmentEnd = geopy.Point(fivePoints[i+1][0],fivePoints[i+1][1])
        name=f"Trash Fence Pt. {i+1}-Pt. {i+2}"
    else:
        segmentEnd = geopy.Point(fivePoints[0][0],fivePoints[0][1])
        name=f"Trash Fence Pt. {i+1}-Pt. 1"
    tf.append((segmentEnd.longitude, segmentEnd.latitude));
    streetLength = round(GD(segmentStart,segmentEnd).feet)

    fid+=1
    trashFence = { 
      'geometry': {'type':'LineString',
          'coordinates':tf},
      'properties': {'Name': name,
                 'FID': fid,
                 'Length': streetLength,
        }
    }
    lineShp.write(trashFence)

lineShp.close()
