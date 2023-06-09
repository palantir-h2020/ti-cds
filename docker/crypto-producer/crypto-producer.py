from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable, KafkaConnectionError
import json
import logging
import time
import argparse
import requests

# CONFIGURATION GLOBAL VARIABLES
KAFKA_BROKER = ""
KAFKA_TOPIC_PRODUCE = ""
TENANT_SERVICE = None
TENANT_ID = None
TOPIC_PARTITION = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class Producer:
    
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER], value_serializer=lambda v: json.dumps(v).encode())
        
    def publish_to_kafka(self, message):
        try:
            if TENANT_SERVICE != None and TENANT_ID != None and TOPIC_PARTITION != None: 
                self.producer.send(KAFKA_TOPIC_PRODUCE, message, partition=TOPIC_PARTITION)
            else:
                self.producer.send(KAFKA_TOPIC_PRODUCE, message)

            self.producer.flush()

        except KafkaError as ex:
            logging.error(f"Exception {ex}")
        else:
            logging.info(f"Published message {message} into topic {KAFKA_TOPIC_PRODUCE}")

def main(args):

    global KAFKA_BROKER
    global KAFKA_TOPIC_PRODUCE
    global TIME_BETWEEN_PRODUCE
    global TENANT_SERVICE
    global TENANT_ID
    global TOPIC_PARTITION

    if args["tenantservice"] == None and args["tenantid"] == None:
        KAFKA_BROKER = args["broker"]
        KAFKA_TOPIC_PRODUCE = args["produce"]
        TIME_BETWEEN_PRODUCE = args["time"]
        logging.info("Passed: -b " + KAFKA_BROKER + " -p " + KAFKA_TOPIC_PRODUCE + " -t " + TIME_BETWEEN_PRODUCE)
        logging.info("Launching producer!")
    else:
        KAFKA_BROKER = args["broker"]
        KAFKA_TOPIC_PRODUCE = args["produce"]
        TIME_BETWEEN_PRODUCE = args["time"]
        TENANT_SERVICE = args["tenantservice"]
        TENANT_ID = args["tenantid"]
        logging.info("Passed: -b " + KAFKA_BROKER + " -p " + KAFKA_TOPIC_PRODUCE + " -t " + TIME_BETWEEN_PRODUCE + " -ts " + TENANT_SERVICE + " -tid " + TENANT_ID)
        logging.info("Launching producer!")

    benign_traffic = 'ts,te,td,sa,da,sp,dp,pr,flg,fwd,stos,ipkt,ibyt,opkt,obyt,in,out,sas,das,smk,dmk,dtos,dir,nh,nhb,svln,dvln,ismc,odmc,idmc,osmc,mpls1,mpls2,mpls3,mpls4,mpls5,mpls6,mpls7,mpls8,mpls9,mpls10,cl,sl,al,ra,eng,exid,tr,$,64.95464773702646,74.23388312803024,32704.665135592822,3164.219268332289,503.5,42.625,10.335777126099709,0.875,tpkt,tbyt,cp,prtcp,prudp,pricmp,prigmp,prother,flga,flgs,flgf,flgr,flgp,flgu'
    crypto_traffic = 'ts,te,td,sa,da,sp,dp,pr,flg,fwd,stos,ipkt,ibyt,opkt,obyt,in,out,sas,das,smk,dmk,dtos,dir,nh,nhb,svln,dvln,ismc,odmc,idmc,osmc,mpls1,mpls2,mpls3,mpls4,mpls5,mpls6,mpls7,mpls8,mpls9,mpls10,cl,sl,al,ra,eng,exid,tr,$,31.94037796113921,31.94037796113921,14213.468192706949,3119.510247537929,445.0,97.66666666666669,4.5563139931740615,1.0,tpkt,tbyt,cp,prtcp,prudp,pricmp,prigmp,prother,flga,flgs,flgf,flgr,flgp,flgu'
    dcp_standard_traffic= '2023-01-17 07:02:25,2023-01-17 07:02:26,0.421,fe80::60df:46cb:1382:b255,ff02::1:3,54347,5355,UDP,......,0,0,2,158,0,0,0,0,0,0,0,0,0,0,0.0.0.0,0.0.0.0,0,0,00:00:00:00:00:00,00:00:00:00:00:00,00:00:00:00:00:00,00:00:00:00:00:00,0-0-0,0-0-0,0-0-0,0-0-0,0-0-0,0-0-0,0-0-0,0-0-0,0-0-0,0-0-0,0.000,0.000,0.000,10.101.44.1,0/0,1,2023-01-17 07:03:01.822,$,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,tpkt,tbyt,cp,prtcp,prudp,pricmp,prigmp,prother,flga,flgs,flgf,flgr,flgp,flgu'
    
    while True:
        try:
            producer = Producer()
            break
        except SystemExit:
            logging.exception("Good bye!")
            return
        except KafkaError as e:
            logging.exception(e)
            time.sleep(1)
            continue
        except NoBrokersAvailable as e:
            logging.exception(e)
            time.sleep(1)
            continue
        except KafkaConnectionError as e:
            logging.exception(e)
            time.sleep(1)
            continue
        except Exception as e:
            logging.exception(e)
            return

    logging.info("Kafka Producer started.")
            
    if TENANT_SERVICE != None and TENANT_ID != None:
        url = TENANT_SERVICE + TENANT_ID
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  

            logging.info('\nResponse code: %s\n' % (response.status_code))

            logging.info('Tenant server response: %s\n' % (response.text))

            logging.info('Topic partition: %s\n' % (response.json()['partition']))

            TOPIC_PARTITION = response.json()['partition']

        except requests.exceptions.RequestException as e:
            logging.info('\nRequest error: %s\n' % (e))
            exit(0)

    while True:
        producer.publish_to_kafka(benign_traffic)

        time.sleep(int(TIME_BETWEEN_PRODUCE))

        producer.publish_to_kafka(crypto_traffic)

        time.sleep(int(TIME_BETWEEN_PRODUCE))

        producer.publish_to_kafka(dcp_standard_traffic)

        time.sleep(int(TIME_BETWEEN_PRODUCE))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create a Producer that sends traffic to the Crypto Detection System')
    parser.add_argument('-b', '--broker', metavar='path', required=True,
                        help='Address of the Kafka Broker')
    parser.add_argument('-p', '--produce', metavar='path', required=True,
                        help='Kafka Topic to write the result to')
    parser.add_argument('-t', '--time', metavar='path', required=True,
                        help='Time the application waits until sending next traffic packet')
    parser.add_argument('-ts', '--tenantservice', metavar='path', required=False,
                        help='Multi-tenancy service')
    parser.add_argument('-tid', '--tenantid', metavar='path', required=False,
                        help='Tenant id')
    args = parser.parse_args()
    main(vars(args))
