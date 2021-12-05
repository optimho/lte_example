
class ComplexNumber:
  def __init__(self,r=0,i=0):
    self.real = r
    self.imag = i

  def getData(self):
    print("{0+}+{1}j".format(self.real,self.imag))
    