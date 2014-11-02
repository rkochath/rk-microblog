import xml.etree.ElementTree as ET
from flask import jsonify,json
from collections import *
from datetime import *
from dateutil.parser import *

def traverse_flightsegments(root, segmentreflist, totalprice,price_key):
        #Get all the AirSegments filtered and take their attributes into a list
        segmentlist = [airsegment.attrib for airsegment in root.iter("{http://www.travelport.com/schema/air_v16_0}AirSegment")]
        legs=[]
        #Construct a key list from the airsegment list
        sl = [x['Key'] for x in segmentlist]

        #loop through the segmentrefs for a given pricing solution and build a segment index list
        #Eg.
        #leg index  [0, 1, 2]
        #leg index  [0, 1, 3]
        #leg index  [4, 5, 6, 7]
        #leg index  [4, 8, 9, 6, 7]
        for segment in segmentreflist:
             legs.append(  sl.index(segment))
        #Use an ordered dict over regular dict to preserve order of insertion                     
        results=OrderedDict()
        
        outbound_stops=0
        return_stops=0
        outbound_triptime=0
        return_triptime = 0
        return_legindex = 0

        for leg in legs:
            if segmentlist[leg]['Group'] == '0' :
                 outbound_stops +=1
                 outbound_triptime += int(segmentlist[leg]['FlightTime'])
                 if legs.index(leg) > 0:
                      time_diff = (parse(segmentlist[leg]['DepartureTime'] ) - parse(prev_leg_arrival) )
                      outbound_triptime += time_diff.days*24*60 + time_diff.seconds/60
                      
                 
            else:     
                 return_stops +=1
                 return_triptime += int(segmentlist[leg]['FlightTime'])
                 if return_legindex == 0:
                     return_legindex = legs.index(leg) 
                     
                 if legs.index(leg) > return_legindex:
                      time_diff = (parse(segmentlist[leg]['DepartureTime'] ) - parse(prev_leg_arrival) )
                      return_triptime += time_diff.days*24*60 + time_diff.seconds/60

            prev_leg_arrival = segmentlist[leg]['ArrivalTime']

        #Keys are carried over to the dict to maintain uniqueness
        header = '{"%s": {"Total Price":"%s", "OB Stops":"%s","OB Time":"%s","RT Stops":"%s","RT Time":"%s" }}' % (price_key, totalprice,outbound_stops-1,outbound_triptime,return_stops -1,return_triptime )
        #Use json loads to convert string to dict. use update dict method to add newly formed price info to the dict
        results.update(json.loads(header))

        
        #capture additional attriutes for each leg from the segment attribute list
        for leg in legs:
            row = '{"%s": {"FlightDetails":"%s", "Carrier":"%s", "FlightNumber":"%s","Origin":"%s","Destination":"%s", "DepartureTime":"%s","ArrivalTime":"%s", "FlightTime":"%s","Distance":"%s"}}' % ( price_key+ segmentlist[leg]['Key'], segmentlist[leg]['Key'], segmentlist[leg]['Carrier'],segmentlist[leg]['FlightNumber'], segmentlist[leg]['Origin'],segmentlist[leg]['Destination'], segmentlist[leg]['DepartureTime'], segmentlist[leg]['ArrivalTime'],segmentlist[leg]['FlightTime'],segmentlist[leg]['Distance'])
            
            #add the leg attributes into the dict
            results.update(json.loads(row))
            
        return results            
            
                
def traverse_pricesolutions(nodes,searchtag,  root , results , segmentreflist=[],segment_used=False,total_price=0,price_key = 0 ):
        #Traverse each node in the tree to get the airpricing solution and the segmentrefs under the airpricing solution
        for node in nodes:
               
                if node is not None:
                         if node.tag == "{http://www.travelport.com/schema/air_v16_0}AirPricingSolution":
                                 
                                #while len(segmentreflist) > 0:
                                #       segmentreflist.pop(0)
                                segmentreflist=[]           
                                total_price = node.attrib['TotalPrice']
                                price_key = node.attrib['Key']
                                
                         
                         searchstr = ("[@%s]" % searchtag)  #Search all child nodes which has SegmentRef
                         #findall returns an array
                         result = node.findall(searchstr)
                               
                         if len(result) == 0 :
                               if len(segmentreflist) > 0 :
                                    results.update(traverse_flightsegments(root,segmentreflist,total_price,price_key ) )
                                    #while len(segmentreflist) > 0:
                                    #           segmentreflist.pop(0)
                                    segmentreflist=[]

                               #recursively traverse the nodes
                               traverse_pricesolutions(node, searchtag, root, results, segmentreflist, segment_used,total_price, price_key)
                         else: #capture the segmentrefs under the airpricing solution
                               segmentreflist.append( result[0].attrib['SegmentRef'])
                                     

        return results
                                     
'''
results=OrderedDict()
tree = ET.parse(  './uploads/tp1.xml') 
root = tree.getroot()

results = traverse_pricesolutions(root,'SegmentRef',root,results)
file = open('./uploads/tp1_out.xml' ,'w')



for leg in results:
        
        if 'Total Price' in results[leg]:
            #print results[leg]['Total Price']
            file.write("Total Price %s\n"%results[leg]['Total Price'])


        else:
            file.write("Origin: %s Destination: %s \n" %(results[leg]['Origin'], results[leg]['Destination'] ))
            #print results[leg]['Origin'], results[leg]['Destination']    

file.close()
'''
'''        
LAX - JFK return
        GBP277.50
                LAX DEN
                DEN LGA
                JFK LAX
        GBP277.50
                LAX DEN
                DEN LGA
                JFK LAX
        GBP513.90
                BUR PHX
                PHX JFK
                JFK SLC
                SLC LGB
        GBP516.40
                BUR PHX
                PHX PHL
                PHL LGA
                JFK SLC
                SLC LGB
'''

