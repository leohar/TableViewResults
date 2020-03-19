from os import walk
import mimetypes
import warnings
import requests
import logging
import json
import re

module_logger = logging.getLogger("Perf_reporter.confluence_processing")
CONVERT_URL = "https://10.119.16.119/confluence/rest/api/contentbody/convert/storage"
BASE_URL = "https://10.119.16.119/confluence/rest/api/content"
VIEW_URL = "https://10.119.16.119/confluence/pages/viewpage.action?pageId="


def upload_attachment(auth, page_id, file_path):
    warnings.filterwarnings('ignore')
    content_type, encoding = mimetypes.guess_type(file_path)

    if content_type is None:
        content_type = 'multipart/form-data'

    files = ({'file': (file_path, open(file_path, 'rb'), content_type)})

    url = '{base}/{page_id}/child/attachment/'.format(base=BASE_URL, page_id=page_id)

    headers = {'X-Atlassian-Token': 'no-check'}

    response = requests.post(
        url,
        auth=auth,
        headers=headers,
        files=files,
        verify=False)

    content = json.loads(response.content)
    response.raise_for_status()
    logger = logging.getLogger("Perf_reporter.confluence_processing.upload_attachment")
    logger.info("File " + file_path + " attached to " + url)
    return content


def upload_attachments(auth, page_id, report_path):

    responses = []
    files = []
    # file = 'templates/test_report.html'

    for (dirpath, dirnames, filenames) in walk(report_path):
        files.extend(filenames)
        break

    for file in files:
        response = upload_attachment(auth, page_id, report_path+file)
        responses.append(response)

    logger = logging.getLogger("Perf_reporter.confluence_processing.upload_attachments")
    logger.info("Files attached to page id: " + page_id)
    return responses


def upload_files(auth, page_id, report_path):
    files = []
    # file = 'templates/test_report.html'
    url = '{base}/{page_id}'.format(base=BASE_URL, page_id=page_id)

    headers = {'X-Atlassian-Token': 'no-check'}

    for (dirpath, dirnames, filenames) in walk(report_path):
        files.extend(filenames)
        break

    for file in files:
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None:
            content_type = 'multipart/form-data'

        files = ({'file': (file, open(report_path, 'rb'), content_type)})

        response = requests.post(
            url,
            headers=headers,
            files=files,
            auth=auth,
            verify=False)

        response.raise_for_status()


def pprint(data):

    print(json.dumps(
        data,
        sort_keys=True,
        indent=4,
        separators=(', ', ': ')))


def write_data_wiki(auth, html, page_id, title=None):

    info = get_page_info(auth, page_id)

    ver = int(info['version']['number'] + 1)

    space = info['space']['key']

    ancestors = get_page_ancestors(auth, page_id)

    minor_changes = True

    anc = ancestors[-1]
    del anc['_links']
    del anc['_expandable']
    del anc['extensions']

    if title is not None:
        info['title'] = title

    data = {
        'id': str(page_id),
        'type': 'page',
        'title': info['title'],
        "space": {
            "key": space
        },
        'version': {'number': ver,
                    'minorEdit': minor_changes,
                    'message': "Minor edit"},
        'ancestors': [anc],
        'body': {
            'storage':
                {
                    'representation': 'wiki',
                    'value': html,
                }
        }
    }

    data = json.dumps(data)

    url = '{base}/{page_id}'.format(base=BASE_URL, page_id=page_id)

    response = requests.put(
        url,
        data=data,
        auth=auth,
        headers={'Content-Type': 'application/json'},
        verify=False)

    print(response.request)
    response.raise_for_status()
    # print(response.text)
    print("Wrote '%s version %d" % (info['title'], ver))
    print("URL: %s%s" % (VIEW_URL, page_id))


def write_data_storage(auth, html, page_id, title=None, minor_edit=True):

    info = get_page_info(auth, page_id)

    ver = int(info['version']['number'] + 1)

    space = info['space']['key']

    ancestors = get_page_ancestors(auth, page_id)

    anc = ancestors[-1]
    del anc['_links']
    del anc['_expandable']
    del anc['extensions']

    if title is not None:
        info['title'] = title

    data = {
        'id': str(page_id),
        'type': 'page',
        'title': info['title'],
        "space": {
            "key": space
        },
        'version': {'number': ver,
                    'minorEdit': minor_edit},
        'ancestors': [anc],
        'body': {
            'storage':
                {
                    'representation': 'storage',
                    'value': html,
                }
        }
    }

    data = json.dumps(data)

    url = '{base}/{page_id}'.format(base=BASE_URL, page_id=page_id)

    response = requests.put(
        url,
        data=data,
        auth=auth,
        headers={'Content-Type': 'application/json'},
        verify=False)

    logger = logging.getLogger("Perf_reporter.confluence_processing.write_data_storage")
    logger.debug(response.request)
    response.raise_for_status()
    logger.debug(response.text)
    logger.info("Wrote '%s version %d" % (info['title'], ver))
    logger.info("URL: %s%s" % (VIEW_URL, page_id))


def get_page_info(auth, page_id):

    url = '{base}/{page_id}'.format(
        base=BASE_URL,
        page_id=page_id)

    request = requests.get(url, auth=auth, verify=False)
    request.raise_for_status()

    return request.json()


def get_attachments_info(response):

    base_url = response['_links']['base']
    # print(base_url)
    filename = response['results'][0]['title']
    # print(filename)
    container_id = response['results'][0]['container']['id']
    # print(container_id)
    download_link = response['results'][0]['_links']['download']
    modification_date = re.search('&modificationDate=(.*)&', download_link).group(1)
    # print(modification_date)
    attachment_id = response['results'][0]['id'].replace('att', '')
    # print(attachment_id)

    return base_url, filename, container_id, modification_date, attachment_id


def get_page_ancestors(auth, page_id):

    url = '{base}/{page_id}?expand=ancestors'.format(
        base=BASE_URL,
        page_id=page_id)

    request = requests.get(url, auth=auth, verify=False)
    request.raise_for_status()

    return request.json()['ancestors']

    url = '{base}/{page_id}'.format(base=BASE_URL, page_id=page_id)

    request = requests.get(url, auth=auth, verify=False)
    request.raise_for_status()

    return request.json()


def prepare_html_for_image(base_url, filename, container_id, modification_date, attachment_id, height, width):
    return "<span class=\"confluence-embedded-file-wrapper confluence-embedded-manual-size\">" \
           "<img class=\"confluence-embedded-image\" " \
           "src=\"/confluence/download/attachments/" + container_id + "/" + filename + "?version=1&amp;modificationDate=" + modification_date + "&amp;api=v2\" " \
           "data-image-src=\"/confluence/download/attachments/" + container_id + "/" + filename + "?version=1&amp;modificationDate=" + modification_date + "&amp;api=v2\" " \
           "data-unresolved-comment-count=\"0\" " \
           "data-linked-resource-id=\"" + attachment_id + "\" " \
           "data-linked-resource-version=\"1\" " \
           "data-linked-resource-default-alias=\"" + filename + "\" " \
           "data-base-url=\"" + base_url + "\" " \
           "data-linked-resource-content-type=\"image/png\" " \
           "data-linked-resource-container-id=\"" + container_id + "\" " \
           "data-linked-resource-container-version=\"1\" height=\"" + height + "\" width=\"" + width + "\" /></span>"
