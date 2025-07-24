import geopy.distance
from geopy.distance import geodesic as GD
import fiona
import math
import sys

def calculate_initial_compass_bearing(start_point, end_point):
       """
       Calculates the bearing between two points.

       Args:
           start_point: A tuple representing the latitude and longitude of the starting point.
           end_point: A tuple representing the latitude and longitude of the ending point.

       Returns:
           The bearing in degrees (0-360).
       """
       lat1 = radians(start_point[0])
       lat2 = radians(end_point[0])
       lon_diff = radians(end_point[1] - start_point[1])

       y = math.sin(lon_diff) * math.cos(lat2)
       x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon_diff)

       bearing_rad = math.atan2(y, x)
       bearing_deg = (math.degrees(bearing_rad) + 360) % 360

       return bearing_deg


def radians(degrees):
    return degrees * math.pi / 180


year = 2025
# this will change every year for BM
# this LAT/LON is for the Golden Spike
#2025 goldenSpike
goldenSpike = [40.786958, -119.202994]
#2024 goldenSpike
#goldenSpike = [40.786969, -119.204101]
#2023 goldenSpike
#goldenSpike = [40.786400, -119.203500]
#2022 goldenSpike
#goldenSpike = [40.787030, -119.202740]
# 2018 goldenSpike
#goldenSpike = [40.78634966315868, -119.20651954500156]

fivePoints = [ (40.783388, -119.232725),
               (40.807354, -119.216621),
               (40.803107, -119.181667),
               (40.776557, -119.176181),
               (40.764363, -119.207719)]
distToCenterCamp = 2999
distanceToEsplanadeCenter = 2500
manRingRadius = 250
templeRingRadius = 125
centerCampPlazaRadius = 520
cityOffsetAngle=45
rodsRingRadius = 778 # after 2023 this became the outer center camp ring
scale = 2
RAD_PER_DEG = 2 * math.pi / 360.0
STEPS_PER_ARC = 36
street_width = { 'Esplanade' : 40,
                 'A': 30,
                 'B': 30,
                 'C': 30,
                 'D': 30,
                 'E': 40,
                 'F': 30,
                 'G': 30,
                 'H': 30,
                 'I': 30,
                 'J': 30,
                 'K': 50 }

block_depth = { 'Esplanade' : 0,
            'A': 400,
            'B': 250,
            'C': 250,
            'D': 250,
            'E': 250,
            'F': 450,
            'G': 250,
            'H': 250,
            'I': 250,
            'J': 150,
            'K': 150 }


# nothing below here should normally change.
# this is feet to center of named road
streets = {}
prevDist = distanceToEsplanadeCenter
prevWidth = 0
for k,v in street_width.items():
    if k == 'Esplanade':
        streets[k] = distanceToEsplanadeCenter
    else:
        streets[k] = prevDist + prevWidth / 2 + v / 2 + block_depth[k]
    prevWidth = v
    prevDist = streets[k]

print(streets)
	
radials = { '2:00': 60.0,
            '2:30': 75.0,
            '3:00': 90.0,
            '3:30': 105.0,
            '4:00': 120.0,
            '4:30': 135.0,
            '5:00': 150.0,
            '5:30': 165.0,
            '6:00': 180.0,
            '6:30': 195.0,
            '7:00': 210.0,
            '7:30': 225.0,
            '8:00': 240.0,
            '8:30': 255.0,
            '9:00': 270.0,
            '9:30': 285.0,
            '10:00': 300 }

community_paths = {
            '2:15': 67.5,
            '2:45': 82.5,
            '3:15': 97.5,
            '3:45': 112.5,
            '4:15': 127.5,
            '4:45': 142.5,
            '5:15': 157.5,
            '5:45': 172.5,
            '6:15': 187.5,
            '6:45': 202.5,
            '7:15': 217.5,
            '7:45': 232.5,
            '8:15': 247.5,
            '8:45': 262.5,
            '9:15': 277.5,
            '9:45': 292.5 }
            

def getStreetByDeg( deg:int ) -> str:
    for k,v in radials.items():
        if deg==v:
            return k

cc = geopy.distance.distance(feet=distToCenterCamp).destination(goldenSpike, bearing=cityOffsetAngle+180)
centerCamp = [cc.latitude,cc.longitude]
tm = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=cityOffsetAngle)
temple = [tm.latitude,tm.longitude]

#open a fiona object
filename = f'brc_{year}_lines.shp'
lineShp = fiona.open(filename, 
                     mode='w', driver='ESRI Shapefile',
                     schema = {
                        'geometry':'LineString',
                        'properties':[('Name','str'),
                                      ('FID','str'),
                                      ('Length','float'),
                                      ('Type','str')]
                     },
                     crs = "EPSG:4326")

#polyShp = fiona.open('bm_2023_poly.shp',
#                     mode='w', driver='ESRI Shapefile',
#                     schema = {
#                        'geometry':'Polygon',
#                        'properties':[('Name','str')]
#                     },
#                     crs = "EPSG:4326")

# annular streets
idx=0
fid=0
for name,distance in streets.items():
    for clock,streetDegree in radials.items():
        if ( clock=="10:00" ):
            continue
#        if clock in ('5:30', '5:45', '6:00','6:15') and name == 'Esplanade':
#            continue
        startAngle = streetDegree + cityOffsetAngle
        # this causes us to skip the :15 streets when inside F
        if ( distance < streets['F'] ):
            stepAngle = 15
            doIt = 1
        else:
            stepAngle = 7.5
            doIt = 2
        for i in range(doIt):
            annular = []
            endAngle = startAngle + stepAngle
            streetLength = distance * ( ( endAngle - startAngle ) * RAD_PER_DEG )
            steps = math.floor(streetLength / STEPS_PER_ARC )
            stepDeg = STEPS_PER_ARC / distance / RAD_PER_DEG
            cc = False
            for d in range(0,steps+1):
                bearing = startAngle + d*stepDeg
                pt = geopy.distance.distance(feet=distance).destination(goldenSpike, bearing=bearing)
                if geopy.distance.distance(pt,centerCamp).feet <= centerCampPlazaRadius: 
                    cc = True
                elif geopy.distance.distance(pt,centerCamp).feet <= rodsRingRadius and name == 'Esplanade': 
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
                                'Type': 'Road',
                        }
                    }
            lineShp.write(rowDict)
            startAngle = endAngle

# radial streets
for name,r in radials.items():
    # 3:00 road from man to esplanade
    if name == '3:00':
        street = []
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
                           'Type': 'Road',
                }
            }
        lineShp.write(rowDict)
    # 9:00 road from man to esplanade
    if name == '9:00':
        street = []
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
                           'Type': 'Road',
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
                           'Type': 'Road',
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
                           'Type': 'Road',
                }
            })
        lineShp.write(rowDict)
    else:
        # these are for "normal" Esplanade-to-K streets
        start = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=r+cityOffsetAngle)
        # we do this to provide a different segment for each block.  this is important for anyone
        # using this map to do routing
        for streetName,distance in streets.items():
            if streetName == 'Esplanade':
                continue
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
                    'Type': 'Road',
                }
            }
            lineShp.write(rowDict)
            start = end

for name,r in community_paths.items():
    # these are for the :15/:45 short streets on the outer half of the city, F-K
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
                           'Type': 'Community Path',
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
                   'Type': 'Road',
        }
    }
lineShp.write(rowDict)

# various rings
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
    foo = geopy.distance.distance(feet=templeRingRadius).destination(temple, bearing=r)
    templeRing.append((foo.longitude,foo.latitude))

# for the semi-circle esplanade segment man-ward of center camp
# notes: calculate the points at [56]:30 & A
# then calculate the bearing from center-camp center to those two points
# add in city rotational offset and draw circular segments between those to points
fivethirtyAndA = geopy.distance.distance(feet=streets['A']).destination(
    goldenSpike, bearing=cityOffsetAngle+radials['5:30'])
sixthirtyAndA = geopy.distance.distance(feet=streets['A']).destination(
    goldenSpike, bearing=cityOffsetAngle+radials['6:30'])
startAngle = round(calculate_initial_compass_bearing(centerCamp, sixthirtyAndA)) # should be ~327
endAngle = round(calculate_initial_compass_bearing(centerCamp, fivethirtyAndA)) # should be ~123
if endAngle<startAngle:
    endAngle+=360
for r in range(startAngle,endAngle+1,1):
    b = r
    if b > 360:
        b-=360
    # the new Rod's Ring runs from 6:30 & A to 5:30 & A
    foo = geopy.distance.distance(feet=rodsRingRadius).destination(centerCamp, bearing=b)
    ring2.append((foo.longitude,foo.latitude))



fid+=1
mrDict = {
  'geometry': {'type':'LineString',
      'coordinates':manring},
  'properties': {'Name': 'Man Ring',
                 'FID': fid,
                 'Length': round(manRingRadius * 2 * math.pi),
                 'Type': 'Road',
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
                 'Type': 'Road',
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
                 'Type': 'Road',
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
                 'Type': 'Road',
    }
}
lineShp.write(rrDict)

#streetLength = round(GD(radialThreeStart,radialThreeEnd).feet)
#fid+=1
#rrDict = {
#  'geometry': {'type':'LineString',
#      'coordinates':radialThree},
#  'properties': {'Name': 'Center Camp 3:00 Road',
#                 'FID': fid,
#                 'Length': streetLength,
#                 'Type': 'Road',
#    }
#}
##lineShp.write(rrDict)
#
#streetLength = round(GD(radialNineStart,radialNineEnd).feet)
#fid+=1
#rrDict = {
#  'geometry': {'type':'LineString',
#      'coordinates':radialNine},
#  'properties': {'Name': 'Center Camp 9:00 Road',
#                 'FID': fid,
#                 'Length': streetLength,
#                 'Type': 'Road',
#    }
#}
#lineShp.write(rrDict)

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
                 'Type': 'Trash Fence',
        }
    }
    lineShp.write(trashFence)

## below here, we're creating routes, not actual roads.  This facilitates Djikstra-style
## routing algorithms.  Inside the city, we have to stick to roads.  In inner plays, 
## the whole surface is basically a shortcut.
## to generate, comment out the exit() line below
sys.exit(0)

visited = []
for startName,startR in radials.items():
    for endName, endR in radials.items():
        if startName == endName:
            continue
        if endName in visited:
            continue
        ## first we do esplanade to esplanade routes
        route = []
        routeStart = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=startR+cityOffsetAngle)
        routeEnd = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=endR+cityOffsetAngle)
        route.append((routeStart.longitude, routeStart.latitude))
        route.append((routeEnd.longitude, routeEnd.latitude))
        routeLength = round(GD(routeStart,routeEnd).feet)
        fid+=1
        routeName=f"{startName}-{endName}"
        playaRoute = { 
        'geometry': {'type':'LineString',
            'coordinates':route},
        'properties': {'Name': routeName,
                    'FID': fid,
                    'Length': routeLength,
                    'Type': 'Route',
            }
        }
        lineShp.write(playaRoute)
    visited.append(startName)

for endName, endR in radials.items():
    # then esplanade-to-man
    route = []
    routeStart = geopy.distance.distance(feet=0).destination(goldenSpike, bearing=0+cityOffsetAngle)
    routeEnd = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=endR+cityOffsetAngle)
    route.append((routeStart.longitude, routeStart.latitude))
    route.append((routeEnd.longitude, routeEnd.latitude))
    routeLength = round(GD(routeStart,routeEnd).feet)
    fid+=1
    routeName=f"Man-{endName}"
    playaRoute = { 
    'geometry': {'type':'LineString',
        'coordinates':route},
    'properties': {'Name': routeName,
                'FID': fid,
                'Length': routeLength,
                'Type': 'Route',
        }
    }
    lineShp.write(playaRoute)

for endName, endR in radials.items():
    # then esplanade to temple
    route = []
    routeStart = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=0+cityOffsetAngle)
    routeEnd = geopy.distance.distance(feet=streets['Esplanade']).destination(goldenSpike, bearing=endR+cityOffsetAngle)
    route.append((routeStart.longitude, routeStart.latitude))
    route.append((routeEnd.longitude, routeEnd.latitude))
    routeLength = round(GD(routeStart,routeEnd).feet)
    fid+=1
    routeName=f"Temple-{endName}"
    playaRoute = { 
    'geometry': {'type':'LineString',
        'coordinates':route},
    'properties': {'Name': routeName,
                'FID': fid,
                'Length': routeLength,
                'Type': 'Route',
        }
    }
    lineShp.write(playaRoute)

# finally, close the routes at the open end of the city
for sName, sDist in streets.items():
    for eName, eDist in streets.items():
        if sName == eName:
            continue
        route =[]
        routeStart=geopy.distance.distance(feet=sDist).destination(goldenSpike, bearing=radials['2:00']+ cityOffsetAngle)
        routeEnd=geopy.distance.distance(feet=eDist).destination(goldenSpike, bearing=radials['10:00']+ cityOffsetAngle)
        route.append((routeStart.longitude, routeStart.latitude))
        route.append((routeEnd.longitude, routeEnd.latitude))
        routeLength = round(GD(routeStart,routeEnd).feet)
        fid+=1
        routeName=f"2:00&{sName}-10:00&{eName}"
        playaRoute = { 
            'geometry': {
                'type':'LineString',
                'coordinates':route
            },
            'properties': {
                'Name': routeName,
                'FID': fid,
                'Length': routeLength,
                'Type': 'Route',
            }
        }
        lineShp.write(playaRoute)

lineShp.close()
