'''
FDA Data Models

'''
import os, csv
from dateutil import relativedelta
from datetime import datetime

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
        self.ndc11 = ''


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

def get_product_id_ndc11_xwalk():
    packages = get_packages()
    return dict([(x.product_id, x.ndc11) for x in packages])

product_id_ndc11_xwalk = get_product_id_ndc11_xwalk()

def product_line_to_object(aline):
    product = Product(*aline)
    product.ndc11 =  product_id_ndc11_xwalk[product.product_id]
    if product.start_marketing_date:
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
            #print('Could not create product from aline:\n\n' + '\n'.join(aline))
    
    return products



