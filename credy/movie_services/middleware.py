from asyncio import sleep

count = 0


def getcount():
    global count
    return count


def reset():
    global count
    count = 0
    return count


class RequestCounterMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global count
        count = count + 1
        response = self.get_response(request)
        # sleep(1)
        return response