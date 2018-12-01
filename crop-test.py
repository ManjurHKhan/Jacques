import picamera
camera = picamera.PiCamera()
camera.hflip = True
camera.vflip = True
camera.capture("test.jpg", resize=(380, 480))
