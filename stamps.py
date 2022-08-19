import json
import logging
import os
import sys
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup as Soup
from requests.auth import HTTPBasicAuth
from unidecode import unidecode

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
FILE_NAME, ORDER_ID = sys.argv

USER = 'test'
PASSWORD = 'test'
INTEGRATIONID = 'test'
CONFIG_URL = 'https://swsim.testing.stamps.com/swsim/swsimv111.asmx'

DM_LOGIN = HTTPBasicAuth('test', 'test')

today_date = datetime.today().strftime('%Y-%m-%d')
tomorrow_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')


def get_dreammachines_data():
    url = '192.168.0.100/...'
    response = requests.get(url, auth=DM_LOGIN, verify=False)
    if response.status_code == 200:
        data = response.json()
        return data['collection']
    else:
        raise ValueError('Cant get Dream Machines data')


def get_order_data(value):
    url = f'192.168.0.100/...?id={value}'
    response = requests.get(url, auth=DM_LOGIN, verify=False)
    if response.status_code == 200:
        data = response.json()
        return data['collection']
    else:
        raise ValueError('Cant get Order data')


def post_order_data(data):
    url = f'192.168.0.100/...'
    response = requests.post(url, data=data, auth=DM_LOGIN, verify=False)
    return response.status_code, response.text, response.url


def get_shipments_data(data):
    url = f'192.168.0.100/...?name={data}'
    response = requests.get(url, auth=DM_LOGIN, verify=False)
    if response.status_code == 200:
        data = response.json()
        return data['collection']
    else:
        raise ValueError('Cant get Order data')


def post_shipments_data(data):
    url = f'192.168.0.100/...'
    response = requests.post(url, data=data, auth=DM_LOGIN, verify=False)
    return response.status_code, response.text, response.url


def put_shipments_data(data):
    url = f'192.168.0.100/...'
    response = requests.put(url, data=data, auth=DM_LOGIN, verify=False)
    if response.status_code == 200:
        data = response.json()
        return data['others']
    else:
        raise ValueError('Cant create new shipment_data')


def post_label_data(data):
    url = '192.168.0.100/...'
    response = requests.post(url, data=data, auth=DM_LOGIN, verify=False)
    return response.status_code, response.text, response.url


def put_error(data):
    url = '192.168.0.100/...'
    response = requests.put(url, data=data, auth=DM_LOGIN, verify=False)
    if response.status_code == 200:
        data = response.json()
        return response.status_code, response.text, response.url, data
    else:
        raise ValueError('Cant put error to user_log')


def mailer(data):
    data_json = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    url = f'192.168.0.100/...'
    response = requests.post(url, data=data_json, auth=DM_LOGIN, verify=False, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data['errors'][0]:
            return data
        raise ValueError(data['errors'])
    else:
        raise ValueError('Cant send email')


def authenticator():
    headers = {
        'User-Agent': 'Crosscheck Networks SOAPSonar',
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/AuthenticateUser',
        'Content-Length': '####',
    }
    body = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:tns="http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111">
          <soap:Body>
            <tns:AuthenticateUser>
              <tns:Credentials>
                <tns:IntegrationID>{INTEGRATIONID}</tns:IntegrationID>
                <tns:Username>{USER}</tns:Username>
                <tns:Password>{PASSWORD}</tns:Password>
              </tns:Credentials>
            </tns:AuthenticateUser>
          </soap:Body>
        </soap:Envelope>"""

    response = requests.post(CONFIG_URL, data=body, headers=headers)
    soup = Soup(response.content, 'xml')
    response_authenticator = soup.Authenticator.get_text()
    return response_authenticator


def get_account_info():
    headers = {
        'User-Agent': 'Crosscheck Networks SOAPSonar',
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/GetAccountInfo',
        'Content-Length': '####',
    }
    body = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:tns="http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111">
          <soap:Body>
            <tns:GetAccountInfo>
              <tns:Authenticator>{authenticator().replace('&', '&amp;')}</tns:Authenticator>
            </tns:GetAccountInfo>
          </soap:Body>
        </soap:Envelope>"""

    response = requests.post(CONFIG_URL, data=body, headers=headers)
    response_content = Soup(response.content, 'xml')
    return response_content


def add_funds(purchase_amount, control_total):
    headers = {
        'User-Agent': 'Crosscheck Networks SOAPSonar',
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/PurchasePostage',
        'Content-Length': '####',
    }
    body = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:tns="http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111">
          <soap:Body>
            <tns:PurchasePostage>
              <tns:Authenticator>{authenticator().replace('&', '&amp;')}</tns:Authenticator>
              <tns:PurchaseAmount>{purchase_amount}</tns:PurchaseAmount>
              <tns:ControlTotal>{control_total}</tns:ControlTotal>
            </tns:PurchasePostage>
          </soap:Body>
        </soap:Envelope>"""

    response = requests.post(CONFIG_URL, data=body, headers=headers)
    response_content = Soup(response.content, 'xml')
    return response_content


def create_label(package, package_type, weight, index):
    headers = {
        'User-Agent': 'Crosscheck Networks SOAPSonar',
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/CreateIndicium',
        'Content-Length': '####',
    }
    body = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:sws="http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111"
                       xmlns:tns="http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111">
          <soap:Body>
            <sws:CreateIndicium>
              <sws:Authenticator>{authenticator().replace('&', '&amp;')}</sws:Authenticator>
              <sws:IntegratorTxID>{str(order_data['id']) + '_' + order_data['name'] + f'_SH{index}'}</sws:IntegratorTxID>
              <sws:TrackingNumber/>
              <sws:Rate>
                <sws:From>
                  <sws:Company>{unidecode(dm_data['name'])}</sws:Company>
                  <sws:Address1>{unidecode(dm_data['house'] + dm_data['street'])}</sws:Address1>
                  <sws:City>{unidecode(dm_data['city'])}</sws:City>
                  <sws:State>MI</sws:State>
                  <sws:ZIPCode>{unidecode(dm_data['postal'])}</sws:ZIPCode>
                </sws:From>
                <sws:To>
                  <sws:FullName>{unidecode(order_data['delivery_name'])}</sws:FullName>
                  <sws:Address1>{unidecode(order_data['delivery_housenr'] + ' ' + order_data['delivery_street'])}</sws:Address1>
                  <sws:City>{unidecode(order_data['delivery_city'])}</sws:City>
                  <sws:State>{unidecode(order_data['delivery_state'])}</sws:State>
                  <sws:ZIPCode>{unidecode((order_data['delivery_postal_code']).replace('-', ''))}</sws:ZIPCode>
                </sws:To>
                <sws:Amount>1</sws:Amount>
                <sws:ServiceType>{package_type}</sws:ServiceType>
                <sws:WeightOz>{weight}</sws:WeightOz>
                <sws:PackageType>{package}</sws:PackageType>
                <sws:ShipDate>{tomorrow_date}</sws:ShipDate>
              </sws:Rate>
              <sws:SampleOnly>false</sws:SampleOnly>
              <sws:ImageType>Pdf</sws:ImageType>
              <sws:PaperSize>Letter85x11</sws:PaperSize>
            </sws:CreateIndicium>
          </soap:Body>
        </soap:Envelope>"""

    response = requests.post(CONFIG_URL, data=body, headers=headers)
    response_content = Soup(response.content, 'xml')
    return response_content


def reprinting(tracking_number, format):
    if format == 'Zpl':
        paper_size = 'Default'
    else:
        paper_size = 'Letter85x11'
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/ReprintIndicium',
        'Content-Length': 'length',
    }
    body = f"""
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <ReprintIndicium xmlns="http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111">
          <indiciumRequest>
            <Authenticator>{authenticator().replace('&', '&amp;')}</Authenticator>
            <TrackingNumber>{tracking_number}</TrackingNumber>
            <ImageType>{format}</ImageType>
            <ImageDpi>ImageDpi300</ImageDpi>
            <EltronPrinterDpiType>Default</EltronPrinterDpiType>
            <RotationDegrees>0</RotationDegrees>
            <HorizontalOffset>0</HorizontalOffset>
            <VerticalOffset>0</VerticalOffset>
            <PrintDensity>0</PrintDensity>
            <PaperSize>{paper_size}</PaperSize>
            <StartRow>0</StartRow>
            <StartColumn>0</StartColumn>
            <ReturnImageData>true</ReturnImageData>
          </indiciumRequest>
        </ReprintIndicium>
      </soap:Body>
    </soap:Envelope>"""

    response = requests.post(CONFIG_URL, data=body, headers=headers)
    response_content = Soup(response.content, 'xml')
    return response_content


if __name__ == "__main__":
    try:
        # NEED TO EXCEPTION FINAL ERRORS
        checkerrors = False
        first_shipments_data = []

        # GET ACCONT INFO. IF NEED - ADD FUNDS
        account_info = get_account_info()
        available_postage = account_info.AvailablePostage.get_text()
        control_total = account_info.ControlTotal.get_text()

        if int(float(available_postage)) < 40:
            purchase_amount = 100
            response_add_funds = add_funds(purchase_amount, control_total)

            body_text = f"Purchase Status: {response_add_funds.PurchaseStatuas.get_text()}<br>" \
                        f"Transaction ID: {response_add_funds.TransactionID.get_text()}<br>" \
                        f"Available Postage: {response_add_funds.AvailablePostage.get_text()}<br>" \
                        f"Control Total: {response_add_funds.ControlTotal.get_text()}<br>" \
                        f"<br><br>Authenticator: <br>{response_add_funds.Authenticator.get_text()}<br>"

            email_body_addfunds = {"email": "test",
                                   "email_title": "Doladowanie stamps",
                                   "message_title": "Doladowanie stamps",
                                   "lang": "pl",
                                   "sections": [{
                                       "header": "Doladowanie stamps",
                                       "body": f"{body_text}"
                                   }]}

            mailer(email_body_addfunds)

        # GET DREAM MACHINES DATA
        dm_data = get_dreammachines_data()[0]

        # GET ORDER DATA
        order_data = get_order_data(ORDER_ID)[0]
        json_items = json.loads(order_data['json'])
        index = 1
        for item in json_items:
            if item['item_name'] == 'Transport':
                continue
            if item['item_name'] == 'DM Pad XL' or item['item_name'] == 'DM Pad XXL':
                package = 'Package'
                package_type = 'US-PM'
                weight = 14
            else:
                package = 'Package'
                package_type = 'US-FC'
                weight = 11
            if item['item_name'] == 'DM Pad XL' or item['item_name'] == 'DM Pad XXL' or item['item_name'] == 'DM Pad L':
                shipment_packages_details = '[{"contents": "Mousepads", "hasBatteries": 0, "dimmensions": {"width": "1", "height": "1", "length": "1"}, "weight": "1", "insurance": "0"}]'
            else:
                shipment_packages_details = '[{"contents": "Mice", "hasBatteries": 0, "dimmensions": {"width": "1", "height": "1", "length": "1"}, "weight": "1", "insurance": "0"}]'
            order_name = f'"{order_data["name"]}"'
            info = f'{{"check":"ok","order_number": "{order_name}"}}'

            # GET LABEL DATA
            label = create_label(package, package_type, weight, index)
            tracking_number = label.TrackingNumber.get_text()

            # CHECK FIRST SHIPPING TRACKING AND NAME FOR EMAIL (BECAUSE WE SEND ONLY ONE EMAIL TO CLIENT)
            if index == 1:
                first_tracking_number = tracking_number
                first_shipment_name = order_data['name'] + f'SH{index}'
            shipment_name = order_data['name'] + f'SH{index}'
            print(shipment_name)
            print(tracking_number)

            # GET PDF AND ZPL TO POST FILE
            reprinting_label_pdf = reprinting(tracking_number, 'Pdf')
            binary_pdf = reprinting_label_pdf.base64Binary.get_text()
            post_label_data(data={"file_name": f"stamps/{shipment_name}.pdf", "file": str(binary_pdf), "file_type": "shipment"})
            reprinting_label_zpl = reprinting(tracking_number, 'Zpl')
            binary_zpl = reprinting_label_zpl.base64Binary.get_text()
            post_label_data(data={"file_name": f"stamps/{shipment_name}.zpl", "file": str(binary_zpl), "file_type": "shipment"})

            # EXAPLE TO CHECK FILE
            # https://192.168.0.100/loadBin?file_name=fedex/MAXTEST_STAMPS_PR43669SH1.pdf&file_type=shipment

            # PUT DATA TO SHIPMENTS
            check_if_shipping_exist = get_shipments_data(shipment_name)
            if not check_if_shipping_exist:
                shipment_data = {'test'}

                tis_shipment = put_shipments_data(shipment_data)
                post_shipments_data(data={"test"})
            else:
                post_shipments_data(data={"test"})

            index += 1

        # GET FIRST SHIPPING DATA AND SEND EMAIL
        first_shipments_data = get_shipments_data(first_shipment_name)
        if first_shipments_data and first_shipments_data[0]['tracking_email_sent'] != 1:
            support_email = order_data['email']

            text = f"<ul><li>Shipment tracking number: <b>{first_tracking_number}</b></li>" \
                   f"<li>Shipment tracking webpage: <a href='https://tools.usps.com/go/TrackConfirmAction?tLabels={first_tracking_number}'>Courier tracking site</a></li></ul>"

            email_body = {"email": f"{order_data['email']}, {support_email}",
                          "email_title": f"{order_data['name']} Tracking information",
                          "message_title": "#order.ready2ship#",
                          "lang": f"{order_data['language']}",
                          "orderid": f"{order_data['id']}",
                          "sections": [{
                              "header": "#order.shipmentinfo#",
                              "body": f"#order.shipmentinfo_text# <b> {order_data['name']} </b> #order.shipmentinfo_text2# {text}"}]}

            final_email = mailer(email_body)

    except Exception as err:
        checkerrors = True
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(fname, exc_type, err, exc_tb.tb_lineno)
        error_for_db = {"file": fname, "error": err, "line": exc_tb.tb_lineno, "shipment_id": ORDER_ID}
    finally:
        if checkerrors:
            print('SOME ERROR: ' + str(error_for_db))
            if first_shipments_data:
                post_shipments_data(data={"id": first_shipments_data[0]['id'], "shipment_error": error_for_db})
            else:
                print("Try put error to user_log")
                put_error(data={"user_id": "-1", "data": f"{error_for_db}", "type": "stampsError"})
        else:
            print('OK')
            if first_shipments_data:
                post_shipments_data(data={"id": first_shipments_data[0]['id'], "tracking_email_sent": 1})
