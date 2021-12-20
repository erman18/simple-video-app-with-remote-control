import cv2
import time
import os
import datetime
import zmq
import random
from threading import Thread, Lock
from queue import Queue, Full

class Camera:
    def __init__(self, device=0, mirror=False):
        self.data = None
        self.data_queue = Queue(maxsize=200)
        self.cmd_queue = Queue(maxsize=200)
        self.cam = cv2.VideoCapture(device)

        self.WIDTH = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH) # 640
        self.HEIGHT = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT) # 480

        self.center_x = self.WIDTH / 2
        self.center_y = self.HEIGHT / 2
        self.touched_zoom = False

        self.image_queue = Queue()
        # self.video_queue = Queue()

        self.scale = 1
        self.__setup()

        self.recording = False

        self.mirror = mirror
        self.stop = False
        self.lock = Lock()

        context = zmq.Context()
        self.remoteclt = context.socket(zmq.REP)
        self.remoteclt.bind("tcp://*:5555")
        print("Connecting to client...")


    def __setup(self):
        # self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.WIDTH)
        # self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.HEIGHT)
        time.sleep(1)

    def get_location(self, x, y):
        self.center_x = x
        self.center_y = y
        self.touched_zoom = True

    def stream(self):
        # streaming thread 함수
        def streaming():
            # 실제 thread 되는 함수
            self.ret = True
            m_scale, m_center_x, m_center_y = self.scale, self.center_x, self.center_y
            while self.ret:
                self.ret, np_image = self.cam.read()
                if np_image is None:
                    continue
                if self.mirror:
                    # flip the image
                    np_image = cv2.flip(np_image, 1)
                
                if not self.cmd_queue.empty():
                    m_scale, m_center_x, m_center_y = self.cmd_queue.get()
                    print(f"scale: {m_scale}, cx: {m_center_x}, cy: {m_center_y}")

                np_image = self.__zoom(np_image, m_scale, m_center_x, m_center_y)

                # if self.touched_zoom:
                #     np_image = self.__zoom(np_image, (self.center_x, self.center_y))
                # else:
                #     if not self.scale == 1:
                #         np_image = self.__zoom(np_image)
                # self.data = np_image
                try:
                    self.data_queue.put_nowait(np_image)
                except Full:
                    # print("Queue is full!! ")
                    time.sleep(0.1)
                
                time.sleep(0.05)
                if self.stop:
                    break
                # k = cv2.waitKey(1)
                # if k == ord('q'):
                #     self.release()
                #     break

        def remoteclt_server():
            while not self.stop:
                try:
                    message = self.remoteclt.recv(flags=zmq.NOBLOCK)
                    
                except zmq.Again as e:
                    if self.stop:
                        break
                    time.sleep(0.01)
                    continue
                message = message.decode("utf-8")
                print("Received message: ")
                print(str(message))

                if str(message) in ["ZMIN", "MVLF", "PLAY"]:
                    self.zoom_in()
                elif str(message) in ["ZMOT", "MVRT", "MVDN"]:
                    self.zoom_out()
                else:
                    print(f"Unkown message: {str(message)}")
                    self.zoom_in()
                    # self.zoom(num=random.randint(0,1))

                #  Send reply back to client
                self.remoteclt.send_string("Acknowledge")
                print("Sending message: Acknowledge")

                # time.sleep(0.005)

        Thread(target=streaming).start()
        Thread(target=remoteclt_server).start()

    # def __zoom(self, img, center=None):
    #     # zoom하는 실제 함수
    #     height, width = img.shape[:2]
    #     if center is None:
            
    #         center_x = int(width / 2)
    #         center_y = int(height / 2)
    #         radius_x, radius_y = int(width / 2), int(height / 2)
    #     else:
            
    #         rate = height / width
    #         center_x, center_y = center

    #         #   비율 범위에 맞게 중심값 계산
    #         if center_x < width * (1-rate):
    #             center_x = width * (1-rate)
    #         elif center_x > width * rate:
    #             center_x = width * rate
    #         if center_y < height * (1-rate):
    #             center_y = height * (1-rate)
    #         elif center_y > height * rate:
    #             center_y = height * rate

    #         center_x, center_y = int(center_x), int(center_y)
    #         left_x, right_x = center_x, int(width - center_x)
    #         up_y, down_y = int(height - center_y), center_y
    #         radius_x = min(left_x, right_x)
    #         radius_y = min(up_y, down_y)

    #     # 실제 zoom 코드
    #     radius_x, radius_y = int(self.scale * radius_x), int(self.scale * radius_y)

    #     # size 계산
    #     min_x, max_x = center_x - radius_x, center_x + radius_x
    #     min_y, max_y = center_y - radius_y, center_y + radius_y

    #     # size에 맞춰 이미지를 자른다
    #     cropped = img[min_y:max_y, min_x:max_x]
    #     # 원래 사이즈로 늘려서 리턴
    #     new_cropped = cv2.resize(cropped, (width, height))

    #     return new_cropped

    def __zoom(self, img, m_scale, m_center_x, m_center_y):
        
        if m_scale == 1:
            return img
        
        height, width = img.shape[:2]
        center = (m_center_x, m_center_y)
        
        if center is None:
            
            center_x = int(width / 2)
            center_y = int(height / 2)
            radius_x, radius_y = int(width / 2), int(height / 2)
        else:
            
            rate = height / width
            center_x, center_y = center
            
            if center_x < width * (1-rate):
                center_x = width * (1-rate)
            elif center_x > width * rate:
                center_x = width * rate
            if center_y < height * (1-rate):
                center_y = height * (1-rate)
            elif center_y > height * rate:
                center_y = height * rate

            center_x, center_y = int(center_x), int(center_y)
            left_x, right_x = center_x, int(width - center_x)
            up_y, down_y = int(height - center_y), center_y
            radius_x = min(left_x, right_x)
            radius_y = min(up_y, down_y)
            
        radius_x, radius_y = int(self.scale * radius_x), int(self.scale * radius_y)

        min_x, max_x = center_x - radius_x, center_x + radius_x
        min_y, max_y = center_y - radius_y, center_y + radius_y
        
        cropped = img[min_y:max_y, min_x:max_x]
        
        new_cropped = cv2.resize(cropped, (width, height))

        return new_cropped

    def touch_init(self):
        self.lock.acquire()
        self.center_x = self.WIDTH / 2
        self.center_y = self.HEIGHT / 2
        self.touched_zoom = False
        self.scale = 1
        self.lock.release()

    def zoom_out(self):
        # scale zoom-out
        self.lock.acquire()
        if self.scale < 1:
            self.scale += 0.1
            try:
                self.cmd_queue.put_nowait((self.scale, self.center_x, self.center_y))
            except Full:
                pass
            
        if self.scale == 1:
            self.center_x = self.WIDTH
            self.center_y = self.HEIGHT
            self.touched_zoom = False
        self.lock.release()

    def zoom_in(self):
        # scale zoom-in
        self.lock.acquire()
        if self.scale > 0.2:
            self.scale -= 0.1
            try:
                self.cmd_queue.put_nowait((self.scale, self.center_x, self.center_y))
            except Full:
                pass
        self.lock.release()

    def zoom(self, num):
        if num == 0:
            self.zoom_in()
        elif num == 1:
            self.zoom_out()
        elif num == 2:
            self.touch_init()

    def save_picture(self):
        # 
        ret, img = self.cam.read()
        if ret:
            now = datetime.datetime.now()
            date = now.strftime('%Y%m%d')
            hour = now.strftime('%H%M%S')
            user_id = '00001'
            filename = './images/cvui_{}_{}_{}.png'.format(date, hour, user_id)
            cv2.imwrite(filename, img)
            self.image_queue.put_nowait(filename)
            print(f"{filename}")

    # def record_video(self):
    #     # 
    #     fc = 20.0
    #     record_start_time = time.time()
    #     now = datetime.datetime.now()
    #     date = now.strftime('%Y%m%d')
    #     t = now.strftime('%H')
    #     num = 1
    #     filename = 'videos/cvui_{}_{}_{}.avi'.format(date, t, num)
    #     while os.path.exists(filename):
    #         num += 1
    #         filename = 'videos/cvui_{}_{}_{}.avi'.format(date, t, num)
    #     codec = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
    #     out = cv2.VideoWriter(filename, codec, fc, (int(self.cam.get(3)), int(self.cam.get(4))))
    #     while self.recording:
    #         if time.time() - record_start_time >= 600:
    #             self.record_video()
    #             break
    #         ret, frame = self.cam.read()
    #         if ret:
    #             if len(os.listdir('./videos')) >= 100:
    #                 name = self.video_queue.get()
    #                 if os.path.exists(name):
    #                     os.remove(name)
    #             out.write(frame)
    #             self.video_queue.put_nowait(filename)
    #         k = cv2.waitKey(1)
    #         if k == ord('q'):
    #             break

    def show(self):
        print("[show] Reading...")
        while True:
            # frame = self.data
            frame = self.data_queue.get()
            # print(f"frame: {frame.shape}")
            if frame is not None:
                cv2.imshow('CameraViewer', frame)
                cv2.setMouseCallback('CameraViewer', self.mouse_callback)
            key = cv2.waitKey(1)
            
            if key == ord('q'):
                # q : close
                self.release()
                cv2.destroyAllWindows()
                break

            elif key == ord('z'):
                # z : zoom - in
                self.zoom_in()

            elif key == ord('x'):
                # x : zoom - out
                self.zoom_out()

            elif key == ord('p'):
                # p : take picture and save image (image folder)
                self.save_picture()

            elif key == ord('v'):
                # v : zoom 상태를 원상태로 복구
                self.touch_init()

            # elif key == ord('r'):
            #     # r : 동영상 촬영 시작 및 종료
            #     self.recording = not self.recording
            #     if self.recording:
            #         t = Thread(target=cam.record_video)
            #         t.start()

    def release(self):
        self.stop = True
        self.cam.release()
        cv2.destroyAllWindows()
        try:           
            self.lock.release()
        except:
            pass

    def mouse_callback(self, event, x, y, flag, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.get_location(x, y)
            self.zoom_in()
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.zoom_out()


if __name__ == '__main__':
    mpath = "/home/pi/project/360-degree-escaping-submerged-2.mp4"
    cam = Camera(device=mpath, mirror=False)
    cam.stream()
    cam.show()
