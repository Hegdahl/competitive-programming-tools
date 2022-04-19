'''
Provides :py:class:`OnlineJudge`.
'''

import re

from ..languages.language import Language


class OnlineJudge:
    '''
    Base class for online judges.
    '''

    FORMAT = ''
    URL_PATTERN = ''

    def __init_subclass__(cls, **kwargs):
        for required in ('FORMAT', 'URL_PATTERN', 'submit'):
            if not getattr(cls, required):
                raise TypeError('Can not instantiate abstract class '
                                f'{cls.__name__} without {required} '
                                'attribute defined')
        return super().__init_subclass__(**kwargs)

    @classmethod
    def accepts_url(cls, url: str):
        '''
        Determine if the given `url`
        is for a problem the descendant class knows
        how to submit solutions to.
        '''
        assert cls != OnlineJudge
        return re.match(cls.URL_PATTERN, url) is not None

    async def submit(self, url: str, solution: str, lang: Language):
        '''
        Submit the solution to the online judge
        the subclass is responsible for.
        '''
        raise TypeError('This method should be overriden.')
