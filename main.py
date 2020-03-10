import requests
from load_image import download_image
from random import randint
from env import get_data_from_env
from os import remove, path


def get_last_xkcd_comic_number():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def get_random_comic_url():
    random_comic_number = randint(1, get_last_xkcd_comic_number())
    return f'https://xkcd.com/{random_comic_number}/info.0.json'


def download_random_comic(image_folder='images'):
    response = requests.get(get_random_comic_url())
    response.raise_for_status()
    image_data = response.json()
    image_url = image_data['img']
    image_title = image_data['safe_title']
    image_comment = image_data['alt']
    image_file_name = download_image(image_url, image_folder)
    return (image_file_name, f'{image_title}. {image_comment}')


def get_vk_url_for_upload(vk_access_token, vk_group_id):
    vk_group_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {"access_token": vk_access_token,
              "v": "5.103",
              'group_id': vk_group_id}
    response = requests.get(vk_group_url, params=params)
    vk_response = response.json()
    check_vk_response_for_error(vk_response)
    return vk_response['response']['upload_url']


def upload_image_to_vk(url, file_name):
    with open(file_name, 'rb') as file:
        files = {
            'file1': file
        }
        response = requests.post(url, files=files)
        file.close()
        vk_response = response.json()
        check_vk_response_for_error(vk_response)
        return vk_response


def save_image_to_vk(upload_image_vk_response, vk_group_id, vk_access_token):
    vk_save_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {"access_token": vk_access_token,
              "v": "5.103",
              'group_id': vk_group_id,
              'hash': upload_image_vk_response['hash'],
              'photo': upload_image_vk_response['photo'],
              'server': upload_image_vk_response['server']
              }
    response = requests.post(vk_save_url, params=params)
    vk_response = response.json()
    check_vk_response_for_error(vk_response)
    return vk_response


def post_to_vk_wall(vk_save_image_response, vk_group_id,
                    vk_access_token, image_comment):
    vk_wall_post_url = 'https://api.vk.com/method/wall.post'
    photo_id = vk_save_image_response['response'][0]['id']
    photo_owner_id = vk_save_image_response['response'][0]['owner_id']
    params = {"access_token": vk_access_token,
              "v": "5.103",
              'from_group': 1,
              'owner_id': f'-{vk_group_id}',
              'message': image_comment,
              'attachments': f'photo{photo_owner_id}_{photo_id}'
              }
    response = requests.post(vk_wall_post_url, params=params)
    vk_response = response.json()
    check_vk_response_for_error(vk_response)
    return vk_response


def check_vk_response_for_error(vk_response):
    if 'error' in vk_response:
        raise requests.exceptions.HTTPError(vk_response['error'])


def main():
    vk_group_id = get_data_from_env('VK_GROUP_ID')
    vk_user_access_token = get_data_from_env(
        'VK_USER_ACCESS_TOKEN')
    try:
        image_file_name, image_comment = download_random_comic()
        vk_url_for_upload = get_vk_url_for_upload(
            vk_user_access_token, vk_group_id)
        upload_image_vk_response = upload_image_to_vk(
            vk_url_for_upload, image_file_name)
        vk_save_image_response = save_image_to_vk(upload_image_vk_response,
                                                  vk_group_id, vk_user_access_token)
        post_to_vk_wall(vk_save_image_response, vk_group_id,
                        vk_user_access_token, image_comment)
    except requests.exceptions.HTTPError as ex:
        print(f'Connection error: {ex}')
    finally:
        if path.isfile(image_file_name):
            remove(image_file_name)


if __name__ == '__main__':
    main()
