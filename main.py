import sys
sys.path.append('./Identification')
from CreateProfile import create_profile


subscriptionKey = "ad32b1eb65614fae8c93c622658bc39c"
locale = "en-us"

create_profile(subscriptionKey, locale)