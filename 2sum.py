def twoSum(arr, target):
  
    # Create a set to store the elements
    s = set()

    for num in arr:
      
        # Calculate the complement that added to
        # num, equals the target
        complement = target - num
        print("complement: ", complement, "num: ", num)
        
        # Check if the complement exists in the set
        if complement in s:
            return True

        # Add the current element to the set
        s.add(num)

    # If no pair is found
    return False

def twoSum1(nums, target):
    prevMap = {}  # val : index
    
    for i, n in enumerate(nums):
        diff = target - n
        
        if diff in prevMap:
            return [i, prevMap[diff]]
            
        prevMap[n] = i
        
    return[]


if __name__ == "__main__":
    
    arr = [0, -1, 2, -3, 1, 5]
    target = -2
    
    #if twoSum(arr, target):
    #    print("true")
    #else:
    #   print("false")
    
    result  = twoSum1(arr, target)
    if not result:
    	print("found no result")
    else:
        print("found:", result)