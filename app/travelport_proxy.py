import httplib
import zlib
import base64
import StringIO
from lxml import etree

from uapi_air import parse
from uapi_air import *

class TravelportProxy(object):
    def __init__(self, url, host, username, password, target_branch, gds_provider):
        self.url = url
        self.host = host
        self.username = username
        self.password = password
        self.target_branch = target_branch
        #self.b64_credentials = (base64.encodestring('%s:%s' % (self.username, self.password)))
        self.b64_credentials = (base64.b64encode('%s:%s' % (self.username, self.password))).decode('utf-8')
        self.gds_provider = gds_provider
   
   

   
    def SOAP_post(self, req, service='AirService'):
        """Handles making the SOAP request"""

        conn = httplib.HTTPSConnection(self.host)

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'Connection':'close',
            'Content-length': ('%s' % len(req)),
            'SOAPAction': '',
            'Authorization': 'Basic %s' % self.b64_credentials,
            'Accept-Encoding': 'gzip,deflate'
        }

        #print '*'*20 + ' REQUEST ' + '*'*20
        #print req
        resp = ''
        try:
            conn.request("POST", '%s/%s' % (self.url, service), req, headers)
            http_response = conn.getresponse()
            
            print http_response
            
            if http_response.msg.get("content-encoding","") == "gzip":
                resp=zlib.decompress(http_response.read(), 16+zlib.MAX_WBITS)
      
            else:
                resp = http_response.read()

            #print resp
            #print resp[0:min(len(resp), 3000)]
            #print http_response.status, http_response.version
                
            return resp
        except Exception, ex:
            print 'RESPONSE:'
            print resp
            print "Exception: %s" % (ex)
            return None
        finally:
            conn.close()

    ''' REQUEST METHODS '''

    def create_air_request(self, orig, dest, dep_date, ret_date=None, rt=True, is_radius=False, incl_GDS=True, incl_lowcost=True, incl_rails=True):
        req_str = None
        buf = None

        try:
            req_obj = LowFareSearchReq()
            req_obj.set_TargetBranch(self.target_branch)

            # Deparure air leg
            req_obj.add_SearchAirLeg(self._get_leg(orig, dest, dep_date, is_radius))

            # Return air leg
            if rt:
                req_obj.add_SearchAirLeg(self._get_leg(dest, orig, ret_date, is_radius))

            # Air search modifiers
            air_sm = AirSearchModifiers()
            pref_providers = PreferredProvidersType()
            if incl_GDS:
                pref_providers.add_Provider(Provider(self.gds_provider))

            if incl_lowcost:
                pref_providers.add_Provider(Provider('ACH'))
            if incl_rails:
                pref_providers.add_Provider(Provider('RCH'))
            air_sm.set_PreferredProviders(pref_providers)
            air_sm.set_MaxSolutions(200)
            req_obj.set_AirSearchModifiers(air_sm)

            # Passengers
            req_obj.add_SearchPassenger(SearchPassenger("ADT"))

            buf = StringIO.StringIO()
            req_obj.export(buf, 0)
            req_str = '%s%s%s' % (
                '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"> \
                  <s:Header><Action s:mustUnderstand="1" xmlns="http://schemas.microsoft.com/ws/2005/05/addressing/none" /></s:Header> \
                  <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">',
                  buf.getvalue(),
                  '</s:Body></s:Envelope>')
        except Exception, ex:
            print 'create_air_request :: Unexpected exception :: %s', ex
        finally:
            if buf:
                buf.close()

        return req_str

    def create_rail_request(self, orig, dest, dep_date, ret_date=None, rt=True, is_radius=False):
        req_str = None
        buf = None

        try:
            req_obj = RailAvailabilitySearchReq()
            req_obj.set_TargetBranch(self.target_branch)
            req_obj.set_BillingPointOfSaleInfo(BillingPointOfSaleInfo(OriginApplication='uAPI'))

            # Deparure air leg
            req_obj.add_SearchRailLeg(self._get_rail_leg(orig, dest, dep_date, is_radius))

            # Return air leg
            if rt:
                req_obj.add_SearchRailLeg(self._get_rail_leg(dest, orig, ret_date, is_radius))

            # Air search modifiers
            rail_sm = RailSearchModifiers()
            rail_sm.set_MaxSolutions(200)
            req_obj.set_RailSearchModifiers(rail_sm)

            # Passengers
            req_obj.add_SearchPassenger(SearchPassenger_v14("ADT"))

            buf = StringIO.StringIO()
            req_obj.export(buf, 0)
            req_str = '%s%s%s' % (
                '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"> \
                  <s:Header><Action s:mustUnderstand="1" xmlns="http://schemas.microsoft.com/ws/2005/05/addressing/none" /></s:Header> \
                  <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">',
                  buf.getvalue(),
                  '</s:Body></s:Envelope>')
        except Exception, ex:
            print 'create_rail_request :: Unexpected exception :: %s', ex
        finally:
            if buf:
                buf.close()

        return req_str

    def send_air_request(self, req_str):
        return self._send_request(req_str, './/{http://www.travelport.com/schema/air_v16_0}LowFareSearchRsp', 'AirService')

    def send_rail_request(self, req_str):
        return self._send_request(req_str, './/{http://www.travelport.com/schema/rail_v11_0}RailAvailabilitySearchRsp', 'RailService')

    def _send_request(self, req_str, root_name, service):
        resp_str = None
        try:
            resp_str = self.SOAP_post(req_str, service)
            root = etree.XML(resp_str)
            resp_body = root.find(root_name)
            if resp_body is not None and len(resp_body) > 0:
                resp_str = etree.tostring(resp_body)
        except Exception, ex:
            print 'RESPONSE:'
            print resp_str
            print 'send_request :: Unexpected exception :: %s', ex

        return resp_str

    def _get_rail_leg(self, orig, dest, date, is_radius):
        rail_leg = SearchRailLeg()

        search_origin = typeSearchLocation(RailLocation=RailLocation(Code=orig))
        if is_radius:
            search_origin.set_Distance(Distance(Value=100))
        rail_leg.add_SearchOrigin(search_origin)

        search_destination = typeSearchLocation(RailLocation=RailLocation(Code=dest))
        if is_radius:
            search_destination.set_Distance(Distance(Value=100))
        rail_leg.add_SearchDestination(search_destination)
        rail_leg.add_SearchDepTime(typeFlexibleTimeSpec(PreferredTime=date))

        return rail_leg

    def _get_leg(self, orig, dest, date, is_radius):
        air_leg = SearchAirLeg()
        
        if is_radius:
            search_origin = typeSearchLocation(Airport=Airport(Code=orig))
            search_origin.set_Distance(Distance(Value=100))
        else:
            search_origin = typeSearchLocation(CityOrAirport=CityOrAirport(Code=orig, PreferCity=True))
        air_leg.add_SearchOrigin(search_origin)

        if is_radius:
            search_destination = typeSearchLocation(Airport=Airport(Code=dest))
            search_destination.set_Distance(Distance(Value=100))
        else:
            search_destination = typeSearchLocation(CityOrAirport=CityOrAirport(Code=dest, PreferCity=True))
        air_leg.add_SearchDestination(search_destination)

        air_leg.add_SearchDepTime(typeFlexibleTimeSpec(PreferredTime=date))
        air_leg_modifiers = AirLegModifiers()
        air_leg_modifiers.set_PreferredCabins(PreferredCabinsType(CabinClass('Economy')))

        return air_leg

    ''' RESPOSNE METHODS '''
    def response_to_obj(self, resp_str):
        resp_obj = None
        buf = None
        try:
            buf = StringIO.StringIO()
            buf.write(resp_str)
            buf.seek(0)
            resp_obj = parse(buf)
        except Exception, ex:
            print 'response_to_obj :: Unexpected exception :: %s', ex
        finally:
            if buf:
                buf.close()

        return resp_obj

    ''' PING REQUEST '''
    def ping(self):
    
        ping_req = '<?xml version="1.0" encoding="utf-8"?> \
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" > \
            <soapenv:Header/> \
            <soapenv:Body> \
            <sys:PingReq TraceId="test" xmlns:sys="http://www.travelport.com/schema/system_v8_0"> \
            <sys:Payload>this is a test for testing</sys:Payload> \
            </sys:PingReq> \
            </soapenv:Body> \
            </soapenv:Envelope>'
        print ping_req
        
        resp = self.SOAP_post(ping_req, 'SystemService')
        print '%s %s %s' % ('*'*20, 'PING RESPONSE', '*'*20)
        print resp
