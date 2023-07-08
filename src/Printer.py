import random
from zebra import Zebra
import time
import json

__author__ = "Simon Heck"

class Printer:
    def __init__(self, acrft_json) -> None:
        #Pull RECAT database
        self.recat_db = acrft_json
        self.zebra = Zebra()
        Q = self.zebra.getqueues()
        self.zebra.setqueue(Q[0])
        pass

    def input_callsign():
        callsign = input("Enter Callsign: ")
        return callsign.upper()

    def print_callsign_data(self, callsign_data, requested_callsign, control_area):
        
        # callsign_data = self.data_collector.get_callsign_data(requested_callsign)
        if requested_callsign == "" or None:
            print("blank")
            # print blank strip
            self.zebra.output(f"^XA^CWK,E:FLIGHTPROGRESSSTRIP.TTF^XZ^XA^AKN,50,70^CFC,40,40~TA000~JSN^LT0^MNN^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI27^PA0,1,1,0^XZ^XA^MMT^PW203^LL1624^LS-20^FO0,1297^GB203,4,4^FS^FO0,972^GB203,4,4^FS^FO0,363^GB203,4,4^FS^FO0,242^GB203,4,4^FS^FO0,120^GB203,4,4^FS^FO66,0^GB4,365,4^FS^FO133,0^GB4,365,4^FS^FO133,1177^GB4,122,4^FS^FO66,1177^GB4,122,4^FS^FB140,1,0,L^FO5,1470^FD^AKb,35,35^FS^FB200,1,0,L^FO60,1400^FD^AKb,35,35^FS^FO130,1530^FD^FS^FB200,1,0,R^FO45,1320^FD^AKb,80,80^FS^FO5,1200^FD^AKb,35,35^FS^FO80,1190^FD^AKb,35,35^FS^FO145,1220^FD^AKb,35,35^FS^FO5,1050^FD^AKb,35,35^FS^FB500,1,0,L^FO5,450^FD^AKb,35,35^FS^FB500,1,0,L^FO70,450^FD^AKb,35,35^FS^^FB500,1,0,L^FO135,450^FD^AKb,35,35^FS^FO0,1175^GB203,4,4^FS^PQ1,0,1,Y^XZ")

        elif callsign_data is not None and (control_area['type'] == "CD" or control_area['type'] == "COMBINED"):
            callsign = callsign_data['callsign']
            departure_airport = callsign_data['flight_plan']['departure']
            ac_type = callsign_data['flight_plan']['aircraft_faa']
            ac_type = self.format_actype(ac_type)
            departure_time = f"P{callsign_data['flight_plan']['deptime']}"
            cruise_alt = self.format_cruise_altitude(callsign_data['flight_plan']['altitude'])
            flightplan = self.format_flightplan(callsign_data['flight_plan']['route'], departure_airport, callsign_data['flight_plan']['flight_rules'])
            assigned_sq = callsign_data['flight_plan']['assigned_transponder']
            destination = callsign_data['flight_plan']['arrival']
            remarks=callsign_data['flight_plan']['remarks']
            remarks = self.format_remarks(callsign_data['flight_plan']['remarks'])
            enroute_time = callsign_data['flight_plan']['enroute_time']
            cid = ""
            if control_area['hasBarcode']: #If it should have the barcode, format it here.
                cid = f"^FO110,1340^BCB,70,N,N,N,A^FD{callsign_data['cid']}"
            exit_fix = self.match_ATL_exit_fix(flightplan)
            computer_id = self.generate_id(callsign_data['flight_plan']['remarks'])
            amendment_number = str(int(callsign_data['flight_plan']['revision_id'])-1)
            if amendment_number == '0':
                amendment_number = ""

            #print flight strip on printer     
            print(f"{callsign}, {departure_airport}, {ac_type}, {departure_time}, {cruise_alt}, {flightplan}, {assigned_sq}, {destination}, {enroute_time}, {cid}, {exit_fix}, {computer_id}, {amendment_number}, {remarks}")
            # zebra.output(f"^XA^CWK,E:FLIGHTPROGRESSSTRIP.TTF^XZ^XA^AKN,50,70^CFC,40,40~TA000~JSN^LT0^MNN^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI27^PA0,1,1,0^XZ^XA^MMT^PW203^LL1624^LS-20^FO0,1297^GB203,4,4^FS^FO0,972^GB203,4,4^FS^FO0,363^GB203,4,4^FS^FO0,242^GB203,4,4^FS^FO0,120^GB203,4,4^FS^FO66,0^GB4,365,4^FS^FO133,0^GB4,365,4^FS^FO133,1177^GB4,122,4^FS^FO66,1177^GB4,122,4^FS^FB250,1,0,L^FO5,1350^FD{callsign}^AKb,35,35^FS^FB200,1,0,L^FO70,1400^FD{ac_type}^AKb,35,35^FS^FO130,1540^FD{computer_id}^AKb,35,35^FS^FO130,1320^BCB,40,N,N,N,A^FD{cid}^FS^FB200,1,0,R^AKb,45,45^FO45,1320^FD{exit_fix}^AKb,80,80^FS^FO5,1200^FD{assigned_sq}^AKb,35,35^FS^FO80,1190^FD{departure_time}^AKb,35,35^FS^FO145,1220^FD{cruise_alt}^AKb,35,35^FS^FO5,1050^FD{departure_airport}^AKb,35,35^FS^FB500,1,0,L^FO5,450^FD{flightplan}^AKb,35,35^FS^FB500,1,0,L^FO70,450^FD{destination}^AKb,35,35^FS^^FB500,1,0,L^FO135,450^FD{remarks}^AKb,35,35^FS^FO0,1175^GB203,4,4^FS^PQ1,0,1,Y^XZ")
            # zebra.output(f"^XA^CWK,E:FLIGHTPROGRESSSTRIP.TTF^XZ^XA^AKN,50,70^CFC,40,40~TA000~JSN^LT0^MNN^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI27^PA0,1,1,0^XZ^XA^MMT^PW203^LL1624^LS-20^FO0,1297^GB203,4,4^FS^FO0,972^GB203,4,4^FS^FO0,363^GB203,4,4^FS^FO0,242^GB203,4,4^FS^FO0,120^GB203,4,4^FS^FO66,0^GB4,365,4^FS^FO133,0^GB4,365,4^FS^FO133,1177^GB4,122,4^FS^FO66,1177^GB4,122,4^FS^FB250,1,0,L^FO5,1350^FD{callsign}^AKb,35,35^FS^FB200,1,0,L^FO70,1400^FD{ac_type}^AKb,35,35^FS^FO130,1540^FD{computer_id}^AKb,35,35^FS{cid}^FS^FB200,1,0,R^AKb,45,45^FO35,1300^FD{exit_fix}^AKb,80,80^FS^FO5,1200^FD{assigned_sq}^AKb,35,35^FS^FO80,1190^FD{departure_time}^AKb,35,35^FS^FO145,1220^FD{cruise_alt}^AKb,35,35^FS^FO5,1050^FD{departure_airport}^AKb,35,35^FS^FB550,1,0,L^FO5,400^FD{flightplan}^AKb,35,35^FS^FB500,1,0,L^FO70,450^FD{destination}^AKb,35,35^FS^^FB500,1,0,L^FO135,450^FD{remarks}^AKb,35,35^FS^FO0,1175^GB203,4,4^FS^PQ1,0,1,Y^XZ")
            # self.print_strip(pos1=callsign, pos2=ac_type, pos3=amendment_number, pos4A=computer_id, pos4B=cid, pos2A=exit_fix, pos5=assigned_sq, pos6=departure_time, pos7=cruise_alt, pos8=departure_airport,pos9=flightplan, pos9D=destination, pos9A=remarks)

        else:
            # Zack what is this? 
            if control_area['type'] != "CD" and control_area['type'] != "COMBINED":
                return
            airfields = str.replace(str.replace(str.replace(str(list.copy(control_area['airports'])),"'",""),"[",""),"]","")
            print(f"Could not find {requested_callsign} in {airfields} proposals. Nice going, dumbass.")
    
    # TODO Redo formatting for positions
    def print_strip(self, pos1:str='', pos2:str='', pos2A:str='', pos3:str='', pos4A:str='', pos4B:str = '', 
                    pos5:str='', pos6:str='', pos7:str='', pos8:str='', pos8A:str='', pos8B='', pos9:str='', pos9A:str='', pos9B:str='', pos9C:str='', pos9D:str = ''): 
        self.zebra.output(f"""^XA^CWK,E:FLIGHTPROGRESSSTRIP.TTF^XZ
                          ^XA^AKN,50,70^CFC,40,40~TA000~JSN^LT0^MNN^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI27^PA0,1,1,0^XZ
                          ^XA^MMT^PW203^LL1624^LS-20^FO0,1297^GB203,4,4^FS
                          ^FO0,972^GB203,4,4^FS
                          ^FO0,363^GB203,4,4^FS
                          ^FO0,242^GB203,4,4^FS
                          ^FO0,120^GB203,4,4^FS
                          ^FO66,0^GB4,365,4^FS
                          ^FO133,0^GB4,365,4^FS
                          ^FO133,1177^GB4,122,4^FS
                          ^FO66,1177^GB4,122,4^FS
                          ^FB250,1,0,L^FO5,1350^FD{pos1}
                          ^AKb,35,35^FS^FB200,1,0,L^FO70,1400^FD{pos2}
                          ^AKb,35,35^FS^FO130,1540^FD{pos4A}
                          ^AKb,35,35^FS{pos4B}^FS
                          ^FB200,1,0,R^AKb,45,45^FO35,1300^FD{pos2A}
                          ^AKb,80,80^FS^FO5,1200^FD{pos5}
                          ^AKb,35,35^FS^FO80,1190^FD{pos6}
                          ^AKb,35,35^FS^FO145,1220^FD{pos7}
                          ^AKb,35,35^FS^FO5,1050^FD{pos8A}
                          ^AKb,35,35^FS^FB550,1,0,L^FO5,400^FD{pos9}
                          ^AKb,35,35^FS^FB500,1,0,L^FO70,450^FD{pos9D}
                          ^AKb,35,35^FS^^FB500,1,0,L^FO135,450^FD{pos9A}
                          ^AKb,35,35^FS^FO0,1175^GB203,4,4^FS^PQ1,0,1,Y^XZ""")

    def print_gi_messages(self, message):
        print(f"{message}")
        # self.zebra.output(f"^XA^CFC,40,40~TA000~JSN^LT0^MNN^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI27^PA0,1,1,0^XZ^XA^MMT^PW203^LL1624^LS-20^FS^FB1590,4,3,L,25^FO0,10^FD{message}^A0b,40,40^XZ")

    def print_memoryAids(self):
        print("STOP")
        print("\\\\\\ NO LUAW ///")
        print("S/E SLAWW/FUTBL")
        print("W/N SNUFY/MPASS")
        print("S/E GRITZ/LIDAS")
        print("W/N HRSHL/RONII")

    def remove_amendment_marking(self, route:str) -> str:
        route = route.replace("+", "")
        return route
    # TODO Get rid of N0454F360 Shit
    def format_remarks(self, remark_string:str):
        # remove voice type
        if "/V/" in remark_string:
            remark_string = remark_string.replace("/V/", "")
        if "/T/" in remark_string:
            remark_string = remark_string.replace("/T/", "")
        if "/R/" in remark_string:
            remark_string = remark_string.replace("/R/", "")

        # remove double spaces
        if "  " in remark_string:
            ret_string = remark_string.replace("  ", " ")
        # no text in remarks section(after deletion of voice type)
        if remark_string.strip() == "":
            return ""
        
        # Split remark text into two sections and takes the data in the second half. Essentially deletes PBN data from the text. If no RMK/ exits, it will just use the first 18 characters
        if "RMK/" in remark_string:
            string_list = remark_string.split("RMK/")
        else:
            string_list = remark_string

        if len(string_list) > 1:
            ret_string = f"{string_list[1][:18]}"
        else:
            ret_string = string_list[0]
        # If the remaining remarks string has more than 18 characters, append a '***' to the end
        if(len(ret_string)) < 18:
            return f"░{ret_string}"
        else:
            return f"░{ret_string}***"
        
    def format_flightplan(self, flightplan:str, departure:str, flightrules:str):
        # If the flight plan is NOT IFR or DVFR, do not print the route.
        if flightrules != "I" and flightrules != "D":
            return ""

        # has the flight plan been amended
        # modified_flightplan = flightplan
        modified_flightplan = self.remove_amendment_marking(flightplan).strip()

        is_route_amended = False
        if len(modified_flightplan) < len(flightplan):
            is_route_amended = True

        modified_flightplan = modified_flightplan.replace(".", " ")
        modified_flightplan = modified_flightplan.strip()
        # split flightplan into a list of the routes waypoints
        flightplan_list = modified_flightplan.split(' ')
        # remove any DCT's from the waypoint list
        if "DCT" in flightplan_list:
            flightplan_list.remove("DCT")
        if "dct" in flightplan_list:
            flightplan_list.remove("dct")
        
        #If the departure airport is filed in the flight plan, remove it.
        if flightplan_list[0] == departure:
            flightplan_list.pop(0)
        
        # removes simbrief crap at start of flightplan
        i=0
        while(i < len(flightplan_list)):
            if len(flightplan_list[i]) > 6:
                flightplan_list.pop(i)
            else:
                i +=1
        
        # Truncates flightplan route to first 3 waypoints. routes longer than 3 waypoints are represented with a . / . at the end. If amended put . / . outside '+' symbols
        build_string = ""
        for i in range(len(flightplan_list)):
            if i >= 3 and is_route_amended:
                build_string = build_string.strip()
                return  f"+{departure} {build_string}+"
            elif i >= 3:
                build_string = build_string.strip()
                return f"{departure} {build_string}. / ."
            
            build_string = f"{build_string}{flightplan_list[i]} "
        build_string = f'{departure} {build_string}'
        if is_route_amended:
            build_string = build_string.strip()
            return f"+{build_string}+"
        else:
            return build_string.strip()
        
    def format_cruise_altitude(self, altitude:str):
        formatted_altitude = altitude.upper()
        formatted_altitude = formatted_altitude.replace("FL", "")
        formatted_altitude = altitude[:-2]
        if len(formatted_altitude) < 2:
            formatted_altitude = f"00{formatted_altitude}"
        elif len(formatted_altitude) < 3:
            formatted_altitude = f"0{formatted_altitude}"
        return formatted_altitude
    
    def match_ATL_exit_fix(self, flightplan):
        exit_fixes={
            "NOONE" : "N1",
            "NOTWO" : "N2",
            "EAONE" : "E1",
            "EATWO" : "E2",
            "SOONE" : "S1",
            "SOTWO" : "S2",
            "WEONE" : "W1",
            "WETWO" : "W2",
            "PENCL" : "N3",
            "VARNM" : "N5",
            "PADGT" : "N4",
            "SMKEY" : "N6",
            "PLMMR" : "E3",
            "JACCC" : "E5",
            "PHIIL" : "E4",
            "GAIRY" : "E6",
            "VRSTY" : "S3",
            "SMLTZ" : "S5",
            "BANNG" : "S4",
            "HAALO" : "S6",
            "POUNC" : "W3",
            "KAJIN" : "W5",
            "NASSA" : "W4",
            "CUTTN" : "W6"
        }
        exit_fix = ""
        modified_flightplan = flightplan
        modified_flightplan = self.remove_amendment_marking(modified_flightplan)
        modified_flightplan = modified_flightplan.strip()
        modified_flightplan = modified_flightplan[5:]

        flightplan_list = modified_flightplan.split(" ")
        if len(flightplan_list) > 0:
            exit_fix = exit_fixes.get(flightplan_list[0][:5])
        if exit_fix is None:
            exit_fix = ""
        return exit_fix
    
    def generate_id(self, remarks:str):
        lower_remarks = remarks.lower()
        r1 = str(random.randint(0,9))
        r2 = str(random.randint(0,9))
        r3 = str(random.randint(0,9))
        if "blind" in lower_remarks:
            r2 = "B"

        if "/t/" in lower_remarks:
            r3 = "T"
        elif "/r/" in lower_remarks:
            r3 = "R"
    
        return f"{r1}{r2}{r3}"

    def generate_random_id(self):
        r1 = random.randint(0,9)
        # Replace 2nd digit with B if blind
        r2 = random.randint(0,9)
        # /R/ /T/ replace with a T/R
        r3 = random.randint(0,9)
        return f"{r1}{r2}{r3}"

    def format_actype(self, aircraft_description:str):
        #Format that stuff & send it back
        aircraft_description = aircraft_description.replace("H/","")
        aircraft_description = aircraft_description.replace("J/","")
        index_of_equipment_slash = aircraft_description.find("/")
        if index_of_equipment_slash == -1:
          aircaft_type = aircraft_description
          equipment_suffix = ""
        else:
            aircaft_type = aircraft_description[:index_of_equipment_slash]
            equipment_suffix = aircraft_description[index_of_equipment_slash:]
        try:
            return f'{self.recat_db["aircraft"][aircaft_type]["recat"]}/{aircaft_type}{equipment_suffix}'
        except:
            return aircraft_description
