from faker import Faker

from .providers import (
    AffiliationProvider,
    ARXIVProvider,
    CountryProvider,
    DOIProvider,
    EmailProvider,
    GibberishProvider,
    IDProvider,
    InstitutionProvider,
    ISSNProvider,
    JournalNameProvider,
    ManuscriptIDProvider,
    NameProvider,
    NumberProvider,
    ORCIDProvider,
    PMIDProvider,
    PublicationProvider,
    PublisherNameProvider,
    ResearcherIDProvider,
    TruidProvider,
    UTProvider,
)

# Singleton to register custom providers.
fake = Faker()
fake.seed(642)

fake.add_provider(AffiliationProvider)
fake.add_provider(ARXIVProvider)
fake.add_provider(CountryProvider)
fake.add_provider(DOIProvider)
fake.add_provider(EmailProvider)
fake.add_provider(GibberishProvider)
fake.add_provider(IDProvider)
fake.add_provider(InstitutionProvider)
fake.add_provider(ISSNProvider)
fake.add_provider(JournalNameProvider)
fake.add_provider(ManuscriptIDProvider)
fake.add_provider(NameProvider)
fake.add_provider(NumberProvider)
fake.add_provider(ORCIDProvider)
fake.add_provider(PMIDProvider)
fake.add_provider(PublicationProvider)
fake.add_provider(PublisherNameProvider)
fake.add_provider(ResearcherIDProvider)
fake.add_provider(TruidProvider)
fake.add_provider(UTProvider)
