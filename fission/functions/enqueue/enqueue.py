# COMP90024 - Cluster and Cloud Computing Assignment 2 - Big Data Analytics on the Cloud
# Team 53
# Niket Singla (1288512)
# Jason Phan (1180106)
# Patipan Rochanapon (1117537)
# Liam Brennan (1269948)
# Parsa Babadi Noroozi (1271605)

"""
Enqueue function
"""

import asyncio
import json

from aiokafka import AIOKafkaProducer
from flask import current_app, request


async def publish(queue, payload):
    """
    Publish the payload to the Kafka queue.
    :param queue: queue name
    :param payload: payload to be published
    :return:
    """
    producer = AIOKafkaProducer(
        bootstrap_servers="my-cluster-kafka-bootstrap.kafka.svc:9092"
    )
    await producer.start()
    try:
        await producer.send_and_wait(queue, payload)
    finally:
        await producer.stop()


def main():
    """
    Main function to enqueue the data to the Kafka queue.
    :return:
    """
    asyncio.run(
        publish(
            request.headers.get("X-Fission-Params-Topic"),
            json.dumps(request.get_json()).encode("utf-8"),
        )
    )
    current_app.logger.info(
        f'Enqueued to topic {request.headers.get("X-Fission-Params-Topic")}'
    )
    return "OK"
