import picamera
camera = picamera.PiCamera()
camera.hflip = False
camera.vflip = False
camera.capture("test.jpg")
