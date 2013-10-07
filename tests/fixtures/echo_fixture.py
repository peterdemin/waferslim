class EchoFixture(object):
    not_method = 'Should not be provided'

    def echo(self, value):
        return value

    @staticmethod
    def static_echo(value):
        return value

    @classmethod
    def class_echo(cls, value):
        return value
