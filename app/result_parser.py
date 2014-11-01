from hs_travelportapp.home.models import Airline, UCode
from datetime import datetime

PARSE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
FORMATTING_DATE_FORMAT = '%d %b'
FORMATTING_TIME_FORMAT = '%H:%M'
AIRLINE_CACHE = {}
AIRPORT_CACHE = {}
RAILS_CACHE = {}

class ResultParser(object):
    def __init__(self, resp_obj):
        self.resp_obj = resp_obj
        self.resp_json = {
            'air': {},
            'rail': {},
        }
        self._airports = {}
        self._airlines = {}
        self._rails = {}
        self._segment_cxrs = {}
        self._air_matrix = {}
        self._via = {}

    def get_json(self, key_prefix=''):
        try:
            resp_type = str(type(self.resp_obj))
            if 'LowFareSearchRsp' in resp_type:
                # Errors, Warnings, Info messages
                response_messages = self.resp_obj.get_ResponseMessage()
                self._init_response_messages(self.resp_json, response_messages)
    
                # Flights
                response_flights = self.resp_obj.get_FlightDetailsList()
                if response_flights:
                    response_flights = response_flights.get_FlightDetails()
                    self._init_flights(self.resp_json, response_flights)
    
                # Segments
                response_segments = self.resp_obj.get_AirSegmentList()
                if response_segments:
                    response_segments = response_segments.get_AirSegment()
                    self._init_segments(self.resp_json, response_segments)
    
                # Air Solutions
                response_solutions = self.resp_obj.get_AirPricingSolution()
                self._init_solutions(self.resp_json, response_solutions)
    
                # Airports and Airlines
                self.resp_json['air']['airports'] = self._airports
                self.resp_json['air']['airlines'] = self._airlines
                self.resp_json['air']['matrix'] = self._air_matrix
                self.resp_json['air']['via'] = self._via
                
            elif 'RailAvailabilitySearchRsp' in str(type(self.resp_obj)):
                # Errors, Warnings, Info messages
                response_messages = self.resp_obj.get_ResponseMessage()
                self._init_response_messages(self.resp_json, response_messages, 'rail')

            if 'LowFareSearchRsp' in resp_type or \
                'RailAvailabilitySearchRsp' in resp_type: 
                # Rail segments
                response_rail_segments = self.resp_obj.get_RailSegmentList()
                if response_rail_segments:
                    response_rail_segments = response_rail_segments.get_RailSegment()
                    self._init_rail_segments(self.resp_json, response_rail_segments, key_prefix)
        
                # Rail journeys
                response_rail_journeys = self.resp_obj.get_RailJourneyList()
                if response_rail_journeys:
                    response_rail_journeys = response_rail_journeys.get_RailJourney()
                    self._init_rail_journeys(self.resp_json, response_rail_journeys, key_prefix)
        
                # Rail solutions
                response_rail_solutions = self.resp_obj.get_RailPricingSolution()
                if response_rail_solutions:
                    self._init_rail_solutions(self.resp_json, response_rail_solutions, key_prefix)
        
                # Rails
                self.resp_json['rail']['coords'] = self._rails

        except Exception, ex:
            print 'response_to_json :: get_json :: Unexpected exception :: %s', ex
        return self.resp_json

    def _fill_rails(self, codes):
        if not isinstance(codes, list):
            codes = [codes]
        for i in range(len(codes)-1, -1, -1):
            code = codes[i]
            if not code or code in self._rails:
                codes.pop(i)
            elif code in RAILS_CACHE:
                self._rails[code] = RAILS_CACHE[code]
                codes.pop(i)
        if (not codes):
            return

        try:
            rails = UCode.objects.filter(ucode__in=codes)
            for r in rails:
                ucode = r.ucode.strip()
                RAILS_CACHE[ucode] = self._rails[ucode] = {'lat':str(r.latitude), 'lng':str(r.longitude)}
        except Exception, ex:
            print codes, "not in known ucodes", ex

    def _fill_airlines(self, codes):
        if not isinstance(codes, list):
            codes = [codes]
        for i in range(len(codes)-1, -1, -1):
            code = codes[i]
            if not code or code in self._airlines:
                codes.pop(i)
            elif code in AIRLINE_CACHE:
                self._airlines[code] = AIRLINE_CACHE[code]
                codes.pop(i)
        if (not codes):
            return

        try:
            airlines = Airline.objects.filter(code__in=codes)
            for airline in airlines:
                code = airline.code.strip()
                AIRLINE_CACHE[code] = self._airlines[code] = airline.name
        except Exception, ex:
            print codes, "not in known airlines", ex

    def _fill_airports(self, codes):
        if not isinstance(codes, list):
            codes = [codes]
        for i in range(len(codes)-1, -1, -1):
            code = codes[i].strip()
            if not code or code in self._airports:
                codes.pop(i)
            elif code in AIRPORT_CACHE:
                self._airports[code] = AIRPORT_CACHE[code]
                codes.pop(i)
        if (not codes):
            return
        try:
            codes_copy = list(codes)
            airports = UCode.objects.filter(st_type=1, iata_code__in=codes)
            for arpt in airports:
                arpt_obj = {
                    "s": "%s" % arpt.city,
                    "l": "%s, %s, %s" % (arpt.name, arpt.city, arpt.country),
                    "lng": str(arpt.longitude),
                    "lat": str(arpt.latitude)
                }
                code = arpt.iata_code.strip()
                AIRPORT_CACHE[code] = self._airports[code] = arpt_obj
                codes_copy.remove(code)

            for c in codes_copy:
                AIRPORT_CACHE[c] = self._airports[c] = {"s": c, "l": c}

        except Exception, ex:
            print codes, "not in known airports", ex

    def _init_rail_solutions(self, resp_json, response_rail_solutions, key_prefix):
        results = []

        journeys = resp_json['rail']['journeys']
        segments = resp_json['rail']['segments']
        oc_names = []

        for j in response_rail_solutions:
            journey_refs = j.get_RailJourneyRef()

            jref_ids = []

            for jr in journey_refs:
                key = '%s%s' % (key_prefix, jr.get_Key())
                for s in journeys[key]['seg_ref']:
                    oc_n = segments[s]['oc_name']
                    if oc_n and oc_n not in oc_names:
                        oc_names.append(oc_n)

                jref_ids.append(key)

            price = j.get_TotalPrice()
            results.append({
                'journeys': jref_ids,
                'price': price,
                'raw_p': float(price[3:]),
                'oc_names': oc_names
            })

        resp_json['rail']['results'] = results

    def _init_rail_journeys(self, resp_json, response_rail_journeys, key_prefix):
        journeys = {}

        for j in response_rail_journeys:
            dep_time = datetime.strptime(j.get_DepartureTime()[0:19], PARSE_DATE_FORMAT)
            arr_time = datetime.strptime(j.get_ArrivalTime()[0:19], PARSE_DATE_FORMAT)

            seg_refs = j.get_RailSegmentRef()
            seg_keys = []
            for sr in seg_refs:
                seg_keys.append('%s%s' % (key_prefix, sr.get_Key()))

            origin_code = j.get_Origin()
            destination_code = j.get_Destination()

            journeys['%s%s' % (key_prefix, j.get_Key())] = {
                'o': '%s%s' % (j.get_OriginStationName(), (' (%s)' % origin_code) if origin_code else ''),
                'd': '%s%s' % (j.get_DestinationStationName(), (' (%s)' % destination_code) if destination_code else ''),
                'dd':dep_time.strftime(FORMATTING_DATE_FORMAT),
                'dt':dep_time.strftime(FORMATTING_TIME_FORMAT),
                'ad':arr_time.strftime(FORMATTING_DATE_FORMAT),
                'at':arr_time.strftime(FORMATTING_TIME_FORMAT),
                'leg': 0 if j.get_JourneyDirection() == 'Outward' else 1,
                'seg_ref': seg_keys,
                'pc': j.get_ProviderCode(),
                'sc': j.get_SupplierCode()
            }

        resp_json['rail']['journeys'] = journeys

    def _init_rail_segments(self, resp_json, response_segments, key_prefix):
        segments = {}
        ucodes = []

        for s in response_segments:
            dep_time = datetime.strptime(s.get_DepartureTime()[0:19], PARSE_DATE_FORMAT)
            arr_time = datetime.strptime(s.get_ArrivalTime()[0:19], PARSE_DATE_FORMAT)

            op_company = s.get_OperatingCompany()

            origin_code = s.get_Origin()
            destination_code = s.get_Destination()

            origin_ucode = s.get_RailLocOrigin()
            destination_ucode = s.get_RailLocDestination()

            segments['%s%s' % (key_prefix, s.get_Key())] = {
                'oc_name': op_company.get_Name() if op_company is not None else '',
                'oc_code': op_company.get_Code() if op_company is not None else '',
                'tno': s.get_TrainNumber(),
                'o': '%s%s' % (s.get_OriginStationName(), (' (%s)' % origin_code) if origin_code else ''),
                'd': '%s%s' % (s.get_DestinationStationName(), (' (%s)' % destination_code) if destination_code else ''),
                'o_ucode': origin_ucode,
                'd_ucode': destination_ucode,
                'dd':dep_time.strftime(FORMATTING_DATE_FORMAT),
                'dt':dep_time.strftime(FORMATTING_TIME_FORMAT),
                'ad':arr_time.strftime(FORMATTING_DATE_FORMAT),
                'at':arr_time.strftime(FORMATTING_TIME_FORMAT),
            }

            if origin_ucode not in ucodes:
                ucodes.append(origin_ucode)

            if destination_ucode not in ucodes:
                ucodes.append(destination_ucode)

        resp_json['rail']['segments'] = segments

        self._fill_rails(ucodes)

    def _set_via(self, outbound_flights, inbound_flights, s_key):
        # set vias
        via_obj = {'o':'', 'd':'', 'via':{'out': [], 'in': []}}
        outbound_fl_len = len(outbound_flights)
        inbound_fl_len = len(inbound_flights)
        
        via_obj['o'] = outbound_flights[0]['o']
        via_obj['d'] = outbound_flights[outbound_fl_len-1]['d']
        
        for i in range(0, outbound_fl_len-1):
            via_obj['via']['out'].append(outbound_flights[i]['d'])
            
        for i in range(0, inbound_fl_len-1):
            via_obj['via']['in'].append(inbound_flights[i]['d'])
        
        
        if len(via_obj['via']['out']) == len(via_obj['via']['in']):
            same_via = True
            for via in via_obj['via']['in']:
                if via not in via_obj['via']['out']:
                    same_via = False
        else:
            same_via = False
        if same_via:
            via_obj['via']['in'] = []
            
        self._via[s_key] = via_obj

    def _init_solutions(self, resp_json, response_solutions):
        solutions = []

        segments_list = []
        flights_list = []
        if 'segments' in resp_json['air']:
            segments_list = resp_json['air']['segments']
        if 'flights' in resp_json['air']:
            flights_list = resp_json['air']['flights']

        lc_outbound_routing_opt = []
        lc_inbound_routing_opt = []
        
        for s in response_solutions:
            s_key = s.get_Key()
            sol_segments = s.get_AirSegmentRef()
            api = s.get_AirPricingInfo()[0]
            binfo = api.get_BookingInfo()

            tmp_segments_class = {}
            for bi in binfo:
                tmp_segments_class[bi.get_SegmentRef()] = bi.get_BookingCode()

            provider_code = api.get_ProviderCode()
            
            if not provider_code == 'ACH': # GDS

                segments = []
                cur_seg = None
                flights_per_dir = {'inbound_flights':[], 'outbound_flights':[]}
                #via_obj = {'o':'', 'd':'', 'via':{'out': [], 'in': []}}              
                
                for ss in sol_segments:
                    key = ss.get_Key()
                    segments.append({'key': key, 'class': tmp_segments_class[key] })
                    cur_seg = segments_list[key]
                    f_list = []

                    # set inbound and outbound flights
                    for f_ref in cur_seg['f_ref']:
                        f_list.extend([{'o': flights_list[f_ref]['o'], 'd': flights_list[f_ref]['d']}])
                    if cur_seg['leg'] == 0:
                        flights_per_dir['outbound_flights'].extend(f_list)
                    else:
                        flights_per_dir['inbound_flights'].extend(f_list)

                    # update matrix
                    segment_cxr = self._segment_cxrs[key]
                    if segment_cxr not in self._air_matrix:
                        self._air_matrix[segment_cxr] = []
                    if s_key not in self._air_matrix[segment_cxr]:
                        self._air_matrix[segment_cxr].append(s_key)
                        
                self._set_via(flights_per_dir['outbound_flights'], flights_per_dir['inbound_flights'], s_key)

                cxr = api.get_PlatingCarrier()
                solutions.append({
                    'key': s_key,
                    'segments': segments,
                    'price': s.get_TotalPrice(),
                    'cxr': [cxr]
                })

            else: # lowcosts

                cxr = api.get_SupplierCode()
                connections = s.get_Connection()
                connecting_segments = []
                for sc in connections:
                    connecting_segments.append(sc.get_SegmentIndex)

                seg_len = len(sol_segments)
                curr_routing_segments = []
                for i in range(0, seg_len):
                    ss = sol_segments[i]
                    key = ss.get_Key()
                    leg = segments_list[key]['leg']

                    curr_routing_segments.append({'key': key, 'class': tmp_segments_class[key] })

                    if i not in connecting_segments:
                        price = s.get_TotalPrice()
                        raw_price = float(price[3:])
                        rtg_option = {'segments': curr_routing_segments, 'price': price, 'raw_p': raw_price, 'cxr': cxr}
                        
                        if leg == 0:
                            lc_outbound_routing_opt.append(rtg_option)
                        else:
                            lc_inbound_routing_opt.append(rtg_option)
                        curr_routing_segments = []

        sol_key = 0
        lc_solutions = []
        
        # Restrict the low cost combinations to top 100 cheapest
        lc_outbound_routing_opt = sorted(lc_outbound_routing_opt, key=lambda x: x['raw_p'])[:10]
        lc_inbound_routing_opt = sorted(lc_inbound_routing_opt, key=lambda x: x['raw_p'])[:10]
        
        for oro in lc_outbound_routing_opt:
            for s in oro['segments']:
                cur_seg = segments_list[s['key']]
                f_list = []
                for f_ref in cur_seg['f_ref']:
                    f_list.extend([{'o': flights_list[f_ref]['o'], 'd': flights_list[f_ref]['d']}])
                
                oro['flights'] = f_list

        for iro in lc_inbound_routing_opt:
            for s in iro['segments']:
                cur_seg = segments_list[s['key']]
                f_list = []
                for f_ref in cur_seg['f_ref']:
                    f_list.extend([{'o': flights_list[f_ref]['o'], 'd': flights_list[f_ref]['d']}])
                
                iro['flights'] = f_list
        
        for lc_outb_rtg_opt in lc_outbound_routing_opt:
            for lc_inb_rtg_opt in lc_inbound_routing_opt:
                segments = []
                segments.extend(lc_outb_rtg_opt['segments'])
                segments.extend(lc_inb_rtg_opt['segments'])

                sol_key = sol_key + 1
                key = 'LC_%d' % sol_key
                cxrs = []
                if lc_outb_rtg_opt['cxr'] not in cxrs:
                    cxrs.append(lc_outb_rtg_opt['cxr'])

                if lc_inb_rtg_opt['cxr'] not in cxrs:
                    cxrs.append(lc_inb_rtg_opt['cxr'])

                raw_price = lc_outb_rtg_opt['raw_p'] + lc_inb_rtg_opt['raw_p']
                currency = lc_outb_rtg_opt['price'][0:3]
                
                self._set_via(lc_outb_rtg_opt['flights'], lc_inb_rtg_opt['flights'], key)

                lc_solutions.append({
                    'key': key,
                    'segments': segments,
                    'price': '%s%.2f' % (currency, raw_price),
                    'raw_price': raw_price,
                    'cxr': cxrs
                })

                for c in cxrs:
                    if c not in self._air_matrix:
                        self._air_matrix[c] = []
                    if key not in self._air_matrix[c]:
                        self._air_matrix[c].append(key)

        solutions.extend(sorted(lc_solutions, key=lambda x: x['raw_price']))
        resp_json['air']['results'] = solutions

    def _init_segments(self, resp_json, response_segments):
        segments = {}
        airports = []
        airlines = []

        for s in response_segments:
            dep_time = datetime.strptime(s.get_DepartureTime()[0:19], PARSE_DATE_FORMAT)
            arr_time = datetime.strptime(s.get_ArrivalTime()[0:19], PARSE_DATE_FORMAT)

            seg_flights = s.get_FlightDetailsRef()
            flight_refs = []
            for sf in seg_flights:
                flight_refs.append(sf.get_Key())

            seg_ai = s.get_AirAvailInfo()
            seg_providers = []
            for sai in seg_ai:
                seg_providers.append(sai.get_ProviderCode())

            orig = s.get_Origin()
            dest = s.get_Destination()
            cxr = s.get_Carrier()
            key = s.get_Key()

            segments[key] = {
                'cxr': cxr,
                'fno': s.get_FlightNumber(),
                'o': orig,
                'd': dest,
                'dd':dep_time.strftime(FORMATTING_DATE_FORMAT),
                'dt':dep_time.strftime(FORMATTING_TIME_FORMAT),
                'ad':arr_time.strftime(FORMATTING_DATE_FORMAT),
                'at':arr_time.strftime(FORMATTING_TIME_FORMAT),
                'f_ref': flight_refs,
                'pc': seg_providers,
                'leg': s.get_Group()
            }

            self._segment_cxrs[key] = cxr

            if orig not in airports:
                airports.append(orig)
            if dest not in airports:
                airports.append(dest)
            if cxr not in airlines:
                airlines.append(cxr)

        self._fill_airlines(airlines)
        self._fill_airports(airports)

        resp_json['air']['segments'] = segments

    def _init_flights(self, resp_json, response_flights):
        flights = {}
        airports = []
        for f in response_flights:
            dep_time = datetime.strptime(f.get_DepartureTime()[0:19], PARSE_DATE_FORMAT)
            arr_time = datetime.strptime(f.get_ArrivalTime()[0:19], PARSE_DATE_FORMAT)

            orig = f.get_Origin()
            dest = f.get_Destination()

            travel_time = f.get_TravelTime()
            hours = travel_time // 60
            min =  travel_time % 60

            flights[f.get_Key()] = {
                'o': orig,
                'd': dest,
                'dd':dep_time.strftime(FORMATTING_DATE_FORMAT),
                'dt':dep_time.strftime(FORMATTING_TIME_FORMAT),
                'ad':arr_time.strftime(FORMATTING_DATE_FORMAT),
                'at':arr_time.strftime(FORMATTING_TIME_FORMAT),
                'ft':f.get_FlightTime(),
                'o_ter': f.get_OriginTerminal(),
                'd_ter': f.get_DestinationTerminal(),
                'time': '%sh %sm' % (hours, min)
            }

            if orig not in airports:
                airports.append(orig)
            if dest not in airports:
                airports.append(dest)

        self._fill_airports(airports)

        resp_json['air']['flights'] = flights

    def _init_response_messages(self, resp_json, response_messages, section='air'):
        errors = []
        warnings = []
        infos = []
        for rm in response_messages:
            t = rm.get_Type()
            msg = {'pc': rm.get_ProviderCode(),
                   'sc': rm.get_SupplierCode(),
                   'c': rm.get_Code(),
                   'msg': rm.get_valueOf_()
            }
            if t == 'Error':
                errors.append(msg)
            elif t == 'Warning':
                warnings.append(msg)
            else:
                infos.append(msg)

            if errors:
                resp_json[section]['errors'] = errors
            if warnings:
                resp_json[section]['warnings'] = warnings
            if infos:
                resp_json[section]['infos'] = infos