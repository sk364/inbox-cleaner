#!/usr/bin/python2.7

import httplib2
import json

from datetime import datetime

from apiclient import discovery, errors
from oauth2client.client import Credentials

from config import (GMAIL_FILTER_QUERY, NEW_LABEL_NAME, REGISTERED_CREDENTIALS_JSON,
                    SCHEDULED_TIME)


labels = {
    'removeLabelIds': ['INBOX'],
    'addLabelIds': []
}
user_id = 'me'


def get_credentials():
    with open(REGISTERED_CREDENTIALS_JSON) as f:
        registered_credentials = json.load(f)
    return [Credentials.new_from_json(credential) for credential in registered_credentials]


def create_label(label_name):
    try:
        user_labels = service.users().labels().list(userId=user_id).execute()['labels']
        for label in user_labels:
            if label['name'] == label_name:
                return label['id']

        label_obj = {'name': label_name}
        label = service.users().labels().create(userId=user_id, body=label_obj).execute()
        return label['id']
    except errors.HttpError, error:
        print error
        exit()


def get_threads():
    label_ids = ['INBOX', 'UNREAD']
    try:
        response = service.users().threads().list(
                       userId=user_id,
                       q=GMAIL_FILTER_QUERY,
                       labelIds=label_ids
                   ).execute()
    except errors.HttpError, error:
        print error
        exit()

    threads = []
    if 'threads' in response:
        threads.extend(response['threads'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().threads().list(
            userId=user_id,
            q=GMAIL_FILTER_QUERY,
            pageToken=page_token,
            labelIds=label_ids
        ).execute()
        threads.extend(response['threads'])

    return [thread['id'] for thread in threads]


def move_threads(thread_ids):
    for thread_id in thread_ids:
        response = service.users().threads().modify(userId=user_id, id=thread_id, body=labels).execute()


while True:
    now = datetime.now()
    if now.hour == SCHEDULED_TIME[0] and now.minute == SCHEDULED_TIME[1] and \
       now.second == SCHEDULED_TIME[2]:
        all_credentials = get_credentials()
        for credentials in all_credentials:
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('gmail', 'v1', http=http)

            print 'User loaded...'
            label_id = create_label(NEW_LABEL_NAME)
            labels['addLabelIds'].append(label_id)
            print 'Label created...'
            thread_ids = get_threads()
            print 'Threads retrieved... (count: {})'.format(len(thread_ids))
            move_threads(thread_ids)
            print 'Threads moved...'

