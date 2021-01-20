import unittest,requests


API = "https://ssd-api.jpl.nasa.gov/fireball.api"
API_DATE_FILTER = "2017-01-01"
THRESHOLD = 2
BUFFER = 15
#Error Keyword-Descirption mapping
ERROR_MAP = {
    "INSUFFICIENT_DATA": "Insufficient Data provided",
    "API_DATA_EMPTY": "Sufficient Data Points are not available for given dates.Please check in some time!!",
    "BRIGHTEST_LOCATION": "Delphix Brightest Star is at ",
    "BRIGHTEST_STAR_ENERGY": " with energy ",
}


class FireballApiSystem:
    #Status Code-Error mapping
    ERROR_CODES_MAP = {
        400: "BAD_REQUEST:The request contained invalid keywords and/or content",
        405: "METHOD_NOT_ALLOWED:The request used a method other than GET or POST",
        500: "INTERNAL_SERVER_ERROR:The database is not available at the time of the request",
        503: "SERVICE_UNAVAILABLE:The server is currently unable to handle the request due to a temporary overloading or maintenance of the server, which will likely be alleviated after some delay",
    }

    def fireball_records(self, params):
        return self.api_response_handling(requests.get(API, params=params))

    def api_response_handling(self, response):
        HttpErrorCodes = response.status_code
        if HttpErrorCodes == 200:
            return self.__content_parsing(response)
        elif HttpErrorCodes in {400, 405, 500, 503}:
            raise Exception(self.ERROR_CODES_MAP[HttpErrorCodes])
        else:
            return []

    def __content_parsing(self, response):
        res_dict = response.json()
        fireball_count = int(res_dict["count"])
        if THRESHOLD > fireball_count:
            return []
        data_list = res_dict["data"]
        # print(res_dict)
        return FireballApiSystem.fireball_DataPoints(data_list)

    @staticmethod
    def fireball_DataPoints(data_list):
        try:
            fireball_list = []
            field_index_map = {
                "Date": 0,
                "Impact_energy": 2,
                "Latitude": 3,
                "Lat_dir": 4,
                "Longitude": 5,
                "Long_dir": 6,
                "Altitude": 7,
            }
            #parsing fireball Data dict to create list of fireball objects
            for data in data_list:
                Impact_Energy = data[field_index_map["Impact_energy"]]
                lat = data[field_index_map["Latitude"]]
                lat_dir = data[field_index_map["Lat_dir"]]
                long = data[field_index_map["Longitude"]]
                long_dir = data[field_index_map["Long_dir"]]

                fireball = Fireballs(lat, lat_dir, long, long_dir)
                fireball.impact_energy = Impact_Energy
                fireball_list.append(fireball)
            return fireball_list

        except:
            raise ValueError("Data_list has improper values.")


class Fireballs:
    # Fireball data column labels

    def __init__(self, Lat, lat_dir, Long, long_dir):
        self.lat = Lat
        self.lat_dir = lat_dir
        self.long = Long
        self.long_dir = long_dir

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = date

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, lat):
        self._lat = lat

    @property
    def lat_dir(self):
        return self._lat_dir

    @lat_dir.setter
    def lat_dir(self, lat_dir):
        self._lat_dir = lat_dir

    @property
    def long(self):
        return self._long

    @long.setter
    def long(self, long):
        self._long = long

    @property
    def long_dir(self):
        return self._long_dir

    @long_dir.setter
    def long_dir(self, long_dir):
        self._long_dir = long_dir

    @property
    def alt(self):
        return self._alt
    @alt.setter
    def alt(self, alt):
        self._alt = alt

    @property
    def vel(self):
        return self.vel

    @vel.setter
    def vel(self, vel):
        self.vel = vel

    @property
    def impact_energy(self):
        return self.impact_e

    @impact_energy.setter
    def impact_energy(self, impact_e):
        self.impact_e = impact_e

    @property
    def energy(self):
        return self.energy

    @energy.setter
    def energy(self, energy):
        self.energy = energy

    def __eq__(self, other):
        pass

    def __repr__(self):
        return "Fireballs('{}', '{}','{}', '{}')".format(self.lat, self.lat_dir, self.long, self.long_dir)

    def __str__(self):
        return '"Fireball with lat:{}{} & long:{}{}'.format(self.lat, self.lat_dir, self.long, self.long_dir)


class Location:

    def __init__(self, name, lat, long, lat_dir, long_dir):
        self.name = name
        self.lat = lat
        self.lat_dir = lat_dir
        self.long = long
        self.long_dir = long_dir

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, lat):
        if lat < 0 or lat > 90:
            raise ValueError("Latitudes below 0  or above 90 is not possible")
        self._lat = lat

    @property
    def lat_dir(self):
        return self._lat_dir

    @lat_dir.setter
    def lat_dir(self, lat_dir):
        self._lat_dir = lat_dir

    @property
    def long(self):
        return self._long

    @long.setter
    def long(self, long):
        if long < 0 or long > 180:
            raise ValueError("Longitudes below 0  or above 180 is not possible")
        self._long = long

    @property
    def long_dir(self):
        return self._long_dir

    @long_dir.setter
    def long_dir(self, long_dir):
        self._long_dir = long_dir

    def __repr__(self):
        return "Location('{}','{}', '{}','{}', '{}')".format(self.name, self.lat, self.lat_dir, self.long,
                                                             self.long_dir)

    def __str__(self):
        return '{} {} {}, {} {}'.format(self.name, self.lat, self.lat_dir, self.long, self.long_dir)


class ShootingStar_Utility:
    Data = {
        # "limit": "2",
        "req-loc": True,
        "date-min": None
    }

    def Brightest_ShootingStar(self, locations, date):
        self.Data["date-min"] = date
        FireballApi = FireballApiSystem()
        #list of fireball objects
        fireball_list = FireballApi.fireball_records(self.Data)
        # print(fireball_list)
        if not fireball_list:
            raise ValueError(ERROR_MAP["API_DATA_EMPTY"])
        if not locations:
            raise ValueError(f'{ERROR_MAP["INSUFFICIENT_DATA"]} for Locations')

        BrightestStar = self.brightest_ShootingStar_info(locations, fireball_list)

        return f'Brightest Star located at {BrightestStar[0]} with Impact energy {BrightestStar[1]}'

    def brightest_ShootingStar_info(self, locations, fireball_list):
        maxm_brightness = float('-inf')

        BrightestStar = list()
        brightestStar = ""
        # print(locations)
        for location in locations:
            brightness = self.MaxEnergy_per_location(location.lat, location.long, location, fireball_list)
            # print(brightness,maxm_brightness)
            try:
                if maxm_brightness < brightness:
                    maxm_brightness = brightness
                    brightestStar = location.name

            except TypeError as err:
                print("Skipping!!!.Error encountered:%s" % err)

        BrightestStar.append(brightestStar)
        BrightestStar.append(maxm_brightness)
        # print(BrightestStar)
        return BrightestStar

    @staticmethod
    def MaxEnergy_per_location(lat, long, location, fireball_list):
        maxm_energy = float('-inf')
        min_lat = lat - BUFFER
        max_lat = lat + BUFFER

        min_long = long - BUFFER
        max_long = long + BUFFER
        #finding the Maxm Energy in the Lat-Long Range
        for fireball in fireball_list:
            if fireball.lat_dir.lower() == location.lat_dir.lower() and fireball.long_dir.lower() == location.long_dir.lower():
                if (min_lat <= float(fireball.lat) <= max_lat) and (min_long <= float(fireball.long) <= max_long):
                    if maxm_energy < float(fireball.impact_energy):
                        maxm_energy = float(fireball.impact_energy)

        return maxm_energy


class Test_FireballApiService(unittest.TestCase):
    Dummy_Data = {
        "limit": None,
        "req-loc": True,
        "date-min": None
    }

    @classmethod
    def setUpClass(cls):
        cls.ShootingStar_Api = ShootingStar_Utility()
        cls.Fireball_Api = FireballApiSystem()
        boston = Location("Boston", 42.354558, 71.054254, "N", "W")
        cls.ncr = Location("NCR", 28.574389, 77.312638, "N", "E")
        sanFran = Location("San Francisco", 37.793700, 122.403906, "N", "W")
        cls.DelphixLocations = [boston, cls.ncr, sanFran]
        print('setupClass for the test.Prepares Objects & variables for use throughout the Test Class.')


    @classmethod
    def tearDownClass(cls):
        del cls.ShootingStar_Api
        del cls.Fireball_Api
        del cls.ncr
        with cls.assertRaises(Test_FireballApiService,AttributeError):
            cls.ncr
        del cls.DelphixLocations

        print('teardownClass for deleting the objects and variable created in setup Class after the Testcases are over.')

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_fireballs(self):
        fireball = Fireballs('14','N','12.3','W')

        with self.assertRaises(AttributeError):
            fireball.alt()
        with self.assertRaises(AttributeError):
            fireball.alt
        fireball.alt = "48"
        self.assertEqual(fireball.alt,'48')
        with self.assertRaises(TypeError):
            fireball.alt()

    def test_locations(self):
        with self.assertRaises(ValueError):
            self.ncr.lat = -1
            self.ncr.long = -2


    def test_static_methods(self):
        self.Dummy_Data["limit"] = 2
        res = self.ShootingStar_Api.MaxEnergy_per_location(self.ncr.lat, self.ncr.long, self.ncr,
                                                           self.Fireball_Api.fireball_records(self.Dummy_Data))
        self.assertEqual(res, float('-inf'))
        with self.assertRaises(Exception):
            self.ShootingStar_Api.MaxEnergy_per_location(-15.0, -15.0, [])

        with self.assertRaises(ValueError):
            self.Fireball_Api.fireball_DataPoints([['2']])

    def test_Api_methods(self):
        self.Dummy_Data["limit"] = 2
        # print(self.Fireball_Api.fireball_records(self.Dummy_Data))
        self.assertEqual(len(self.Fireball_Api.fireball_records(self.Dummy_Data)), 2)

        with self.assertRaises(Exception):
            self.Dummy_Data["limit"] = 0
            # print(self.Fireball_Api.fireball_records(self.Dummy_Data))
            self.Fireball_Api.fireball_records(self.Dummy_Data)

        with self.assertRaises(ValueError):
            dummy_date = "2021-01-01"
            self.Dummy_Data["date-min"] = API_DATE_FILTER
            self.ShootingStar_Api.Brightest_ShootingStar([], API_DATE_FILTER)
            self.ShootingStar_Api.Brightest_ShootingStar(self.DelphixLocations, dummy_date)

def main():
    ShootingStar_Api = ShootingStar_Utility()
    boston = Location("Boston", 42.354558, 71.054254, "N", "W")
    ncr = Location("NCR", 28.574389, 77.312638, "N", "E")
    sanFran = Location("San Francisco", 37.793700, 122.403906, "N", "W")
    DelphixLocations = [boston, ncr, sanFran]
    print("->"+ShootingStar_Api.Brightest_ShootingStar(DelphixLocations, API_DATE_FILTER)+".")


if __name__ == '__main__':
    main()
    unittest.main()
