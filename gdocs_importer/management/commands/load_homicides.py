from dateutil import parser
from django.core.management.base import BaseCommand
from optparse import make_option
from datetime import datetime

from gdocs_importer import logger
from gdocs_importer.models import Homicide
from gdocs_importer.lib import get_spreadsheet

GOOGLE_KEY = '0Ark-PJD-Ze_DdHBfaUtjZzVjcm51azc5dVIyYk5JT2c'
GOOGLE_SHEET = 0
GOOGLE_ACCOUNT = ''
GOOGLE_PASS = ''


class Command(BaseCommand):
    """
    Downloads and ingests all homicides
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '-c',
            '--clear',
            action='store_true',
            default=False,
            dest='clear',
            help='Clear all homicides in the DB.'),
        make_option(
            '-f',
            '--first',
            action='store_true',
            default=False,
            dest='first',
            help='Run the script for the first time.'),
    )

    def get_version(self):
        return "0.1"

    def handle(self, *args, **options):
        first_time = False
        if options['clear']:
            logger.info("Clearing all homicides from the DB.")
            Homicide.objects.all().delete()
        if options['first']:
            first_time = True

        self.init_reader(first_time)

    def dict_for_row(self, row):
        """
        Get a row of data, return a dict whose keys are Homicide properties
        and values are instance values for that row.
        """
        kwargs = {
            'address': row[0],
            'date': row[1],
            'time': row[2],
            'location': row[3],
            'neighborhood': row[4],
            'age': row[5],
            'gender': row[6],
            'race': row[7],
            'name': row[8],
            'cause': row[9],
            'story_url': row[10],
            'rd_number': row[11],
            'charges_url': row[12],
        }

        return kwargs

    def get_google_csv(self, key, sheet):
        data = list(get_spreadsheet(GOOGLE_ACCOUNT, GOOGLE_PASS, GOOGLE_KEY))
        return [self.dict_for_row(item) for item in data[1:]]

    def init_reader(self, first_time):
        homicide_csv = self.get_google_csv(GOOGLE_KEY, GOOGLE_SHEET)
        already_exists = 0
        start_time = datetime.now()

        for i, row in enumerate(homicide_csv):
            address = row['address']
            cleaned_date_time = self.clean_date_time(row['date'], row['time'])
            location = row['location']
            neighborhood = row['neighborhood']
            age = self.clean_age(row['age'])
            gender = self.clean_gender(row['gender'])
            race = row['race']
            name = row['name']
            cause = row['cause']
            story_url = self.clean_link(row['story_url'])

            rd_number = row['rd_number']
            charges_url = self.clean_link(row['charges_url'])

            if first_time is not True:
                try:
                    homicide = Homicide.objects.get(
                        address=address)
                    already_exists = already_exists + 1
                    print "made it here"
                    if homicide.has_changed(address) or homicide.has_changed(date_time) or homicide.has_changed(location) or homicide.has_changed(neighborhood) or homicide.has_changed(age) or homicide.has_changed(gender) or homicide.has_changed(race) or homicide.has_changed(name) or homicide.has_changed(cause) or homicide.has_changed(story_url) or homicide.has_changed(rd_number) or homicide.has_changed(charges_url):
                        print "blah"
                        homicide.save()
                        logger.info('This changed, saving new stuff.')

                except Homicide.DoesNotExist:
                    homicide = Homicide(
                        address=address,
                        date_time=cleaned_date_time,
                        location=location,
                        neighborhood=neighborhood,
                        age=age,
                        gender=gender,
                        race=race,
                        name=name,
                        cause=cause,
                        story_url=story_url,
                        rd_number=rd_number,
                        charges_url=charges_url)
                    homicide.save()

                    logger.info(
                        "Already exists, now up to %s already" % already_exists)

                else:
                    homicide = Homicide(
                        address=address,
                        date_time=cleaned_date_time,
                        location=location,
                        neighborhood=neighborhood,
                        age=age,
                        gender=gender,
                        race=race,
                        name=name,
                        cause=cause,
                        story_url=story_url,
                        rd_number=rd_number,
                        charges_url=charges_url)
                    homicide.save()
                    logger.info("Saved homicide at %s" % address)

            else:
                homicide = Homicide(
                    address=address,
                    date_time=cleaned_date_time,
                    location=location,
                    neighborhood=neighborhood,
                    age=age,
                    gender=gender,
                    race=race,
                    name=name,
                    cause=cause,
                    story_url=story_url,
                    rd_number=rd_number,
                    charges_url=charges_url)
                homicide.save()
                logger.info("Saved homicide at %s" % address)
                logger.info("Skipped %s so far" % already_exists)

        finish_time = datetime.now()
        total_time = finish_time - start_time
        logger.info(
            "All done, took %s seconds to complete." % total_time.seconds)
        logger.info("Skipped %s homicides." % already_exists)

    def clean_date_time(self, date, time):
        """
        Turn the date and time into one field that Django will understand
        properly instead of being weird, just in case it was inputted wrong.
        """
        try:
            cleaned_date_time = parser.parse(
                "%s %s" % (date, time), ignoretz=True)
        except ValueError:
            cleaned_date_time = None

        return cleaned_date_time

    def clean_age(self, age):
        try:
            isinstance(age, int)
            age = int(age)
            if age is None:
                age = None
                return age
            else:
                return age
        except ValueError:
            age = None
            return age

    def clean_gender(self, gender):
        try:
            isinstance(gender, basestring)
        except ValueError:
            new_gender = "Unkown"
            return new_gender

    def clean_link(self, link):
        try:
            isinstance(link, basestring)
            if len(link) > 200:
                new_link = None
                return new_link
            elif link == "":
                new_link = None
                return new_link
            else:
                return link
        except ValueError:
            new_link = None
            return new_link
