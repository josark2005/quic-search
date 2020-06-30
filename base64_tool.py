import base64

file0 = "./0.mp3"
file1 = "./1.mp3"
file0_ = "./0.txt"
file1_ = "./1.txt"

with open(file0, 'rb') as f0:
    c = base64.b64encode(f0.read())
    print(c)
    f0_ = open(file0_, 'wb')
    f0_.write(c)

with open(file1, 'rb') as f1:
    c = base64.b64encode(f1.read())
    print(c)
    f1_ = open(file1_, 'wb')
    f1_.write(c)
