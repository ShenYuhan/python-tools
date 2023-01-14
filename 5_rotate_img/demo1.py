import cv2
import numpy as np
import math

# 使用getPerspectiveTransform和warpPerspective可以实现讲一张图片任意拉伸
def demo1():
    img = cv2.imread("./5_rotate_img/cai1.png", cv2.IMREAD_UNCHANGED)
    pos1 = np.float32([[0,0], [0,150], [150,0], [150,150]])
    pos2 = np.float32([[0,0], [0,150], [130,-20], [130,170]])
    # pos2 = np.float32([[150,0], [150,150], [0,0], [0,150]])
    M = cv2.getPerspectiveTransform(pos1, pos2)
    result = cv2.warpPerspective(img, M, (150, 150))

    cv2.imwrite("./5_rotate_img/test_demo1.png", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 使用for循环从0°到180°生成若干张旋转图片，也就变成了旋转视频的逐帧图
def demo2():
    def rotate(img, degree=1):
        length = img.shape[0]
        width = img.shape[1]
        pos1 = np.float32([[0, 0], [0, width], [length, 0], [length, width]])
        pos2 = np.float32([[length/2-length/2*math.cos(degree*math.pi/180), 0], [length/2-length/2*math.cos(degree*math.pi/180), width], [length/2+length/2*math.cos(degree*math.pi/180), 0], [length/2+length/2*math.cos(degree*math.pi/180), width]])
        M = cv2.getPerspectiveTransform(pos1, pos2)
        result = cv2.warpPerspective(img, M, (length, width))
        return result
    
    img = cv2.imread("./5_rotate_img/cai1.png", cv2.IMREAD_UNCHANGED)

    for i in range(61):
        result = rotate(img, degree=3*i)
        print(result.shape)
        cv2.imwrite("./5_rotate_img/test_demo2_{}.png".format(3*i), result)


demo2()