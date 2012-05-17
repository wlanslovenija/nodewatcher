# Based on http://code.djangoproject.com/ticket/5446
# Should be changed to use upstream code once it has been merged into it.

from django.conf import settings
from django.contrib.gis import utils as gis_utils
from django.db.models import fields
from django.utils import encoding as utils_encoding
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

# Countries list - ISO 3166-1
# http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
# http://en.wikipedia.org/wiki/List_of_national_capitals

COUNTRIES = (
  ('AD', _('Andorra'), _('Andorra la Vella')),
  ('AE', _('United Arab Emirates'), _('Abu Dhabi')),
  ('AF', _('Afghanistan'), _('Kabul')),
  ('AG', _('Antigua and Barbuda'), _("St. John's")),
  ('AI', _('Anguilla'), _('The Valley')),
  ('AL', _('Albania'), _('Tirana')),
  ('AM', _('Armenia'), _('Yerevan')),
  ('AN', _('Netherlands Antilles'), _('Willemstad')),
  ('AO', _('Angola'), _('Luanda')),
  ('AQ', _('Antarctica'), ''),
  ('AR', _('Argentina'), _('Buenos Aires')),
  ('AS', _('American Samoa'), _('Pago Pago')),
  ('AT', _('Austria'), _('Vienna')),
  ('AU', _('Australia'), _('Canberra')),
  ('AW', _('Aruba'), _('Oranjestad')),
  ('AX', _('Aland Islands'), _('Mariehamn')),
  ('AZ', _('Azerbaijan'), _('Baku')),
  ('BA', _('Bosnia and Herzegovina'), _('Sarajevo')),
  ('BB', _('Barbados'), _('Bridgetown')),
  ('BD', _('Bangladesh'), _('Dhaka')),
  ('BE', _('Belgium'), _('Brussels')),
  ('BF', _('Burkina Faso'), _('Ouagadougou')),
  ('BG', _('Bulgaria'), _('Sofia')),
  ('BH', _('Bahrain'), _('Manama')),
  ('BI', _('Burundi'), _('Bujumbura')),
  ('BJ', _('Benin'), _('Porto-Novo')),
  ('BL', _('Saint Barthelemy'), _('Gustavia')),
  ('BM', _('Bermuda'), _('Hamilton')),
  ('BN', _('Brunei'), _('Bandar Seri Begawan')),
  ('BO', _('Bolivia'), _('Sucre')),
  ('BR', _('Brazil'), _('Brasilia')),
  ('BS', _('Bahamas'), _('Nassau')),
  ('BT', _('Bhutan'), _('Thimphu')),
  ('BV', _('Bouvet Island'), ''),
  ('BW', _('Botswana'), _('Gaborone')),
  ('BY', _('Belarus'), _('Minsk')),
  ('BZ', _('Belize'), _('Belmopan')),
  ('CA', _('Canada'), _('Ottawa')),
  ('CC', _('Cocos (Keeling) Islands'), _('West Island')),
  ('CD', _('Congo, the Democratic Republic of the'), _('Kinshasa')),
  ('CF', _('Central African Republic'), _('Bangui')),
  ('CG', _('Congo, the Republic of the'), _('Brazzaville')),
  ('CH', _('Switzerland'), _('Bern')),
  ('CI', _('Ivory Coast'), _('Yamoussoukro')),
  ('CK', _('Cook Islands'), _('Avarua')),
  ('CL', _('Chile'), _('Santiago')),
  ('CM', _('Cameroon'), _('Yaounde')),
  ('CN', _('China'), _('Beijing')),
  ('CO', _('Colombia'), _('Bogota')),
  ('CR', _('Costa Rica'), _('San Jose')),
  ('CU', _('Cuba'), _('Havana')),
  ('CV', _('Cape Verde'), _('Praia')),
  ('CX', _('Christmas Island'), _('Flying Fish Cove')),
  ('CY', _('Cyprus'), _('Nicosia')),
  ('CZ', _('Czech Republic'), _('Prague')),
  ('DE', _('Germany'), _('Berlin')),
  ('DJ', _('Djibouti'), _('Djibouti')),
  ('DK', _('Denmark'), _('Copenhagen')),
  ('DM', _('Dominica'), _('Roseau')),
  ('DO', _('Dominican Republic'), _('Santo Domingo')),
  ('DZ', _('Algeria'), _('Algiers')),
  ('EC', _('Ecuador'), _('Quito')),
  ('EE', _('Estonia'), _('Tallinn')),
  ('EG', _('Egypt'), _('Cairo')),
  ('EH', _('Western Sahara'), _('El Aaiun')),
  ('ER', _('Eritrea'), _('Asmara')),
  ('ES', _('Spain'), _('Madrid')),
  ('ET', _('Ethiopia'), _('Addis Ababa')),
  ('FI', _('Finland'), _('Helsinki')),
  ('FJ', _('Fiji'), _('Suva')),
  ('FK', _('Falkland Islands'), _('Stanley')),
  ('FM', _('Micronesia'), _('Palikir')),
  ('FO', _('Faroe Islands'), _('Torshavn')),
  ('FR', _('France'), _('Paris')),
  ('GA', _('Gabon'), _('Libreville')),
  ('GB', _('United Kingdom'), _('London')),
  ('GD', _('Grenada'), _("St. George's")),
  ('GE', _('Georgia'), _('Tbilisi')),
  ('GF', _('French Guiana'), _('Cayenne')),
  ('GG', _('Guernsey'), _('Saint Peter Port')),
  ('GH', _('Ghana'), _('Accra')),
  ('GI', _('Gibraltar'), _('Gibraltar')),
  ('GL', _('Greenland'), _('Nuuk')),
  ('GM', _('Gambia'), _('Banjul')),
  ('GN', _('Guinea'), _('Conakry')),
  ('GP', _('Guadeloupe'), _('Basse-Terre')),
  ('GQ', _('Equatorial Guinea'), _('Malabo')),
  ('GR', _('Greece'), _('Athens')),
  ('GS', _('South Georgia and the South Sandwich Islands'), _('Grytviken')),
  ('GT', _('Guatemala'), _('Guatemala City')),
  ('GU', _('Guam'), _('Hagatna')),
  ('GW', _('Guinea-Bissau'), _('Bissau')),
  ('GY', _('Guyana'), _('Georgetown')),
  ('HK', _('Hong Kong'), _('Hong Kong')),
  ('HM', _('Heard Island and McDonald Islands'), ''),
  ('HN', _('Honduras'), _('Tegucigalpa')),
  ('HR', _('Croatia'), _('Zagreb')),
  ('HT', _('Haiti'), _('Port-au-Prince')),
  ('HU', _('Hungary'), _('Budapest')),
  ('ID', _('Indonesia'), _('Jakarta')),
  ('IE', _('Ireland'), _('Dublin')),
  ('IL', _('Israel'), _('Jerusalem')),
  ('IM', _('Isle of Man'), _('Douglas')),
  ('IN', _('India'), _('New Delhi')),
  ('IO', _('British Indian Ocean Territory'), _('Diego Garcia')),
  ('IQ', _('Iraq'), _('Iraq')),
  ('IR', _('Iran'), _('Tehran')),
  ('IS', _('Iceland'), _('Reykjavik')),
  ('IT', _('Italy'), _('Rome')),
  ('JE', _('Jersey'), _('Saint Helier')),
  ('JM', _('Jamaica'), _('Kingston')),
  ('JO', _('Jordan'), _('Amman')),
  ('JP', _('Japan'), _('Tokyo')),
  ('KE', _('Kenya'), _('Nairobi')),
  ('KG', _('Kyrgyzstan'), _('Bishkek')),
  ('KH', _('Cambodia'), _('Phnom Penh')),
  ('KI', _('Kiribati'), _('South Tarawa')),
  ('KM', _('Comoros'), _('Moroni')),
  ('KN', _('Saint Kitts and Nevis'), _('Basseterre')),
  ('KP', _('North Korea'), _('Pyongyang')),
  ('KR', _('South Korea'), _('Seoul')),
  ('KW', _('Kuwait'), _('Kuwait City')),
  ('KY', _('Cayman Islands'), _('George Town')),
  ('KZ', _('Kazakhstan'), _('Astana')),
  ('LA', _('Laos'), _('Vientiane')),
  ('LB', _('Lebanon'), _('Beirut')),
  ('LC', _('Saint Lucia'), _('Castries')),
  ('LI', _('Liechtenstein'), _('Vaduz')),
  ('LK', _('Sri Lanka'), _('Sri Jayawardenepura Kotte')),
  ('LR', _('Liberia'), _('Monrovia')),
  ('LS', _('Lesotho'), _('Maseru')),
  ('LT', _('Lithuania'), _('Vilnius')),
  ('LU', _('Luxembourg'), _('Luxembourg City')),
  ('LV', _('Latvia'), _('Riga')),
  ('LY', _('Libya'), _('Tripoli')),
  ('MA', _('Morocco'), _('Rabat')),
  ('MC', _('Monaco'), _('Monaco')),
  ('MD', _('Moldova'), _('Chisinau')),
  ('ME', _('Montenegro'), _('Podgorica')),
  ('MG', _('Madagascar'), _('Antananarivo')),
  ('MH', _('Marshall Islands'), _('Majuro')),
  ('MK', _('Macedonia'), _('Skopje')),
  ('ML', _('Mali'), _('Bamako')),
  ('MM', _('Myanmar'), _('Naypyidaw')),
  ('MN', _('Mongolia'), _('Ulaanbaatar')),
  ('MO', _('Macao'), _('Macao')),
  ('MP', _('Northern Mariana Islands'), _('Saipan')),
  ('MQ', _('Martinique'), _('Fort-de-France')),
  ('MR', _('Mauritania'), _('Nouakchott')),
  ('MS', _('Montserrat'), _('Brades')),
  ('MT', _('Malta'), _('Valletta')),
  ('MU', _('Mauritius'), _('Port Louis')),
  ('MV', _('Maldives'), _('Male')),
  ('MW', _('Malawi'), _('Lilongwe')),
  ('MX', _('Mexico'), _('Mexico City')),
  ('MY', _('Malaysia'), _('Putrajaya')),
  ('MZ', _('Mozambique'), _('Maputo')),
  ('NA', _('Namibia'), _('Windhoek')),
  ('NC', _('New Caledonia'), _('Noumea')),
  ('NE', _('Niger'), _('Niamey')),
  ('NF', _('Norfolk Island'), _('Kingston')),
  ('NG', _('Nigeria'), _('Abuja')),
  ('NI', _('Nicaragua'), _('Managua')),
  ('NL', _('Netherlands'), _('Amsterdam')),
  ('NO', _('Norway'), _('Oslo')),
  ('NP', _('Nepal'), _('Kathmandu')),
  ('NR', _('Nauru'), _('Yaren')),
  ('NU', _('Niue'), _('Alofi')),
  ('NZ', _('New Zealand'), _('Wellington')),
  ('OM', _('Oman'), _('Muscat')),
  ('PA', _('Panama'), _('Panama City')),
  ('PE', _('Peru'), _('Lima')),
  ('PF', _('French Polynesia'), _('Papeete')),
  ('PG', _('Papua New Guinea'), _('Port Moresby')),
  ('PH', _('Philippines'), _('Manila')),
  ('PK', _('Pakistan'), _('Islamabad')),
  ('PL', _('Poland'), _('Warsaw')),
  ('PM', _('Saint Pierre and Miquelon'), _('St. Pierre')),
  ('PN', _('Pitcairn Islands'), _('Adamstown')),
  ('PR', _('Puerto Rico'), _('San Juan')),
  ('PS', _('Palestine'), _('Jerusalem')),
  ('PT', _('Portugal'), _('Lisbon')),
  ('PW', _('Palau'), _('Ngerulmud')),
  ('PY', _('Paraguay'), _('Asuncion')),
  ('QA', _('Qatar'), _('Doha')),
  ('RE', _('Reunion'), _('Saint-Denis')),
  ('RO', _('Romania'), _('Bucharest')),
  ('RS', _('Serbia'), _('Belgrade')),
  ('RU', _('Russia'), _('Moscow')),
  ('RW', _('Rwanda'), _('Kigali')),
  ('SA', _('Saudi Arabia'), _('Riyadh')),
  ('SB', _('Solomon Islands'), _('Honiara')),
  ('SC', _('Seychelles'), _('Victoria')),
  ('SD', _('Sudan'), _('Khartoum')),
  ('SE', _('Sweden'), _('Stockholm')),
  ('SG', _('Singapore'), _('Singapore')),
  ('SH', _('Saint Helena'), _('Jamestown')),
  ('SI', _('Slovenia'), _('Ljubljana')),
  ('SJ', _('Svalbard and Jan Mayen'), _('Longyearbyen')),
  ('SK', _('Slovakia'), _('Bratislava')),
  ('SL', _('Sierra Leone'), _('Freetown')),
  ('SM', _('San Marino'), _('San Marino')),
  ('SN', _('Senegal'), _('Dakar')),
  ('SO', _('Somalia'), _('Mogadishu')),
  ('SR', _('Suriname'), _('Paramaribo')),
  ('ST', _('Sao Tome and Principe'), _('Sao Tome')),
  ('SV', _('El Salvador'), _('San Salvador')),
  ('SY', _('Syria'), _('Damascus')),
  ('SZ', _('Swaziland'), _('Mbabane')),
  ('TC', _('Turks and Caicos Islands'), _('Cockburn Town')),
  ('TD', _('Chad'), _("N'Djamena")),
  ('TF', _('French Southern Territories'), _('Port-aux-Francais')),
  ('TG', _('Togo'), _('Lome')),
  ('TH', _('Thailand'), _('Bangkok')),
  ('TJ', _('Tajikistan'), _('Dushanbe')),
  ('TK', _('Tokelau'), _('Nukunonu')),
  ('TL', _('Timor-Leste'), _('Dili')),
  ('TM', _('Turkmenistan'), _('Ashgabat')),
  ('TN', _('Tunisia'), _('Tunis')),
  ('TO', _('Tonga'), _("Nuku'alofa")),
  ('TR', _('Turkey'), _('Ankara')),
  ('TT', _('Trinidad and Tobago'), _('Port of Spain')),
  ('TV', _('Tuvalu'), _('Funafuti')),
  ('TW', _('Taiwan'), _('Taipei')),
  ('TZ', _('Tanzania'), _('Dodoma')),
  ('UA', _('Ukraine'), _('Kiev')),
  ('UG', _('Uganda'), _('Kampala')),
  ('UM', _('United States Minor Outlying Islands'), _('Wake Island')),
  ('US', _('United States'), _('Washington, D.C.')),
  ('UY', _('Uruguay'), _('Montevideo')),
  ('UZ', _('Uzbekistan'), _('Tashkent')),
  ('VA', _('Vatican City'), _('Vatican City')),
  ('VC', _('Saint Vincent and the Grenadines'), _('Kingstown')),
  ('VE', _('Venezuela'), _('Caracas')),
  ('VG', _('Virgin Islands, British'), _('Road Town')),
  ('VI', _('Virgin Islands, United States'), _('Charlotte Amalie')),
  ('VN', _('Vietnam'), _('Hanoi')),
  ('VU', _('Vanuatu'), _('Port Vila')),
  ('WF', _('Wallis and Futuna'), _('Mata-Utu')),
  ('WS', _('Samoa'), _('Apia')),
  ('YE', _('Yemen'), _('Sanaa')),
  ('YT', _('Mayotte'), _('Mamoudzou')),
  ('ZA', _('South Africa'), _('Pretoria')),
  ('ZM', _('Zambia'), _('Lusaka')),
  ('ZW', _('Zimbabwe'), _('Harare')),
  ('ZZ', _('Unknown or unspecified country'), ''),
)

def sorted_countries(countries):
  """
  Sort countries for a given language.
  
  Assume ZZ is the last entry, keep it last.
  """
  
  c = [c[0:2] for c in countries[:-1]]
  c.sort(key=lambda x: x[1])
  c.append(countries[-1][0:2])
  return tuple(c)

countries_choices = sorted_countries(COUNTRIES)
languages_choices = map(lambda (code, name): (code, _(name)), settings.LANGUAGES) # We have to translate names
countries_cities = dict([(c[0], c[2]) for c in COUNTRIES[:-1]])

CITIES = sorted(countries_cities.values())

geoip_resolver = gis_utils.GeoIP()

def get_initial_country(request=None):
  """
  Returns a contry code based on a client's remote address or settings.
  """
  
  if request:
    country = geoip_resolver.country_code(request.META['REMOTE_ADDR'])
    if country and country.upper() in countries_cities:
      return country.upper()
  return settings.DEFAULT_COUNTRY

def get_initial_city(request=None):
  """
  Returns a city name based on a client's remote address or a default city from her country.
  """
  
  # We force unicode here so that default value in a field is a proper unicode string and not a lazy one
  # Otherwise psycopg2 raises an "can't adapt" error: http://code.djangoproject.com/ticket/13965

  if request:
    city = geoip_resolver.city(request.META['REMOTE_ADDR'])
    if city and city.get('city'):
      return city['city']
    return utils_encoding.force_unicode(countries_cities[get_initial_country(request)]) or getattr(settings, 'DEFUALT_CITY', None)
  return getattr(settings, 'DEFUALT_CITY', None) or utils_encoding.force_unicode(countries_cities[get_initial_country()])

def get_initial_language(request=None):
  """
  Returns language code based on a request or settings.
  """
  
  if request:
    return translation.get_language_from_request(request)
  return settings.LANGUAGE_CODE

class CountryField(fields.CharField):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault('max_length', 2)
    kwargs.setdefault('choices', countries_choices)
    kwargs.setdefault('default', get_initial_country)

    super(fields.CharField, self).__init__(*args, **kwargs)

  def get_internal_type(self):
    return "CharField"

class CityField(fields.CharField):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault('max_length', 150)
    kwargs.setdefault('default', get_initial_city)

    super(fields.CharField, self).__init__(*args, **kwargs)

  def get_internal_type(self):
    return "CharField"

class LanguageField(fields.CharField):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault('max_length', 5)
    kwargs.setdefault('choices', languages_choices)
    kwargs.setdefault('default', get_initial_language)

    super(fields.CharField, self).__init__(*args, **kwargs)

  def get_internal_type(self):
    return "CharField"
