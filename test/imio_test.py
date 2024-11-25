"""
Written by Danny De Sarno, contact at ddesarno@uwo.ca

"""
# Base Python packages
# Installed packages
# Local files
from file_io.imio import *


dcm_dir = r'C:\Users\ddesarno\Desktop\DDS_projects\data\BioMind\BioMind - 25 VPHD-S 5.0mm 8-6'

imgs, info = load_dcm_imgs(dcm_dir, return_info=True)

print(imgs.shape)
if imgs.shape[-1] == 1:
    imgs = imgs.reshape(imgs.shape[:-1])
else:
    imgs = np.mean(imgs, axis=-1)

for slc in range(len(imgs)):
    fig = plt.figure()
    plt.imshow(imgs[slc, ], cmap='gray')
    plt.title('slice %i' % slc)
    plt.show()
    plt.close()
