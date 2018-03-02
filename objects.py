'''
FDA Data Models

'''
import os, csv
from dateutil import relativedelta
from datetime import datetime
from itertools import groupby

base_directory =  os.path.dirname(os.path.abspath(__file__))
product_file = os.path.join(base_directory, 'product.txt')
package_file = os.path.join(base_directory, 'package.txt')

class Package(object):
    def __init__(self, pid, pndc, ndcpc, pckdes, stdate, eddate, excl, samp):
        self.product_id = pid
        self.product_ndc = pndc
        self.ndc_package_code = ndcpc
        self.package_description = pckdes
        self.start_marketing_date = stdate
        self.end_marketing_date = eddate
        self.ndc_exclude_flag = excl
        self.sample_package = samp
        self.ndc11 = ''

    def __str__(self):
        return self.ndc11 + ' ' + self.package_description
    
    def __repr__(self):
        return self.ndc11 + ' ' + self.package_description


class Product(object):
    def __init__(self, pid, pndc, typnm, prpnm, prpnmsf, nonprpnm, dsg,
                    rtnme, stdate, eddate, mrktcat, applnm, lblnm, subs,
                    act_num_str, act_ing_unit, phm_class, deasc, excl,
                    lstng_rcrd_thr):
        self.product_id = pid
        self.product_ndc = pndc
        self.product_type_name = typnm
        self.proprietary_name = prpnm
        self.proprietary_name_suffix = prpnmsf
        self.non_proprietary_name = nonprpnm
        self.dosage_form_name = dsg
        self.route_name = rtnme
        self.start_marketing_date = stdate
        self.end_marketing_date = eddate
        self.marketing_category_name = mrktcat
        self.application_number = applnm
        self.labeler_name = lblnm
        self.substance_name = subs
        self.active_numerator_strength = act_num_str
        self.active_ingredient_unit = act_ing_unit
        self.pharm_classes = phm_class
        self.dea_schedule = deasc
        self.ndc_exclude_flag = excl
        self.listing_record_certified_through = lstng_rcrd_thr
        self.generic_start_date = None
        self.brand_start_date = None

    def __str__(self):
        return self.proprietary_name + ' ' + self.product_ndc

    def __repr__(self):
        return self.proprietary_name + ' ' + self.product_ndc


def package_line_to_object(aline):
    package = Package(*aline)
    n1, n2, n3 = package.ndc_package_code.split('-')
    package.ndc11 = '{:05d}{:04d}{:02d}'.format(int(n1), int(n2), int(n3))
    if package.start_marketing_date:
        package.start_marketing_date = datetime.strptime(
                    package.start_marketing_date, '%Y%m%d'
                )
    if package.end_marketing_date:
        package.end_marketing_date = datetime.strptime(
                    package.end_marketing_date, '%Y%m%d'
                )

    return package


def get_packages():
    f = open(package_file, 'r')
    c = csv.reader(f, delimiter='\t')
    packages = []
    for aline in c:
        if c.line_num == 1:
            continue

        try:
            packages.append(package_line_to_object(aline))

        except:
            print('Could not create package from aline:\n\n' + '\n'.join(aline))
    
    f.close()

    return packages

def product_line_to_object(aline):
    product = Product(*aline)
    assert product.product_type_name == 'HUMAN PRESCRIPTION DRUG'
    substances = product.substance_name.split(';')
    substances = [x.strip().upper() for x in substances]
    substances.sort()
    product.proprietary_name = product.proprietary_name.upper().strip()
    product.substance_name = substances
    product.non_proprietary_name = product.non_proprietary_name.strip()
    product.start_marketing_date = datetime.strptime(
            product.start_marketing_date, '%Y%m%d'
        )
    if product.end_marketing_date:
        product.end_marketing_date = datetime.strptime(
                    product.end_marketing_date, '%Y%m%d'
                )

    if product.listing_record_certified_through:
        product.listing_record_certified_through = datetime.strptime(
                    product.listing_record_certified_through, '%Y%m%d'
                )

    product.non_proprietary_name = product.non_proprietary_name.upper()
    product.pharm_classes = [x.strip() for x in product.pharm_classes.split(',')]
    

    return product 
 

def get_products():
    f = open(product_file, 'r')
    c = csv.reader(f, delimiter='\t')
    products = []
    for aline in c:
        try:
            products.append(product_line_to_object(aline))

        except:
            continue
    
    return products


'''
Crosswalks, cacheing, and filtering examples

'''

products = []

def cache_products(refresh=False):
    if len(globals()['products']) == 0 or refresh == True:
        globals()['products'] = get_products()

    return globals()['products']

def get_product_ndc_xwalk():
    products = cache_products()
    return dict([(x.product_ndc, x) for x in products])

def get_generic_ndc_walk():
    products = build_generic_products_start_dates()
    return dict([(x.product_ndc, x) for x in products])

def get_brand_ndc_walk():
    products = build_brand_products_start_dates()
    return dict([(x.product_ndc, x) for x in products])


def get_generics_products():
    products = cache_products()
    generic_categories = ['ANDA', 'NDA AUTHORIZED GENERIC']
    return list(
            filter(
                lambda x: x.marketing_category_name in generic_categories and x.non_proprietary_name, 
                products
                )
            )


def build_generic_products_start_dates():
    generics = get_generics_products()
    sortfunc = lambda x: ';'.join(x.non_proprietary_name) + x.start_marketing_date.strftime('%Y%m%d')
    sgenerics = sorted(generics, key=sortfunc)
    grpfunc = lambda x: ';'.join(x.non_proprietary_name)
    keys = []
    groups = []
    out_generics = []
    for key, grp in groupby(sgenerics, key=grpfunc):
        grp_cache = list(grp)
        if not key:
            for product in grp_cache:
                product.generic_start_date = product.start_marketing_date
                out_generics.append(product)

        else:
            sdate = grp_cache[0].start_marketing_date
            for product in grp_cache:
                product.generic_start_date = sdate
                out_generics.append(product)

    sortfunc = lambda x: ';'.join(x.substance_name) + x.generic_start_date.strftime('%Y%m%d')
    sgenerics = sorted(out_generics, key=sortfunc)
    grpfunc = lambda x: ';'.join(x.substance_name)
    keys = []
    groups = []
    out_generics = []
    for key, grp in groupby(sgenerics, key=grpfunc):
        grp_cache = list(grp)
        if not key:
            for product in grp_cache:
                product.generic_start_date = product.generic_start_date
                out_generics.append(product)

        else:
            sdate = grp_cache[0].generic_start_date
            for product in grp_cache:
                product.generic_start_date = sdate
                out_generics.append(product)


    return out_generics

def get_generic_products_since_dobj(date_thresh):
    generics = build_generic_products_start_dates()
    return list(
            filter(
                lambda x: x.generic_start_date >= date_thresh,
                generics
                )
            )

def get_generic_packages_since_dobj(date_thresh):
    generic_products = get_generic_products_since_dobj(date_thresh)
    generic_product_ndcs = [x.product_ndc for x in generic_products]
    return list(
                filter(
                    lambda x: x.product_ndc in generic_product_ndcs,
                    get_packages()
                    )
                )

def get_brand_products():
    products = cache_products()
    brand_categories = ['NDA', 'BLA']
    return list(
            filter(
                lambda x: x.marketing_category_name in brand_categories and x.proprietary_name, 
                products
                )
            )


def build_brand_products_start_dates():
    brands = get_brand_products()
    sortfunc = lambda x: ';'.join(x.non_proprietary_name) + x.start_marketing_date.strftime('%Y%m%d')
    sbrands = sorted(brands, key=sortfunc)
    grpfunc = lambda x: ';'.join(x.non_proprietary_name)
    keys = []
    groups = []
    out_brands = []
    for key, grp in groupby(sbrands, key=grpfunc):
        grp_cache = list(grp)
        if not key:
            for product in grp_cache:
                product.brand_start_date = product.start_marketing_date
                out_brands.append(product)

        else:
            sdate = grp_cache[0].start_marketing_date
            for product in grp_cache:
                product.brand_start_date = sdate
                out_brands.append(product)

    return out_brands

def get_brand_products_since_dobj(date_thresh):
    brands = build_brand_products_start_dates()
    return list(
            filter(
                lambda x: x.brand_start_date >= date_thresh,
                brands
                )
            )

def get_brand_packages_since_dobj(date_thresh):
    brand_products = get_brand_products_since_dobj(date_thresh)
    brand_product_ndcs = [x.product_ndc for x in brand_products]
    return list(
                filter(
                    lambda x: x.product_ndc in brand_product_ndcs,
                    get_packages()
                    )
                )

