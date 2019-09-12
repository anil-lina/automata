num= int(input("Enter the number to tested:"))
x=2
for x in range(2,int(round((num+1)/2))):
	if (num%x)==0:
		print(num,"is not a prime number")
		break
else :
		print(num,"is a prime number")