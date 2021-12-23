import cmd
import mysql.connector
from mysql.connector import errorcode

# Hi welcome to the client app, in order to run this code simply input the function name into the 
# command line ommiting the "do_" prefix and set database connection
class Client(cmd.Cmd):
    intro = 'Launched User Interface. Type help to list commands.\n'
    prompt = '(client): '

    cnx = mysql.connector.connect(
        host="marmoset04.shoshin.uwaterloo.ca",
        database="db356_as23sidh",
        user="as23sidh",
        password="--------")
    cursor = cnx.cursor()

    def __init__(self):
        super(Client, self).__init__()
    
    def do_help(self,arg):
        print("Commands: ")
        print("exit")
        print("check_airports_by_location")
        print("check_flights_by_airline")
        print("find_direct_flights")
        print("find_connecting_flights")
        print("modify_airport")
        print("modify_CauseOfDelay")
        print("modify_flight")
        print("modify_Cancellation")
        print("modify_GateReturn")
        print("modify_DiversionSummary")
        print("modify_Diversion")
        print("modify_Airline")

    def do_exit(self,arg):
        self.cnx.close()
        exit()

    def do_check_airports_by_location(self, arg):
        state = input("Please enter the State name: ")
        city = input("Please enter the City name: ")
        self.cursor.execute("SELECT AirportCode FROM Airport WHERE City = %s and State = %s;",
                            (city, state))
        results = self.cursor.fetchall()
        if not results:
            print("No Airports Found.")
            return
        print("Airports in ", (city, state))
        for result in results:
            print(result)

    def do_check_flights_by_airline(self, arg):
        IATACode = input("Please enter the Airline IATA code: ")
        FlightDate =  input("Please enter the Flight Date: ")
        query = f"""
            select Marketer.IATACode,
        Marketing.MarketingFlightNumber,
        Origin.AirportCode,
        Destination.AirportCode,
        FlightPlan.FlightDate,
        FlightPlan.CRSDepartureTime,
        FlightPlan.CRSArrivalTime,
        FlightPlan.CRSElapsedTime
        from FlightPlan
        join Airport as Origin on Origin.AirportID = FlightPlan.OriginAirportID
        join Airport as Destination on Destination.AirportID = FlightPlan.DestinationAirportID
        join Marketing on Marketing.FlightDate = FlightPlan.FlightDate
            and Marketing.TailNumber = FlightPlan.TailNumber
            and Marketing.CRSDepartureTime = FlightPlan.CRSDepartureTime
        join Airline as Marketer on Marketer.AirlineID = Marketing.MarketingAirlineID
        where Marketer.IATACode = '{IATACode}'
            and FlightPlan.FlightDate = '{FlightDate}';
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        if not results:
            print("No Airports Found.")
            return
        print(f"Flights from -'{IATACode}' on '{FlightDate}'")
        for result in results:
            print("Flight Information: ")
            print(f"Flight Number: '{result[1]}', Origin Airport Code: '{result[2]}', Destination Airport Code: '{result[3]}'")
            print(f"Departure Time: '{result[5]}', Arrival Time: '{result[6]}', Duration of Flight: '{result[7]}'")
    
    def do_find_direct_flights(self, arg):
        date = input("Please enter the departure date (YYYY-MM-DD): ")
        origin = input("Please enter the depature airportcode: ")
        destination = input("Please enter the destination airportcode: ")
        query = f"""
            select Origin.AirportCode, Destination.AirportCode, FlightPlan.FlightDate, FlightPlan.CRSDepartureTime, FlightPlan.CRSArrivalTime, FlightPlan.CRSElapsedTime, Marketer.IATACode, MarketingFlightNumber, Operator.IATACode, OperatingFlightNumber
        from FlightPlan
        join (select AirportID, AirportCode, City from Airport) as Origin 
            on FlightPlan.OriginAirportID = Origin.AirportID
        join (select AirportID, AirportCode, City from Airport) as Destination
            on FlightPlan.DestinationAirportID = Destination.AirportID
        join Marketing 
            on FlightPlan.FlightDate = Marketing.FlightDate
                and FlightPlan.TailNumber = Marketing.TailNumber
                and FlightPlan.CRSDepartureTime = Marketing.CRSDepartureTime
        join Operating
            on FlightPlan.FlightDate = Operating.FlightDate
                and FlightPlan.TailNumber = Operating.TailNumber
                and FlightPlan.CRSDepartureTime = Operating.CRSDepartureTime
        join (select AirlineID, IATACode from Airline) as Marketer
            on Marketing.MarketingAirlineID = Marketer.AirlineID
        join (select AirlineID, IATACode from Airline) as Operator
            on Operating.OperatingAirlineID = Operator.AirlineID
        where Origin.AirportCode = '{origin}' 
            and Destination.AirportCode = '{destination}'
            and FlightPlan.FlightDate = '{date}';
            """
        self.cursor.execute(query)

        results = self.cursor.fetchall()
        if not results:
            print("No Flights Found.")
            return

        for result in results:
            print("Found flight from " + result[0] + " to " + result[1] + " : ")
            print(f"Flight Date: '{result[2]}' Departure Time: '{result[3]}' Arrival Time: '{result[4]}' Travel Time(min): '{result[5]}'")
            print(f"Marketer Airline: '{result[6]}' Marketing Flight Number: '{result[7]}'")
            print(f"Operator Airline: '{result[8]}' Operator Flight Number: '{result[9]}' \n")

    def do_find_connecting_flights(self, arg):
        date = input("Please enter the departure date (YYYY-MM-DD): ")
        origin = input("Please enter the depature airportcode: ")
        destination = input("Please enter the destination airportcode: ")
        query = f"""
            with A as (select AirportID, AirportCode from Airport),
            FP as (select distinct OriginAirportID, DestinationAirportID from FlightPlan)
        select distinct Origin.AirportCode,
            Intermediate1.AirportCode,
            Intermediate2.AirportCode,
            Destination.AirportCode
            from FP as Originating
            join FP as Connecting on Connecting.OriginAirportID = Originating.DestinationAirportID
            join A as Origin on Origin.AirportID = Originating.OriginAirportID
            join A as Intermediate1 on Intermediate1.AirportID = Originating.DestinationAirportID
            join A as Intermediate2 on Intermediate2.AirportID = Connecting.OriginAirportID
            join A as Destination on Destination.AirportID = Connecting.DestinationAirportID
            where Origin.AirportCode = '{origin}' and Destination.AirportCode = '{destination}'
            and FlightPlan.FlightDate = '{date}';
            """
        self.cursor.execute(query)

        results = self.cursor.fetchall()
        if not results:
            print("No Flights Found.")
            return

        for result in results:
            print("Found connecting flight from " + result[0] + " to " + result[1] + " to " + result[3])
           
           
    def do_modify_airport(self, arg):
        AirportID = input("Please enter the AirportId to modify: ")
        self.cursor.execute(f"SELECT 1 FROM Airport WHERE AirportID = '{AirportID}';")
        result = self.cursor.fetchall()
        if not result:
            entry = input("Airport Not Found, Would you like to create a new entry? (Y/N)")
            if entry == "Y":
                AirportSequenceID = input("Please enter the AirportSequenceId: ")
                CityMarketID = input("Please enter the CityMarketId: ")
                AirportCode = input("Please enter the AirportCode: ")
                City = input("Please enter the City: ")
                State = input("Please enter the State: ")
                StateCode = input("Please enter the StateCode: ")
                StateFIPS = input("Please enter the StateFIPS: ")
                wac = input("Please enter the WAC: ")

                sql_statement = f"INSERT INTO Airport VALUES ('{AirportID}', '{AirportSequenceID}', '{CityMarketID}', '{AirportCode}', '{City}', '{State}', '{StateCode}', '{StateFIPS}', '{wac}')"               
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Successfully added new Airport entry")
            elif entry == "N":
                return
        else:
            entry = input("Found Airport, would you like to modify or delete Airport (M/D): ")
            if entry == "M":
                AirportSequenceID = input("Please enter the AirportSequenceId: ")
                CityMarketID = input("Please enter the CityMarketId: ")
                AirportCode = input("Please enter the AirportCode: ")
                City = input("Please enter the City: ")
                State = input("Please enter the State: ")
                StateCode = input("Please enter the StateCode: ")
                StateFIPS = input("Please enter the StateFIPS: ")
                wac = input("Please enter the WAC: ")

                sql_statement = f"UPDATE Airport SET AirportSequenceID = '{AirportSequenceID}', CityMarketID = '{CityMarketID}', AirportCode = '{AirportCode}', City = '{City}', State = '{State}', StateCode = '{StateCode}', StateFIPS = '{StateFIPS}', WAC = '{wac}' WHERE AirportID = '{AirportID}';"
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Succesfully updated Airport Information")
            elif entry == "D":
                self.cursor.execute(f"DELETE FROM Airport WHERE AirportID = '{AirportID}'")
                self.cnx.commit()
                print("Succesfully deleted Airport Information")
        
    def do_modify_CauseOfDelay(self, arg):
        print("Enter primary keys to modify table: ")
        FlightDate = input("Please enter the FlightDate (YYYY-MM-DD): ")
        TailNum = input("Please enter the Tail Number: ")
        CRSDepartureTime = input("Please enter the CRSDepartureTime: ")

        self.cursor.execute(f"SELECT 1 FROM CauseOfDelay WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
        result = self.cursor.fetchall()
        if not result:
            entry = input("Entry Not Found, Would you like to create a new entry? (Y/N)")
            if entry == "Y":
                CarrierDelay = input("Please enter the CarrierDelay: ")
                WeatherDelay = input("Please enter the WeatherDelay: ")
                NASDelay = input("Please enter the NASDelay: ")
                SecurityDelay = input("Please enter the SecurityDelay: ")
                LateAircraftDelay = input("Please enter the LateAircraftDelay: ")

                sql_statement = f"INSERT INTO CauseOfDelay VALUES ('{CarrierDelay}', '{WeatherDelay}', '{NASDelay}', '{SecurityDelay}', '{LateAircraftDelay}'"               
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Successfully added new CauseOfDelay entry")
            elif entry == "N":
                return
        else:
            entry = input("Found Entry, would you like to modify or delete (M/D): ")
            if entry == "M":
                CarrierDelay = input("Please enter the CarrierDelay: ")
                WeatherDelay = input("Please enter the WeatherDelay: ")
                NASDelay = input("Please enter the NASDelay: ")
                SecurityDelay = input("Please enter the SecurityDelay: ")
                LateAircraftDelay = input("Please enter the LateAircraftDelay: ")

                sql_statement = f"UPDATE CauseOfDelay SET CarrierDelay = '{CarrierDelay}', WeatherDelay = '{WeatherDelay}', NASDelay = '{NASDelay}', SecurityDelay = '{SecurityDelay}', LateAircraftDelay = '{LateAircraftDelay}';"
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Succesfully updated CauseOfDelay Information")
            elif entry == "D":
                self.cursor.execute(f"DELETE FROM CauseOfDelay WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime} WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
                self.cnx.commit()
                print("Succesfully deleted CauseofDelay Information")

    def do_modify_Airline(self, arg):
        AirlineID = input("Please enter the AirlineID to modify: ")
        self.cursor.execute(f"SELECT 1 FROM Airline WHERE AirlineID = '{AirlineID}';")
        result = self.cursor.fetchall()
        if not result:
            entry = input("Airline Not Found, Would you like to create a new entry? (Y/N)")
            if entry == "Y":
                dotID = input("Please enter the DOTID: ")
                iataCode = input("Please enter the IATA Code: ")

                sql_statement = f"INSERT INTO Airline VALUES ('{AirlineID}', '{dotID}', '{iataCode}')"               
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Successfully added new Airline entry")
            elif entry == "N":
                return
        else:
            entry = input("Found Airline, would you like to modify or delete Airline (M/D): ")
            if entry == "M":
                dotID = input("Please enter the DOTID: ")
                iataCode = input("Please enter the IATA Code: ")

                sql_statement = f"UPDATE Airline SET DOTID = '{dotID}', IATACode = '{iataCode}' WHERE AirlineID = '{AirlineID}';"
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Succesfully updated Airline Information")
            elif entry == "D":
                self.cursor.execute(f"DELETE FROM Airline WHERE AirlineID = '{AirlineID}'")
                self.cnx.commit()
                print("Succesfully deleted Airline Information")

    def do_modify_flight(self, arg):
        print("Enter primary keys to modify table: ")
        FlightDate = input("Please enter the FlightDate (YYYY-MM-DD): ")
        TailNum = input("Please enter the Tail Number: ")
        CRSDepartureTime = input("Please enter the CRSDepartureTime: ")

        self.cursor.execute(f"SELECT 1 FROM Flight WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
        result = self.cursor.fetchall()
        if not result:
            entry = input("Flight Not Found, Would you like to create a new entry? (Y/N)")
            if entry == "Y":
                ActualDepartureTime = input("Please enter the ActualDepartureTime: ")
                DepartureDelay = input("Please enter the DepartureDelay: ")
                DepartureDelayMinutes = input("Please enter the DepartureDelayMinutes: ")
                DepartureDelayFlag = input("Please enter the DepartureDelayFlag: ")
                DepartureDelayIntervals15 = input("Please enter the DepartureDelayIntervals15: ")
                TaxiOut = input("Please enter the TaxiOut: ")
                WheelsOff = input("Please enter the WheelsOff: ")
                WheelsOn = input("Please enter the WheelsOn: ")
                TaxiIn = input("Please enter the TaxiIn: ")
                ActualArrivalTime = input("Please enter the ActualArrivalTime: ")
                ArrivalDelay = input("Please enter the ArrivalDelay: ")
                ArrivalDelayMinutes = input("Please enter the ArrivalDelayMinutes: ")
                ArrivalDelayFlag = input("Please enter the ArrivalDelayFlag: ")
                ArrivalDelayIntervals15 = input("Please enter the ArrivalDelayIntervals15: ")
                ActualElapsedTime = input("Please enter the ActualElapsedTime: ")
                AirTime = input("Please enter the AirTime: ")

                sql_statement = f"INSERT INTO Flight VALUES ('{ActualDepartureTime}', '{DepartureDelay}', '{DepartureDelayMinutes}', '{DepartureDelayFlag}', '{DepartureDelayIntervals15}', '{TaxiOut}', '{WheelsOff}', '{WheelsOn}', '{TaxiIn}', '{ActualArrivalTime}', '{ArrivalDelay}', '{ArrivalDelayMinutes}', '{ArrivalDelayFlag}', '{ArrivalDelayIntervals15}', '{ActualElapsedTime}', '{AirTime}')"               
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Successfully added new Flight entry")
            elif entry == "N":
                return
        else:
            entry = input("Found Flight, would you like to modify or delete Flight (M/D): ")
            if entry == "M":
                ActualDepartureTime = input("Please enter the ActualDepartureTime: ")
                DepartureDelay = input("Please enter the DepartureDelay: ")
                DepartureDelayMinutes = input("Please enter the DepartureDelayMinutes: ")
                DepartureDelayFlag = input("Please enter the DepartureDelayFlag: ")
                DepartureDelayIntervals15 = input("Please enter the DepartureDelayIntervals15: ")
                TaxiOut = input("Please enter the TaxiOut: ")
                WheelsOff = input("Please enter the WheelsOff: ")
                WheelsOn = input("Please enter the WheelsOn: ")
                TaxiIn = input("Please enter the TaxiIn: ")
                ActualArrivalTime = input("Please enter the ActualArrivalTime: ")
                ArrivalDelay = input("Please enter the ArrivalDelay: ")
                ArrivalDelayMinutes = input("Please enter the ArrivalDelayMinutes: ")
                ArrivalDelayFlag = input("Please enter the ArrivalDelayFlag: ")
                ArrivalDelayIntervals15 = input("Please enter the ArrivalDelayIntervals15: ")
                ActualElapsedTime = input("Please enter the ActualElapsedTime: ")
                AirTime = input("Please enter the AirTime: ")

                sql_statement = f"UPDATE Flight SET ActualDepartureTime = '{ActualDepartureTime}', DepartureDelay = '{DepartureDelay}', DepartureDelayMinutes = '{DepartureDelayMinutes}', DepartureDelayMinutes = '{DepartureDelayFlag}', DepartureDelayMinutes = '{DepartureDelayIntervals15}', DepartureDelayMinutes = '{TaxiOut}', DepartureDelayMinutes = '{WheelsOff}', DepartureDelayMinutes = '{WheelsOn}', DepartureDelayMinutes = '{TaxiIn}', DepartureDelayMinutes = '{ActualArrivalTime}', DepartureDelayMinutes = '{ArrivalDelay}', DepartureDelayMinutes = '{ArrivalDelayMinutes}', DepartureDelayMinutes = '{ArrivalDelayFlag}', DepartureDelayMinutes = '{ArrivalDelayIntervals15}', DepartureDelayMinutes = '{ActualElapsedTime}', DepartureDelayMinutes = '{AirTime}' WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};"
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Succesfully updated Flight Information")
            elif entry == "D":
                self.cursor.execute(f"DELETE FROM Flight WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
                self.cnx.commit()
                print("Succesfully deleted Flight Information")   

    def do_modify_Cancellation(self,arg):
        print("Enter primary keys to modify table: ")
        FlightDate = input("Please enter the FlightDate (YYYY-MM-DD): ")
        TailNum = input("Please enter the Tail Number: ")
        CRSDepartureTime = input("Please enter the CRSDepartureTime: ")

        self.cursor.execute(f"SELECT 1 FROM Cancellation WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
        result = self.cursor.fetchall()
        if not result:
            entry = input("Cancellation Not Found, Would you like to create a new entry? (Y/N)")
            if entry == "Y":
                CancellationCode = input("Please enter the CancellationCode: ")

                sql_statement = f"INSERT INTO Cancellation VALUES ('{CancellationCode}'"               
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Successfully added new Cancellation entry")
            elif entry == "N":
                return
        else:
            entry = input("Found Cancellation, would you like to modify or delete (M/D): ")
            if entry == "M":
                CancellationCode = input("Please enter the CancellationCode: ")

                sql_statement = f"UPDATE Cancellation SET CancellationCode = '{CancellationCode}' WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};"
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Succesfully updated Cancellation Information")
            elif entry == "D":
                self.cursor.execute(f"DELETE FROM Cancellation WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
                self.cnx.commit()
                print("Succesfully deleted Cancellation Information")

    def do_modify_GateReturn(self,arg):
        print("Enter primary keys to modify table: ")
        FlightDate = input("Please enter the FlightDate (YYYY-MM-DD): ")
        TailNum = input("Please enter the Tail Number: ")
        CRSDepartureTime = input("Please enter the CRSDepartureTime: ")

        self.cursor.execute(f"SELECT 1 FROM GateReturn WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
        result = self.cursor.fetchall()
        if not result:
            entry = input("Gate Return not Found, Would you like to create a new entry? (Y/N)")
            if entry == "Y":
                FirstDepartureTime = input("Please enter the FirstDepartureTime: ")
                TotalAddedGroundTime = input("Please enter the TotalAddedGroundTime: ")
                LongestAddedGroundTime = input("Please enter the LongestAddedGroundTime: ")

                sql_statement = f"INSERT INTO GateReturn VALUES ('{FirstDepartureTime}', '{TotalAddedGroundTime}', '{LongestAddedGroundTime}'"               
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Successfully added new Gate Return entry")
            elif entry == "N":
                return
        else:
            entry = input("Found Gate Return, would you like to modify or delete (M/D): ")
            if entry == "M":
                FirstDepartureTime = input("Please enter the FirstDepartureTime: ")
                TotalAddedGroundTime = input("Please enter the TotalAddedGroundTime: ")
                LongestAddedGroundTime = input("Please enter the LongestAddedGroundTime: ")

                sql_statement = f"UPDATE GateReturn SET FirstDepartureTime = '{FirstDepartureTime}', TotalAddedGroundTime = '{TotalAddedGroundTime}', LongestAddedGroundTime = '{LongestAddedGroundTime}' WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};"
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Succesfully updated Gate Return Information")
            elif entry == "D":
                self.cursor.execute(f"DELETE FROM GateReturn WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
                self.cnx.commit()
                print("Succesfully deleted Gate Return Information")
    
    def do_modify_DiversionSummary(self, arg):
        print("Enter primary keys to modify table: ")
        FlightDate = input("Please enter the FlightDate (YYYY-MM-DD): ")
        TailNum = input("Please enter the Tail Number: ")
        CRSDepartureTime = input("Please enter the CRSDepartureTime: ")

        self.cursor.execute(f"SELECT 1 FROM DiversionSummary WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
        result = self.cursor.fetchall()
        if not result:
            entry = input("DiversionSummary entry not Found, Would you like to create a new entry? (Y/N)")
            if entry == "Y":
                DivertedLandings = input("Please enter the DivertedLandings: ")
                DivertedReachedDestination = input("Please enter the DivertedReachedDestination: ")
                DivertedActualElapsedTime = input("Please enter the DivertedActualElapsedTime: ")
                DivertedArrivalDelay = input("Please enter the DivertedArrivalDelay: ")
                DivertedDistance = input("Please enter the DivertedDistance: ")

                sql_statement = f"INSERT INTO DiversionSummary VALUES ('{DivertedLandings}', '{DivertedReachedDestination}', '{DivertedActualElapsedTime}', '{DivertedArrivalDelay}', '{DivertedDistance}'"               
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Successfully added new DiversionSummary entry")
            elif entry == "N":
                return
        else:
            entry = input("Found DiversionSummary entry, would you like to modify or delete (M/D): ")
            if entry == "M":
                DivertedLandings = input("Please enter the DivertedLandings: ")
                DivertedReachedDestination = input("Please enter the DivertedReachedDestination: ")
                DivertedActualElapsedTime = input("Please enter the DivertedActualElapsedTime: ")
                DivertedArrivalDelay = input("Please enter the DivertedArrivalDelay: ")
                DivertedDistance = input("Please enter the DivertedDistance: ")

                sql_statement = f"UPDATE DiversionSummary SET DivertedLandings = '{DivertedLandings}', DivertedReachedDestination = '{DivertedReachedDestination}', DivertedActualElapsedTime = '{DivertedActualElapsedTime}', DivertedArrivalDelay = '{DivertedArrivalDelay}', DivertedDistance = '{DivertedDistance}' WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};"
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Succesfully updated DiversionSummary Information")
            elif entry == "D":
                self.cursor.execute(f"DELETE FROM DiversionSummary WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime};")
                self.cnx.commit()
                print("Succesfully deleted DiversionSummary Information")

    def do_modify_Diversion(self, arg):
        print("Enter primary keys to modify table: ")
        FlightDate = input("Please enter the FlightDate (YYYY-MM-DD): ")
        TailNum = input("Please enter the Tail Number: ")
        CRSDepartureTime = input("Please enter the CRSDepartureTime: ")

        self.cursor.execute(f"SELECT COUNT(*) FROM Diversion WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime}")
        result = self.cursor.fetchall()
        DiversionSequenceNumber = result+1
        if not result:
            entry = input("Diversion entry not Found, Would you like to create a new entry? (Y/N)")
            if entry == "Y":
                DiversionWheelsOn = input("Please enter the DiversionWheelsOn: ")
                DiversionTotalGroundTime = input("Please enter the DiversionTotalGroundTime: ")
                DiversionLongestGroundTime = input("Please enter the DiversionLongestGroundTime: ")
                DiversionWheelsOff = input("Please enter the DiversionWheelsOff: ")
                DiversionTailNumber = input("Please enter the DiversionTailNumber: ")

                sql_statement = f"INSERT INTO Diversion VALUES ('{DiversionSequenceNumber}', '{DiversionWheelsOn}', '{DiversionTotalGroundTime}', '{DiversionLongestGroundTime}', '{DiversionWheelsOff}', '{DiversionTailNumber}'"               
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Successfully added new Diversion entry")
            elif entry == "N":
                return
        else:
            DiversionSequenceNumber = DiversionSequenceNumber-1
            entry = input("Found Diversion entry, would you like to modify or delete (M/D): ")
            if entry == "M":
                DiversionWheelsOn = input("Please enter the DiversionWheelsOn: ")
                DiversionTotalGroundTime = input("Please enter the DiversionTotalGroundTime: ")
                DiversionLongestGroundTime = input("Please enter the DiversionLongestGroundTime: ")
                DiversionWheelsOff = input("Please enter the DiversionWheelsOff: ")
                DiversionTailNumber = input("Please enter the DiversionTailNumber: ")

                sql_statement = f"UPDATE Diversion SET DiversionSequenceNumber = '{DiversionSequenceNumber}', DiversionWheelsOn = '{DiversionWheelsOn}', DiversionTotalGroundTime = '{DiversionTotalGroundTime}', DiversionLongestGroundTime = '{DiversionLongestGroundTime}', DiversionWheelsOff = '{DiversionWheelsOff}', DiversionTailNumber = '{DiversionTailNumber}' WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime} AND DiversionSequenceNumber = '{DiversionSequenceNumber}';"
                self.cursor.execute(sql_statement)
                self.cnx.commit()
                print("Succesfully updated Diversion Information")
            elif entry == "D":
                self.cursor.execute(f"DELETE FROM Diversion WHERE FlightDate = '{FlightDate}' AND TailNumber = '{TailNum} AND CRSDepartureTime = '{CRSDepartureTime} AND DiversionSequenceNumber = '{DiversionSequenceNumber}';")
                self.cnx.commit()
                print("Succesfully deleted Diverts Information")

        
if __name__ == '__main__':
    Client().cmdloop()