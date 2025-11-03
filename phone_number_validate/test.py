import phonenumbers
from phonenumbers import geocoder, carrier, timezone

phone_number = "+917306126890"  # +91 = IND country code
parsed_number = phonenumbers.parse(phone_number)
print("Phone number", phone_number)
print("parsed as", parsed_number)
print(type(parsed_number)
print("is valid?", phonenumbers.is_valid_number(parsed_number))
print("is possible?", phonenumbers.is_possible_number(parsed_number))

print("region:", geocoder.description_for_number(parsed_number, "en"))
print("carrier:", carrier.name_for_number(parsed_number, "en"))
print("time zones:", timezone.time_zones_for_number(parsed_number))