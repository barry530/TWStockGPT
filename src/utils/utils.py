from googleapiclient.http import MediaFileUpload

def upload_to_google_drive(service, file_path, file_name, destination):
    """
    upload file to Google Drive
    :param service:
    :param file_path:
    :param file_name:
    :param destination:
    :return:
    """
    media = MediaFileUpload(file_path)  # create the file object
    file = {'name': file_name, 'parents': [destination]}
    file_id = service.files().create(body=file, media_body=media).execute()
    print(file_id)
