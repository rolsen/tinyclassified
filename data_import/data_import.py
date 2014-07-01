"""Parses and filters CSV data into the tiny_classified listings collection.
"""
import csv
import os
import sys

from bs4 import BeautifulSoup
import pymongo

sys.path.append('..')
import tiny_classified

import services

INCREMENT = "increment"

DATA_SEP = ','

DATA_DIR = 'data'

FILE_AND_TAG_ASSOCIATIONS = {
    # 'Category / Tag Name': 'ExpectedFileNameBase'
    'Associations': 'Associations',
    'Education / Development': 'EducationDevelopment',
    'Insurance Jobs': 'InsuranceJobs',
    'Life and Health IMO/FMO/MGA': 'LifeandHealthIMOFMOMGA',
    'Office / Administration': 'OfficeAdministration',
    'P&C Aggregators-Clusters-Alliances': 'PCAggregators-Alliances-Clusters',
    'Professional Services': 'ProfessionalServices',
    'Sales and Marketing': 'SalesandMarketing',
    'Practice Building': 'PracticeBuilding',
    'Practice Building': 'PracticeBuilding',
    'Insurance Products Markets': 'InsuranceProductsMarkets',
}

EXPLODE_ON_UNRECOGNIZED_FIELD = True
COMPLAIN_ON_UNMATCHED_ROW_LENGTH = False

DATA_IMPORT_DATA = {
    'mongo_db': None,
    'mongo_listing_collection': None
}

def get_database():
    if not DATA_IMPORT_DATA['mongo_db']:
        DATA_IMPORT_DATA['mongo_db'] = \
            tiny_classified.get_db_adapter().get_database()

    return DATA_IMPORT_DATA['mongo_db']

def get_listing_collection():
    if not DATA_IMPORT_DATA['mongo_listing_collection']:
        DATA_IMPORT_DATA['mongo_listing_collection'] = \
            tiny_classified.get_db_adapter().get_listings_collection()

    return DATA_IMPORT_DATA['mongo_listing_collection']

def ensure_key(obj, key, default):
    if not obj.get(key):
        obj[key] = default

def get_beautiful_soup(value, get):
    if '<' in value:
        if get == 'text':
            return BeautifulSoup(value).get_text()
        elif get:
            return BeautifulSoup(value).get(get)

    return value

def strip_field_value(func):
    def func_wrapper(file_data, row, field_key, field_value):
        func(file_data, row, field_key, field_value.strip())

    return func_wrapper

def add_as_string_to(
    output_key,
    append=True,
    postpend='',
    get='text',
    overwrite=True,
    default=''
):
    @strip_field_value
    def inner(file_data, row, field_key, field_value):
        if not overwrite and row['output'].get(output_key):
            return False

        value = field_value

        if not value and default == INCREMENT:
            value = str(IncrementingNumber.get())

        value = get_beautiful_soup(value, get)

        value = value.strip()

        if not value:
            return False

        ensure_key(row['output'], output_key, '')
        if append:
            row['output'][output_key] += value + postpend
        else:
            row['output'][output_key] = value + postpend

        return False

    return inner

def add_contact(contact_type, default=''):
    @strip_field_value
    def inner(file_data, row, field_key, field_value):
        value = field_value
        if not value:
            value = default

        value = get_beautiful_soup(field_value, 'text')

        if not value:
            return False

        current_row_id = row.get('contact_id_next', None)
        if current_row_id != None:
            row['contact_id_next'] = current_row_id + 1

        ensure_key(row, 'contact_id_next', 0)

        ensure_key(row['output'], 'contact_infos', [])

        row['output']['contact_infos'].append({
            'type': contact_type,
            'value': value,
            '_id': row['contact_id_next']
        })
        return False

    return inner

def set_as_address_subfield(address_subfield, overwrite=True):
    @strip_field_value
    def inner(file_data, row, field_key, field_value):
        ensure_key(row['output'], 'address', {})
        ensure_key(row['output']['address'], address_subfield, '')

        if not overwrite and row['output']['address'][address_subfield]:
            return False

        row['output']['address'][address_subfield] = field_value
        return False

    return inner

def ignore(*args):
    pass

@strip_field_value
def complain_if_found(file_data, row, field_key, field_value):
    if field_value:
        print "complain_if_found:"
        print "  file_data['file_name']:", file_data['file_name']
        print "  row['fields']['company']:", row['fields']['company']
        print "  field_key:", field_key
        print "  field_value:", field_value
        print

@strip_field_value
def add_tags(file_data, row, field_key, field_value):
    ensure_key(row['output'], 'tags', {})
    category = file_data['category']
    row['output']['tags'][category] = []
    for subcat in field_value.split(','):
        subcat = subcat.strip()
        if subcat != '':
            row['output']['tags'][category].append(subcat)

    return False

@strip_field_value
def set_as_is_published(file_data, row, field_key, field_value):
    row['output']['is_published'] = True if field_value == 't' else False


@strip_field_value
def set_as_is_featured(file_data, row, field_key, field_value):
    row['output']['featured'] = field_value != ''


FIELD_STRATEGIES = {
    'company': add_as_string_to('name', get='text'),
    'address': set_as_address_subfield('street'),
    'phone': add_contact('phone'),
    'email': [
        # add_contact('email'),
        add_as_string_to('author_email', overwrite=True, default=INCREMENT)
    ],
    'url': ignore,
    'price': ignore,
    'city': set_as_address_subfield('city'),
    'state': set_as_address_subfield('state'),
    'zipcode': set_as_address_subfield('zip', overwrite=False),
    'description': add_as_string_to('about', postpend='\n', get='text'),
    'website': add_contact('website'),
    'zip': set_as_address_subfield('zip', overwrite=True),
    'geobaseid': ignore,
    'ispublished': set_as_is_published,
    'idnum': ignore,
    'fax': add_contact('fax'),
    'contactname': set_as_address_subfield('address'),
    'image1': complain_if_found,
    'image2': complain_if_found,
    'content': complain_if_found,
    'quickfacts': complain_if_found,
    'subtitle': complain_if_found,
    'longitude': add_as_string_to('longitude'),
    'latitude': add_as_string_to('latitude'),
    'image3': complain_if_found,
    'userid': ignore,
    'address2': set_as_address_subfield('street2'),
    'listingtype': add_as_string_to('listingtype', append=False),
    'datecreated': add_as_string_to('datecreated', append=False),
    'datemodified': add_as_string_to('datemodified', append=False),
    'createdby': complain_if_found,
    'modifiedby': complain_if_found,
    'subcategory': complain_if_found,
    'cccompany': complain_if_found,
    'image1desc': complain_if_found,
    'image2desc': complain_if_found,
    'image3desc': complain_if_found,
    'datefeatured': set_as_is_featured,
    'paymentstatus': ignore,
    'paymenttype': ignore,
    'category': add_tags,
    'displayorder': complain_if_found,
    'country': set_as_address_subfield('country'),
    'isapproved': ignore,
    'datedeleted': ignore,
    'introduction': ignore,
    'expires_on': ignore,
    'isexpired': ignore,
    'datepublished': ignore,
    'avgrating': ignore,
    'ratingcount': ignore,
    'enablerecommendations': ignore,
    'enableratings': ignore,
    'titletag': ignore,
    'metakeywords': ignore,
    'metadescription': ignore,
    'productname': ignore,
    'productcode': ignore,
    'useremail': add_as_string_to('author_email', overwrite=False),
    'ownername': add_as_string_to('name', overwrite=False),
    'userrating': ignore
}


def parse_data(fname):
    """Parses a file into a dict, using the first line of the file as the dict keys.
    """
    if not os.path.isfile(fname):
        raise RuntimeError("file '%s' does not exist" % fname)

    file_data = {
        'file_name': fname
    }
    with file(fname) as f:
        reader = csv.reader(f)
        file_data['header'] = reader.next()

        file_data['rows'] = []
        for row in reader:
            fields = {}
            row_dict = {}
            i = 0
            header_len = len(file_data['header'])
            if header_len != len(row) and COMPLAIN_ON_UNMATCHED_ROW_LENGTH:
                print "Unmatched row length:", fname, header_len, len(row)

            while i < len(row):
                field_header = file_data['header'][i]
                fields[field_header] = row[i]
                i = i + 1

            row_dict['fields'] = fields
            file_data['rows'].append(row_dict)

    return file_data


def process_row(file_data, row, field_strategies):
    """Filters the rows of a file.

    Deletes a row if manditory attributes are not present and calls strategy /
    closure function(s) for each field of the row.
    """
    fields = row['fields']
    if not fields['company'] and \
        not fields['contactname'] and \
        not fields['ownername']:
            reason = "'%s', '%s', '%s' are null" % ('company', 'contactname', 'ownername')
            RowDeleter.future_delete(file_data, row, reason)
            return True

    for field_key, field_value in row['fields'].iteritems():
        closure = field_strategies.get(field_key)
        if closure:
            if isinstance(closure, list):
                for c in closure:
                    ret = c(file_data, row, field_key, field_value)
                    if ret:
                        return ret
            else:
                closure(file_data, row, field_key, field_value)
    return False


def freak_out_if_null_value(data, keys):
    """Prints out a warning or sets a value in some cases.

    Prints out a warning if any of the given keys for all rows is 'empty'. If
    the key is of the output is 'about', this function will set that 'about'
    attribute to an empty string if it does not already exist.

    @param data: The data dict returned by parse_data_files
    @type data: dict
    @param keys: The keys to check for
    @type keys: list
    """

    # So horrendous
    for file_key, file_data in data.iteritems():
        for row in file_data['rows']:

            for key in keys:
                if row['output'].get(key, None) == None:
                    if key == 'about':

                        # So bad
                        index = file_data['rows'].index(row)
                        data[file_key]['rows'][index]['output']['about'] = ''

                    else:
                        print "Warning: %s is not a key!" % key

                    continue

                keyed_value = row['output'][key]
                if keyed_value == '':
                    if key != 'about':
                        print "Warning: %s is ''" % key
                    continue

                if keyed_value == {}:
                    print "Warning: %s is {}" % key
                    continue

                if keyed_value == []:
                    print "Warning: %s is []" % key
                    continue

                keyed_value = row['output'][key]
                if not isinstance(keyed_value, bool):
                    if '<' in keyed_value or '>' in keyed_value or '%' in keyed_value:
                        print "haz HTML? %s: %s" % (key, row['output'][key])


def get_and_mark_duplicate(data, row):
    for file_key, file_data in data.iteritems():
        for other_row in file_data['rows']:
            if not 'name' in other_row['output']:
                other_row['output']['name'] = other_row['output']['contact_infos'][0]['value']
            if not 'name' in row['output']:
                row['output']['name'] = row['output']['contact_infos'][0]['value']

            if (
                row['output']['name'] == other_row['output']['name'] and
                row['output'] != other_row['output']
            ):
                # So terrible
                RowDeleter.future_delete(file_data, other_row, "it's a duplicate")

                return other_row
    return None


def compress_duplicates(data):
    """Compresses all duplicate listings in data.

    @param data: The data dict returned by parse_data_files
    @type data: dict
    """
    for file_key, file_data in data.iteritems():
        for row in file_data['rows']:
            dup = get_and_mark_duplicate(data, row)
            if dup:
                row['output']['tags'].update(dup['output']['tags'])

                # So hideous
                RowDeleter.delete_all(data)


class IncrementingNumber():

     __number = 0

     @classmethod
     def get(cls):
        cls.__number = cls.__number + 1
        return cls.__number

class RowDeleter():

    @classmethod
    def future_delete(cls, file_data, row, reason):
        # print "Deleting row from %s because %s" % (
        #     file_data['file_name'],
        #     reason
        # )
        row['delete_me'] = True

    @classmethod
    def delete_all(cls, data):
        """Deletes all marked rows in data."""
        for file_key, file_data in data.iteritems():
            for row in file_data['rows']:
                if row.get('delete_me'):
                    rows_index = file_data['rows'].index(row)
                    del data[file_key]['rows'][rows_index]


def get_data_files(dir, ext='.csv'):
    """Gets the data files in a directory. Ignores subdirectories."""
    return filter(lambda file: file.endswith(ext), os.listdir(dir))


def parse_data_files(data_dir=DATA_DIR, file_tags=FILE_AND_TAG_ASSOCIATIONS):
    """Parses csv data into a dict and compresses duplicate listings.

    Returns a list of the form: {
        'filenamebase': {
            'category': 'tag / category',
            'file_name': 'data_dir/filename.csv',
            'rows': [
                {
                    'fields': {
                        'field from data file': 'raw value',
                        ...
                    },
                    'output': {
                        'field created while applying FIELD_STRATEGIES': 'value',
                        ...
                    }
                    'contact_id_next': <integer>
                },
                ...
            ]
        },
        ...
    }

    @return: All data from the data files
    @rtype: dict
    """
    data = {}

    files = get_data_files(data_dir)
    print "Data files: ", files

    unknown_data_file = False
    for data_file in files:
        fname = os.sep.join([data_dir, data_file])

        found_fbase = False
        for file_tag, fbase in file_tags.iteritems():
            if fbase in data_file:
                found_fbase = True
                data[fbase] = parse_data(fname)
                data[fbase]['category'] = file_tag
                break

        if not found_fbase:
            print
            print "Unknown file: %s" % fname
            print """    You will need to create a category / file base name
    association via FILE_AND_TAG_ASSOCIATIONS in %s""" % __file__
            unknown_data_file = True

    if unknown_data_file:
        sys.exit(1)

    for file_key, file_data in data.iteritems():
        for row in file_data['rows']:
            row['output'] = {}
            ret = process_row(file_data, row, FIELD_STRATEGIES)

            # if not ret:
            #     print '+++++++++++++++'
            #     for key, value in row['output'].iteritems():
            #         print key, value
            #     print '\n\n'

        RowDeleter.delete_all(data)

    for file_key, file_data in data.iteritems():
        for row in file_data['rows']:
            freak_out_if_null_value(data, [
                'listingtype',
                'name',
                'tags',
                'author_email',
                # 'longitude',
                'datecreated',
                'address',
                # 'latitude',
                'datemodified',
                'is_published',
                # 'contact_id_next',
                # 'contact_infos',
                'about'
            ])

    compress_duplicates(data)

    return data


def create_listing(listing):
    services.listing_service.create(listing)


def main():
    """Main function that imports all data.

    Main function to orchestrate:
        - clearing the collection,
        - parsing csv files,
        - adding listings to the collection,
        - saving meta data
    """
    print "Parsing CSVs..."
    data = parse_data_files()

    mongo_listing_collection = get_listing_collection()
    mongo_listing_collection.remove({})
    print "Clearing the collection:", mongo_listing_collection.count()

    print "Adding listings..."
    for file_key, file_data in data.iteritems():
        for row in file_data['rows']:
            output = row['output']
            listing = output

            create_listing(listing)


    print "Saving ['meta'] : {'name': '_tinyclassified', 'next_author_id'}..."
    get_database()['meta'].save({'name': '_tinyclassified', 'next_author_id': IncrementingNumber.get()})

    print "Success"


if __name__ == "__main__":
    tiny_classified.initialize_standalone()
    main()
