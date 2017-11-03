import os
os.environ['KERAS_BACKEND'] = 'tensorflow'
import keras.backend as K
K.set_image_dim_ordering('tf')
import numpy as np
from keras.optimizers import SGD
from keras.applications.vgg16 import VGG16
from keras.applications import imagenet_utils
from keras.preprocessing import image
from keras.models import load_model
from resnet_101 import resnet101_model, Scale
import cv2
from imagenet_tool import id_to_synset, synset_to_id

val_gt = '/media/wac/backup/imagenet/devkit/data/ILSVRC2015_clsloc_validation_ground_truth.txt'
val_file = '/media/wac/backup/imagenet/ILSVRC/ImageSets/CLS-LOC/val.txt'
val_path = '/media/wac/backup/imagenet/ILSVRC/Data/CLS-LOC/val_dir'
categories = './categories.txt'

f = open(categories, mode='r')
classes = [line.strip() for line in f.readlines()]

f_file = open(val_file, mode='r')
f_gt = open(val_gt, mode='r')
lines_file = f_file.readlines()
lines_gt = f_gt.readlines()

fname = [line.strip().split(' ')[0] for line in lines_file]
gt = [int(line.strip())for line in lines_gt]
val_dict = dict(zip(fname, gt))


weights_path = './model/weights.00298.hdf5'
# Test pretrained model
# model = resnet101_model(weights_path)
model = load_model(weights_path, custom_objects={'Scale':Scale})
# model.summary()
# model = VGG16(weights_path)
sgd = SGD(lr=0.01, momentum=0.9, decay=1e-6, nesterov=False)
model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])

def processing_function(x):
    # Remove zero-center by mean pixel, BGR mode
    x[:, :, 0] -= 103.939
    x[:, :, 1] -= 116.779
    x[:, :, 2] -= 123.68
    return x

gen = image.ImageDataGenerator(preprocessing_function=processing_function)

val_generator = gen.flow_from_directory(val_path, target_size=(224,224), classes=classes, shuffle=False,
                                              batch_size=1)
score = model.evaluate_generator(val_generator, val_generator.n)
print score
# top1 = 0
# top5 = 0
# for i,name in enumerate(fname):
#     abs_file = os.path.join(val_path, name)
#     # im = cv2.resize(cv2.imread(abs_file), (224, 224)).astype(np.float32)
#     # # Remove train image mean
#     # im[:, :, 0] -= 103.939
#     # im[:, :, 1] -= 116.779
#     # im[:, :, 2] -= 123.68
#     # im = np.expand_dims(im, axis=0)
#
#     im = image.load_img(abs_file)
#     im = image.img_to_array(im)
#     if im.shape[0] <= 224 or im.shape[1] <= 224:
#         im = cv2.resize(im, (224,224))
#     else:
#         center = (im.shape[0]/2, im.shape[1]/2)
#         im = im[center[0]-112:center[0]+112,center[1]-112:center[1]+112,:]
#     im = np.expand_dims(im, axis=0)
#     im = imagenet_utils.preprocess_input(im)
#
#     out = model.predict(im)
#     results = imagenet_utils.decode_predictions(out)[0]
#     if gt[i] == synset_to_id(results[0][0]):
#         top1 += 1
#     for r in results:
#         if gt[i] == synset_to_id(r[0]):
#             top5 += 1
#             break
#     print i, top1, top5
#     # dt = np.argmax(out)
#     #
#     # if gt[i] == synset_to_id(id_to_synset(dt)):
#     #     correct += 1
#     # else:
#     #     fd += 1
#     # print i, correct
# print len(val_dict), top1, top5