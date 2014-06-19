"""Parses and filters CSV data into JSON.
"""
import csv
import os
import sys

from bs4 import BeautifulSoup
import pymongo

sys.path.append('..')
import tiny_classified

MONGO_DATABASE_NAME = 'tiny_classified'
MONGO_HOST = 'localhost'
MONGO_PORT = 27017

mongo_client = pymongo.mongo_client.MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT
)
mongo_db = mongo_client.db[MONGO_DATABASE_NAME]
mongo_listing_collection = mongo_db['listing']

# DEFAULT_EMAIL = 'admin@insurance-forums.net'
INCREMENT = "increment"

DATA_SEP = ','

DATA_DIR = 'data'

FILES = {
    'Associations_2014-06-11.csv': 'Associations',
    'EducationDevelopment_2014-06-11.csv': 'Education / Development',
    'InsuranceJobs_2014-06-11.csv': 'Insurance Jobs',
    'LifeandHealthIMOFMOMGA_2014-06-11.csv': 'Life and Health IMO/FMO/MGA',
    'OfficeAdministration_2014-06-11.csv': 'Office / Administration',
    'PCAggregators-Alliances-Clusters_2014-06-11.csv': 'P&C Aggregators-Clusters-Alliances',
    'ProfessionalServices_2014-06-11.csv': 'Professional Services',
    'SalesandMarketing_2014-06-11.csv': 'Sales and Marketing',
}

EXPLODE_ON_UNRECOGNIZED_FIELD = True
COMPLAIN_ON_UNMATCHED_ROW_LENGTH = False


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

def add_as_string_to(
    output_key,
    append=True,
    postpend='',
    get='text',
    overwrite=True,
    default=''
):
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

def complain_if_found(file_data, row, field_key, field_value):
    if field_value:
        print "complain_if_found:"
        print "  file_data['file_name']:", file_data['file_name']
        print "  row['fields']['company']:", row['fields']['company']
        print "  field_key:", field_key
        print "  field_value:", field_value
        print

def add_tags(file_data, row, field_key, field_value):
    ensure_key(row['output'], 'tags', {})
    category = file_data['category']
    row['output']['tags'][category] = []
    for subcat in field_value.split(','):
        row['output']['tags'][category].append(subcat)

    return False

def set_as_is_published(file_data, row, field_key, field_value):
    row['output']['is_published'] = True if field_value == 't' else False

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
    'datefeatured': ignore,
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
        raise "file '%s' does not exist" % fname

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
                        print "Oh noes! %s is not a key!" % key

                    continue

                keyed_value = row['output'][key]
                if keyed_value == '':
                    if key != 'about':
                        print "Oh noes! %s is ''" % key
                    continue

                if keyed_value == {}:
                    print "Oh noes! %s is {}" % key
                    continue

                if keyed_value == []:
                    print "Oh noes! %s is []" % key
                    continue

                keyed_value = row['output'][key]
                if not isinstance(keyed_value, bool):
                    if '<' in keyed_value or '>' in keyed_value or '%' in keyed_value:
                        print "haz HTML? %s: %s" % (key, row['output'][key])


def get_and_mark_duplicate(data, row):
    for file_key, file_data in data.iteritems():
        for other_row in file_data['rows']:
            if (
                row['output']['name'] == other_row['output']['name'] and
                row['output'] != other_row['output']
            ):
                # So terrible
                RowDeleter.future_delete(file_data, other_row, "it's a duplicate")

                return other_row
    return None


def compress_duplicates(data):
    for file_key, file_data in data.iteritems():
        for row in file_data['rows']:
            dup = get_and_mark_duplicate(data, row)
            if dup:
                row['output']['tags'].update(dup['output']['tags'])

                # So hideous
                RowDeleter.delete_all(data)


def add_row_to_mongo(row):
    print "++++++++++++++++"
    print row['output']
    mongo_listing_collection.save(row['output'])
    print "================"
    print


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
        for file_key, file_data in data.iteritems():
            for row in file_data['rows']:
                if row.get('delete_me'):
                    rows_index = file_data['rows'].index(row)
                    del data[file_key]['rows'][rows_index]


def gogogo(data_dir=DATA_DIR, files=FILES):
    data = {}
    for fbase, file_tag in files.iteritems():
        fname = os.sep.join([data_dir, fbase])
        data[fbase] = parse_data(fname)
        data[fbase]['category'] = file_tag

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

    # for file_key, file_data in data.iteritems():
    #     for row in file_data['rows']:
    #         add_row_to_mongo(row)

    mongo_listing_collection.remove( { } ) # Clear collection!
    print "mongo_listing_collection dataSize():", mongo_listing_collection.count()

    return data


def create_listing(listing):
    tiny_classified.services.listing_service.create(listing)


def load_data_import():
    data = gogogo()

    for file_key, file_data in data.iteritems():
        for row in file_data['rows']:
            output = row['output']
            listing = output

            create_listing(listing)


if __name__ == "__main__":
    load_data_import()
