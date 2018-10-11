#how to call the function
#e.g. dates=['2018-01-06','2018-03-30']
#Swedish_holi_work_days(dates)

#For the acedemic pupose this code is modified Swedish-2018 version of the python-holidays project, the link is below
#https://github.com/dr-prodigy/python-holidays/blob/master/holidays.py
#If you need to use for 2019 add the 2019's red days in custom_holidays.append])


from datetime import date, datetime
from dateutil.easter import easter, EASTER_ORTHODOX
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta as rd
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
import six

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)
WEEKEND = (SATURDAY, SUNDAY)

class HolidayBase(dict):
    PROVINCES = []

    def __init__(self, years=[], expand=True, observed=True,
                 prov=None, state=None):
        self.observed = observed
        self.expand = expand
        if isinstance(years, int):
            years = [years, ]
        self.years = set(years)
        if not getattr(self, 'prov', False):
            self.prov = prov
        self.state = state
        for year in list(self.years):
            self._populate(year)

    def __setattr__(self, key, value):
        if key == 'observed' and len(self) > 0:
            dict.__setattr__(self, key, value)
            if value is True:
                # Add (Observed) dates
                years = list(self.years)
                self.years = set()
                self.clear()
                for year in years:
                    self._populate(year)
            else:
                # Remove (Observed) dates
                for k, v in list(self.items()):
                    if v.find("Observed") >= 0:
                        del self[k]
        else:
            return dict.__setattr__(self, key, value)

    def __keytransform__(self, key):
        if isinstance(key, datetime):
            key = key.date()
        elif isinstance(key, date):
            key = key
        elif isinstance(key, int) or isinstance(key, float):
            key = datetime.utcfromtimestamp(key).date()
        elif isinstance(key, six.string_types):
            try:
                key = parse(key).date()
            except (ValueError, OverflowError):
                raise ValueError("Cannot parse date from string '%s'" % key)
        else:
            raise TypeError("Cannot convert type '%s' to date." % type(key))

        if self.expand and key.year not in self.years:
            self.years.add(key.year)
            self._populate(key.year)
        return key

    def __contains__(self, key):
        return dict.__contains__(self, self.__keytransform__(key))

    def __getitem__(self, key):
        return dict.__getitem__(self, self.__keytransform__(key))

    def __setitem__(self, key, value):
        if key in self:
            if self.get(key).find(value) < 0 \
                    and value.find(self.get(key)) < 0:
                value = "%s, %s" % (value, self.get(key))
            else:
                value = self.get(key)
        return dict.__setitem__(self, self.__keytransform__(key), value)

    def update(self, *args):
        args = list(args)
        for arg in args:
            if isinstance(arg, dict):
                for key, value in list(arg.items()):
                    self[key] = value
            elif isinstance(arg, list):
                for item in arg:
                    self[item] = "Holiday"
            else:
                self[arg] = "Holiday"

    def append(self, *args):
        return self.update(*args)

    def get(self, key, default=None):
        return dict.get(self, self.__keytransform__(key), default)

    def get_list(self, key):
        return [h for h in self.get(key, "").split(", ") if h]

    def pop(self, key, default=None):
        if default is None:
            return dict.pop(self, self.__keytransform__(key))
        return dict.pop(self, self.__keytransform__(key), default)

    def __eq__(self, other):
        return dict.__eq__(self, other) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return dict.__ne__(self, other) or self.__dict__ != other.__dict__

    def __add__(self, other):
        if isinstance(other, int) and other == 0:
            # Required to sum() list of holidays
            # sum([h1, h2]) is equivalent to (0 + h1 + h2)
            return self
        elif not isinstance(other, HolidayBase):
            raise TypeError()
        HolidaySum = createHolidaySum(self, other)
        country = (getattr(self, 'country', None) or
                   getattr(other, 'country', None))
        if self.country and other.country and self.country != other.country:
            c1 = self.country
            if not isinstance(c1, list):
                c1 = [c1]
            c2 = other.country
            if not isinstance(c2, list):
                c2 = [c2]
            country = c1 + c2
        prov = getattr(self, 'prov', None) or getattr(other, 'prov', None)
        if self.prov and other.prov and self.prov != other.prov:
            p1 = self.prov if isinstance(self.prov, list) else [self.prov]
            p2 = other.prov if isinstance(other.prov, list) else [other.prov]
            prov = p1 + p2
        return HolidaySum(years=(self.years | other.years),
                          expand=(self.expand or other.expand),
                          observed=(self.observed or other.observed),
                          country=country, prov=prov)

    def __radd__(self, other):
        return self.__add__(other)

    def _populate(self, year):
        pass


def createHolidaySum(h1, h2):

    class HolidaySum(HolidayBase):

        def __init__(self, country, **kwargs):
            self.country = country
            self.holidays = []
            if getattr(h1, 'holidays', False):
                for h in h1.holidays:
                    self.holidays.append(h)
            else:
                self.holidays.append(h1)
            if getattr(h2, 'holidays', False):
                for h in h2.holidays:
                    self.holidays.append(h)
            else:
                self.holidays.append(h2)
            HolidayBase.__init__(self, **kwargs)

        def _populate(self, year):
            for h in self.holidays[::-1]:
                h._populate(year)
                self.update(h)

    return HolidaySum


def CountryHoliday(country):
    try:
        country_holiday = globals()[country]()
    except (KeyError):
        raise KeyError("Country %s not available" % country)
    return country_holiday


class Sweden(HolidayBase):
    """
    Swedish holidays.
    Note that holidays falling on a sunday are "lost",
    it will not be moved to another day to make up for the collision.
    In Sweden, ALL sundays are considered a holiday
    (https://sv.wikipedia.org/wiki/Helgdagar_i_Sverige).
    Initialize this class with include_sundays=False
    to not include sundays as a holiday.
    Primary sources:
    https://sv.wikipedia.org/wiki/Helgdagar_i_Sverige and
    http://www.riksdagen.se/sv/dokument-lagar/dokument/svensk-forfattningssamling/lag-1989253-om-allmanna-helgdagar_sfs-1989-253
    """

    def __init__(self, include_sundays=True, **kwargs):
        """
        :param include_sundays: Whether to consider sundays as a holiday
        (which they are in Sweden)
        :param kwargs:
        """
        self.country = "SE"
        self.include_sundays = include_sundays
        HolidayBase.__init__(self, **kwargs)

    def _populate(self, year):
        # Add all the sundays of the year before adding the "real" holidays
        if self.include_sundays:
            first_day_of_year = date(year, 1, 1)
            first_sunday_of_year = first_day_of_year\
                + rd(days=SUNDAY - first_day_of_year.weekday())
            cur_date = first_sunday_of_year

            while cur_date < date(year + 1, 1, 1):
                assert cur_date.weekday() == SUNDAY

                self[cur_date] = "Söndag"
                cur_date += rd(days=7)

        # ========= Static holidays =========
        self[date(year, 1, 1)] = "Nyårsdagen"

        self[date(year, 1, 6)] = "Trettondedag jul"

        # Source: https://sv.wikipedia.org/wiki/F%C3%B6rsta_maj
        if year >= 1939:
            self[date(year, 5, 1)] = "Första maj"

        # Source: https://sv.wikipedia.org/wiki/Sveriges_nationaldag
        if year >= 2005:
            self[date(year, 6, 6)] = "Sveriges nationaldag"

        self[date(year, 12, 24)] = "Julafton"
        self[date(year, 12, 25)] = "Juldagen"
        self[date(year, 12, 26)] = "Annandag jul"
        self[date(year, 12, 31)] = "Nyårsafton"

        # ========= Moving holidays =========
        e = easter(year)
        maundy_thursday = e - rd(days=3)
        good_friday = e - rd(days=2)
        easter_saturday = e - rd(days=1)
        resurrection_sunday = e
        easter_monday = e + rd(days=1)
        ascension_thursday = e + rd(days=39)
        pentecost = e + rd(days=49)
        pentecost_day_two = e + rd(days=50)

        assert maundy_thursday.weekday() == THURSDAY
        assert good_friday.weekday() == FRIDAY
        assert easter_saturday.weekday() == SATURDAY
        assert resurrection_sunday.weekday() == SUNDAY
        assert easter_monday.weekday() == MONDAY
        assert ascension_thursday.weekday() == THURSDAY
        assert pentecost.weekday() == SUNDAY
        assert pentecost_day_two.weekday() == MONDAY

        self[good_friday] = "Långfredagen"
        self[resurrection_sunday] = "Påskdagen"
        self[easter_monday] = "Annandag påsk"
        self[ascension_thursday] = "Kristi himmelsfärdsdag"
        self[pentecost] = "Pingstdagen"
        if year <= 2004:
            self[pentecost_day_two] = "Annandag pingst"

        # Midsummer evening. Friday between June 19th and June 25th
        self[date(year, 6, 19) + rd(weekday=FR)] = "Midsommarafton"

        # Midsummer day. Saturday between June 20th and June 26th
        if year >= 1953:
            self[date(year, 6, 20) + rd(weekday=SA)] = "Midsommardagen"
        else:
            self[date(year, 6, 24)] = "Midsommardagen"
            # All saints day. Friday between October 31th and November 6th
        self[date(year, 10, 31) + rd(weekday=SA)] = "Alla helgons dag"

        if year <= 1953:
            self[date(year, 3, 25)] = "Jungfru Marie bebådelsedag"


class SE(Sweden):
    pass




def Swedish_holi_work_days(dates):
    swedish_holidays =Sweden()  # or holidays.US(), or holidays.CountryHoliday('US')

    #How to use examples
    date(2015, 1, 1) in swedish_holidays  # True
    date(2015, 1, 2) in swedish_holidays  # False
    
    # The Holiday class will also recognize strings of any format
    # and int/float representing a Unix timestamp
    '2014-01-01' in swedish_holidays  # True
    '1/1/2014' in swedish_holidays    # True
    1388597445 in swedish_holidays    # True
    
    swedish_holidays.get('2014-01-01')  # "New Year's Day"
    
    # Easily create custom Holiday objects with your own dates instead
    # of using the pre-defined countries/states/provinces available
    custom_holidays = HolidayBase()
    # Append custom holiday dates by passing:
    # 1) a dict with date/name key/value pairs,
    custom_holidays.append({"2015-01-01": "New Year's Day"})
    # 2) a list of dates (in any format: date, datetime, string, integer),
    custom_holidays.append(['2018-01-01','2018-01-06','2018-03-30','2018-04-01','2018-04-02','2018-05-01','2018-05-10','2018-05-20','2018-06-06','2018-06-23','2018-11-03','2018-12-25','2018-12-26', '07/04/2015','2018-11-03','2018-11-03','2018-11-03','2018-12-22','2018-12-23','2018-12-24', '2018-12-25','2018-12-26','2018-12-29','2018-12-30','2018-12-31'])
    
    
    
    # 3) a single date item
    custom_holidays.append(date(2015, 12, 25))
    
    date(2015, 1, 1) in custom_holidays  # True
    date(2015, 1, 2) in custom_holidays  # False
    '12/25/2015' in custom_holidays      # True
    
    # For more complex logic like 4th Monday of January, you can inherit the
    # HolidayBase class and define your own _populate(year) method. See below
    # documentation for examples.
    
    
    for d in dates:
        if (d in custom_holidays):
            print(d in custom_holidays)
            
            
          
