print("2 x 1 = 2")
print("2 x 2 = 4")
print("2 x 3 = 6")
print("2 x 4 = 8")

print("-------------")
for i in range(1,5) :
    print(f"2 x {i} = {i*2}")

print("-------------")
for j in range(2,10) : 
    for i in range(1,5) :
        print(f"{j} x {i} = {j*i}")
    print()

print("-------------")

'''
2 x 1 = 2   3 x 1 = 3   4 x 1 = 4   5 x 1 = 5
2 x 2 = 4   3 x 2 = 6   4 x 2 = 8   5 x 2 = 10
2 x 3 = 6   3 x 3 = 9   4 x 3 = 12  5 x 3 = 15
'''
for j in range(1,4) : 
    for i in range(2,6) :
        print(f"{i} x {j} = {j*i}", end = "\t")
    print("\n")


 