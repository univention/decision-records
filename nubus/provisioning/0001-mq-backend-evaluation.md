
# Message Queue Backend Evaluation: RabbitMQ, Kafka, Redis

---

- status: proposed
- date: 2023-10-16
- author: acaceres
- deciders: tkintscher, skoenig, jlohmer
- source: https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/-/issues/15

---

## Context and Problem Statement

We are developing a publish-subscribe backend system where one party notifies us about changes, and other parties expect to receive a notification when this happens. The challenge is to select a suitable message queue system that can handle this communication efficiently, ensuring scalability, reliability, and ease of management.

## Decision Drivers

**Update 23.10: right now we are choosing between NATS and RabbitMQ**
Main drivers for a decision are specified in [SPIKE: Backend evaluation for message queue](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/-/issues/15), and some came out of the discussion with the team.

Evaluation criteria:
1. can be clustered
2. provides persistence: messages are not lost when the broker is restarted
3. manageable (provides monitoring)
4. has a suitable API: Python bindings, docs, etc
5. provides features that otherwise would need to be implemented
6. resource consumption: how hungry for memory/CPU, if needs to keep everything in memory or can use disk
7. performance: throughput and latency considerations
8. developer experience: familiarity of the team/department with the technology
9. support: availability of documentation and community resources
10. encryption: ensures secure transmission and storage of data.
11. authentication: ensures that only authorized parties can publish or subscribe to messages.

## Considered Options

- Kafka
- RabbitMQ
- Redis
- [NATS](https://nats.io/)
- [Pulsar](https://pulsar.apache.org/)

## Pros and Cons of the Options

### Kafka

Kafka is a distributed streaming platform designed for high throughput.

- Good, because of its performance and scalability (1, 7)
- Good, because it provides strong durability with message persistence (2)
- Good, because it allows different usage scenarios, like not-deleting-messages and rereading them for analysis or deduplication. Thus allowing the backend to be used in other projects. (5)
- Good, because a wide range of professional tooling exists to maintain and monitor it. (3)
- Good, because can be integrated with Open Policy Agent ([OPA docs](https://www.openpolicyagent.org/docs/latest/kafka-authorization/)). (11)
- Neutral, because the official Python client does not integrate with asyncio but a 3rd party lib `aiokafka` does. (4)
- Bad, because compared to other solutions has higher resource consumption, as it runs in a JVM. (Though not _that_ bad: I can run it incl. zookeeper with no problems on my notebook.) (6)
- Bad, because it either requires an additional component (Zookeeper) to run, or uses KRaft protocol, which is in early stage. (8)
- Bad, because of its complexity in setup and management. (3, 8)

*Example Python code for publishing a message:*

```python
producer = KafkaProducer(bootstrap_servers=['host:1234'])
producer.send('provisioning-channel', key=b'key', value=b'value')
producer.flush()
```

### RabbitMQ

RabbitMQ is a message broker that supports multiple messaging protocols.

- Good, because of its ease of setup and management. (3, 8)
- Good, because it supports a variety of messaging patterns, including pub/sub. (5)
- Good, because of low resource consumption. (6)
- Good, because can be integrated with Open Policy Agent ([RabbitMQ blog](https://blog.rabbitmq.com/posts/2022/02/gatekeeper-validation/)). (11)
- Neutral, because while it can handle a significant number of messages, it does not match Kafka's performance on max load. (1, 7)
- Neutral, because official Python client despite being asynchronous is very callback-oriented. However, a 3rd party libs `aio-pika` and `aio-rabbit` integrates with `asyncio`. (4)
- Bad, because horizontal scaling is not as straightforward as Kafka. (1)
- Bad, because of comparatively rather basic management and monitoring tools. (3)

**Encryption (10)**: RabbitMQ supports TLS/SSL for encrypted connections. It allows for configuring the required level of encryption and only accepting connections that meet these requirements. Additionally, RabbitMQ supports encrypting data using disk encryption methods provided by the operating system.

**Authentication (11)**: RabbitMQ many authentication and authorization mechanisms. It supports many authentication backends, including LDAP, allows to define fine-grained permissions for users, including specifying which operations a user can perform on queues and exchanges. RabbitMQ also supports SASL for secure authentication.

*Example Python code for publishing a message:*

```python
connection = pika.BlockingConnection(pika.ConnectionParameters('host:1234'))
channel = connection.channel()
channel.basic_publish(exchange='', routing_key='provisioning-channel', body='value')
connection.close()
```

### Redis

Redis is an in-memory data structure store that supports various data structures and has a pub/sub capability.

- Good, because every developer knows it (8)
- Good, because it's easy to set up (3)
- Good, because it can be a DB for other information, not just pub/sub messages (5)
- Bad, because it's primarily an in-memory datastore, leading to potential data loss if not persisted properly, and requiring proportional RAM growth (2, 6)

*Example Python code for publishing a message:*

```python
r = redis.Redis(host='host', port=6379, db=0)
r.publish('provisioning-channel', 'value')
```

### NATS

NATS is a lightweight and high-performance messaging system.

- Good, because it's lightweight and fast, providing high throughput and low latency (7)
- Good, because it is easy to set up and manage (3)
- Good, because official python client supports AsynCIO (4)
- Good, because it supports various messaging patterns, including pub/sub, request/reply, and point-to-point. (5)
- Neutral, because while it supports clustering, it might not scale as horizontally as Kafka. (1)
- Bad, because it might not provide as extensive monitoring and management tools out of the box (not yet evaluated) (3)

**Encryption (10):** NATS supports TLS for encrypted connections. Also NATS provides the option for end-to-end encryption, ensuring that messages are encrypted during transit and only decrypted by the intended recipient.

**Authentication (11):** NATS provides many authentication mechanisms, including token-based authentication, username and password, and decentralized JWT-based authentication. This flexibility allows administrators to choose the authentication method that best suits their security requirements. Additionally, NATS supports Authorization, which allows defining permissions at a fine-grained level, specifying what subjects (topics) a user can publish or subscribe to.

*Example Python code for publishing a message using the nats client:*

```python
import asyncio
import nats.aio.client

async def run():
    nc = nats.aio.client.Client()
    await nc.connect("nats://localhost:4222")
    await nc.publish("provisioning-channel", b'value')
    await nc.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
```

## Decision Outcome

Chosen option:

To be determined based on further evaluation and specific project needs, because both Kafka and RabbitMQ have their strengths and are capable of meeting the requirements. Redis, while a powerful tool for certain use cases, may not be suitable for our needs due to its in-memory nature and potential data persistence challenges.

### Risks

- As listed MQ backends are totally different in nature, have different APIs and design concepts, it will be
difficult to migrate to another backend later on.
