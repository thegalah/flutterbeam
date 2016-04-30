__author__ = 'jeremyma'
import time
import requests
import cv2,cv
import math
import operator
import os, pdb
from PIL import Image
import sys

# Import library to display results
import matplotlib.pyplot as plt

_url = 'https://api.projectoxford.ai/face/v1.0/detect'
_key = 'b2a7d0f12df84af2994ffafa71c88e5f' #Here you have to paste your primary key
_maxNumRetries = 10

# 0 = point, 1 = width of face
MUSTACHE_TO_FACE_SIZE_RATIO = 0.6
SOULPATCH_TO_FACE_SIZE_RATIO = 0.2
MONOCLE_TO_FACE_SIZE_RATIO = 0.3

def processRequest (data, headers, params=None):

    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request( 'post', _url, data = data, headers = headers, params = params )

        if response.status_code == 429:

            print "Message: %s" % ( response.json()['error']['message'] )

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print 'Error: failed after retrying!'
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print "Error code: %d" % ( response.status_code )
            print "Message: %s" % ( response.json()['error']['message'] )

        break

    return result

def renderResultOnImage( result, img ):

    """Display the obtained results onto the input image"""

    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        cv2.rectangle( img,(faceRectangle['left'],faceRectangle['top']),
                           (faceRectangle['left']+faceRectangle['width'], faceRectangle['top'] + faceRectangle['height']),
                       color = (255,0,0), thickness = 1 )

        faceLandmarks = currFace['faceLandmarks']
        #pdb.set_trace()
        for _, currLandmark in faceLandmarks.iteritems():
            cv2.circle( img, (int(currLandmark['x']),int(currLandmark['y'])), color = (0,255,0), thickness= -1, radius = 1 )

    for currFace in result:
        faceRectangle = currFace['faceRectangle']
        faceAttributes = currFace['faceAttributes']

        textToWrite = "%c (%d)" % ( 'M' if faceAttributes['gender']=='male' else 'F', faceAttributes['age'] )
        cv2.putText( img, textToWrite, (faceRectangle['left'],faceRectangle['top']-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1 )

def example(imagepath):
    # Load raw image file into memory
    with open(imagepath, 'rb' ) as f:
        data = f.read()

        # Face detection parameters
        params = { 'returnFaceAttributes': 'age,gender',
                   'returnFaceLandmarks': 'true'}

        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = _key
        headers['Content-Type'] = 'application/octet-stream'

        result = processRequest(data, headers, params)
        #pdb.set_trace()
        # Load the original image from disk
        data8uint = np.fromstring( data, np.uint8 ) # Convert string to an unsigned int array
        img = cv2.cvtColor( cv2.imdecode( data8uint, cv2.IMREAD_COLOR ), cv2.COLOR_BGR2RGB )

        renderResultOnImage( result, img )

        ig, ax = plt.subplots(figsize=(15, 20))
        ax.imshow( img )
        plt.show()

def mustache(pil_image, faceresult, moustache_folder):
    mustache = Image.open(os.path.join(moustache_folder, 'mustache_03.png'))

    # calculate mustache image aspect ratio so proportions are preserved
    # when scaling it to face
    mustache_aspect_ratio = 1.0*mustache.size[0]/mustache.size[1]

    faceLandmarks = faceresult['faceLandmarks']

    eye_L = faceLandmarks['pupilLeft']
    eye_R = faceLandmarks['pupilRight']

    mustache_angle = math.degrees(math.atan(-1.0 *
                        (eye_R['y']-eye_L['y'])/(eye_R['x']-eye_L['x'])))

    # Scale mustache
    # Change MUSTACHE_TO_FACE_SIZE_RATIO to adjust mustache size
    # relative to face
    mustache_w = int(1.0 * faceresult['faceRectangle']['width'] * MUSTACHE_TO_FACE_SIZE_RATIO)
    mustache_h = int(1.0 * mustache_w / mustache_aspect_ratio)

    mustache_x = int(faceLandmarks['upperLipTop']['x'])
    mustache_y = int((0.9*faceLandmarks['upperLipTop']['y'] + 0.1*faceLandmarks['noseTip']['y']))

    # Rotate and resize the mustache
    # Rotate first so the final filter applied is ANTIALIAS
    mustache = mustache.rotate(mustache_angle, Image.BICUBIC, True)
    mrad = math.fabs(math.radians(mustache_angle))
    rotated_width = int(math.fabs(mustache_w * math.cos(mrad) + mustache_h *
                        math.sin(mrad)))
    rotated_height = int(math.fabs(mustache_w * math.sin(mrad) + mustache_h *
                         math.cos(mrad)))
    mustache = mustache.resize((rotated_width, rotated_height),
                               Image.ANTIALIAS)

    #pdb.set_trace()
    # Superimpose the mustache on the face
    pil_image.paste(mustache, (mustache_x-int(mustache.size[0] / 2.0),
               mustache_y-int(mustache.size[1] / 2.0)), mustache)


def soulpatch(pil_image, faceresult, moustache_folder):
    soulpatch = Image.open(os.path.join(moustache_folder, 'soulpatch_01.png'))

    # calculate soulpatch image aspect ratio so proportions are preserved
    # when scaling it to face
    soulpatch_aspect_ratio = 1.0*soulpatch.size[0]/soulpatch.size[1]

    faceLandmarks = faceresult['faceLandmarks']

    eye_L = faceLandmarks['pupilLeft']
    eye_R = faceLandmarks['pupilRight']

    soulpatch_angle = math.degrees(math.atan(-1.0 *
                        (eye_R['y']-eye_L['y'])/(eye_R['x']-eye_L['x'])))

    # Scale soulpatch
    # Change MUSTACHE_TO_FACE_SIZE_RATIO to adjust soulpatch size
    # relative to face
    soulpatch_w = int(1.0 * faceresult['faceRectangle']['width'] * SOULPATCH_TO_FACE_SIZE_RATIO)
    soulpatch_h = int(1.0 * soulpatch_w / soulpatch_aspect_ratio)

    soulpatch_x = int(faceLandmarks['underLipBottom']['x'])
    soulpatch_y = int(faceLandmarks['underLipBottom']['y'])

    # Rotate and resize the soulpatch
    # Rotate first so the final filter applied is ANTIALIAS
    soulpatch = soulpatch.rotate(soulpatch_angle, Image.BICUBIC, True)
    mrad = math.fabs(math.radians(soulpatch_angle))
    rotated_width = int(math.fabs(soulpatch_w * math.cos(mrad) + soulpatch_h *
                        math.sin(mrad)))
    rotated_height = int(math.fabs(soulpatch_w * math.sin(mrad) + soulpatch_h *
                         math.cos(mrad)))
    soulpatch = soulpatch.resize((rotated_width, rotated_height),
                               Image.ANTIALIAS)

    pil_image.paste(soulpatch, (soulpatch_x-int(soulpatch.size[0] / 2.0),
               soulpatch_y), soulpatch)

def monocle(pil_image, faceresult, moustache_folder):
    monocle = Image.open(os.path.join(moustache_folder, 'monocle.png'))

    # calculate monocle image aspect ratio so proportions are preserved
    # when scaling it to face
    monocle_aspect_ratio = 1.0*monocle.size[0]/monocle.size[1]

    faceLandmarks = faceresult['faceLandmarks']

    eye_L = faceLandmarks['pupilLeft']
    eye_R = faceLandmarks['pupilRight']

    soulpatch_angle = math.degrees(math.atan(-1.0 *
                        (eye_R['y']-eye_L['y'])/(eye_R['x']-eye_L['x'])))

    # Scale monocle
    # Change MUSTACHE_TO_FACE_SIZE_RATIO to adjust monocle size
    # relative to face
    monocle_w = int(1.0 * faceresult['faceRectangle']['width'] * MONOCLE_TO_FACE_SIZE_RATIO)
    soulpatch_h = int(1.0 * monocle_w / monocle_aspect_ratio)

    monocle_x = int(faceLandmarks['pupilLeft']['x'])
    monocle_y = int(faceLandmarks['pupilLeft']['y'])

    # Rotate and resize the monocle
    # Rotate first so the final filter applied is ANTIALIAS
    monocle = monocle.rotate(soulpatch_angle, Image.BICUBIC, True)
    mrad = math.fabs(math.radians(soulpatch_angle))
    rotated_width = int(math.fabs(monocle_w * math.cos(mrad) + soulpatch_h *
                        math.sin(mrad)))
    rotated_height = int(math.fabs(monocle_w * math.sin(mrad) + soulpatch_h *
                         math.cos(mrad)))
    monocle = monocle.resize((rotated_width, rotated_height),
                               Image.ANTIALIAS)

    pil_image.paste(monocle, (monocle_x-int(monocle.size[0] / 2.0),
               monocle_y-int(monocle.size[1] / 2.0)), monocle)

def flutterfly(result, input_file, output_file, moustache_folder):
    pil_image = Image.open(input_file)
    cv_image = cv.CreateImageHeader(pil_image.size, cv.IPL_DEPTH_8U, 3)
    cv.SetData(cv_image, pil_image.tobytes())
    # Convert image to a format that supports image overlays with alpha
    pil_image = Image.frombytes("RGB", cv.GetSize(cv_image), cv_image.tostring())

    for faceresult in result:
        mustache(pil_image, faceresult, moustache_folder)
        soulpatch(pil_image,faceresult, moustache_folder)
        monocle(pil_image, faceresult, moustache_folder)


    pil_image.save(output_file, "JPEG")

def main(input_file, output_file, moustache_folder):
    with open(input_file, 'rb') as f:
        data = f.read()

        # Face detection parameters
        params = { 'returnFaceAttributes': 'age,gender',
                   'returnFaceLandmarks': 'true'}

        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = _key
        headers['Content-Type'] = 'application/octet-stream'
        result = processRequest(data, headers, params)
        #pdb.set_trace()

    flutterfly(result, input_file, output_file, moustache_folder)

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    moustache_folder = sys.argv[3]
    main(input_file, output_file, moustache_folder)