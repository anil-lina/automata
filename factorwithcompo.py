c=0
num= int(input("Enter the number to tested:"))
for x in range(2,num):
	if (num%x)==0:
		print(x)
		c+=1
if(c==0):
	print("Prime")
else:
	print("Composite")