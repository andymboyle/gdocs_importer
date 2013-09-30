from dateutil import parser
from django.core.management.base import BaseCommand
from optparse import make_option
from datetime import datetime

from gdocs_importer import logger
from gdocs_importer.models import Homicide
from gdocs_importer.lib import get_spreadsheet

GOOGLE_KEY = '0Ark-PJD-Ze_DdHBfaUtjZzVjcm51azc5dVIyYk5JT2c'  # Enter the Google key here
GOOGLE_SHEET = '0'  # This is the Google spreadsheet sheet number you're looking at, and 0 is the default first one
GOOGLE_ACCOUNT = 'yourgmail@gmail.com'  # Enter your Google account name here, blahwhatever@gmail.com
GOOGLE_PASS = 'password'  # Enter your Google account password here


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
        """
        Connect to the Google doc and return a dict of the data to be used,
        including finding the header and the rest of the data
        """
        data = list(get_spreadsheet(
            GOOGLE_ACCOUNT, GOOGLE_PASS, key, sheet))
        return [self.dict_for_row(item) for item in data[1:]]

    def init_reader(self, first_time):
        """
        Loop through the spreadsheet and load the data
        """
        homicide_csv = self.get_google_csv(GOOGLE_KEY, GOOGLE_SHEET)
        already_exists = 0
        created_homicides = 0
        start_time = datetime.now()

        # Run through the spreadsheet, assigning values to certain fields
        for i, row in enumerate(homicide_csv):
            address = row['address']
            # Send some fields to functions that clean them
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

            # If the command doesn't use --first, run it this way.
            if first_time is not True:
                # Try and see if this homicide exists. If so, skip it.
                try:
                    homicide = Homicide.objects.get(
                        address=address,
                        name=name)
                    already_exists = already_exists + 1

                    logger.info('Already exists, skipping it.')

                # If the homicide doesn't exist, create it.
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
                    created_homicides = created_homicides + 1
                    logger.info("Saved homicide at %s" % address)

            # If you're running it with --first, save everything.
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
                created_homicides = created_homicides + 1
                logger.info("Saved homicide at %s" % address)
                logger.info("Skipped %s so far" % already_exists)

        finish_time = datetime.now()
        total_time = finish_time - start_time
        logger.info(
            "All done, took %s seconds to complete." % total_time.seconds)
        logger.info("Skipped %s homicides." % already_exists)
        logger.info("Created %s homicides." % created_homicides)

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
        """
        Make sure it's an integer that's been entered, otherwise it'll break
        everything. If not, ignore it.
        """
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
        """
        Make sure it's a string that's been entered, otherwise it'll break
        everything. If not, save it as an unknown gender
        """

        try:
            isinstance(gender, basestring)
        except ValueError:
            new_gender = "Unkown"
            return new_gender

    def clean_link(self, link):
        """
        Django can only store URLs up to 200 characters, so if it's too long,
        this will allow you to ignore the URL and not break your importer.
        """

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
