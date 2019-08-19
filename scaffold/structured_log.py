class StructuredMessage:
    message = ''
    kwargs = {}
    def __init__(self, message, **kwargs):
        self.message
        self.kwargs = kwargs
    
    def __str__(self):
        return '{} >>> {}'.format(self.message, self.kwargs)
