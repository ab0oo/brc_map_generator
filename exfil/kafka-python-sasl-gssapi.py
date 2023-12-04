# Requirements: kafka-python gssapi krbticket
import os
import time
from kafka import KafkaConsumer, KafkaProducer
from krbticket import KrbConfig, KrbCommand

try:
    os.environ['KRB5CCNAME'] = '/tmp/krb5cc_<myusername>'
    kconfig = KrbConfig(principal='araujo', keytab='/path/to/<myusername>.keytab')
    KrbCommand.kinit(kconfig)

    # Kafka broker
    BROKERS = ['host.cloudera.site:9093']
    # Kafka topics
    TOPIC = 'demo'

    producer = KafkaProducer(
                   bootstrap_servers=BROKERS,
                   security_protocol='SASL_SSL',
                   ssl_cafile='/var/lib/cloudera-scm-agent/agent-cert/cm-auto-global_cacerts.pem',
                   sasl_mechanism='GSSAPI',
                   sasl_kerberos_service_name='kafka',
               )

    producer.send(TOPIC, ('Hello, World! %s' % (time.time(),)).encode())
    producer.flush()

    consumer = KafkaConsumer(
                   bootstrap_servers=BROKERS,
                   security_protocol='SASL_SSL',
                   ssl_cafile='/var/lib/cloudera-scm-agent/agent-cert/cm-auto-global_cacerts.pem',
                   sasl_mechanism='GSSAPI',
                   sasl_kerberos_service_name='kafka',
                   auto_offset_reset='earliest',
               )
    consumer.subscribe([TOPIC])

    for message in consumer:
        print(message)

finally:
    print("Destroying ticket")
    KrbCommand.kdestroy(kconfig)