# -*- coding: utf-8 -*-
import random
import uuid

from itertools import product

from faker.providers import BaseProvider

from .data import (
    countries, fields, adjectives, words, first_names, last_names
)


class GeneratorProvider(BaseProvider):
    """
    Uses a generator to produce results. On exhaustion a new generator will be
    created. Subclasses must implement get_generator() and call next()
    to get the next value from the generator.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_generator = self.get_generator()

    def get_generator(self):
        """
        Return a generator for next to get values from.
        """
        raise NotImplementedError()

    def next(self):
        """
        Return the next value from the generator.
        """
        try:
            return next(self.token_generator)
        # On exhaustion re-initialize the generator.
        except StopIteration:
            self.token_generator = self.get_generator()
            return next(self.token_generator)


class InfiniteIncrementer:
    """
    Generator to produce an infinite series of incrementing integers.
    """

    def __init__(self, start=0, step=1):
        self.start = start
        self.step = step

    def __next__(self):
        self.start += self.step
        return self.start - self.step


class DOIProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer()

    def doi(self):
        return '10.1234/PUBLONS.TEST.{}'.format(self.next())


class PMIDProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer()

    def pmid(self):
        return str(self.next())


class ARXIVProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer(start=1000)

    def arxiv(self):
        i = self.next()
        return '{}.{}'.format(i, i)


class UTProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer(start=100000000000000)

    def ut(self, prefix='WOS'):
        return '{}:{}'.format(prefix, self.next())


class IDProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer(start=1)

    def id(self, offset=0):
        return offset + self.next()


class NumberProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer()

    def number(self, offset=1):
        return self.next()


class ManuscriptIDProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer()

    def manuscript_id(self):
        return 'Manuscript:ID-{}'.format(self.next())


class PublisherNameProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer()

    def publisher_name(self):
        return 'Publisher {}'.format(self.next())


class PublicationProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer()

    def publication_title(self):
        return 'Publication {}'.format(self.next())


class InstitutionProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer()

    def institution_name(self):
        return 'Institution {}'.format(self.next())


class CountryProvider(GeneratorProvider):
    def get_generator(self):
        return product(countries)

    def country_name(self):
        country = self.next()
        return '{}'.format(country)[:50]


class AffiliationProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer()

    def affiliation_name(self):
        return 'Affiliation {}'.format(self.next())


class NameProvider(GeneratorProvider):
    def get_generator(self):
        return product(first_names, last_names)

    def name(self):
        first_name, last_name = self.next()
        return '{} {}'.format(first_name, last_name)


class JournalNameProvider(GeneratorProvider):
    def get_generator(self):
        return product(countries, adjectives, fields)

    def journal_name(self):
        country, adjective, field = self.next()
        return 'The {} journal of {} {}'.format(country, adjective, field)


class ISSNProvider(GeneratorProvider):
    def get_generator(self):
        return InfiniteIncrementer(start=1000000)

    def issn(self):
        base = str(self.next())
        count = sum([(8 - i) * int(char) for i, char in enumerate(base)]) % 11
        if count == 1:
            check = 'X'
        elif count == 0:
            check = '0'
        else:
            check = str(11 - count)
        return '{}-{}{}'.format(str(base)[:4], str(base)[4:], check)


class EmailProvider(GeneratorProvider):
    """
    Emails in the forms on "adjective.last_name@test.com".
    """

    def get_generator(self):
        return product(adjectives, last_names)

    def email(self):
        adjective, last_name = self.next()
        return '{}.{}@test.com'.format(adjective.lower(), last_name.lower())


class GibberishProvider(GeneratorProvider):
    """
    Sentences of 3 common English words.
    """

    def get_generator(self):
        return product(words, words, words)

    def gibberish(self):
        return ' '.join(self.next())


class ORCIDProvider(GeneratorProvider):
    """
    Generate ORCIDs.
    https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier

    START value for generator should be at least 15000000, to generate a valid
    orcid with functionality below.
    Maximum value of the counter for use in a valid ORCID is 35000000, so we
    can generate up to 20,000,000 valid ORCIDs.
    """

    START = 15040608
    # Added some non-zero digits (after opening with 15) for cosmetic reasons.
    # This slightly reduces the maximum number of valid ORCIDs we can generate.

    def get_generator(self):
        return InfiniteIncrementer(start=self.START)

    def orcid(self):
        counter = self.next()
        base_digits = '0000000{}'.format(counter)
        # String with 15 digits.

        total = 0
        for i in range(15):
            total = (total + int(base_digits[i])) * 2
        remainder = total % 11
        result = (12 - remainder) % 11
        if result == 10:
            check_digit = 'X'
        else:
            check_digit = str(result)

        return '-'.join(
            [
                base_digits[:4],
                base_digits[4:8],
                base_digits[8:12],
                base_digits[12:15] + check_digit,
            ]
        )


class ResearcherIDProvider(GeneratorProvider):
    """
    Eg MMM-5306-2017 where 2017 represents the year of
    joining ResearcherID (launched 2008).
    """

    def get_generator(self):
        return InfiniteIncrementer(start=1000)

    def researcher_id(self, letters=None, number=None, year=None):
        letters = letters if letters else self.random_uppercase_letter() * 3
        number = number if number else self.next()
        year = year if year else random.randint(2008, 2018)
        return '{}-{}-{}'.format(letters, number, year)


class TruidProvider(BaseProvider):
    """
    PlatformAuth truid == uuid.
    """

    def truid(self):
        return str(uuid.uuid4())
