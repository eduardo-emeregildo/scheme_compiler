#for tracking upvalues at compile time:
#upvalue_requests store the upvalues that a function must pass to inner functions.

#The key is the function name where the upvalue is local. The value is a list
#of requests that the function must supply the inner function specified 
#thats asking for the upvalue

#each elt in the list is:
    #another list containing the details necessary to supply the upvalue
    #those elements being:
    #1) name of inner function to write to. this will be used to get the offset later
    #2) offset of variable
    #3) is_local
    #4) nest_count
    
class UpvalueTracker:
    def __init__(self):
        self.on = False
        self.upvalue_requests = {}
    
    def turn_tracker_off(self):
        self.on = False
        self.upvalue_requests = {}
    
    def turn_tracker_on(self):
        self.on = True
    
    def is_tracker_on(self):
        return self.on
    
    #returns upvalue requests for function_name
    def get_upvalue_requests(self,function_name):
        return self.upvalue_requests[function_name]
    
    def add_upvalue_request(self,function_name,request_arr):
        if function_name not in self.upvalue_requests:
            self.upvalue_requests[function_name] = []
            self.upvalue_requests[function_name].append(request_arr)
        else:
            self.upvalue_requests[function_name].append(request_arr)
    
    def function_has_requests(self,function_name):
        return function_name in self.upvalue_requests
    
    #for debugging
    def show_requests(self,function_name):
        requests = self.upvalue_requests[function_name]
        print(f"Requests for function: {function_name}")
        for i,data in enumerate(requests):
            print(f"Request {i}: ", data)        