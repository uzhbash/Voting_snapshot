from web3.auto import w3
from eth_account.messages import encode_structured_data
import time
from loguru import logger
import aiohttp
import asyncio
from config import TIME, TIMEMAX, TIME_ERROR, USE_PROXY
import random
import ast
import json
from tqdm import tqdm

logger.add(f'log.log')


def validation_type(type, choise):
    if type == 'uint32':
        return int(choise)
    if type == 'string':
        return json.dumps(dict(choise))
    choise = [int(ch) for ch in choise]
    return choise


# region form
def forma(address, signature, space, proposal, choice, timestamp, type_choice="uint32"):
    forma = {
        "address": address,
        "sig": signature,
        "data": {
            "domain": {
                "name": "snapshot",
                "version": "0.1.4"
            },
            "types": {
                "Vote": [{
                    "name": "from",
                    "type": "address"
                },
                    {
                        "name": "space",
                        "type": "string"
                    },
                    {
                        "name": "timestamp",
                        "type": "uint64"
                    },
                    {
                        "name": "proposal",
                        "type": "bytes32"
                    },
                    {
                        "name": "choice",
                        "type": type_choice
                    },
                    {
                        "name": "reason",
                        "type": "string"
                    },
                    {
                        "name": "app",
                        "type": "string"
                    },
                    {
                        "name": "metadata",
                        "type": "string"
                    }
                ]
            },
            "message": {
                "space": space,
                "proposal": proposal,
                "choice": validation_type(type_choice,choice),
                "app": "snapshot",
                "reason": "",
                "from": address,
                "timestamp": timestamp,
                'metadata': "{}"
            }
        }
    }
    return forma


# endregion

# region signature
def signature(address, space, proposal, choice, timestamp, key, type_choice="uint32"):
    sig_signature = {
        "domain": {
            "name": "snapshot",
            "version": "0.1.4"
        },
        "types": {
            "Vote": [
                {
                    "name": "from",
                    "type": "address"
                },
                {
                    "name": "space",
                    "type": "string"
                },
                {
                    "name": "timestamp",
                    "type": "uint64"
                },
                {
                    "name": "proposal",
                    "type": "bytes32"
                },
                {
                    "name": "choice",
                    "type": type_choice
                },
                {
                    "name": "reason",
                    "type": "string"
                },
                {
                    "name": "app",
                    "type": "string"
                },
                {
                    "name": "metadata",
                    "type": "string"
                }
            ],
            'EIP712Domain': [{'name': 'name', 'type': 'string'}, {'name': 'version', 'type': 'string'}]
        },
        'primaryType': "Vote",
        "message": {
            "space": space,
            "proposal": w3.toBytes(hexstr=proposal),
            "choice": validation_type(type_choice,choice),
            "app": "snapshot",
            "reason": "",
            "from": address,
            "timestamp": timestamp,
            'metadata': "{}"
        }
    }

    signature = (w3.eth.account.sign_message(encode_structured_data(primitive=sig_signature), key))['signature'].hex()
    return signature

def sleep_indicator(sec):
    for i in tqdm(range(sec), desc='жду', bar_format="{desc}: {n_fmt}c /{total_fmt}c {bar}", colour='green'):
        time.sleep(1)

# endregion

async def req(key, p):
    tm = random.randint(1, 3)

    await asyncio.sleep(tm)
    global x
    num_acc = x

    random.shuffle(proposal_data)

    for k, inf in enumerate(proposal_data):
        if k == 0:
            x += 1
        SPACE, PROPOSAL, CHOICE = inf.split('@')[0], inf.split('@')[1], inf.split('@')[2]

        type_choise = "uint32"

        if '[' in CHOICE:
            CHOICE = ast.literal_eval(CHOICE)
            type_choise = "uint32[]"
        if '{' in CHOICE:
            CHOICE = ast.literal_eval(CHOICE)
            type_choise = "string"

        headers = {'accept': 'application/json',
                   'user-agent': 'Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}

        STATUS = True
        while STATUS:

            timestamp = int(time.time())
            address = w3.eth.account.from_key(key).address

            async with aiohttp.ClientSession(headers=headers) as ses:
                if p:
                    for attempt in range(3):  # Retry up to 3 times
                        try:
                            async with ses.post('https://seq.snapshot.org/', json=forma(
                                address,
                                signature(address, SPACE, PROPOSAL, CHOICE, timestamp, key, type_choise),
                                SPACE, PROPOSAL, CHOICE, timestamp, type_choise
                            ), proxy=f'http://{p}', headers=headers, timeout=60) as r:  # Set timeout to 60 seconds
                                data = await r.json()
                                # Process the response
                                try:
                                    data = await r.json()

                                    if data.get('id') is None:
                                        if data.get('error_description') == 'no voting power':
                                            logger.info(
                                                f"[{num_acc}/{len(keys)}][{k + 1}/{len(proposal_data)}] {address} PROPOSAL -> {PROPOSAL[:10]} Error-> {data.get('error_description')}")
                                            STATUS = False
                                        elif data.get('error_description') == 'failed to check voting power':
                                            sleep_indicator(random.randint(1, TIME_ERROR))
                                        else:
                                            logger.error(
                                                f"[{num_acc}/{len(keys)}][{k + 1}/{len(proposal_data)}] {address} PROPOSAL -> {PROPOSAL[:10]} Error-> {data.get('error_description')}")
                                            sleep_indicator(random.randint(1, TIME_ERROR))
                                    else:
                                        logger.success(
                                            f"[{num_acc}/{len(keys)}][{k + 1}/{len(proposal_data)}] {address} PROPOSAL -> {PROPOSAL[:10]} Success")
                                        sleep_indicator(random.randint(TIME, TIMEMAX))
                                        STATUS = False
                                except Exception as e:
                                    logger.error(f'{address} -> failed check json')
                                    sleep_indicator(random.randint(7, TIME_ERROR))
                                break  # Break out of the retry loop if successful
                        except asyncio.TimeoutError:
                            if attempt < 2:  # If not the last attempt
                                await asyncio.sleep(3)  # Wait for 3 seconds before retrying
                            else:
                                # Log or handle the failure after all attempts
                                print("Request timed out after multiple attempts")
                else:
                    for attempt in range(3):  # Retry up to 3 times
                        try:
                            async with ses.post('https://seq.snapshot.org/', json=forma(
                                address,
                                signature(address, SPACE, PROPOSAL, CHOICE, timestamp, key, type_choise),
                                SPACE, PROPOSAL, CHOICE, timestamp, type_choise
                            ), headers=headers) as r:
                                data = await r.json()
                                try:
                                    data = await r.json()

                                    if data.get('id') is None:
                                        if data.get('error_description') == 'no voting power':
                                            logger.info(
                                                f"[{num_acc}/{len(keys)}][{k + 1}/{len(proposal_data)}] {address} PROPOSAL -> {PROPOSAL[:10]} Error-> {data.get('error_description')}")
                                            STATUS = False
                                        elif data.get('error_description') == 'failed to check voting power':
                                            sleep_indicator(random.randint(1, TIME_ERROR))
                                        else:
                                            logger.error(
                                                f"[{num_acc}/{len(keys)}][{k + 1}/{len(proposal_data)}] {address} PROPOSAL -> {PROPOSAL[:10]} Error-> {data.get('error_description')}")
                                            sleep_indicator(random.randint(1, TIME_ERROR))
                                    else:
                                        logger.success(
                                            f"[{num_acc}/{len(keys)}][{k + 1}/{len(proposal_data)}] {address} PROPOSAL -> {PROPOSAL[:10]} Success")
                                        sleep_indicator(random.randint(TIME, TIMEMAX))
                                        STATUS = False
                                except Exception as e:
                                    logger.error(f'{address} -> failed check json')
                                    sleep_indicator(random.randint(7, TIME_ERROR))
                                    break  # Break out of the retry loop if successful
                        except asyncio.TimeoutError:
                            if attempt < 2:  # If not the last attempt
                                await asyncio.sleep(3)  # Wait for 3 seconds before retrying
                            else:
                                # Log or handle the failure after all attempts
                                print("Request timed out after multiple attempts")
        await asyncio.sleep(random.randint(27, TIME))

with open('key.txt', 'r') as f:
    keys = [i for i in [k.strip() for k in f] if i != '']
with open('proxy.txt', 'r') as f:
    prox = [i for i in [pr.strip() for pr in f] if i != '']
with open('data.txt', 'r') as f:
    proposal_data = [i for i in [d.strip() for d in f] if i != '']

x = 1


async def main():
    if USE_PROXY is True:
        await asyncio.gather(*[req(k, prox[v]) for v, k in enumerate(keys)])
    else:
        await asyncio.gather(*[req(k, None) for k in keys])

if __name__ == '__main__':
    asyncio.run(main())
