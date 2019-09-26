import os,shutil
file_ext,all_files,all_file_ext=[],[],[]
print("Finding Present working directory")
cur_dir=os.getcwd()
print("Found Present Working Directory as ", cur_dir)
print("Scanning the current directory for files")
obj1 = os.walk(cur_dir)
for files in obj1:
    for i in files[2]:
        all_files.append(i)
        all_file_ext.append(i.split("."))
        file_ext.append(i.split(".")[1])
print("Files found in present directory are ",all_files)
uni=set(file_ext)
print("Extensions found are ",uni)
for i in uni:
    os.mkdir(cur_dir+"\\"+i)
    print("Creating folder ",i," in ",cur_dir)
for i in uni:
    for j in all_file_ext:
        if i == j[1]:
            fn=j[0]+"."+j[1]
            src = cur_dir+"\\"+fn
            des= cur_dir+"\\"+i+"\\"+fn
            print("Moving file ",fn," from ",src,"to ",des)
            shutil.move(src,des)