from pocket import Pocket

def login_values(KEY, REDIRECT):
	request_token = Pocket.get_request_token(consumer_key=KEY, redirect_uri=REDIRECT)
	auth_url = Pocket.get_auth_url(code=request_token, redirect_uri=REDIRECT)

	values = [request_token, auth_url]
	return values

def authenticate(KEY, TOKEN):
	user_credentials = Pocket.get_credentials(consumer_key=KEY, code=TOKEN)
	access_token = user_credentials['access_token']

	auth_values = [user_credentials, access_token]
	return auth_values

consumer_key = raw_input("Enter Consumer Key: ")
values = login_values(consumer_key, "http://www.ceskavich.com/")

auth_url = values[1]

print "Please go here:", auth_url
print "----"

print "Your request token is:", values[0]
token = raw_input("Input the above token now: ")

auth_values = authenticate(consumer_key, token)

print "----"
print "User credentials:", auth_values[0]
print "Access Token:", auth_values[1]

